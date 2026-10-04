"""Strict JSON and input-preserving atomic artifact writes (stdlib only)."""
import json
import math
import os
from pathlib import Path
import stat
import tempfile


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def finite_json(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('JSON numbers must be finite')
    if isinstance(value, dict):
        for item in value.values():
            finite_json(item)
    elif isinstance(value, list):
        for item in value:
            finite_json(item)


def read_json(path):
    value = json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)
    finite_json(value)
    return value


def safe_path(root, value):
    root = Path(root).resolve()
    if not isinstance(value, (str, Path)) or not str(value).strip() or '\0' in str(value):
        raise ValueError('Path must be a nonempty string without NUL')
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'Path escapes project root: {value}')
    return path


def snapshot(path):
    if not path.exists():
        return None
    info = path.stat()
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def checked_output(root, value, protected=(), replace_if=None):
    root = Path(root).resolve()
    requested = root / value
    path = safe_path(root, value)
    if not root.is_dir() or path == root:
        raise ValueError('Output requires an existing project and a file path')
    for component in (requested, *requested.parents):
        if component.resolve() == root:
            break
        if component.is_symlink():
            raise ValueError('Output cannot use a symlink or symlinked project directory')
    if path.is_relative_to(root / 'inputs'):
        raise ValueError('Output cannot modify the read-only input area')
    for source in protected:
        source = Path(source).resolve()
        if path == source or (path.exists() and source.exists() and path.samefile(source)):
            raise ValueError('Output cannot overwrite an input or its hardlink')
    if path.exists():
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('Output must be a regular file with no hardlink aliases')
        if not info.st_mode & 0o222:
            raise ValueError('Output cannot replace a read-only frozen file')
        if replace_if is None or not replace_if(path):
            raise ValueError('Output cannot replace an unrelated existing artifact')
    return path


def write_json_output(root, value, data, protected=(), replace_if=None):
    path = checked_output(root, value, protected, replace_if)
    expected = snapshot(path)
    content = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.mcm-artifact-', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        checked_output(root, value, protected, replace_if)
        if snapshot(path) != expected:
            raise ValueError('Output changed during preparation; refusing replacement')
        if expected is None:
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path
