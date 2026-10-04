"""Installer checks use tiny synthetic packages and never the real skill home."""
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from safe_install import fingerprint, install
from suite_config import EXPECTED_SKILLS


@pytest.fixture
def package(tmp_path):
    source = tmp_path / 'source'
    for name in EXPECTED_SKILLS:
        folder = source / name
        folder.mkdir(parents=True)
        (folder / 'SKILL.md').write_text('source ' + name, encoding='utf-8')
    return source, tmp_path / 'destination'


def test_exact_names_required(package):
    source, destination = package
    (source / EXPECTED_SKILLS[0]).rename(source / 'unrelated-module')
    with pytest.raises(ValueError, match='complete expected named'):
        install(source, destination, EXPECTED_SKILLS)
    assert not destination.exists()


def test_check_is_read_only(package):
    source, destination = package
    assert install(source, destination, EXPECTED_SKILLS, check=True)['status'] == 'INSTALLABLE'
    assert not destination.exists()


def test_fresh_install_and_identical_reuse(package):
    source, destination = package
    result = install(source, destination, EXPECTED_SKILLS)
    assert set(result['installed']) == set(EXPECTED_SKILLS)
    for name in EXPECTED_SKILLS:
        assert fingerprint(source / name) == fingerprint(destination / name)
    again = install(source, destination, EXPECTED_SKILLS)
    assert not again['installed'] and set(again['reused']) == set(EXPECTED_SKILLS)


def test_different_existing_skill_preserved(package):
    source, destination = package
    target = destination / EXPECTED_SKILLS[0]
    target.mkdir(parents=True)
    (target / 'SKILL.md').write_text('user-edited', encoding='utf-8')
    with pytest.raises(ValueError, match='Refusing to overwrite'):
        install(source, destination, EXPECTED_SKILLS)
    assert (target / 'SKILL.md').read_text() == 'user-edited'
    assert len(list(destination.iterdir())) == 1


def test_prepare_failure_never_publishes(package):
    source, destination = package
    original = shutil.copytree
    calls = 0

    def fail_second(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError('copy interrupted')
        return original(*args, **kwargs)

    with patch('safe_install.shutil.copytree', side_effect=fail_second):
        with pytest.raises(ValueError, match='rolled back'):
            install(source, destination, EXPECTED_SKILLS)
    assert not list(destination.iterdir())


def test_publication_failure_rolls_back_only_new_skills(package):
    source, destination = package
    unrelated = destination / 'unrelated'
    unrelated.mkdir(parents=True)
    (unrelated / 'keep.txt').write_text('keep', encoding='utf-8')
    import safe_install
    original = safe_install.os.replace
    calls = 0

    def fail_second(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError('publish interrupted')
        return original(*args, **kwargs)

    with patch('safe_install.os.replace', side_effect=fail_second):
        with pytest.raises(ValueError, match='rolled back'):
            install(source, destination, EXPECTED_SKILLS)
    assert [path.name for path in destination.iterdir()] == ['unrelated']
    assert (unrelated / 'keep.txt').read_text() == 'keep'


def test_symlink_source_resource_rejected(package, tmp_path):
    source, destination = package
    external = tmp_path / 'external.txt'
    external.write_text('outside', encoding='utf-8')
    (source / EXPECTED_SKILLS[0] / 'source-link.txt').symlink_to(external)
    with pytest.raises(ValueError, match='Symlink'):
        install(source, destination, EXPECTED_SKILLS)
    assert not destination.exists()


def test_overlap_rejected(package):
    source, _ = package
    with pytest.raises(ValueError, match='overlap'):
        install(source, source / 'nested', EXPECTED_SKILLS)


def test_symlink_source_root_rejected(package, tmp_path):
    source, destination = package
    link = tmp_path / 'linked-source'
    link.symlink_to(source, target_is_directory=True)
    with pytest.raises(ValueError, match='Symlink skill-set source'):
        install(link, destination, EXPECTED_SKILLS)
    assert not destination.exists()


def test_cache_named_ancestor_does_not_hide_skill_content(package, tmp_path):
    source, _ = package
    cache_parent = tmp_path / '__pycache__'
    nested_source = cache_parent / 'source'
    shutil.copytree(source, nested_source)
    destination = cache_parent / 'destination'
    target = destination / EXPECTED_SKILLS[0]
    target.mkdir(parents=True)
    (target / 'SKILL.md').write_text('different content', encoding='utf-8')
    with pytest.raises(ValueError, match='Refusing to overwrite'):
        install(nested_source, destination, EXPECTED_SKILLS)
    assert fingerprint(nested_source / EXPECTED_SKILLS[0])
    assert (target / 'SKILL.md').read_text() == 'different content'


def test_concurrent_edit_preserved_during_rollback(package):
    source, destination = package
    import safe_install
    original = safe_install.os.replace
    published = []

    def interfere(prepared, target):
        if published:
            (published[0] / 'SKILL.md').write_text('concurrent edit', encoding='utf-8')
            raise OSError('later publication failed')
        original(prepared, target)
        published.append(Path(target))

    with patch('safe_install.os.replace', side_effect=interfere):
        with pytest.raises(ValueError, match='preserved concurrent edits'):
            install(source, destination, EXPECTED_SKILLS)
    assert (published[0] / 'SKILL.md').read_text() == 'concurrent edit'
