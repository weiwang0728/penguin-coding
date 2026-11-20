"""One fresh process per instance. Workspace env must be set before startup."""
import argparse
import json
from pathlib import Path

from ..agent import Agent
from ..agent_loop import usage_stats
from ..execution_log import ExecutionLog
from ..prdbench.tools import ExitLoopTool  # noqa: F401 — registers exit_loop into ToolRegistry
from ..workspace import WORKSPACE_DIR


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--max-iterations', type=int, required=True)
    args = parser.parse_args()
    item = json.loads(Path(args.input).read_text())
    output = Path(args.output)
    log = ExecutionLog(output / 'events.jsonl', run_id=item['instance_id'])
    log.log_run_started(item['instance_id'], str(WORKSPACE_DIR))
    result = {'status': 'error'}
    try:
        agent = Agent(
            tools=['read_file', 'write_file', 'edit_file', 'search_files', 'list_directory', 'run_command'],
            skills=[], permission_profile='permissive', max_iterations=args.max_iterations,
            system_prompt=(f'You are fixing a repository issue. Workspace: {WORKSPACE_DIR}. '
                           'Read the code, reproduce the issue, implement a minimal correct fix and run relevant tests. '
                           'Leave changes in the working tree. Do not commit. '
                           'Never modify, weaken, skip, or delete existing tests: do not edit files '
                           'under test directories or files named test_*.py. The evaluation runs the '
                           'original unmodified tests, so a fix that only passes altered tests is a '
                           'failed fix. If an existing test fails after your change, fix the product '
                           'code, not the test. '
                           'Do not access benchmark answers, future commits, or external solutions. '
                           'Keep temporary artifacts out of the final changes. '
                           'When you are done — the fix is implemented and verified — call the '
                           'exit_loop tool as your final action to signal completion. '
                           'Call exit_loop exactly once, after your work is finished.'))
        agent.add_tool('exit_loop')
        response, messages = agent.run(
            None, item['problem_statement'], messages=[],
            confirm_callback=lambda *_: True,
            on_content=log.log_llm_text, on_tool_start=log.log_tool_start,
            on_tool_result=log.log_tool_result)
        status = 'completed'
        if response == 'Agent reached maximum iterations without completing the task.':
            status = 'iteration_limit'
        elif response.startswith(('API error (', 'API connection error after retries:',
                                  'Context too long even after reactive compact.')):
            status = 'api_error'
        result.update(status=status, response=response,
                      turns=sum(m['role'] == 'assistant' for m in messages))
        (output / 'messages.json').write_text(json.dumps(messages, ensure_ascii=False, default=str))
        log.log_run_finished(result['turns'], log.tool_call_count, int(status != 'completed'))
    except Exception as error:
        result['error'] = str(error)
        log.log_run_terminated(str(error))
    finally:
        result.update(usage=dict(usage_stats), tool_calls=log.tool_call_count)
        (output / 'worker_result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return int(result['status'] != 'completed')


if __name__ == '__main__':
    raise SystemExit(main())
