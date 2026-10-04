#!/usr/bin/env python3
"""PDF/rules/review preflight. This never proves official receipt or visual quality."""
import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

from freeze_artifacts import digest, safe_path
from artifact_safety import read_json, snapshot, write_json_output


def validate_metadata(context, rules, qa):
    for name, data in [('context', context), ('rules', rules), ('review', qa)]:
        if not isinstance(data, dict):
            raise ValueError(f'{name} must be a JSON object')
    for name, data in [('context', context), ('rules', rules)]:
        if type(data.get('schema_version')) is not int or data['schema_version'] != 1:
            raise ValueError(f'{name} schema_version must be integer 1')
        if type(data.get('year')) is not int or not 1985 <= data['year'] <= 9999:
            raise ValueError(f'{name} year must be a valid integer')
    if context.get('mode') not in ['live', 'practice', 'reproduce']:
        raise ValueError('Context mode must be live, practice or reproduce')
    if not isinstance(rules.get('claims'), dict) or not isinstance(rules.get('sources'), list):
        raise ValueError('Rules claims/sources must be an object/array')
    identifiers = []
    for source in rules['sources']:
        if not isinstance(source, dict) or not isinstance(source.get('id'), str) or not source['id'].strip():
            raise ValueError('Rule source requires a nonempty string id')
        identifiers.append(source['id'])
    if len(set(identifiers)) != len(identifiers):
        raise ValueError('Duplicate rule source ids')
    if not isinstance(qa.get('unresolved'), list):
        raise ValueError('Review unresolved must be an array')


def existing_preflight(path):
    try:
        value = read_json(path)
        return (isinstance(value, dict) and value.get('scope') == 'static_preflight_only'
                and value.get('status') in ['PRECHECK_PASS', 'FAIL', 'ERROR']
                and isinstance(value.get('checks'), list)
                and value.get('official_submission') == 'NOT_SUBMITTED')
    except (ValueError, TypeError, OSError, UnicodeError, RecursionError):
        return False


def audit(root, pdf, review, now=None):
    root = Path(root).resolve()
    pdf = safe_path(root, pdf)
    review_path = safe_path(root, review)
    context_path = safe_path(root, 'context.json')
    rules_path = safe_path(root, 'rules.json')
    paths = [context_path, rules_path, review_path, pdf]
    before = {path: snapshot(path) for path in paths}
    hashes = {path: digest(path) for path in paths}
    context = read_json(context_path)
    rules = read_json(rules_path)
    qa = read_json(review_path)
    validate_metadata(context, rules, qa)
    from pypdf import PdfReader
    reader = PdfReader(str(pdf))
    if reader.is_encrypted:
        raise ValueError('Encrypted PDF cannot be reviewed as a submission')
    page_count = len(reader.pages)
    checks = []

    def check(name, ok, detail):
        checks.append(dict(id=name, status='PASS' if ok else 'FAIL', detail=detail))

    def claim(key):
        row = rules.get('claims', {}).get(key, {})
        if not isinstance(row, dict) or row.get('status') != 'verified' or row.get('source_id') not in {x.get('id') for x in rules.get('sources', [])}:
            raise ValueError(f'Unverified or unsourced rule: {key}')
        return row.get('value')

    check('MCM_SCOPE', context.get('contest') == 'MCM' and context.get('problem') in ['A', 'B', 'C'], 'MCM A-C required')
    check('YEAR', context.get('year') == rules.get('year') and rules.get('contest') == 'MCM', 'Context and rules year must match')
    live = context.get('mode') == 'live'
    check('RULE_REFRESH', rules.get('verification') == 'verified' if live else rules.get('verification') in ['verified', 'reference_snapshot'], 'Live requires freshly verified rules')
    number = context.get('team_control_number')
    needs_number = live or number is not None
    check('FILENAME', isinstance(number, str) and number.isascii() and number.isdigit() and pdf.name == number + '.pdf' if needs_number else pdf.suffix.lower() == '.pdf',
          'Live/assigned team uses actual control number; training without a team number uses an ordinary PDF filename')
    if live:
        check('PROBLEM_RULES', rules.get('problem_specific_requirements_status') == 'verified', 'Actual current problem requirements must be verified')
    check('PDF_REVIEW_HASH', qa.get('pdf_sha256') == hashes[pdf], 'Review must match final PDF bytes')
    check('REVIEW_STATUS', qa.get('status') == 'PASS' and qa.get('unresolved') == [], 'No unresolved layout findings')
    main = qa.get('main_page_count')
    start = qa.get('ai_report_start_page')
    valid_main = isinstance(main, int) and not isinstance(main, bool) and 1 <= main <= page_count
    check('PAGE_MAP', valid_main and (start is None and main == page_count or type(start) is int and start == main + 1 and start <= page_count), 'Only trailing AI report can be excluded')
    limit = claim('max_main_pages')
    check('PAGE_LIMIT', type(limit) is int and limit > 0 and valid_main and main <= limit, f'Main pages limit: {limit}')
    check('PAGE_COUNT_MATCH', type(qa.get('page_count')) is int and qa['page_count'] == page_count, f'Actual physical pages: {page_count}')
    check('AI_PAGE_EXCLUSION', start is None or claim('ai_report_excluded') is True, 'Exclude only verified AI report pages')
    ai_used = qa.get('ai_used')
    check('AI_USE_DECLARED', type(ai_used) is bool, 'ai_used must be explicit boolean')
    required = claim('ai_report_required_if_used')
    if type(required) is not bool:
        raise ValueError('ai_report_required_if_used must be a boolean')
    check('AI_REPORT_PRESENT', ai_used is False or ai_used is True and (required is False or start is not None), 'AI use requires report under current rule')
    size_limit = claim('max_file_mb_exclusive')
    check('FILE_SIZE', type(size_limit) in [int, float] and math.isfinite(size_limit) and size_limit > 0 and pdf.stat().st_size < size_limit * 1_000_000, f'Bytes must be strictly below {size_limit} decimal MB')
    for key in ['main_pages_verified', 'summary_first_page_verified', 'english_verified', 'anonymous_verified',
                'control_number_each_page_verified', 'minimum_font_verified', 'visual_all_pages_verified',
                'ai_report_appropriate_verified', 'citations_verified', 'task_coverage_verified']:
        if key == 'control_number_each_page_verified' and not needs_number:
            check(key.upper(), True, 'Not applicable to training without an assigned control number')
            continue
        check(key.upper(), qa.get(key) is True, 'Requires actual review evidence, not automatic inference')
    evidence = qa.get('evidence')
    check('REVIEW_EVIDENCE', isinstance(evidence, list) and bool(evidence) and all(isinstance(x, (str, dict)) and bool(x) for x in evidence), 'Nonempty review evidence required')
    if live:
        stop = datetime.fromisoformat(claim('stop_work_at'))
        submit = datetime.fromisoformat(claim('submit_by'))
        if stop.tzinfo is None or submit.tzinfo is None:
            raise ValueError('Official deadlines require timezone')
        if stop > submit:
            raise ValueError('Stop-work cannot be after submission deadline')
        moment = datetime.now(timezone.utc) if now is None else now
        if not isinstance(moment, datetime) or moment.tzinfo is None:
            raise ValueError('Audit time must be a timezone-aware datetime')
        check('EDIT_WINDOW', datetime.fromtimestamp(pdf.stat().st_mtime, timezone.utc) <= stop, 'PDF must be frozen before stop-work deadline')
        check('UPLOAD_WINDOW', moment <= submit, 'After deadline, local audit cannot establish timely submission')
    check('INPUTS_STABLE', all(snapshot(path) == before[path] for path in paths),
          'Inputs must not change while auditing')
    return dict(status='PRECHECK_PASS' if all(x['status'] == 'PASS' for x in checks) else 'FAIL',
                scope='static_preflight_only', pdf_sha256=hashes[pdf],
                context_sha256=hashes[context_path], rules_sha256=hashes[rules_path],
                review_sha256=hashes[review_path], page_count=page_count,
                main_page_count=main, checks=checks, official_submission='NOT_SUBMITTED')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--pdf', required=True)
    p.add_argument('--review', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    root, target, protected = None, None, None
    try:
        root = Path(a.root).resolve()
        target = safe_path(root, a.output)
        protected = [safe_path(root, a.pdf), safe_path(root, a.review), root / 'rules.json', root / 'context.json']
        if target in protected:
            raise ValueError('Output cannot overwrite an input')
        result = audit(root, a.pdf, a.review)
        write_json_output(root, a.output, result, protected, existing_preflight)
    except Exception as exc:
        result = dict(status='ERROR', scope='static_preflight_only', checks=[],
                      error=str(exc), official_submission='NOT_SUBMITTED')
        if root is not None and target is not None and protected is not None:
            try:
                write_json_output(root, a.output, result, protected, existing_preflight)
            except Exception:
                # An unsafe output is never modified, including error reporting.
                pass
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result['status'] == 'PRECHECK_PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
