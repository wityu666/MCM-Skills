#!/usr/bin/env python3
"""Run repository and bundled Python regression tests with relative paths."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-only', action='store_true', help='Run bundled skill tests only')
    parser.add_argument('--junitxml', type=Path)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    targets = ['skills'] if args.skill_only else ['tests', 'skills']
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    # A historical stdlib unittest imports seasonal_naive as a top-level module.
    # This path is derived from this checkout, never an author's local directory.
    env['PYTHONPATH'] = str(root / 'skills/mcm-modeling-time-series/scripts')
    command = [sys.executable, '-B', '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
               '--import-mode=importlib'] + targets
    if args.junitxml:
        command += ['--junitxml', str(args.junitxml)]
    return subprocess.run(command, cwd=root, env=env, check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
