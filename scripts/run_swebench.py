#!/usr/bin/env python3
"""Generate SWE-bench predictions. Does not import the agent in the supervisor."""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.observability import run_context, current_trace_fields, trace_headers, flush
PUBLIC_FIELDS = ('instance_id', 'repo', 'base_commit', 'problem_statement')


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env, stderr=subprocess.PIPE)


def is_test_path(path):
    """Test files are owned by the benchmark's test patch; model edits there are discarded."""
    parts = Path(path).parts
    if any(part in ('tests', 'testing', 'test') for part in parts[:-1]):
        return True
    return bool(parts) and parts[-1].startswith('test_') and parts[-1].endswith('.py')


def strip_test_changes(diff):
    """Drop whole-file hunks for test paths from a unified diff."""
    if not diff:
        return diff
    sections = re.split(r'(?m)^(?=diff --git )', diff)
    kept = []
    for section in sections:
        if not section.startswith('diff --git'):
            continue
        match = re.search(r'(?m)^\+\+\+ (?:b/)?(.+)$', section)
        if match and is_test_path(match.group(1).rstrip()):
            continue
        kept.append(section)
    return ''.join(kept)


def export_patch(repo, base):
    """Use a temporary index: include staged, unstaged, committed and new files."""
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
        git(repo, 'read-tree', base, env=env)
        # Track all changes to existing files, including deletions.
        git(repo, 'add', '-u', '--', '.', env=env)
        new_files = git(repo, 'ls-files', '--others', '--exclude-standard', '-z', env=env)
        ignored_parts = {'.penguin_tasks', '.agent', '.team', '.inbox', 'shared',
                         '__pycache__', '.pytest_cache', '.venv', 'venv'}
        for raw in new_files.split(b'\0'):
            if not raw:
                continue
            name = os.fsdecode(raw)
            if any(part in ignored_parts for part in Path(name).parts):
                continue
            if name.endswith(('.pyc', '.log')):
                continue
            git(repo, 'add', '--', name, env=env)
        return strip_test_changes(git(repo, 'diff', '--cached', '--binary', '--full-index', '--no-ext-diff', base, env=env).decode('utf-8'))


def run_process(command, cwd, env, log, timeout):
    """Kill the entire process group on timeout, including tool subprocesses."""
    with log.open('w') as output:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdout=output,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        finally:
            # Also remove descendants left behind by a normally exiting worker.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def load_instances(args):
    if args.dataset_file:
        with Path(args.dataset_file).open() as source:
            rows = [json.loads(line) for line in source if line.strip()]
    else:
        from datasets import load_dataset
        rows = load_dataset(args.dataset, split=args.split)
    wanted = set(args.instance_ids or [])
    result = []
    seen = set()
    for row in rows:
        if wanted and row['instance_id'] not in wanted:
            continue
        item = {key: row[key] for key in PUBLIC_FIELDS}
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', item['instance_id']) or item['instance_id'] in ('.', '..'):
            raise ValueError('Invalid instance_id')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', item['repo']):
            raise ValueError('Invalid repo')
        if not re.fullmatch(r'[0-9a-fA-F]{7,40}', item['base_commit']):
            raise ValueError('Invalid base_commit')
        if item['instance_id'] in seen:
            raise ValueError('Duplicate instance_id')
        seen.add(item['instance_id'])
        result.append(item)
    if wanted - seen:
        raise ValueError(f'Unknown instance IDs: {sorted(wanted - seen)}')
    if args.limit:
        result = result[:args.limit]
    if not result:
        raise ValueError('No instances selected')
    return result


def run_instance(item, args, output):
    experiment_id = uuid.uuid5(uuid.NAMESPACE_URL, str(output.resolve())).hex
    with run_context(
        "swebench.instance", session_id=f"{experiment_id}:{item['instance_id']}",
        run_id=uuid.uuid4().hex,
        metadata={"benchmark": "swebench", "experiment_id": experiment_id,
                  "instance_id": item['instance_id'], "model": args.model},
    ) as span:
        result = _run_instance(item, args, output)
        span.set_status(result['status'], exit_code=result.get('exit_code'))
        span.update(metadata={"patch_bytes": result['patch_bytes']})
        return result


def _run_instance(item, args, output):
    case = output / item['instance_id']
    case.mkdir()
    repo = case / 'repo'
    start = time.monotonic()
    record = {**current_trace_fields(), 'instance_id': item['instance_id'], 'status': 'preparing'}
    write_json(case / 'result.json', record)
    patch = ''
    prepared = False
    env = dict(os.environ, CODE_AGENT_WORKSPACE_DIR=str(repo), PRDBENCH_MODE='false',
               MODEL_ID=args.model, PYTHONPATH=str(ROOT))
    parent = trace_headers().get('traceparent')
    if parent:
        env['PENGUIN_TRACEPARENT'] = parent
    for field in ('session_id', 'run_id', 'experiment_id'):
        if record.get(field):
            env[f'PENGUIN_{field.upper()}'] = str(record[field])
    try:
        source = (str(Path(args.repo_root).resolve() / item['repo']) if args.repo_root
                  else f"https://github.com/{item['repo']}.git")
        code = run_process(['git', 'clone', '--no-hardlinks', '--no-checkout', '--', source, str(repo)],
                           ROOT, env, case / 'clone.log', args.setup_timeout)
        if code:
            raise RuntimeError(f'Clone failed ({code}); see clone.log')
        git(repo, 'checkout', '--detach', item['base_commit'])
        prepared = True
        if args.setup_command:
            code = run_process(['bash', '-lc', args.setup_command], repo, env,
                               case / 'setup.log', args.setup_timeout)
            if code:
                raise RuntimeError(f'Setup failed ({code}); see setup.log')
        write_json(case / 'input.json', item)
        record['status'] = 'running'
        write_json(case / 'result.json', record)
        code = run_process([sys.executable, '-m', 'src.swebench.worker',
                            '--input', str(case / 'input.json'), '--output', str(case),
                            '--max-iterations', str(args.max_iterations)], repo, env,
                           case / 'worker.log', args.timeout)
        if (case / 'worker_result.json').exists():
            worker_result = json.loads((case / 'worker_result.json').read_text())
            if worker_result.get('span_id'):
                record['worker_span_id'] = worker_result.pop('span_id')
            if worker_result.get('parent_span_id'):
                record['worker_parent_span_id'] = worker_result.pop('parent_span_id')
            record.update(worker_result)
        else:
            record['status'] = 'worker_error'
        record['exit_code'] = code
        if code and record['status'] == 'completed':
            record['status'] = 'worker_error'
    except subprocess.TimeoutExpired:
        record['status'] = 'timeout'
    except Exception as error:
        record.update(status='error', error=str(error))
    finally:
        if prepared:
            try:
                patch = export_patch(repo, item['base_commit'])
            except Exception as error:
                record.update(status='patch_error', patch_error=str(error))
        (case / 'patch.diff').write_text(patch, encoding='utf-8')
        prediction = {'instance_id': item['instance_id'], 'model_name_or_path': args.model_name,
                      'model_patch': patch}
        write_json(case / 'prediction.json', prediction)
        record.update(elapsed_seconds=round(time.monotonic() - start, 3),
                      patch_bytes=len(patch.encode('utf-8')), finished=True)
        write_json(case / 'result.json', record)
    return record


IGNORE_PARTS = {'.penguin_tasks', '.agent', '.team', '.inbox', 'shared',
                '__pycache__', '.pytest_cache', '.venv', 'venv'}

EXPORT_PATCH_SH = """#!/bin/bash
set -x
cd /testbed
BASE=$(/opt/miniconda3/bin/python -c "import json;print(json.load(open('/out/input.json'))['base_commit'])")
export GIT_INDEX_FILE=/tmp/export_index.$$
git read-tree "$BASE"
git add -u -- .
git ls-files --others --exclude-standard -z |
while IFS= read -r -d '' name; do
  skip=0
  IFS='/' read -ra parts <<< "$name"
  for part in "${parts[@]}"; do
    case "$part" in
      .penguin_tasks|.agent|.team|.inbox|shared|__pycache__|.pytest_cache|.venv|venv) skip=1 ;;
    esac
  done
  case "$name" in
    *.pyc|*.log) skip=1 ;;
  esac
  [ "$skip" = 0 ] && git add -- "$name"
done
git diff --cached --binary --full-index --no-ext-diff "$BASE" > /out/patch.diff.raw
/opt/miniconda3/bin/python - <<'PYEOF'
import re
from pathlib import Path

def is_test_path(path):
    parts = Path(path).parts
    if any(part in ('tests', 'testing', 'test') for part in parts[:-1]):
        return True
    return bool(parts) and parts[-1].startswith('test_') and parts[-1].endswith('.py')

raw = Path('/out/patch.diff.raw').read_text()
sections = re.split(r'(?m)^(?=diff --git )', raw)
kept = []
for section in sections:
    if not section.startswith('diff --git'):
        continue
    match = re.search(r'(?m)^\\+\\+\\+ (?:b/)?(.+)$', section)
    if match and is_test_path(match.group(1).rstrip()):
        continue
    kept.append(section)
Path('/out/patch.diff').write_text(''.join(kept))
PYEOF
"""


def docker_cli(*args):
    return subprocess.run(['docker', *args], stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)


def image_exists(tag):
    return docker_cli('image', 'inspect', tag).returncode == 0


def load_full_rows(args, items):
    """Fetch full dataset rows (test specs need more than the public fields)."""
    from swebench.harness.utils import load_swebench_dataset
    wanted = [i['instance_id'] for i in items]
    rows = load_swebench_dataset(args.dataset, split=args.split, instance_ids=wanted)
    return {row['instance_id']: row for row in rows}


def find_local_repo(instance_id):
    """Search previous run directories for an existing checkout of this instance."""
    artifacts = ROOT / 'artifacts' / 'swebench'
    if artifacts.is_dir():
        for candidate in sorted(artifacts.glob(f'*/{instance_id}/repo/.git')):
            return candidate.parent
    return None


def prepare_repo_checkout(item, case, args, env):
    """Ensure a local git checkout exists to build the image bundle from."""
    repo = find_local_repo(item['instance_id'])
    if repo:
        return repo
    repo = case / 'repo'
    source = (str(Path(args.repo_root).resolve() / item['repo']) if args.repo_root
              else f"https://github.com/{item['repo']}.git")
    for attempt in range(3):
        code = run_process(['git', 'clone', '--no-hardlinks', '--no-checkout', '--', source, str(repo)],
                           ROOT, env, case / 'clone.log', args.setup_timeout)
        if not code:
            break
        shutil.rmtree(repo, ignore_errors=True)
    else:
        raise RuntimeError('Host clone failed after 3 attempts; see clone.log')
    git(repo, 'checkout', '--detach', item['base_commit'])
    return repo


def build_instance_image(item, repo, case, spec):
    """Build the sweb.eval instance image offline from a local git bundle."""
    bundle = case / 'repo.bundle'
    subprocess.run(['git', '-C', str(repo), 'bundle', 'create', str(bundle), '--all'],
                   check=True, capture_output=True)
    context = case / 'imgbuild'
    context.mkdir(exist_ok=True)
    shutil.copy(bundle, context / 'repo.bundle')
    (context / 'setup_repo.sh').write_text(f"""#!/bin/bash
set -euxo pipefail
git clone -o origin /tmp/repo.bundle /testbed
chmod -R 777 /testbed
cd /testbed
git reset --hard {item['base_commit']}
git remote remove origin
source /opt/miniconda3/bin/activate
conda activate testbed
echo "Current environment: $CONDA_DEFAULT_ENV"
# Old repos (astropy 3.x era) need legacy build tooling: modern pip refuses
# setup.py develop, new setuptools removed dep_util, .pyx needs Cython.
# pyproject-only repos (e.g. sphinx>=7.2, flit_core backend, no setup.py)
# must NOT go through the legacy path: no pinning, no pyproject move.
if [ -f setup.py ]; then
  python -m pip install "pip<23.1" "setuptools<60" "cython<3" extension_helpers wheel
  [ -f pyproject.toml ] && mv pyproject.toml pyproject.toml.bak
  python -m pip install -e . --no-build-isolation
else
  python -m pip install flit_core
  python -m pip install -e . --no-build-isolation
fi
""", encoding='utf-8')
    (context / 'Dockerfile').write_text(f"""FROM --platform=linux/x86_64 {spec.env_image_key}

COPY ./repo.bundle /tmp/
COPY ./setup_repo.sh /root/
RUN sed -i -e 's/\\r$//' /root/setup_repo.sh
RUN /bin/bash /root/setup_repo.sh

WORKDIR /testbed/
""", encoding='utf-8')
    result = docker_cli('build', '-t', spec.instance_image_key, str(context))
    if result.returncode:
        raise RuntimeError(f'Instance image build failed: {result.stdout[-500:]}')


def ensure_env_images(args, items):
    """Build missing sweb.env images via the official harness (conda network only)."""
    import docker as docker_sdk
    from swebench.harness.docker_build import build_env_images
    wanted = {i['instance_id'] for i in items}
    rows = [row for row in load_full_rows(args, [{'instance_id': iid} for iid in wanted]).values()]
    client = docker_sdk.from_env()
    build_env_images(client, rows, False, 3)


def ensure_dev_image(item, spec, case):
    """Instance image plus agent dependencies; testbed env goes first on PATH."""
    tag = f"sweb.dev.x86_64.{item['instance_id']}:latest"
    if image_exists(tag):
        return tag
    context = case / 'devbuild'
    context.mkdir(exist_ok=True)
    (context / 'Dockerfile').write_text(f"""FROM --platform=linux/x86_64 {spec.instance_image_key}
ENV PATH=/opt/miniconda3/envs/testbed/bin:/opt/miniconda3/bin:$PATH \\
    CONDA_DEFAULT_ENV=testbed
RUN git config --system --add safe.directory '*' \\
    && /opt/miniconda3/bin/pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \\
    anthropic python-dotenv prompt_toolkit rich pyyaml
WORKDIR /testbed/
""", encoding='utf-8')
    result = docker_cli('build', '-t', tag, str(context))
    if result.returncode:
        raise RuntimeError(f'Dev image build failed: {result.stdout[-500:]}')
    return tag


def run_instance_docker(item, args, output):
    """Run the worker inside the official sweb.eval image for this instance."""
    case = output / item['instance_id']
    case.mkdir()
    start = time.monotonic()
    record = {'instance_id': item['instance_id'], 'status': 'preparing'}
    patch = ''
    name = f"swebdev-{item['instance_id']}"
    try:
        from swebench.harness.test_spec import make_test_spec
        spec = make_test_spec(args.full_rows[item['instance_id']])
        write_json(case / 'input.json', item)
        if not image_exists(spec.instance_image_key):
            ensure_env_images(args, [item])
            repo = prepare_repo_checkout(item, case, args, os.environ.copy())
            build_instance_image(item, repo, case, spec)
        dev_tag = ensure_dev_image(item, spec, case)
        (case / 'export_patch.sh').write_text(EXPORT_PATCH_SH, encoding='utf-8')
        record['status'] = 'running'
        write_json(case / 'result.json', record)
        docker_cli('rm', '-f', name)  # clear leftovers from a crashed supervisor
        inner = (f"/opt/miniconda3/bin/python -m src.swebench.worker "
                 f"--input /out/input.json --output /out "
                 f"--max-iterations {args.max_iterations}; "
                 f"code=$?; bash /out/export_patch.sh || true; exit $code")
        run = ['docker', 'run', '--name', name,
               '--user', f"{os.getuid()}:{os.getgid()}",
               '-v', f"{case}:/out",
               '-v', f"{ROOT}:/opt/penguin:ro",
               '-e', 'CODE_AGENT_WORKSPACE_DIR=/testbed',
               '-e', 'PRDBENCH_MODE=true',
               '-e', 'CODE_AGENT_EXTRA_ALLOWED_DIRS=/tmp',
               '-e', f"MODEL_ID={args.model}",
               '-e', 'PYTHONPATH=/opt/penguin',
               '-w', '/testbed',
               dev_tag, 'bash', '-c', inner]
        code = run_process(run, ROOT, os.environ.copy(), case / 'worker.log', args.timeout)
        if (case / 'worker_result.json').exists():
            record.update(json.loads((case / 'worker_result.json').read_text()))
        else:
            record['status'] = 'worker_error'
        record['exit_code'] = code
        if code and record['status'] == 'completed':
            record['status'] = 'worker_error'
    except subprocess.TimeoutExpired:
        # The docker client was killed; the container is still running, so
        # export whatever the worker left behind before tearing it down.
        export = docker_cli('exec', name, 'bash', '/out/export_patch.sh')
        record['status'] = 'timeout'
        if export.returncode:
            record['patch_export_error'] = export.stdout[-300:]
    except Exception as error:
        record.update(status='error', error=str(error))
    finally:
        docker_cli('rm', '-f', name)
        patch_file = case / 'patch.diff'
        if patch_file.exists():
            try:
                patch = patch_file.read_text(encoding='utf-8')
            except OSError as error:
                record.setdefault('patch_export_error', str(error))
                patch = ''
        else:
            patch_file.write_text(patch, encoding='utf-8')
        prediction = {'instance_id': item['instance_id'], 'model_name_or_path': args.model_name,
                      'model_patch': patch}
        write_json(case / 'prediction.json', prediction)
        record.update(elapsed_seconds=round(time.monotonic() - start, 3),
                      patch_bytes=len(patch.encode('utf-8')), finished=True)
        write_json(case / 'result.json', record)
    return record


def process_item(item, args, output):
    """Run one instance, reusing a finished record or archiving an interrupted case."""
    case = output / item['instance_id']
    result_path = case / 'result.json'
    runner = run_instance_docker if getattr(args, 'docker', False) else run_instance
    if case.exists():
        if not result_path.exists() or not json.loads(result_path.read_text()).get('finished'):
            archived = output / 'interrupted'
            archived.mkdir(exist_ok=True)
            case.rename(archived / f"{item['instance_id']}-{uuid.uuid4().hex[:8]}")
            record = runner(item, args, output)
        else:
            record = json.loads(result_path.read_text())
    else:
        record = runner(item, args, output)
    prediction = json.loads((case / 'prediction.json').read_text())
    return record, prediction


def main():
    try:
        return _main()
    finally:
        flush()


def _main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', default='princeton-nlp/SWE-bench_Lite')
    parser.add_argument('--split', default='test')
    parser.add_argument('--dataset-file', help='Local JSONL; gold fields are discarded')
    parser.add_argument('--instance-ids', nargs='+')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--output', required=True, help='New run directory, or same directory with --resume')
    parser.add_argument('--model', required=True)
    parser.add_argument('--model-name', default='penguin-baseline')
    parser.add_argument('--max-iterations', type=int, default=100)
    parser.add_argument('--timeout', type=int, default=1800, help='Per-agent wall time in seconds')
    parser.add_argument('--setup-timeout', type=int, default=900)
    parser.add_argument('--setup-command', help='Trusted shell command run in each checkout before the agent')
    parser.add_argument('--repo-root', help='Local repository mirror root, arranged as owner/repo')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--docker', action='store_true',
                        help='Run the worker inside the official sweb.eval Docker image '
                             '(real testbed env; ignores --setup-command)')
    parser.add_argument('--parallel', type=int, default=1,
                        help='Number of instances to run concurrently (default 1)')
    args = parser.parse_args()
    if min(args.max_iterations, args.timeout, args.setup_timeout, args.parallel) <= 0 or (args.limit is not None and args.limit <= 0):
        parser.error('Limits and timeouts must be positive')
    if args.docker and args.setup_command:
        parser.error('--setup-command is not supported with --docker (env images already ship deps)')
    items = load_instances(args)
    if args.docker:
        args.full_rows = load_full_rows(args, items)
    output = Path(args.output).expanduser().resolve()
    config = {key: value for key, value in vars(args).items() if key not in ('resume', 'output')}
    config['instances'] = items
    if output.exists():
        if not args.resume or not (output / 'run.json').exists():
            parser.error('Output exists; choose a new directory or --resume an existing run')
        if json.loads((output / 'run.json').read_text()) != config:
            parser.error('Resume configuration differs from original run')
    else:
        output.mkdir(parents=True)
        write_json(output / 'run.json', config)
    records = {}
    predictions = {}
    persist_lock = threading.Lock()

    def persist():
        # Write in the dataset's original order regardless of completion order.
        ordered_records = [records[i['instance_id']] for i in items if i['instance_id'] in records]
        ordered_predictions = [predictions[i['instance_id']] for i in items if i['instance_id'] in predictions]
        tmp = output / 'predictions.jsonl.tmp'
        tmp.write_text(''.join(json.dumps(p, ensure_ascii=False) + '\n' for p in ordered_predictions), encoding='utf-8')
        tmp.replace(output / 'predictions.jsonl')
        write_json(output / 'summary.json', ordered_records)

    def task(item):
        record, prediction = process_item(item, args, output)
        with persist_lock:
            records[item['instance_id']] = record
            predictions[item['instance_id']] = prediction
            persist()
        print(f"{item['instance_id']}: {record['status']} ({record['patch_bytes']} patch bytes)", flush=True)

    if args.parallel == 1:
        for item in items:
            task(item)
    else:
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            list(pool.map(task, items))  # iterating surfaces exceptions in dataset order
    return int(any(r['status'] != 'completed' for r in records.values()))


if __name__ == '__main__':
    sys.exit(main())
