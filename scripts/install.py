#!/usr/bin/env python3
"""Install this repository's 26 MCM skills without replacing different skills."""
import argparse
import json
import os
from pathlib import Path

from safe_install import install
from suite_config import EXPECTED_SKILLS


def default_destination():
    return Path(os.environ.get('CODEX_HOME') or str(Path.home() / '.codex')) / 'skills'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=default_destination())
    parser.add_argument('--check', action='store_true', help='Check names and conflicts without writing')
    args = parser.parse_args(argv)
    try:
        result = install(Path(__file__).resolve().parents[1] / 'skills',
                         args.destination, EXPECTED_SKILLS, check=args.check)
    except (OSError, ValueError) as error:
        print(json.dumps({'status': 'ERROR', 'error': str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
