# Repository work

This repository is dedicated to MCM A–C. Keep all skill routing and required
resources within the 26 MCM modules under `skills/`. Model content belongs in
the skill directories; do not add references to a developer's machine or a
separate private corpus.

Preserve model assumptions, mathematical meaning, and evidence grades. A
theoretical guide, a tested reference implementation, and a reproduced real
case are separate claims. Keep Python and MATLAB execution evidence distinct.

After substantive changes, run `python3 scripts/validate.py`, relevant tests,
and `python3 scripts/check_fresh_install.py` when installation or resource
layout changed. Never generate publication metadata by rewriting historical
test commands to imply a new execution.
