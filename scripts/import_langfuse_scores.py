#!/usr/bin/env python3
"""Attach official SWE-bench results to recorded traces; safe to rerun."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.observability import score, flush


def resolved_results(report):
    """Accept the official aggregate report or per-instance harness reports.

    Only explicitly evaluated resolved/unresolved instances receive a score.
    Missing, errored or unsubmitted instances are never inferred as failures.
    """
    if not isinstance(report, dict):
        raise ValueError('Expected an official harness report object')
    result = {}
    for key, resolved in (('resolved_ids', True), ('unresolved_ids', False)):
        for instance_id in report.get(key, []):
            if not isinstance(instance_id, str):
                raise ValueError(f'{key} must contain instance IDs')
            if instance_id in result and result[instance_id] != resolved:
                raise ValueError(f'Conflicting result for {instance_id}')
            result[instance_id] = resolved
    for instance_id, value in report.items():
        if isinstance(value, dict) and isinstance(value.get('resolved'), bool):
            if instance_id in result and result[instance_id] != value['resolved']:
                raise ValueError(f'Conflicting result for {instance_id}')
            result[instance_id] = value['resolved']
    for instance_id in report.get('error_ids', []):
        result.pop(instance_id, None)
    if not result:
        raise ValueError('No explicit resolved/unresolved results found')
    return result


def import_scores(run_dir, report):
    outcomes = resolved_results(report)
    counts = {'submitted': 0, 'missing_trace': 0, 'unavailable': 0}
    # Enumerating existing files also keeps report-provided IDs out of paths.
    for result_file in Path(run_dir).glob('*/result.json'):
        record = json.loads(result_file.read_text(encoding='utf-8'))
        instance_id = record.get('instance_id')
        if instance_id not in outcomes:
            continue
        trace_id = record.get('trace_id')
        if not trace_id:
            counts['missing_trace'] += 1
            continue
        score_id = hashlib.sha256(f'{trace_id}:swebench.resolved'.encode()).hexdigest()
        ok = score('swebench.resolved', int(outcomes[instance_id]), trace_id=trace_id,
                   score_id=score_id, data_type='BOOLEAN',
                   comment='Official SWE-bench harness result')
        counts['submitted' if ok else 'unavailable'] += 1
    return counts


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True, help='Output directory from run_swebench.py')
    parser.add_argument('--report', required=True, help='Official aggregate or per-instance report JSON')
    args = parser.parse_args()
    try:
        report = json.loads(Path(args.report).read_text(encoding='utf-8'))
        counts = import_scores(args.run_dir, report)
        print(json.dumps(counts))
        return int(bool(counts['unavailable'] or counts['missing_trace']))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    finally:
        flush()


if __name__ == '__main__':
    raise SystemExit(main())
