"""Install a complete named skill set, preserving unrelated/current skills on errors."""
import hashlib
import os
import shutil
import tempfile
from pathlib import Path


def fingerprint(folder):
    folder = Path(folder)
    result = {}
    for path in folder.rglob('*'):
        if any(part in {'__pycache__', '.pytest_cache', '.DS_Store'} for part in path.relative_to(folder).parts) or path.suffix == '.pyc':
            continue
        if path.is_symlink():
            raise ValueError('Symlink inside skill package: ' + str(path))
        if path.is_file():
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            result[path.relative_to(folder).as_posix()] = digest.hexdigest()
    return result


def install(source, destination, expected, check=False):
    source = Path(source)
    if source.is_symlink():
        raise ValueError('Symlink skill-set source: ' + str(source))
    source = source.resolve(); destination = Path(destination).expanduser().resolve()
    if not source.is_dir():
        raise ValueError('Source must be a skill-set directory')
    if destination == source or destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError('Source and destination trees must not overlap')
    folders = sorted(p for p in source.iterdir() if (p / 'SKILL.md').is_file())
    if {p.name for p in folders} != set(expected):
        raise ValueError('Source is not the complete expected named skill set')
    snapshots = {}; needed = []; reused = []
    for folder in folders:
        if folder.is_symlink():raise ValueError('Symlink skill source: ' + str(folder))
        snapshots[folder.name] = fingerprint(folder)
        target = destination / folder.name
        if target.is_symlink():raise ValueError('Symlink skill destination: ' + str(target))
        if target.exists():
            if not target.is_dir() or fingerprint(target) != snapshots[folder.name]:
                raise ValueError('Refusing to overwrite existing different skill: ' + folder.name)
            reused.append(folder.name)
        else:needed.append(folder)
    if check:return {'status':'INSTALLABLE','modules':len(folders),'destination':str(destination)}
    destination.mkdir(parents=True,exist_ok=True)
    installed = []; rollback_conflicts = []
    with tempfile.TemporaryDirectory(prefix='.skill-install-',dir=destination) as temp:
        prep = Path(temp)
        try:
            # Complete and validate every copy before publishing the first module.
            for folder in needed:
                shutil.copytree(folder,prep/folder.name,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.pytest_cache','.DS_Store'))
                if fingerprint(prep/folder.name) != snapshots[folder.name]:
                    raise ValueError('Source changed while copying: '+folder.name)
            for folder in needed:
                target=destination/folder.name
                if target.exists() or target.is_symlink():
                    raise ValueError('Destination appeared during installation: '+folder.name)
                os.replace(prep/folder.name,target)
                installed.append(folder.name)
            for folder in folders:
                target=destination/folder.name
                if target.is_symlink() or fingerprint(target)!=snapshots[folder.name]:
                    raise ValueError('Installed readback mismatch: '+folder.name)
        except (OSError,ValueError) as error:
            for name in reversed(installed):
                target=destination/name
                try:
                    if target.is_symlink() or not target.is_dir() or fingerprint(target)!=snapshots[name]:
                        rollback_conflicts.append(name);continue
                    shutil.rmtree(target)
                except (OSError,ValueError):rollback_conflicts.append(name)
            suffix='; rollback preserved concurrent edits in: '+','.join(rollback_conflicts) if rollback_conflicts else '; newly published modules rolled back'
            raise ValueError(str(error)+suffix) from error
    return {'status':'INSTALLED','destination':str(destination),'installed':installed,'reused':reused}
