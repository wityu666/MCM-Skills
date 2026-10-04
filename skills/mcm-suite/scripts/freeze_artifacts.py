#!/usr/bin/env python3
"""Freeze or verify project-relative artifacts using actual byte hashes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

from artifact_safety import read_json, safe_path, snapshot, write_json_output


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_manifest(data):
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError('Manifest must be a schema_version=1 object')
    if not isinstance(data.get('freeze_id'), str) or not data['freeze_id'].strip():
        raise ValueError('Manifest freeze_id must be a nonempty string')
    if not isinstance(data.get('created_at'), str) or not data['created_at'].strip():
        raise ValueError('Manifest created_at must be a nonempty string')
    if not isinstance(data.get('files'), list) or not data['files']:
        raise ValueError('Manifest files must be a nonempty array')
    for item in data['files']:
        if not isinstance(item, dict):
            raise ValueError('Manifest file entries must be objects')
        value = item.get('path')
        if not isinstance(value, str) or not value.strip() or Path(value).is_absolute() or '..' in Path(value).parts:
            raise ValueError('Manifest entry path must be project-relative without traversal')
        expected = item.get('sha256')
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
            raise ValueError('Invalid SHA-256')
        if type(item.get('bytes')) is not int or item['bytes'] < 0:
            raise ValueError('Manifest bytes must be a nonnegative integer')
    return data


def existing_manifest(path):
    try:
        validate_manifest(read_json(path))
        return True
    except (ValueError, TypeError, OSError, UnicodeError, RecursionError):
        return False


def create(root, manifest, freeze_id, files):
    root = Path(root).resolve()
    if not root.is_dir() or not isinstance(freeze_id, str) or not freeze_id.strip():
        raise ValueError('Existing project and nonempty string freeze_id required')
    if isinstance(files, (str, bytes, dict)):
        raise ValueError('Nonempty file list required')
    try:
        files = list(files)
    except TypeError as exc:
        raise ValueError('Nonempty file list required') from exc
    if not files:
        raise ValueError('Nonempty file list required')
    target = safe_path(root, manifest)
    entries, seen, sources = [], set(), []
    for value in files:
        path = safe_path(root, value)
        if path == target or not path.is_file() or path in seen or (target.exists() and path.samefile(target)):
            raise ValueError(f'Self-reference, duplicate, or missing file: {value}')
        seen.add(path)
        sources.append(path)
        before = path.stat()
        hashed = digest(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError(f'Artifact changed while hashing: {value}')
        entries.append(dict(path=path.relative_to(root).as_posix(), sha256=hashed, bytes=after.st_size))
    data = dict(schema_version=1, freeze_id=freeze_id, created_at=datetime.now(timezone.utc).isoformat(),
                files=sorted(entries, key=lambda x: x['path']))
    write_json_output(root, manifest, data, sources + [root/'context.json', root/'rules.json'], existing_manifest)
    return data


def verify(root, manifest):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Project root must be an existing directory')
    target = safe_path(root, manifest)
    manifest_before = snapshot(target)
    data = validate_manifest(read_json(target))
    checks, seen = [], set()
    for item in data['files']:
        path = safe_path(root, item['path'])
        if path == target or path in seen or (path.exists() and path.samefile(target)):
            raise ValueError('Self-reference or duplicate manifest entry')
        seen.add(path)
        before = snapshot(path)
        actual = digest(path) if path.is_file() else None
        size_matches = path.is_file() and path.stat().st_size == item['bytes'] and before == snapshot(path)
        checks.append(dict(path=item['path'], expected=item['sha256'], actual=actual,
                           status='PASS' if actual == item['sha256'] and size_matches else 'CHANGED' if actual else 'MISSING'))
    manifest_hash = digest(target)
    if snapshot(target) != manifest_before:
        raise ValueError('Manifest changed during verification')
    return dict(status='PASS' if all(x['status'] == 'PASS' for x in checks) else 'FAIL',
                freeze_id=data['freeze_id'], manifest_sha256=manifest_hash, checks=checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['create', 'verify'])
    parser.add_argument('--root', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--freeze-id')
    parser.add_argument('--files', nargs='+')
    args = parser.parse_args()
    try:
        result = create(args.root, args.manifest, args.freeze_id, args.files) if args.action == 'create' else verify(args.root, args.manifest)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 1 if result.get('status') == 'FAIL' else 0
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, RecursionError) as exc:
        print(json.dumps(dict(status='ERROR', error=str(exc))), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
