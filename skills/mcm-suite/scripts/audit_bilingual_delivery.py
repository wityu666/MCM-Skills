#!/usr/bin/env python3
"""Check bilingual artifact bindings and review records, never infer translation quality."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

from artifact_safety import read_json, safe_path, snapshot, write_json_output
from audit_delivery import audit as audit_english
from freeze_artifacts import digest, validate_manifest, verify


FLAGS = (
    'structure_and_task_mapping_verified', 'source_dependencies_verified', 'models_equations_symbols_verified',
    'numbers_units_scenarios_verified', 'figures_tables_data_verified',
    'citations_verified', 'conclusions_limits_verified',
    'actual_ai_disclosure_verified', 'zh_visual_all_pages_verified',
)
BINDINGS = ('zh_source', 'en_source', 'zh_pdf', 'en_pdf', 'english_layout_review', 'paper_content_manifest')
SCOPE = 'bilingual_static_preflight_only'


def validate_review(data, template=False):
    if (not isinstance(data, dict) or type(data.get('schema_version')) is not int
            or data['schema_version'] != 1):
        raise ValueError('Bilingual review must be a schema_version=1 object')
    if data.get('status') not in ['PASS', 'FAIL', 'INCOMPLETE', 'STALE']:
        raise ValueError('Invalid bilingual review status')
    for name in BINDINGS:
        if not isinstance(data.get(name), dict) or not {'path', 'sha256'} <= data[name].keys():
            raise ValueError(f'Bilingual review requires {name} path/hash binding')
    for name in FLAGS:
        if type(data.get(name)) is not bool:
            raise ValueError(f'{name} must be an explicit boolean')
    for name in ['evidence', 'unresolved', 'zh_page_evidence']:
        if not isinstance(data.get(name), list):
            raise ValueError(f'{name} must be an array')
    if template and (data['status'] != 'INCOMPLETE'
                     or any(data[name] for name in FLAGS)
                     or any(data[name]['path'] is not None or data[name]['sha256'] is not None for name in BINDINGS)
                     or data.get('freeze_id') is not None or data.get('result_manifest_sha256') is not None
                     or data.get('zh_page_count') is not None
                     or data['evidence'] != [] or data['zh_page_evidence'] != []
                     or not data['unresolved']):
        raise ValueError('Invalid unreviewed bilingual template')


def evidence_present(value):
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, (str, dict)) and bool(item) and (not isinstance(item, str) or bool(item.strip()))
        for item in value
    )


def binding_path(root, row):
    value = row.get('path')
    if (not isinstance(value, str) or not value.strip() or Path(value).is_absolute()
            or '..' in Path(value).parts):
        raise ValueError('Artifact bindings must use project-relative paths without traversal')
    expected = row.get('sha256')
    if (not isinstance(expected, str) or len(expected) != 64
            or any(char not in '0123456789abcdef' for char in expected)):
        raise ValueError('Artifact binding requires a lowercase SHA-256')
    return safe_path(root, value)


def editable_source(path):
    """Check supported source container, not completeness or language."""
    if path.suffix.lower() == '.tex':
        try:
            text = path.read_text(encoding='utf-8-sig')
            return bool(text.strip()) and not text.lstrip().startswith('%PDF-')
        except UnicodeError:
            return False
    if path.suffix.lower() == '.docx':
        try:
            with ZipFile(path) as document:
                if '[Content_Types].xml' not in document.namelist():
                    return False
                root = ET.fromstring(document.read('word/document.xml'))
                return root.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}document'
        except (BadZipFile, KeyError, ET.ParseError, OSError):
            return False
    return False


def existing_preflight(path):
    try:
        data = read_json(path)
        return (isinstance(data, dict) and data.get('scope') == SCOPE
                and data.get('status') in ['PRECHECK_PASS', 'FAIL', 'ERROR']
                and data.get('official_submission') == 'NOT_SUBMITTED'
                and isinstance(data.get('checks'), list))
    except (ValueError, TypeError, OSError, UnicodeError, RecursionError):
        return False


def protected_inputs(root, review, manifest):
    """Include source/result files so even an error output cannot replace inputs."""
    paths = [safe_path(root, review), safe_path(root, manifest),
             safe_path(root, 'context.json'), safe_path(root, 'rules.json')]
    data = read_json(paths[0])
    validate_review(data)
    for name in BINDINGS:
        row = data[name]
        if row['path'] is not None:
            paths.append(binding_path(root, row))
    result = validate_manifest(read_json(paths[1]))
    paths.extend(safe_path(root, item['path']) for item in result['files'])
    content_row = data['paper_content_manifest']
    if content_row['path'] is not None:
        content_path = binding_path(root, content_row)
        if content_path.is_file():
            content = validate_manifest(read_json(content_path))
            paths.extend(safe_path(root, item['path']) for item in content['files'])
    return list(dict.fromkeys(paths))


def audit_bilingual(root, review='verification/bilingual_review.json',
                    result_manifest='results/run_manifest.json', now=None):
    root = Path(root).resolve()
    review_path = safe_path(root, review)
    manifest_path = safe_path(root, result_manifest)
    base_paths = [review_path, manifest_path, safe_path(root, 'context.json'), safe_path(root, 'rules.json')]
    before = {path: snapshot(path) for path in base_paths}
    review_hash = digest(review_path)
    manifest_hash = digest(manifest_path)
    paths = protected_inputs(root, review, result_manifest)
    before.update({path: snapshot(path) for path in paths if path not in before})
    qa = read_json(review_path)
    validate_review(qa)
    frozen = verify(root, result_manifest)
    checks = []

    def check(name, ok, detail):
        checks.append(dict(id=name, status='PASS' if ok else 'FAIL', detail=detail))

    check('REVIEW_STATUS', qa['status'] == 'PASS' and qa['unresolved'] == [],
          'A completed human review without unresolved findings is required')
    check('RESULTS_STABLE', frozen['status'] == 'PASS', 'Frozen result artifacts must still match')
    check('RESULT_BINDING', qa.get('freeze_id') == frozen['freeze_id']
          and qa.get('result_manifest_sha256') == frozen['manifest_sha256'],
          'Review must bind the current result freeze and manifest bytes')
    bound, hashes = {}, {}
    for name in BINDINGS:
        row = qa[name]
        if row['path'] is None or row['sha256'] is None:
            check(name.upper() + '_HASH', False, 'Artifact has not been bound and reviewed')
            continue
        path = binding_path(root, row)
        bound[name] = path
        hashes[name] = digest(path) if path.is_file() else None
        check(name.upper() + '_HASH', hashes[name] is not None and row['sha256'] == hashes[name],
              'Binding must match the existing artifact bytes')
    complete = len(bound) == len(BINDINGS) and all(path.is_file() for path in bound.values())
    check('TWO_VERSIONS_PRESENT', complete, 'Both editable sources, PDFs, and English layout review are required')
    content_path = bound.get('paper_content_manifest')
    content_verified = None
    content_paths = set()
    if content_path is not None and content_path.is_file():
        content_verified = verify(root, str(content_path))
        content = validate_manifest(read_json(content_path))
        content_paths = {safe_path(root, item['path']) for item in content['files']}
    check('PAPER_CONTENT_STABLE', content_verified is not None and content_verified['status'] == 'PASS',
          'All declared paper source dependencies, figures and PDFs must still match their frozen bytes')
    check('PAPER_CONTENT_COVERAGE', all(bound.get(name) in content_paths
          for name in ['zh_source', 'en_source', 'zh_pdf', 'en_pdf']),
          'The paper content manifest must include both editable sources and both PDFs')
    excluded = {review_path, bound.get('english_layout_review'), safe_path(root, 'paper/paper_manifest.json')}
    check('PAPER_CONTENT_ACYCLIC', bool(content_paths) and not content_paths.intersection(excluded)
          and all(not path.is_relative_to(root / 'verification') for path in content_paths),
          'Content freezes exclude review records and the paper handoff manifest to avoid hash cycles')
    for name in ['zh_source', 'en_source']:
        path = bound.get(name)
        check(name.upper() + '_EDITABLE', path is not None and path.is_file() and editable_source(path),
              'Use an actual editable .docx or UTF-8 .tex source; a PDF is not a source')
    if complete:
        distinct = len(set(bound.values())) == len(BINDINGS) and all(
            not first.samefile(second)
            for index, first in enumerate(bound.values())
            for second in list(bound.values())[index + 1:]
        )
        check('DISTINCT_ARTIFACTS', distinct and hashes['zh_pdf'] != hashes['en_pdf'],
              'Separate language versions cannot reuse the same file or identical PDF bytes')
    else:
        check('DISTINCT_ARTIFACTS', False, 'Separate language artifacts are missing')
    zh_count = None
    zh_pdf = bound.get('zh_pdf')
    if zh_pdf is not None and zh_pdf.is_file():
        from pypdf import PdfReader
        if zh_pdf.suffix.lower() != '.pdf':
            raise ValueError('Chinese review artifact must be a PDF')
        reader = PdfReader(str(zh_pdf))
        if reader.is_encrypted:
            raise ValueError('Encrypted Chinese PDF cannot be reviewed')
        zh_count = len(reader.pages)
    check('ZH_PAGE_COUNT', type(qa.get('zh_page_count')) is int
          and zh_count is not None and zh_count > 0 and qa['zh_page_count'] == zh_count,
          f'Chinese review must match actual physical pages: {zh_count}')
    page_rows = qa['zh_page_evidence']
    page_evidence_ok = zh_count is not None and all(
        isinstance(row, dict) and type(row.get('page')) is int
        and evidence_present(row.get('evidence')) for row in page_rows
    )
    if page_evidence_ok:
        pages = [row['page'] for row in page_rows]
        page_evidence_ok = len(pages) == zh_count and set(pages) == set(range(1, zh_count + 1))
    check('ZH_ALL_PAGE_RECORDS', page_evidence_ok,
          'Record actual visual review evidence for every Chinese PDF page once')
    for name in FLAGS:
        check(name.upper(), qa[name] is True, 'Human review declaration; not inferred by this tool')
    check('BILINGUAL_REVIEW_EVIDENCE', evidence_present(qa['evidence']),
          'Record actual correspondence review locations and findings')
    english = None
    if complete:
        english = audit_english(root, str(bound['en_pdf']), str(bound['english_layout_review']), now=now)
    check('ENGLISH_PREFLIGHT', english is not None and english['status'] == 'PRECHECK_PASS',
          'The existing English submission preflight must pass for its bound current PDF')
    context = read_json(safe_path(root, 'context.json'))
    if context.get('mode') == 'live' and english is not None:
        # English preflight already verifies this claim and its timezone.
        rules = read_json(safe_path(root, 'rules.json'))
        stop = datetime.fromisoformat(rules['claims']['stop_work_at']['value'])
        check('BILINGUAL_EDIT_WINDOW', all(
            path.is_file() and datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) <= stop
            for path in content_paths.union({bound[name] for name in ['zh_source', 'en_source', 'zh_pdf', 'en_pdf']})
        ), 'Both language sources, PDFs and all declared paper input resources must be frozen before stop-work')
    check('INPUTS_STABLE', all(snapshot(path) == before[path] for path in paths),
          'Bound artifacts, rules and review records must remain unchanged during preflight')
    return dict(status='PRECHECK_PASS' if all(row['status'] == 'PASS' for row in checks) else 'FAIL',
                scope=SCOPE, review_sha256=review_hash,
                result_manifest_sha256=manifest_hash, freeze_id=frozen['freeze_id'],
                artifact_sha256=hashes, zh_page_count=zh_count, checks=checks,
                english_preflight=english, official_submission='NOT_SUBMITTED',
                limitation='Checks bytes, containers and supplied review records only; does not verify language equivalence, visual quality or completeness of declared TeX dependencies.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--review', default='verification/bilingual_review.json')
    parser.add_argument('--result-manifest', default='results/run_manifest.json')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root, protected = Path(args.root).resolve(), None
    try:
        protected = protected_inputs(root, args.review, args.result_manifest)
        result = audit_bilingual(root, args.review, args.result_manifest)
        protected = list(dict.fromkeys(protected + protected_inputs(root, args.review, args.result_manifest)))
        if (digest(safe_path(root, args.review)) != result['review_sha256']
                or digest(safe_path(root, args.result_manifest)) != result['result_manifest_sha256']):
            raise ValueError('Review or result manifest changed before preflight publication')
        write_json_output(root, args.output, result, protected, existing_preflight)
    except Exception as error:
        result = dict(status='ERROR', scope=SCOPE, checks=[], error=str(error), official_submission='NOT_SUBMITTED')
        if protected is not None:
            try:
                write_json_output(root, args.output, result, protected, existing_preflight)
            except Exception:
                pass
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result['status'] == 'PRECHECK_PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
