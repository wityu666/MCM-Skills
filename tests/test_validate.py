"""Tamper a private package copy to exercise integrity and portability failures."""
import json
import hashlib
from pathlib import Path
import shutil
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate import validate

REPOSITORY = Path(__file__).resolve().parents[1]


@pytest.fixture
def private_package(tmp_path):
    destination = tmp_path / 'repository'
    shutil.copytree(REPOSITORY / 'skills', destination / 'skills',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.pytest_cache'))
    return destination


def test_real_bundle_is_valid():
    result = validate(REPOSITORY)
    assert result['status'] == 'PASS', result['errors']
    assert result['counts']['skills'] == 26
    assert result['counts']['cards'] == 198
    assert result['counts']['implementation_bindings'] == 10


@pytest.mark.parametrize('text,expected', [
    ('\n[missing](references/not-present.md)\n', 'Missing bundled resource'),
    ('\n[escape](../../outside.md)\n', 'escapes bundled skills'),
    ('\nUse $mcm-not-installed.\n', 'Unbundled skill call'),
    ('\nUse $cumcm-live-python-coder.\n', 'Dependency on an unbundled'),
    ('\nRead /Users/example/private/model.py.\n', 'Machine-specific path'),
])
def test_nonportable_dependency_rejected(private_package, text, expected):
    path = private_package / 'skills/mcm-suite/SKILL.md'
    path.write_text(path.read_text(encoding='utf-8') + text, encoding='utf-8')
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any(expected in error['error'] for error in result['errors'])


def test_changed_implementation_invalidates_evidence(private_package):
    path = private_package / 'skills/mcm-modeling-discrete/assets/discrete_reference.py'
    path.write_text(path.read_text(encoding='utf-8') + '\n# Changed source\n', encoding='utf-8')
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('hash mismatch' in error['error'] for error in result['errors'])


def test_missing_current_evidence_rejected(private_package):
    family = private_package / 'skills/mcm-modeling-evaluation'
    cards = json.loads((family / 'references/cards.json').read_text())
    tested = next(card for card in cards if card['knowledge_level'] == 'REFERENCE_IMPL_TESTED')
    path = family / tested['implementation_evidence']['python']['report']
    path.unlink()
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('Missing bundled resource' in error['error'] for error in result['errors'])


@pytest.mark.parametrize('change,expected', [
    (lambda report: {}, 'passing evidence report'),
    (lambda report: {**report, 'status': 'FAIL'}, 'passing evidence report'),
    (lambda report: {**report, 'scope': ' '}, 'nonempty scope'),
    (lambda report: {**report, 'tests': 0}, 'positive integer test count'),
    (lambda report: {**report, 'tests': True}, 'positive integer test count'),
    (lambda report: {**report, 'tests': 1.5}, 'positive integer test count'),
    (lambda report: {**report, 'runtime': {}}, 'python runtime evidence'),
    (lambda report: {**report, 'source_files': []}, 'source_files must be a nonempty array'),
    (lambda report: {**report, 'test_files': []}, 'test_files must be a nonempty array'),
])
def test_tested_claim_requires_actual_report_metadata(private_package, change, expected):
    path = private_package / 'skills/mcm-modeling-evaluation/tests/release_evidence.json'
    report = json.loads(path.read_text(encoding='utf-8'))
    path.write_text(json.dumps(change(report)), encoding='utf-8')
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any(expected in error['error'] for error in result['errors'])


def test_tested_report_must_bind_the_declared_implementation(private_package):
    family = private_package / 'skills/mcm-modeling-evaluation'
    path = family / 'tests/release_evidence.json'
    report = json.loads(path.read_text(encoding='utf-8'))
    other_file = family / 'tests/test_entropy_topsis.py'
    # A valid hash for a different bundled file does not test the declared source.
    report['source_files'] = [{'path': 'tests/test_entropy_topsis.py',
                               'sha256': hashlib.sha256(other_file.read_bytes()).hexdigest()}]
    path.write_text(json.dumps(report), encoding='utf-8')
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('does not bind its python implementation source' in error['error']
               for error in result['errors'])


def edit_family_and_catalog(repository, family_name, edit):
    """Keep catalog integrity valid so evidence regressions exercise their own gate."""
    path = repository / ('skills/mcm-modeling-' + family_name) / 'references/cards.json'
    cards = json.loads(path.read_text(encoding='utf-8'))
    for card in cards:
        edit(card)
    path.write_text(json.dumps(cards), encoding='utf-8')
    by_id = {card['id']: card for card in cards}
    catalog_path = repository / 'skills/mcm-modeling-library/assets/catalog.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    for index, card in enumerate(catalog['cards']):
        if card['id'] in by_id:
            catalog['cards'][index] = {**by_id[card['id']], 'card_source': card['card_source'],
                                       'card_source_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    catalog_path.write_text(json.dumps(catalog), encoding='utf-8')


@pytest.mark.parametrize('replacement', [{}, {'python': 'NOT_RUN'}, None])
def test_tested_knowledge_grade_needs_current_evidence(private_package, replacement):
    def edit(card):
        if card['knowledge_level'] == 'REFERENCE_IMPL_TESTED':
            card['implementation_evidence'] = replacement
    edit_family_and_catalog(private_package, 'evaluation', edit)
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('tested knowledge level needs current tested implementation evidence' in error['error']
               for error in result['errors'])


def test_python_report_cannot_supply_matlab_execution_evidence(private_package):
    def edit(card):
        if card['knowledge_level'] == 'REFERENCE_IMPL_TESTED':
            card['implementation_evidence']['matlab'] = dict(card['implementation_evidence']['python'])
    edit_family_and_catalog(private_package, 'evaluation', edit)
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('matlab runtime evidence' in error['error'] for error in result['errors'])


def test_language_runtime_label_alone_does_not_change_source_language(private_package):
    report_path = private_package / 'skills/mcm-modeling-evaluation/tests/release_evidence.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    report['runtime']['matlab'] = 'R2026a'
    report_path.write_text(json.dumps(report), encoding='utf-8')
    def edit(card):
        if card['knowledge_level'] == 'REFERENCE_IMPL_TESTED':
            card['implementation_evidence']['matlab'] = dict(card['implementation_evidence']['python'])
    edit_family_and_catalog(private_package, 'evaluation', edit)
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('matlab claim needs a matching implementation source' in error['error']
               for error in result['errors'])


def test_matlab_source_must_be_bound_by_its_report(private_package):
    family = private_package / 'skills/mcm-modeling-mechanisms'
    report_path = family / 'tests/release_evidence.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    report['runtime']['matlab'] = 'R2026a'
    report_path.write_text(json.dumps(report), encoding='utf-8')
    def edit(card):
        if card['id'] == 'mech-heat-diffusion-cn':
            matlab = card['implementation_evidence']['matlab']
            matlab.update({'status': 'PASS', 'report': 'tests/release_evidence.json'})
    edit_family_and_catalog(private_package, 'mechanisms', edit)
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('does not bind its matlab implementation source' in error['error']
               for error in result['errors'])


def test_stale_catalog_hash_rejected(private_package):
    path = private_package / 'skills/mcm-modeling-library/assets/catalog.json'
    payload = json.loads(path.read_text(encoding='utf-8'))
    payload['cards'][0]['card_source_sha256'] = '0' * 64
    path.write_text(json.dumps(payload), encoding='utf-8')
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('Stale family-card hash' in error['error'] for error in result['errors'])


def test_duplicate_json_keys_rejected(private_package):
    path = private_package / 'skills/mcm-modeling-library/assets/catalog.json'
    path.write_text('{"cards": [], "cards": []}', encoding='utf-8')
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('Duplicate JSON key' in error['error'] for error in result['errors'])


def test_external_symlink_is_rejected_without_reading_target(private_package, tmp_path, monkeypatch):
    external = tmp_path / 'private-external.json'
    external.write_text('{"private": "not package data"}', encoding='utf-8')
    path = private_package / 'skills/mcm-modeling-control/references/cards.json'
    path.unlink()
    path.symlink_to(external)
    original = Path.read_text

    def guarded_read(candidate, *args, **kwargs):
        if candidate.resolve() == external.resolve():
            raise AssertionError('Validator attempted to read outside the package')
        return original(candidate, *args, **kwargs)

    monkeypatch.setattr(Path, 'read_text', guarded_read)
    result = validate(private_package)
    assert result['status'] == 'FAIL'
    assert any('Symlink resource' in error['error'] for error in result['errors'])
    assert any('escapes bundled skills' in error['error'] for error in result['errors'])
