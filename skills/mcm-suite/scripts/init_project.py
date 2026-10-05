#!/usr/bin/env python3
"""Create a fresh MCM workspace; never modify supplied originals."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from artifact_safety import read_json


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def initialize(root, year, mode, problem=None, inputs=(), implementation='undecided'):
    if type(year) is not int or not 1985 <= year <= 9999:
        raise ValueError('Invalid contest year: an integer is required')
    if mode not in ['live', 'practice', 'reproduce'] or not isinstance(mode, str):
        raise ValueError('Invalid MCM mode')
    if problem is not None and problem not in ['A', 'B', 'C']:
        raise ValueError('Invalid MCM problem')
    if implementation not in ['python', 'matlab', 'undecided']:
        raise ValueError('Invalid implementation')
    requested = Path(root)
    if requested.is_symlink():
        raise ValueError('Project root cannot be a symlink')
    root = requested.resolve()
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise ValueError('Project root must be new or empty')
    if isinstance(inputs, (str, bytes, Path)):
        raise ValueError('Inputs must be a collection of file paths')
    originals = [Path(p).resolve(strict=True) for p in inputs]
    if any(not p.is_file() for p in originals):
        raise ValueError('Inputs must be files')
    if len({p.name for p in originals}) != len(originals):
        raise ValueError('Input basenames collide; rename working copies first')
    assets = Path(__file__).resolve().parents[1] / 'assets'
    asset = assets / f'rules-{year}.json'
    if asset.exists():
        rules = read_json(asset)
        if (not isinstance(rules, dict) or type(rules.get('schema_version')) is not int
                or rules['schema_version'] != 1 or rules.get('contest') != 'MCM'
                or type(rules.get('year')) is not int or rules['year'] != year
                or not isinstance(rules.get('sources'), list)
                or not isinstance(rules.get('claims'), dict)
                or not isinstance(rules.get('conflicts'), list)):
            raise ValueError('Invalid or year-mismatched rules asset')
        rules['verification'] = 'reference_snapshot'
    else:
        rules = dict(schema_version=1, contest='MCM', year=year, checked_at=None,
                     verification='unresolved', sources=[], claims={}, conflicts=[])
    layout = read_json(assets / 'layout-review.json')
    layout_keys = {'status', 'pdf_sha256', 'page_count', 'main_page_count', 'ai_report_start_page',
                   'ai_used', 'unresolved', 'evidence', 'main_pages_verified',
                   'summary_first_page_verified', 'english_verified', 'anonymous_verified',
                   'control_number_each_page_verified', 'minimum_font_verified',
                   'visual_all_pages_verified', 'ai_report_appropriate_verified',
                   'citations_verified', 'task_coverage_verified'}
    if (not isinstance(layout, dict) or not layout_keys <= layout.keys()
            or layout.get('status') != 'INCOMPLETE'
            or layout.get('ai_used') is not None
            or layout.get('unresolved') != [] or layout.get('evidence') != []
            or any(value is not False for key, value in layout.items() if key.endswith('_verified'))):
        raise ValueError('Invalid unreviewed layout template')
    bilingual = read_json(assets.parent.parent / 'mcm-paper-writer/assets/bilingual-review.json')
    from audit_bilingual_delivery import validate_review
    validate_review(bilingual, template=True)
    # Build in a private sibling first. Malformed assets or copy failures do not
    # leave a partially initialized root, and publication refuses a nonempty root.
    root.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.mcm-init-', dir=root.parent))
    try:
        for name in ['inputs', 'contracts', 'sources', 'data', 'code', 'results', 'verification', 'paper', 'logs']:
            (staging / name).mkdir()
        for language in ['en', 'zh']:
            (staging / 'paper' / language).mkdir()
        write_json(staging / 'context.json', dict(schema_version=1, contest='MCM', year=year, mode=mode,
                   problem=problem, team_control_number=None, working_language='zh', paper_language='en',
                   implementation=implementation))
        write_json(staging / 'rules.json', rules)
        files = []
        for original in originals:
            target = staging / 'inputs' / original.name
            shutil.copyfile(original, target)
            target.chmod(0o444)
            files.append(dict(path=target.relative_to(staging).as_posix(),
                              sha256=hashlib.sha256(target.read_bytes()).hexdigest(), original=str(original)))
        write_json(staging / 'contracts/problem.json', dict(schema_version=1, status='DRAFT', freeze_id=None,
                   statement_files=files, tasks=[], problem_specific_requirements=[], unresolved=[], decisions=[]))
        write_json(staging / 'contracts/model.json', dict(schema_version=1, status='DRAFT', freeze_id=None,
                   problem_sha256=None, assumptions=[], models=[], verification_plan=[], decisions=[], fallback=None))
        with (staging / 'sources/sources.csv').open('x', encoding='utf-8', newline='') as handle:
            csv.writer(handle).writerow(['id', 'url', 'title', 'accessed_at', 'usage', 'kind', 'local_path', 'sha256', 'license', 'limitations'])
        (staging / 'logs/ai_usage.jsonl').touch()
        (staging / 'logs/worklog.md').write_text('# Worklog\n\nInitialized; no model or review completed.\n', encoding='utf-8')
        write_json(staging / 'verification/layout_review.json', layout)
        write_json(staging / 'verification/bilingual_review.json', bilingual)
        if root.is_symlink() or (root.exists() and (not root.is_dir() or any(root.iterdir()))):
            raise ValueError('Project root changed; refusing to replace existing contents')
        os.replace(staging, root)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return dict(status='INITIALIZED', root=str(root), inputs=len(files), rules=rules['verification'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--mode', choices=['live', 'practice', 'reproduce'], required=True)
    parser.add_argument('--problem', choices=['A', 'B', 'C'])
    parser.add_argument('--implementation', choices=['python', 'matlab', 'undecided'], default='undecided')
    parser.add_argument('--input', action='append', default=[])
    args = parser.parse_args()
    try:
        print(json.dumps(initialize(args.root, args.year, args.mode, args.problem, args.input, args.implementation), ensure_ascii=False))
    except (ValueError, OSError, TypeError, RuntimeError, RecursionError) as exc:
        print(json.dumps(dict(status='ERROR', error=str(exc))), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
