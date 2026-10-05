#!/usr/bin/env python3
"""Check bundled skills, model-card integrity and portable resource dependencies.

This is a static package check, not a mathematical, contest or rendering pass.
Only files under the repository's skills directory are inspected.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import yaml

from suite_config import EXPECTED_CARD_COUNT, EXPECTED_SKILLS, MODEL_FAMILIES

LOCAL_PATH = re.compile(r'(?:/(?:Users|Volumes|private|home|Applications)/|/opt/anaconda\w*/|file:(?://|/)|[A-Za-z]:[\\/]Users[\\/])')
EXTERNAL_SKILL = re.compile(r'(?:\$cumcm[-\w]*|cumcm-live-[\w-]+|\$modeling-[\w-]+|\.\./modeling-[\w-]+)')
SKILL_CALL = re.compile(r'\$(mcm-[a-z0-9-]+)\b')
MD_LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)]+)\)')
HASH = re.compile(r'[0-9a-f]{64}\Z')
TEXT_SUFFIXES = {'.md', '.json', '.yaml', '.yml', '.py', '.m', '.txt', '.csv', '.tex'}
TESTED_STATUSES = {'PASS', 'TESTED'}
IMPLEMENTATION_SUFFIXES = {'python': {'.py', '.ipynb'}, 'matlab': {'.m', '.mlx'}}


def digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(block)
    return hasher.hexdigest()


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError('Duplicate JSON key: ' + name)
        result[name] = value
    return result


def reject_constant(value):
    raise ValueError('Nonfinite JSON value: ' + value)


def finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('Nonfinite JSON value: ' + value)
    return number


def read_json(path, boundary=None):
    if boundary is not None and not path.resolve().is_relative_to(boundary):
        raise ValueError('JSON resource escapes bundled skills')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=finite_float)


def resolve_resource(base, relative, skills):
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError('Resource path must be a nonempty string')
    if Path(relative).is_absolute() or '\\' in relative:
        raise ValueError('Resource path must be relative')
    path = (base / relative).resolve()
    if not path.is_relative_to(skills):
        raise ValueError('Resource escapes bundled skills: ' + relative)
    if not path.is_file():
        raise ValueError('Missing bundled resource: ' + relative)
    return path


def frontmatter(text):
    if not text.startswith('---\n'):
        raise ValueError('Missing YAML front matter')
    parts = text.split('---', 2)
    if len(parts) != 3:
        raise ValueError('Unterminated YAML front matter')
    value = yaml.safe_load(parts[1])
    if not isinstance(value, dict):
        raise ValueError('Front matter must be an object')
    return value


def evidence_bindings(report, base, skills, identifier, require_tested):
    """Check report hashes without treating their presence as proof of a run."""
    bound_sources = set()
    count = 0
    for key in ['source_files', 'test_files']:
        bindings = report.get(key, [])
        if not isinstance(bindings, list) or (require_tested and not bindings):
            requirement = 'a nonempty array' if require_tested else 'an array'
            raise ValueError(identifier + ' evidence ' + key + ' must be ' + requirement)
        for binding in bindings:
            if not isinstance(binding, dict) or not HASH.fullmatch(str(binding.get('sha256', ''))):
                raise ValueError(identifier + ' invalid evidence hash binding')
            bound_path = resolve_resource(base, binding.get('path'), skills)
            if digest(bound_path) != binding['sha256']:
                raise ValueError(identifier + ' evidence file hash mismatch: ' + binding['path'])
            if key == 'source_files':
                bound_sources.add(bound_path)
            count += 1
    return bound_sources, count


def validate(root):
    root = Path(root).resolve()
    skills = root / 'skills'
    errors = []
    counts = {'skills': 0, 'cards': 0, 'relative_links': 0, 'skill_calls': 0,
              'implementation_bindings': 0, 'evidence_bindings': 0}

    def record(path, message):
        try:
            name = path.relative_to(root).as_posix()
        except ValueError:
            name = '<outside repository>'
        errors.append({'file': name, 'error': str(message)})

    if not skills.is_dir() or skills.is_symlink():
        record(skills, 'skills must be a real directory')
        return {'status': 'FAIL', 'scope': 'STATIC_PACKAGE_CHECK', 'counts': counts, 'errors': errors}
    folders = {path.name: path for path in skills.iterdir() if path.is_dir() and not path.is_symlink()}
    if set(folders) != set(EXPECTED_SKILLS):
        record(skills, 'Skill names differ; missing=' + ','.join(sorted(set(EXPECTED_SKILLS) - set(folders))) +
               '; extra=' + ','.join(sorted(set(folders) - set(EXPECTED_SKILLS))))
    counts['skills'] = len(folders)

    for path in skills.rglob('*'):
        if path.is_symlink():
            record(path, 'Symlink resource is not self-contained')
            continue
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as error:
            record(path, error)
            continue
        if LOCAL_PATH.search(text):
            record(path, 'Machine-specific path found')
        if EXTERNAL_SKILL.search(text):
            record(path, 'Dependency on an unbundled/general or CUMCM skill found')
        for name in SKILL_CALL.findall(text):
            counts['skill_calls'] += 1
            if name not in folders:
                record(path, 'Unbundled skill call: ' + name)
        if path.suffix == '.md':
            for raw in MD_LINK.findall(text):
                target = raw.strip()
                if target.startswith('<'):
                    target = target[1:].split('>', 1)[0]
                else:
                    target = target.split(' ', 1)[0]
                parsed = urlsplit(target)
                if parsed.scheme == 'file':
                    record(path, 'Local file URI is not portable: ' + target)
                    continue
                if parsed.scheme or parsed.netloc or target.startswith('#'):
                    continue
                relative = unquote(parsed.path)
                if not relative:
                    continue
                try:
                    resolve_resource(path.parent, relative, skills)
                    counts['relative_links'] += 1
                except (OSError, ValueError) as error:
                    record(path, error)
        if path.suffix == '.json':
            try:
                read_json(path, skills)
            except (OSError, ValueError, RecursionError) as error:
                record(path, error)

    for name, folder in folders.items():
        try:
            skill_path = resolve_resource(folder, 'SKILL.md', skills)
            meta = frontmatter(skill_path.read_text(encoding='utf-8'))
            if meta.get('name') != name:
                raise ValueError('Front-matter name must match the folder')
            if not isinstance(meta.get('description'), str) or not meta['description'].strip():
                raise ValueError('description must be nonempty text')
            if not re.fullmatch(r'[a-z0-9-]{1,64}', name):
                raise ValueError('Invalid skill name')
            ui_path = resolve_resource(folder, 'agents/openai.yaml', skills)
            ui = yaml.safe_load(ui_path.read_text(encoding='utf-8'))
            if not isinstance(ui, dict) or not isinstance(ui.get('interface'), dict):
                raise ValueError('Agent UI must contain an interface object')
            for key in ['display_name', 'short_description', 'default_prompt']:
                value = ui['interface'].get(key)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError('Agent UI needs nonempty ' + key)
            if '$' + name not in ui['interface']['default_prompt']:
                raise ValueError('default_prompt must name this skill')
        except (OSError, ValueError, yaml.YAMLError, UnicodeError) as error:
            record(folder, error)

    family_cards = {}
    card_sources = []
    for family in MODEL_FAMILIES:
        references = skills / ('mcm-modeling-' + family) / 'references'
        card_sources.append((family, references / 'cards.json'))
        supplementary = references / 'supplemental-cards.json'
        if supplementary.exists():
            card_sources.append((family, supplementary))
    for family, path in card_sources:
        try:
            cards = read_json(path, skills)
            if not isinstance(cards, list):
                raise ValueError('Family model cards must be an array')
            for card in cards:
                if not isinstance(card, dict) or not isinstance(card.get('id'), str) or not card['id'].strip():
                    raise ValueError('Each card needs a nonempty id')
                identifier = card['id']
                if identifier in family_cards:
                    raise ValueError('Duplicate card id: ' + identifier)
                if card.get('family') != family:
                    raise ValueError('Wrong family for ' + identifier)
                for key in ['name', 'purpose', 'kind', 'knowledge_level']:
                    if not isinstance(card.get(key), str) or not card[key].strip():
                        raise ValueError(identifier + ' needs nonempty ' + key)
                if card['kind'] not in {'model', 'method', 'solver', 'auxiliary'}:
                    raise ValueError(identifier + ' has an unknown model-card kind')
                if card['knowledge_level'] not in {'INDEXED_ONLY', 'THEORY_GUIDE_REVIEWED',
                                                   'REFERENCE_IMPL_TESTED', 'REAL_CASE_REPRODUCED'}:
                    raise ValueError(identifier + ' has an unknown knowledge level')
                if not isinstance(card.get('mathematics'), dict) or not card['mathematics'].get('core'):
                    raise ValueError(identifier + ' needs core mathematics')
                for key in ['minimum_data', 'assumptions', 'algorithm_steps', 'verification', 'failure_modes']:
                    if not isinstance(card.get(key), list) or not card[key]:
                        raise ValueError(identifier + ' needs a nonempty ' + key + ' array')
                for key in ['python', 'matlab']:
                    if not isinstance(card.get(key), dict):
                        raise ValueError(identifier + ' needs ' + key + ' implementation guidance')
                family_cards[identifier] = (card, path)
                implementation = card.get('reference_implementation')
                if implementation is not None:
                    source = resolve_resource(path.parent.parent, implementation, skills)
                    counts['implementation_bindings'] += 1
                else:
                    source = None
                evidence = card.get('implementation_evidence', {})
                tested_languages = set()
                if isinstance(evidence, dict):
                    for language in ['python', 'matlab']:
                        item = evidence.get(language)
                        if not isinstance(item, dict):
                            if isinstance(item, str) and item in TESTED_STATUSES:
                                raise ValueError(identifier + ' claims tested implementation without a bundled report')
                            continue
                        implementation_source = source
                        if 'path' in item:
                            implementation_source = resolve_resource(path.parent.parent, item['path'], skills)
                        claims_tested = item.get('status') in TESTED_STATUSES
                        report_name = item.get('report', item.get('evidence'))
                        if claims_tested and not report_name:
                            raise ValueError(identifier + ' claims tested implementation without a bundled report')
                        if report_name:
                            report_path = resolve_resource(path.parent.parent, report_name, skills)
                            report = read_json(report_path, skills)
                            if not isinstance(report, dict):
                                raise ValueError(identifier + ' evidence report must be an object')
                            if claims_tested:
                                if report.get('status') not in TESTED_STATUSES:
                                    raise ValueError(identifier + ' tested claim needs a passing evidence report')
                                if not isinstance(report.get('scope'), str) or not report['scope'].strip():
                                    raise ValueError(identifier + ' tested report needs nonempty scope')
                                tests = report.get('tests')
                                if not isinstance(tests, int) or isinstance(tests, bool) or tests <= 0:
                                    raise ValueError(identifier + ' tested report needs a positive integer test count')
                                runtime = report.get('runtime', {})
                                if not isinstance(runtime, dict) or not isinstance(runtime.get(language), str) or not runtime[language].strip():
                                    raise ValueError(identifier + ' tested report lacks ' + language + ' runtime evidence')
                                if implementation_source is None or implementation_source.suffix not in IMPLEMENTATION_SUFFIXES[language]:
                                    raise ValueError(identifier + ' tested ' + language + ' claim needs a matching implementation source')
                            bound_sources, binding_count = evidence_bindings(
                                report, path.parent.parent, skills, identifier, claims_tested)
                            counts['evidence_bindings'] += binding_count
                            if claims_tested:
                                if implementation_source not in bound_sources:
                                    raise ValueError(identifier + ' tested report does not bind its ' + language + ' implementation source')
                                tested_languages.add(language)
                        declared_hash = item.get('source_sha256')
                        if declared_hash is not None:
                            if implementation_source is None or not HASH.fullmatch(str(declared_hash)) or digest(implementation_source) != declared_hash:
                                raise ValueError(identifier + ' implementation source hash mismatch')
                if card['knowledge_level'] in {'REFERENCE_IMPL_TESTED', 'REAL_CASE_REPRODUCED'} and not tested_languages:
                    raise ValueError(identifier + ' tested knowledge level needs current tested implementation evidence')
        except (OSError, ValueError, TypeError, RecursionError) as error:
            record(path, error)

    catalog_path = skills / 'mcm-modeling-library/assets/catalog.json'
    try:
        catalog = read_json(catalog_path, skills)
        if not isinstance(catalog, dict) or not isinstance(catalog.get('cards'), list):
            raise ValueError('Catalog must be an object with cards')
        cards = catalog['cards']
        counts['cards'] = len(cards)
        if len(cards) != EXPECTED_CARD_COUNT or len(family_cards) != EXPECTED_CARD_COUNT:
            raise ValueError('Expected exactly ' + str(EXPECTED_CARD_COUNT) + ' model cards')
        seen = set()
        for card in cards:
            if not isinstance(card, dict) or not isinstance(card.get('id'), str):
                raise ValueError('Catalog card needs a string id')
            identifier = card['id']
            if identifier in seen or identifier not in family_cards:
                raise ValueError('Duplicate or unknown catalog id: ' + identifier)
            seen.add(identifier)
            original, original_path = family_cards[identifier]
            source = resolve_resource(skills, card.get('card_source'), skills)
            if source != original_path:
                raise ValueError('Wrong family-card source: ' + identifier)
            if card.get('card_source_sha256') != digest(source):
                raise ValueError('Stale family-card hash: ' + identifier)
            content = {key: value for key, value in card.items() if key not in {'card_source', 'card_source_sha256'}}
            if content != original:
                raise ValueError('Catalog content differs from family card: ' + identifier)
        actual_counts = {
            'cards': len(cards),
            'families': dict(Counter(card['family'] for card in cards)),
            'kinds': dict(Counter(card['kind'] for card in cards)),
            'knowledge_levels': dict(Counter(card['knowledge_level'] for card in cards)),
        }
        if catalog.get('counts') != actual_counts:
            raise ValueError('Catalog counts differ from actual cards')
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        record(catalog_path, error)
    return {'status': 'PASS' if not errors else 'FAIL', 'scope': 'STATIC_PACKAGE_CHECK',
            'counts': counts, 'errors': errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1],
                        help='Repository root containing skills/')
    args = parser.parse_args(argv)
    try:
        result = validate(args.root)
    except (OSError, ValueError) as error:
        result = {'status': 'FAIL', 'scope': 'STATIC_PACKAGE_CHECK', 'errors': [{'error': str(error)}]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
