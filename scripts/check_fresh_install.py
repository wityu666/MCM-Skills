#!/usr/bin/env python3
"""Install to a temporary folder, verify bytes, reuse, and two installed CLIs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from safe_install import fingerprint
from suite_config import EXPECTED_SKILLS


def check_fresh_install():
    source = Path(__file__).resolve().parents[1] / 'skills'
    with tempfile.TemporaryDirectory(prefix='mcm-install-check-') as temp:
        destination = Path(temp) / 'codex-home/skills'
        environment = os.environ.copy()
        environment['CODEX_HOME'] = str(destination.parent)
        environment['PYTHONDONTWRITEBYTECODE'] = '1'

        def installer(*arguments):
            response = subprocess.run([
                sys.executable, '-B', str(source.parent / 'scripts/install.py'), *arguments,
            ], cwd=temp, env=environment, check=True, capture_output=True, text=True)
            return json.loads(response.stdout)

        # Exercise the documented command and CODEX_HOME default from outside
        # the checkout, keeping the user's actual skill directory untouched.
        initial = installer('--check')
        if destination.exists():
            raise ValueError('--check unexpectedly created the destination')
        result = installer()
        if len(result['installed']) != len(EXPECTED_SKILLS):
            raise ValueError('Fresh install did not install every skill')
        for name in EXPECTED_SKILLS:
            if fingerprint(source / name) != fingerprint(destination / name):
                raise ValueError('Readback mismatch: ' + name)
        reused = installer('--destination', str(destination))
        if reused['installed'] or set(reused['reused']) != set(EXPECTED_SKILLS):
            raise ValueError('Identical install was not safely reused')
        query = subprocess.run([
            sys.executable, '-B', str(destination / 'mcm-modeling-library/scripts/query_models.py'),
            '--id', 'disc-knapsack', '--full',
        ], cwd=temp, check=True, capture_output=True, text=True)
        payload = json.loads(query.stdout)
        if payload.get('status') != 'MATCHES' or payload['results'][0]['id'] != 'disc-knapsack':
            raise ValueError('Installed model query returned the wrong card')
        subprocess.run([
            sys.executable, '-B', str(destination / 'mcm-suite/scripts/init_project.py'), '--help',
        ], cwd=temp, check=True, capture_output=True, text=True)
    return {'status': 'PASS', 'scope': 'TEMPORARY_FRESH_INSTALL_AND_READBACK',
            'modules': len(EXPECTED_SKILLS), 'precheck': initial['status'],
            'identical_reinstall': 'REUSED', 'installed_cli_checks': 2}


def main():
    try:
        result = check_fresh_install()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'FAIL', 'error': str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
