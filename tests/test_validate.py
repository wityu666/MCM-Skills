"""Tamper a private package copy to exercise integrity and portability failures."""
import json
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
