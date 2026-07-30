"""PRDBench evaluation runner — drives penguin-coding through the full DEV + EVAL pipeline.

Matches PRDBench's actual evaluation flow, with three hardening changes:
  - DEV:  agent develops code in src/ from PRD.md ONLY — the evaluation/
          materials (test plan, rubrics, expected outputs) are NOT copied into
          the dev workspace (no teaching to the test).
  - EVAL: ready_test.py-style, one prompt per METRIC, agent writes
          {metric_name}.json. evaluation/ is pulled from the source benchmark
          on demand. src/ is snapshotted before eval and verified/restored
          after each metric so a tampering evaluator cannot fake passes.
  - SCORE: reads reports/{metric_name}.json; the denominator is the FULL
          metric set from detailed_test_plan.json (missing metrics score 0).

DEV and EVAL modes run projects in parallel (see --workers).

Usage:
    # DEV stage — develop code from PRD
    python -m src.prdbench.run_evaluation \\
        --source_dir PRDbench/ \\
        --mode dev \\
        --round 1

    # EVAL stage — evaluate developed code
    python -m src.prdbench.run_evaluation \\
        --root_path workspace/penguin_dev_output \\
        --mode eval \\
        --round 1

    # SCORE stage — calculate scores
    python -m src.prdbench.run_evaluation \\
        --root_path workspace/penguin_dev_output \\
        --mode score
"""

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .adapter import run_prdbench_agent, PRDBenchSession, session_manager
from .prompts import DEVELOPMENT_PROMPT, DEBUG_PROMPT, EVALUATION_PROMPT
from .config import WORKSPACE_DIR, MAX_ITERATIONS

logger = logging.getLogger("penguin.prdbench.runner")


# ── Report validation ──

def check_report_format(report_file: str) -> bool:
    """Check if the report file has valid format with score fields."""
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return False

        # JSON array
        if content.startswith("[") and content.endswith("]"):
            items = json.loads(content)
            return any(isinstance(i, dict) and "score" in i for i in items)

        # JSONL or single JSON object
        lines = [l for l in content.splitlines() if l.strip()]
        valid = 0
        for line in lines:
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and "score" in obj:
                    valid += 1
            except json.JSONDecodeError:
                pass
        return valid > 0

    except Exception:
        return False


def check_metric_json(metric_file: str) -> bool:
    """Check if a single metric JSON file is valid (has metric, score, explanation)."""
    try:
        with open(metric_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, str):
            data = json.loads(data)
        return (
            isinstance(data, dict)
            and "score" in data
            and isinstance(data["score"], (int, float))
            and 0 <= data["score"] <= 2
        )
    except Exception:
        return False


# ── Load test plan ──

def load_test_plan(test_plan_path: str) -> list[dict] | None:
    """Load detailed_test_plan.json."""
    try:
        with open(test_plan_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load test plan from {test_plan_path}: {e}")
        return None


# ── DEV stage ──

def run_dev_project(
    project_id: int,
    source_dir: str,
    root_path: str,
    max_iterations: int = MAX_ITERATIONS,
    log_dir: str | None = None,
    run_id: str | None = None,
) -> bool:
    """Run DEV stage: agent reads PRD.md and develops code in src/.

    Only src/ (which contains PRD.md) is copied into the workspace. The
    evaluation/ materials are deliberately withheld so the agent cannot
    tailor the implementation to the test plan or copy expected outputs;
    EVAL mode pulls them from source_dir on demand.
    """
    project_dir = os.path.abspath(os.path.join(root_path, str(project_id)))
    os.makedirs(project_dir, exist_ok=True)

    # Copy PRD from source — evaluation materials stay out of the dev workspace
    src_source = os.path.join(source_dir, str(project_id), "src")
    src_target = os.path.join(project_dir, "src")

    if os.path.exists(src_source) and not os.path.exists(src_target):
        shutil.copytree(src_source, src_target)

    # Skip if already developed
    output_path = os.path.join(project_dir, "query_response.json")
    if os.path.exists(output_path):
        logger.info(f"Project {project_id} already developed, skipping")
        return True

    prompt = DEVELOPMENT_PROMPT.format(
        ID=project_id,
        project_path=project_dir,
    )

    session_id = f"dev_{project_id}"
    session = session_manager.create(session_id, "penguin", "code_agent_local")

    logger.info(f"DEV project {project_id}: {project_dir}")
    log_file = None
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        rid = run_id or "default"
        log_file = os.path.join(log_dir, f"dev_{project_id}_{rid}.jsonl")
    result = run_prdbench_agent(
        user_message=prompt,
        session=session,
        mode="dev",
        max_iterations=max_iterations,
        log_file=log_file,
        run_id=run_id,
    )

    # Only mark the project as developed on success. A failed run writes its
    # result to query_response.error.json instead, so reruns will retry it.
    if result.get("status") == "success":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        error_path = os.path.join(project_dir, "query_response.error.json")
        try:
            with open(error_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except OSError:
            pass
        logger.error(
            f"DEV project {project_id} failed (status={result.get('status')}); "
            "not marking as developed — rerun dev mode to retry"
        )

    session_manager.delete(session_id)
    logger.info(f"DEV project {project_id} done (status={result.get('status')})")
    return result.get("status") == "success"


# ── src/ integrity snapshot (anti-tamper for EVAL) ──

SRC_SNAPSHOT_DIR_NAME = ".src_integrity_snapshot"
_SNAPSHOT_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".git")


def _hash_tree(src_dir: str) -> dict[str, tuple[str, int]]:
    """Hash every file under src_dir -> {relpath: (sha256, size)}."""
    hashes: dict[str, tuple[str, int]] = {}
    for dirpath, dirnames, filenames in os.walk(src_dir):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for filename in sorted(filenames):
            if filename.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, src_dir)
            try:
                digest = hashlib.sha256()
                with open(full, "rb") as f:
                    for chunk in iter(lambda: f.read(1 << 20), b""):
                        digest.update(chunk)
                hashes[rel] = (digest.hexdigest(), os.path.getsize(full))
            except OSError:
                continue
    return hashes


def _snapshot_src(project_dir: str) -> str | None:
    """Back up src/ so EVAL-stage tampering can be detected and reverted."""
    src_dir = os.path.join(project_dir, "src")
    if not os.path.isdir(src_dir):
        return None
    backup_dir = os.path.join(project_dir, SRC_SNAPSHOT_DIR_NAME)
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    shutil.copytree(src_dir, backup_dir, ignore=_SNAPSHOT_IGNORE)
    return backup_dir


def _verify_and_restore_src(project_dir: str, backup_dir: str | None) -> dict:
    """Diff src/ against the snapshot; restore modified/deleted files.

    Returns {"modified": [...], "deleted": [...], "added": [...]}.
    Added files (typically outputs produced by running the project during a
    test) are kept but recorded; modified or deleted files are restored from
    the snapshot so later metrics still evaluate the original code.
    """
    result: dict[str, list[str]] = {"modified": [], "deleted": [], "added": []}
    src_dir = os.path.join(project_dir, "src")
    if not backup_dir or not os.path.isdir(backup_dir):
        return result

    before = _hash_tree(backup_dir)
    after = _hash_tree(src_dir) if os.path.isdir(src_dir) else {}

    result["deleted"] = sorted(before.keys() - after.keys())
    result["added"] = sorted(after.keys() - before.keys())
    result["modified"] = sorted(
        rel for rel in before.keys() & after.keys() if before[rel] != after[rel]
    )

    for rel in result["modified"] + result["deleted"]:
        src_file = os.path.join(backup_dir, rel)
        dst_file = os.path.join(src_dir, rel)
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copy2(src_file, dst_file)

    return result


# ── EVAL stage (per-metric, matching PRDBench's ready_test.py) ──

def transfer_metric_abs_path(metric_data: dict, project_dir: str) -> dict:
    """Convert relative paths in metric_data to absolute paths."""
    import copy
    data = copy.deepcopy(metric_data)

    testcases = data.get("testcases", [])
    if isinstance(testcases, dict):
        testcases = [testcases]

    for testcase in testcases:
        test_input = testcase.get("test_input", "")
        if test_input and not os.path.isabs(test_input):
            abs_path = os.path.join(project_dir, test_input)
            if os.path.exists(abs_path):
                testcase["test_input"] = abs_path

        test_command = testcase.get("test_command", "")
        if test_command:
            testcase["test_command"] = f"cd {project_dir} && {test_command}"

    input_files = data.get("input_files", [])
    if input_files:
        new_files = []
        for f in input_files:
            if os.path.isabs(f):
                new_files.append(f)
            else:
                abs_path = os.path.join(project_dir, f)
                new_files.append(abs_path if os.path.exists(abs_path) else f)
        data["input_files"] = new_files

    return data


# Metric IDs may have arbitrary depth: 1.1, 0.1.1, 2.5.1a, 2.2.2.1b (project 34).
# Truncating to three levels collapses distinct four-level metrics onto the
# same rubric, so match the full ID instead.
_METRIC_ID_RE = re.compile(r"^(\d+(?:\.\d+)+[a-z]?)")


def _extract_metric_id(metric_name: str) -> str | None:
    match = _METRIC_ID_RE.match(metric_name)
    return match.group(1) if match else None


def _load_rubric_by_metric_id(metric_json_path: str) -> dict[str, str]:
    """Load metric.json, index rubric expected_output by metric ID prefix.

    metric.json uses '&', detailed_test_plan.json uses 'and' in metric names,
    so matching by ID prefix (e.g. '0.1.1') is more robust than full name.
    """
    try:
        with open(metric_json_path, "r", encoding="utf-8") as f:
            rubrics = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load rubric from {metric_json_path}: {e}")
        return {}

    index: dict[str, str] = {}
    for item in rubrics:
        metric_name = item.get("metric", "")
        metric_id = _extract_metric_id(metric_name)
        if metric_id:
            index[metric_id] = item.get("expected_output", "")
    return index


def build_eval_prompt(
    metric_data: dict,
    project_dir: str,
    metric_report_file: str,
    retry_round: int = 0,
    rubric_text: str | None = None,
) -> str:
    """Build the per-metric evaluation prompt (matches PRDBench's ready_test.py format)."""
    metric_name = metric_data.get("metric", "Unknown Metric")
    description = metric_data.get("description", "")

    abs_metric_data = transfer_metric_abs_path(metric_data, project_dir)

    if rubric_text:
        scoring_block = f"""### Scoring Rubric (authoritative)
Score the metric according to the rubric below. The rubric is the source of truth for 0/1/2 thresholds.

{rubric_text}

The score must be 0, 1, or 2."""
    else:
        scoring_block = """The score should be 0, 1, or 2.
0 means the test metric is completely not passed.
1 means the test metric is partially passed. For shell_interaction and file_comparison types, this indicates that all steps except the final verification step are correct; for unit_test type, this means that pytest runs without any module import errors.
2 means the test metric is completely passed."""

    prompt = f"""[Round {retry_round}] ### Task
Please evaluate the implementation of {project_dir} based on the evaluation metric: {metric_name}. The project code is located in the src/ directory and the evaluation auxiliary files are located in the evaluation/ directory.
The code should be completed strictly in accordance with the evaluation criteria to be considered qualified. If the code fails to run or adapt to the interface, please directly give the current test point a score of 0.

### Evaluation Metric Details
{json.dumps(abs_metric_data, ensure_ascii=False, indent=2)}

- 'metric': the metric name
- 'description'(Important): Arrange-Act-Assert description of the test metric
- 'type': the type of the test metric, can be 'unit_test', 'shell_interaction' and 'file_comparison'
- 'testcases': reference execution commands and input files
- 'expected_output' / 'expected_output_files': expected output after executing the testcases
- 'input_files': input files for the testcases

### Path Instructions
The project code is located in the {project_dir}/src/ directory. DO NOT MODIFY THE PROJECT CODE.
DO NOT MODIFY THE EVALUATION CRITERIA. DO NOT MODIFY ANY FILES UNDER THE {project_dir}/evaluation DIRECTORY.
The evaluation report must be saved to {metric_report_file} in JSON format.
If you encounter a "No such file or directory" error, please check whether you are in the correct problem path and whether the path has omitted the problem number.

### Tips
If the code is unable to run, please give the score of 0 and report it in the report.
Use the write_file tool to write the report content into a file, passing it to the content variable as a string type when writing.
If the metric has more than one testcase, you should use "start_interactive_shell" tool to start a new shell session for each testcase. And if you need to input content to the shell, use the "run_interactive_shell" tool.

### *Important* File Output Requirement
After completing your evaluation, you MUST write the evaluation result to a JSON file at the following path:
{metric_report_file}

The JSON file should contain the evaluation result in the following format:
{{"metric": "{metric_name}",
"description": "{description}",
"score": <0-2>,
"explanation": "Detailed explanation of the evaluation result"
}}

{scoring_block}

### Final Reminder
The interface of the code must be completed strictly in accordance with the evaluation criteria to be considered qualified.
If the code fails to run or fails to adapt to the interface, please directly give the current test point a score of 0. There is no need to examine the code correctness, just use evaluation metric to give the score.
DO NOT modify the project code. DO NOT MODIFY the evaluation criteria.
""".strip()
    return prompt


def get_completed_metrics(report_dir: str) -> set[str]:
    """Get set of metric names that already have valid JSON reports."""
    completed = set()
    if not os.path.exists(report_dir):
        return completed

    for filename in os.listdir(report_dir):
        if not filename.endswith(".json"):
            continue
        file_path = os.path.join(report_dir, filename)
        metric_name = filename[:-5]
        if check_metric_json(file_path):
            completed.add(metric_name)

    return completed


def run_eval_project(
    project_id: int,
    root_path: str,
    source_dir: str | None = None,
    retry_round: int = 0,
    max_iterations: int = MAX_ITERATIONS,
    log_dir: str | None = None,
    run_id: str | None = None,
) -> bool:
    """Run EVAL stage: evaluate each metric one by one (matches PRDBench's ready_test.py)."""
    project_dir = os.path.abspath(os.path.join(root_path, str(project_id)))

    if not os.path.exists(project_dir):
        logger.warning(f"Project directory {project_dir} does not exist, skipping")
        return False

    # DEV stage no longer copies evaluation materials into the workspace
    # (information isolation), so pull them from the source benchmark here.
    eval_dir = os.path.join(project_dir, "evaluation")
    if not os.path.exists(eval_dir) and source_dir:
        eval_source = os.path.join(source_dir, str(project_id), "evaluation")
        if os.path.isdir(eval_source):
            shutil.copytree(eval_source, eval_dir)

    # Load test plan
    test_plan_path = os.path.join(eval_dir, "detailed_test_plan.json")
    test_plan = load_test_plan(test_plan_path)
    if not test_plan:
        logger.warning(f"No test plan for project {project_id}, skipping")
        return False

    # Prepare reports directory
    report_dir = os.path.join(project_dir, "reports")
    os.makedirs(report_dir, exist_ok=True)

    # Load rubric for scoring guidance (metric.json's 0/1/2 three-tier rubric)
    rubric_path = os.path.join(eval_dir, "metric.json")
    rubric_by_id = _load_rubric_by_metric_id(rubric_path)

    # Snapshot src/ so any tampering by the evaluator is detected and reverted
    snapshot_dir = _snapshot_src(project_dir)
    integrity: dict[str, dict] = {}

    # Prepare execution log directory
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Get already completed metrics
    completed = get_completed_metrics(report_dir)
    logger.info(f"Project {project_id}: {len(completed)} metrics already completed")

    total = len(test_plan)
    done = 0

    for i, metric_data in enumerate(test_plan):
        metric_name = metric_data.get("metric", f"Unknown_{i}")
        metric_report_file = os.path.join(report_dir, f"{metric_name}.json")

        # Skip already completed metrics
        if metric_name in completed:
            logger.info(f"  [{i+1}/{total}] {metric_name}: already done, skipping")
            continue

        # Lookup rubric for this metric by ID prefix
        metric_id = _extract_metric_id(metric_name)
        rubric_text = rubric_by_id.get(metric_id) if metric_id else None

        # Build per-metric prompt
        prompt = build_eval_prompt(
            metric_data=metric_data,
            project_dir=project_dir,
            metric_report_file=metric_report_file,
            retry_round=retry_round,
            rubric_text=rubric_text,
        )

        # Create session for this metric
        session_id = f"eval_{project_id}_{metric_name}"
        if retry_round > 0:
            session_id += f"_r{retry_round}"

        session = session_manager.create(
            session_id, "penguin", "code_eval_agent_workspace_dir"
        )

        logger.info(f"  [{i+1}/{total}] {metric_name}: evaluating...")
        start = time.time()

        exec_log_file = None
        if log_dir:
            safe_metric = re.sub(r"[^\w.\-]", "_", metric_name)
            rid = run_id or "default"
            exec_log_file = os.path.join(log_dir, f"eval_{project_id}_{safe_metric}_{rid}.jsonl")

        result = run_prdbench_agent(
            user_message=prompt,
            session=session,
            mode="eval",
            max_iterations=max_iterations,
            log_file=exec_log_file,
            run_id=run_id,
        )

        elapsed = time.time() - start

        # Check if metric JSON was generated
        if os.path.exists(metric_report_file) and check_metric_json(metric_report_file):
            done += 1
            logger.info(f"  [{i+1}/{total}] {metric_name}: done ({elapsed:.1f}s)")
        else:
            logger.warning(
                f"  [{i+1}/{total}] {metric_name}: no valid report generated ({elapsed:.1f}s)"
            )

        # Verify the evaluator did not modify src/; restore from snapshot if it did
        diff = _verify_and_restore_src(project_dir, snapshot_dir)
        if diff["modified"] or diff["deleted"]:
            logger.warning(
                f"  [{i+1}/{total}] {metric_name}: src/ tampered during eval "
                f"(modified={diff['modified']}, deleted={diff['deleted']}); restored"
            )
        if any(diff.values()):
            integrity[metric_name] = diff

        # Save log
        log_file = os.path.join(report_dir, f"{metric_name}.log")
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        session_manager.delete(session_id)

    # Persist integrity findings (merged across retry rounds) and drop the backup
    if snapshot_dir:
        if integrity:
            report_path = os.path.join(project_dir, "integrity_report.json")
            existing: dict = {}
            if os.path.exists(report_path):
                try:
                    with open(report_path, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                except Exception:
                    existing = {}
            existing.update(integrity)
            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)
            except OSError:
                pass
        shutil.rmtree(snapshot_dir, ignore_errors=True)

    logger.info(
        f"Project {project_id} eval done: {done}/{total} metrics completed"
    )
    return True


def run_eval_project_with_retries(
    project_id: int,
    root_path: str,
    source_dir: str | None = None,
    max_iterations: int = MAX_ITERATIONS,
    max_retries: int = 3,
    log_dir: str | None = None,
    run_id: str | None = None,
) -> None:
    """Initial EVAL pass plus retries for metrics that produced no valid report."""
    run_eval_project(
        project_id=project_id,
        root_path=root_path,
        source_dir=source_dir,
        retry_round=0,
        max_iterations=max_iterations,
        log_dir=log_dir,
        run_id=run_id,
    )

    for retry in range(1, max_retries + 1):
        project_dir = os.path.join(root_path, str(project_id))
        report_dir = os.path.join(project_dir, "reports")
        test_plan_path = os.path.join(
            project_dir, "evaluation", "detailed_test_plan.json"
        )

        if not os.path.exists(test_plan_path):
            break

        test_plan = load_test_plan(test_plan_path)
        if not test_plan:
            break

        completed = get_completed_metrics(report_dir)
        expected = {m["metric"] for m in test_plan if "metric" in m}
        missing = expected - completed

        if not missing:
            logger.info(f"Project {project_id}: all metrics completed!")
            break

        logger.info(
            f"Project {project_id}: retry {retry}, {len(missing)} metrics missing"
        )
        run_eval_project(
            project_id=project_id,
            root_path=root_path,
            source_dir=source_dir,
            retry_round=retry,
            max_iterations=max_iterations,
            log_dir=log_dir,
            run_id=run_id,
        )


# ── Parallel execution ──

def _run_in_parallel(items, fn, workers: int, label: str) -> None:
    """Run fn(item) for each item, in parallel across projects when workers > 1."""
    if workers <= 1:
        for item in items:
            fn(item)
        return
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fn, item): item for item in items}
        for future in as_completed(futures):
            item = futures[future]
            try:
                future.result()
            except Exception:
                logger.exception(f"{label} project {item} failed with unexpected error")


# ── SCORE stage ──

def calculate_scores(root_path: str) -> dict:
    """Calculate average scores across all projects.

    Unlike PRDBench's score_cal.py, the denominator is the FULL metric set
    from evaluation/detailed_test_plan.json: metrics without a valid report
    count as 0, so partial coverage can no longer inflate scores. Projects
    without a test plan fall back to averaging their existing reports.
    """
    results = {}
    coverage = {}
    total_sum = 0.0
    valid_count = 0

    def _sort_key(d: str):
        return (0, int(d)) if d.isdigit() else (1, d)

    subdirs = sorted(
        (
            d for d in os.listdir(root_path)
            if os.path.isdir(os.path.join(root_path, d)) and not d.startswith(".")
        ),
        key=_sort_key,
    )

    for subdir in subdirs:
        project_dir = os.path.join(root_path, subdir)
        report_dir = os.path.join(project_dir, "reports")
        if not os.path.exists(report_dir):
            results[subdir] = "no reports directory"
            continue

        # Collect valid per-metric scores from report files
        scores_by_metric: dict[str, float] = {}
        for filename in os.listdir(report_dir):
            if not filename.endswith(".json"):
                continue
            file_path = os.path.join(report_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, str):
                    data = json.loads(data)
                if isinstance(data, dict) and "score" in data:
                    score = data["score"]
                    if isinstance(score, (int, float)) and 0 <= score <= 2:
                        scores_by_metric[filename[:-5]] = score
            except Exception:
                continue

        # Full denominator: every metric in the test plan (missing => 0)
        test_plan_path = os.path.join(
            project_dir, "evaluation", "detailed_test_plan.json"
        )
        test_plan = (
            load_test_plan(test_plan_path) if os.path.exists(test_plan_path) else None
        )
        expected = [m["metric"] for m in test_plan if "metric" in m] if test_plan else None

        if expected:
            project_score = sum(scores_by_metric.get(name, 0) for name in expected)
            denominator = len(expected)
            evaluated = sum(1 for name in expected if name in scores_by_metric)
        elif scores_by_metric:
            project_score = sum(scores_by_metric.values())
            denominator = len(scores_by_metric)
            evaluated = denominator
        else:
            results[subdir] = "no valid data"
            continue

        # Normalize to 0-1 range (each metric is 0-2)
        normalized = project_score / denominator / 2.0
        results[subdir] = round(normalized, 4)
        coverage[subdir] = {"evaluated": evaluated, "expected": denominator}
        total_sum += normalized
        valid_count += 1

    average = total_sum / valid_count if valid_count > 0 else 0
    return {
        "scores": results,
        "coverage": coverage,
        "valid_count": valid_count,
        "average_score": round(average, 4),
    }


# ── Main ──

def main():
    parser = argparse.ArgumentParser(description="PRDBench evaluation runner for penguin-coding")
    parser.add_argument(
        "--source_dir", type=str, default="PRDbench/",
        help="Source directory containing PRDBench tasks",
    )
    parser.add_argument(
        "--root_path", type=str, default=None,
        help="Output directory for dev output / eval input",
    )
    parser.add_argument(
        "--mode", type=str, default="dev",
        choices=["dev", "eval", "score"],
        help="Run mode: dev, eval, or score",
    )
    parser.add_argument(
        "--round", type=int, default=1,
        help="Round number",
    )
    parser.add_argument(
        "--start", type=int, default=1,
        help="First project ID",
    )
    parser.add_argument(
        "--end", type=int, default=50,
        help="Last project ID",
    )
    parser.add_argument(
        "--max_iterations", type=int, default=MAX_ITERATIONS,
        help="Max agent loop iterations per task",
    )
    parser.add_argument(
        "--max_retries", type=int, default=3,
        help="Max retries for failed metrics (eval mode)",
    )
    parser.add_argument(
        "--workers", type=int, default=4,
        help="Number of projects to process in parallel (dev/eval modes). 1 = sequential.",
    )
    parser.add_argument(
        "--log_dir", type=str, default=None,
        help="Directory for structured execution logs (JSONL). Default: <root_path>/.logs",
    )
    parser.add_argument(
        "--run_id", type=str, default=None,
        help="Run identifier included in log filenames",
    )
    args = parser.parse_args()

    root_path = args.root_path or os.path.join(
        WORKSPACE_DIR, f"penguin_{args.mode}_output"
    )

    log_dir = args.log_dir or os.path.join(root_path, ".logs")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Set workspace for the agent
    os.environ["CODE_AGENT_WORKSPACE_DIR"] = root_path

    logger.info(f"PRDBench runner: mode={args.mode}, projects={args.start}-{args.end}")
    logger.info(f"Source: {args.source_dir}, Output: {root_path}")

    if args.mode == "dev":
        _run_in_parallel(
            items=list(range(args.start, args.end + 1)),
            fn=lambda i: run_dev_project(
                project_id=i,
                source_dir=args.source_dir,
                root_path=root_path,
                max_iterations=args.max_iterations,
                log_dir=log_dir,
                run_id=args.run_id,
            ),
            workers=args.workers,
            label="dev",
        )

    elif args.mode == "eval":
        _run_in_parallel(
            items=list(range(args.start, args.end + 1)),
            fn=lambda i: run_eval_project_with_retries(
                project_id=i,
                root_path=root_path,
                source_dir=args.source_dir,
                max_iterations=args.max_iterations,
                max_retries=args.max_retries,
                log_dir=log_dir,
                run_id=args.run_id,
            ),
            workers=args.workers,
            label="eval",
        )

    elif args.mode == "score":
        scores = calculate_scores(root_path)
        output_path = os.path.join(root_path, "results.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)

        logger.info(f"Results saved to {output_path}")
        logger.info(
            f"Average score: {scores['average_score']} "
            f"({scores['valid_count']} valid projects)"
        )

        # Print per-project scores with coverage
        for project, score in sorted(scores["scores"].items()):
            cov = scores.get("coverage", {}).get(project)
            if cov:
                logger.info(
                    f"  Project {project}: {score} "
                    f"({cov['evaluated']}/{cov['expected']} metrics evaluated)"
                )
            else:
                logger.info(f"  Project {project}: {score}")


if __name__ == "__main__":
    main()
