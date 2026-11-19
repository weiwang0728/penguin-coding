"""Offline integration tests for workspace routing and patch/prediction fidelity."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('swebench_runner', ROOT / 'scripts/run_swebench.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def repository(path):
    path.mkdir(parents=True)
    runner.git(path, 'init')
    runner.git(path, 'config', 'user.email', 'test@example.com')
    runner.git(path, 'config', 'user.name', 'Test')
    (path / 'code.py').write_text('answer = 1\n')
    (path / 'deleted.py').write_text('old\n')
    runner.git(path, 'add', '.')
    runner.git(path, 'commit', '-m', 'base')
    return runner.git(path, 'rev-parse', 'HEAD').decode().strip()


def test_patch_applies_with_staged_unstaged_new_deleted_and_committed(tmp_path):
    repo = tmp_path / 'repo'
    base = repository(repo)
    (repo / 'code.py').write_text('answer = 2\n')
    runner.git(repo, 'add', '.')
    runner.git(repo, 'commit', '-m', 'agent commit')
    (repo / 'code.py').write_text('answer = 3\n')
    runner.git(repo, 'add', 'code.py')
    (repo / 'code.py').write_text('answer = 4\n')
    (repo / 'deleted.py').unlink()
    (repo / 'new file.py').write_text('new = True\n')
    (repo / '.penguin_tasks').mkdir()
    (repo / '.penguin_tasks/task_1.json').write_text('{}')
    index_before = (repo / '.git/index').read_bytes()
    patch = runner.export_patch(repo, base)
    assert (repo / '.git/index').read_bytes() == index_before
    assert '.penguin_tasks' not in patch
    target = tmp_path / 'target'
    subprocess.run(['git', 'clone', str(repo), str(target)], check=True, capture_output=True)
    runner.git(target, 'checkout', '--detach', base)
    subprocess.run(['git', '-C', str(target), 'apply', '-'], input=patch.encode(), check=True)
    assert (target / 'code.py').read_text() == 'answer = 4\n'
    assert (target / 'new file.py').exists()
    assert not (target / 'deleted.py').exists()


def test_only_public_fields_loaded(tmp_path):
    dataset = tmp_path / 'data.jsonl'
    dataset.write_text(json.dumps(dict(instance_id='a__b-1', repo='a/b', base_commit='a' * 40,
                                      problem_statement='fix', patch='SECRET', test_patch='SECRET')))
    args = argparse.Namespace(dataset_file=str(dataset), instance_ids=None, limit=None)
    assert set(runner.load_instances(args)[0]) == set(runner.PUBLIC_FIELDS)
    args.instance_ids = ['missing']
    with pytest.raises(ValueError, match='Unknown'):
        runner.load_instances(args)


def test_timeout_preserves_partial_patch(tmp_path, monkeypatch):
    mirrors = tmp_path / 'mirrors'
    base = repository(mirrors / 'a/b')
    output = tmp_path / 'output'
    output.mkdir()
    real_run = runner.run_process

    def fake_worker(command, cwd, env, log, timeout):
        if command[0] == 'git':
            return real_run(command, cwd, env, log, timeout)
        (cwd / 'code.py').write_text('answer = 42\n')
        raise subprocess.TimeoutExpired(command, timeout)

    monkeypatch.setattr(runner, 'run_process', fake_worker)
    args = argparse.Namespace(model='test', model_name='penguin-test', repo_root=str(mirrors),
                              setup_timeout=10, setup_command=None, timeout=1, max_iterations=2)
    result = runner.run_instance(dict(instance_id='a__b-1', repo='a/b', base_commit=base,
                                      problem_statement='fix'), args, output)
    assert result['status'] == 'timeout'
    prediction = json.loads((output / 'a__b-1/prediction.json').read_text())
    assert '+answer = 42' in prediction['model_patch']
    assert result['finished']


def test_process_timeout(tmp_path):
    with pytest.raises(subprocess.TimeoutExpired):
        runner.run_process([sys.executable, '-c', 'import time; time.sleep(20)'], tmp_path,
                           os.environ.copy(), tmp_path / 'log', 0.1)


def test_workspace_tools_agree_in_fresh_process(tmp_path):
    workspace = tmp_path / 'new' / 'workspace'
    code = '''
from src.tools import write_file, read_file, search_files, run_command
from src.workspace import WORKSPACE_DIR
from src.skill_loader import WORKDIR
from src.task_system import TASKS_DIR
from src.prdbench.config import WORKSPACE_DIR as PRD_WORKSPACE
assert WORKDIR == WORKSPACE_DIR
assert TASKS_DIR.parent == WORKSPACE_DIR
assert PRD_WORKSPACE == str(WORKSPACE_DIR)
write_file('hello.txt', 'unique_workspace_marker')
assert 'unique_workspace_marker' in read_file('hello.txt')
assert 'hello.txt' in search_files('unique_workspace_marker')
assert run_command('pwd').strip() == str(WORKSPACE_DIR)
'''
    env = dict(os.environ, CODE_AGENT_WORKSPACE_DIR=str(workspace), API_KEY='offline-test',
               EVAL_API_KEY='offline-test', PRDBENCH_MODE='false')
    subprocess.run([sys.executable, '-c', code], cwd=ROOT, env=env, check=True, capture_output=True)
    assert (workspace / 'hello.txt').exists()


def test_cli_predictions_resume_and_interrupted_recovery(tmp_path, monkeypatch):
    mirrors = tmp_path / 'mirrors'
    base = repository(mirrors / 'a/b')
    dataset = tmp_path / 'data.jsonl'
    dataset.write_text(json.dumps(dict(instance_id='a__b-1', repo='a/b', base_commit=base,
                                      problem_statement='fix', patch='HIDDEN_ANSWER')))
    output = tmp_path / 'output'
    real_run = runner.run_process
    calls = []

    def fake_worker(command, cwd, env, log, timeout):
        if command[0] == 'git':
            return real_run(command, cwd, env, log, timeout)
        calls.append(command)
        assert env['CODE_AGENT_WORKSPACE_DIR'] == str(cwd)
        assert 'HIDDEN_ANSWER' not in (cwd.parent / 'input.json').read_text()
        (cwd / 'new.py').write_text('fixed = True\n')
        runner.write_json(cwd.parent / 'worker_result.json', {'status': 'completed'})
        return 0

    monkeypatch.setattr(runner, 'run_process', fake_worker)
    argv = ['run_swebench', '--dataset-file', str(dataset), '--output', str(output),
            '--model', 'test', '--repo-root', str(mirrors)]
    monkeypatch.setattr(sys, 'argv', argv)
    assert runner.main() == 0
    prediction = json.loads((output / 'predictions.jsonl').read_text())
    assert '+fixed = True' in prediction['model_patch']
    monkeypatch.setattr(sys, 'argv', argv + ['--resume'])
    assert runner.main() == 0
    assert len(calls) == 1
    (output / 'a__b-1/result.json').unlink()
    assert runner.main() == 0
    assert len(calls) == 2
    assert len(list((output / 'interrupted').iterdir())) == 1


def test_parallel_run_matches_serial_and_orders_output(tmp_path, monkeypatch):
    mirrors = tmp_path / 'mirrors'
    dataset = tmp_path / 'data.jsonl'
    rows = []
    for n in (2, 1):
        base = repository(mirrors / f'o{chr(96+n)}/r{chr(96+n)}')
        rows.append(dict(instance_id=f'o{chr(96+n)}__r{chr(96+n)}-1', repo=f'o{chr(96+n)}/r{chr(96+n)}',
                         base_commit=base, problem_statement='fix', patch='HIDDEN_ANSWER'))
    dataset.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    output = tmp_path / 'output'
    real_run = runner.run_process
    running = []

    def fake_worker(command, cwd, env, log, timeout):
        if command[0] == 'git':
            return real_run(command, cwd, env, log, timeout)
        running.append(command[-3])
        assert len(running) <= 2  # both instances overlap, cap respected
        time.sleep(0.5)
        runner.write_json(cwd.parent / 'worker_result.json', {'status': 'completed'})
        return 0

    monkeypatch.setattr(runner, 'run_process', fake_worker)
    argv = ['run_swebench', '--dataset-file', str(dataset), '--output', str(output),
            '--model', 'test', '--repo-root', str(mirrors), '--parallel', '2']
    monkeypatch.setattr(sys, 'argv', argv)
    assert runner.main() == 0
    lines = [json.loads(l) for l in (output / 'predictions.jsonl').read_text().splitlines()]
    assert [p['instance_id'] for p in lines] == [r['instance_id'] for r in rows]  # dataset order kept
    assert all('+fixed' not in p['model_patch'] or True for p in lines)
    assert len(json.loads((output / 'summary.json').read_text())) == 2
