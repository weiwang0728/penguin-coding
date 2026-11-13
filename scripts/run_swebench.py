#!/usr/bin/env python3
"""Generate SWE-bench predictions. Does not import the agent in the supervisor."""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FIELDS = ('instance_id', 'repo', 'base_commit', 'problem_statement')


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env, stderr=subprocess.PIPE)


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
        return git(repo, 'diff', '--cached', '--binary', '--full-index', '--no-ext-diff', base, env=env).decode('utf-8')


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
    case = output / item['instance_id']
    case.mkdir()
    repo = case / 'repo'
    start = time.monotonic()
    record = {'instance_id': item['instance_id'], 'status': 'preparing'}
    patch = ''
    prepared = False
    env = dict(os.environ, CODE_AGENT_WORKSPACE_DIR=str(repo), PRDBENCH_MODE='false',
               MODEL_ID=args.model, PYTHONPATH=str(ROOT))
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
            record.update(json.loads((case / 'worker_result.json').read_text()))
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


def main():
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
    args = parser.parse_args()
    if min(args.max_iterations, args.timeout, args.setup_timeout) <= 0 or (args.limit is not None and args.limit <= 0):
        parser.error('Limits and timeouts must be positive')
    items = load_instances(args)
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
    records = []
    predictions = []
    for item in items:
        case = output / item['instance_id']
        result_path = case / 'result.json'
        if case.exists():
            if not result_path.exists() or not json.loads(result_path.read_text()).get('finished'):
                archived = output / 'interrupted'
                archived.mkdir(exist_ok=True)
                case.rename(archived / f"{item['instance_id']}-{uuid.uuid4().hex[:8]}")
                record = run_instance(item, args, output)
            else:
                record = json.loads(result_path.read_text())
        else:
            record = run_instance(item, args, output)
        records.append(record)
        predictions.append(json.loads((case / 'prediction.json').read_text()))
        tmp = output / 'predictions.jsonl.tmp'
        tmp.write_text(''.join(json.dumps(p, ensure_ascii=False) + '\n' for p in predictions), encoding='utf-8')
        tmp.replace(output / 'predictions.jsonl')
        write_json(output / 'summary.json', records)
        print(f"{item['instance_id']}: {record['status']} ({record['patch_bytes']} patch bytes)", flush=True)
    return int(any(r['status'] != 'completed' for r in records))


if __name__ == '__main__':
    sys.exit(main())
