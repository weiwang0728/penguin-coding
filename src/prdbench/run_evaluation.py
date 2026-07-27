"""PRDBench evaluation runner — drives penguin-coding through the full DEV + EVAL pipeline.

Matches PRDBench's actual evaluation flow:
  - DEV:  generate_dev.py sends one prompt per project, agent develops code in src/
  - EVAL: ready_test.py sends one prompt per METRIC, agent writes {metric_name}.json
  - SCORE: score_cal.py reads reports/{metric_name}.json and averages scores

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
import json
import logging
import os
import re
import shutil
import time
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
    """Run DEV stage: agent reads PRD.md and develops code in src/."""
    project_dir = os.path.abspath(os.path.join(root_path, str(project_id)))
    os.makedirs(project_dir, exist_ok=True)

    # Copy PRD and evaluation from source
    src_source = os.path.join(source_dir, str(project_id), "src")
    src_target = os.path.join(project_dir, "src")
    eval_source = os.path.join(source_dir, str(project_id), "evaluation")
    eval_target = os.path.join(project_dir, "evaluation")

    if os.path.exists(src_source) and not os.path.exists(src_target):
        shutil.copytree(src_source, src_target)

    if os.path.exists(eval_source) and not os.path.exists(eval_target):
        shutil.copytree(eval_source, eval_target)

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

    # Save response
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    session_manager.delete(session_id)
    logger.info(f"DEV project {project_id} done (status={result.get('status')})")
    return result.get("status") == "success"


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


_METRIC_ID_RE = re.compile(r"^(\d+\.\d+\.\d+[a-z]?)")


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
If the detailed_test_plan mentions that image analysis is required, use the "deal_graph" tool to analyze the images.
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

    # Load test plan
    test_plan_path = os.path.join(project_dir, "evaluation", "detailed_test_plan.json")
    test_plan = load_test_plan(test_plan_path)
    if not test_plan:
        logger.warning(f"No test plan for project {project_id}, skipping")
        return False

    # Prepare reports directory
    report_dir = os.path.join(project_dir, "reports")
    os.makedirs(report_dir, exist_ok=True)

    # Load rubric for scoring guidance (metric.json's 0/1/2 three-tier rubric)
    rubric_path = os.path.join(project_dir, "evaluation", "metric.json")
    rubric_by_id = _load_rubric_by_metric_id(rubric_path)

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

        # Save log
        log_file = os.path.join(report_dir, f"{metric_name}.log")
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        session_manager.delete(session_id)

    logger.info(
        f"Project {project_id} eval done: {done}/{total} metrics completed"
    )
    return True


# ── SCORE stage ──

def calculate_scores(root_path: str) -> dict:
    """Calculate average scores across all projects (matches PRDBench's score_cal.py)."""
    results = {}
    total_sum = 0.0
    valid_count = 0

    subdirs = sorted(
        d for d in os.listdir(root_path)
        if os.path.isdir(os.path.join(root_path, d)) and not d.startswith(".")
    )

    for subdir in subdirs:
        report_dir = os.path.join(root_path, subdir, "reports")
        if not os.path.exists(report_dir):
            results[subdir] = "no reports directory"
            continue

        project_score = 0.0
        metric_count = 0

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
                        project_score += score
                        metric_count += 1
            except Exception:
                continue

        if metric_count > 0:
            # Normalize to 0-1 range (each metric is 0-2)
            normalized = project_score / metric_count / 2.0
            results[subdir] = round(normalized, 4)
            total_sum += normalized
            valid_count += 1
        else:
            results[subdir] = "no valid data"

    average = total_sum / valid_count if valid_count > 0 else 0
    return {
        "scores": results,
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
        for i in range(args.start, args.end + 1):
            run_dev_project(
                project_id=i,
                source_dir=args.source_dir,
                root_path=root_path,
                max_iterations=args.max_iterations,
                log_dir=log_dir,
                run_id=args.run_id,
            )

    elif args.mode == "eval":
        for i in range(args.start, args.end + 1):
            # Initial evaluation
            run_eval_project(
                project_id=i,
                root_path=root_path,
                retry_round=0,
                max_iterations=args.max_iterations,
                log_dir=log_dir,
                run_id=args.run_id,
            )

            # Retry incomplete metrics
            for retry in range(1, args.max_retries + 1):
                project_dir = os.path.join(root_path, str(i))
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
                expected = {
                    m["metric"] for m in test_plan if "metric" in m
                }
                missing = expected - completed

                if not missing:
                    logger.info(f"Project {i}: all metrics completed!")
                    break

                logger.info(
                    f"Project {i}: retry {retry}, {len(missing)} metrics missing"
                )
                run_eval_project(
                    project_id=i,
                    root_path=root_path,
                    retry_round=retry,
                    max_iterations=args.max_iterations,
                    log_dir=log_dir,
                    run_id=args.run_id,
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

        # Print per-project scores
        for project, score in sorted(scores["scores"].items()):
            logger.info(f"  Project {project}: {score}")


if __name__ == "__main__":
    main()
