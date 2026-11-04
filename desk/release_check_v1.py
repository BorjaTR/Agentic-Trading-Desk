#!/usr/bin/env python3
"""release_check_v1.py: the engine's own release check of the GRADE and MONTH records (labcore/release.py check), run with the desk's
PYTHON so a desk that cannot GRADE is told at `desk.py check`, before any run (trial CLEANT01_20261104 found it only at its GRADE job).

  <PYTHON> -B desk/release_check_v1.py        prints RELEASE GRADE OK|REFUSED <why>, RELEASE MONTH ...; exit 0 both OK, 3 else
Reads only alarm/ files; writes nothing (no __pycache__ either)."""
import os, sys

sys.dont_write_bytecode = True
DESK = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.join(os.path.dirname(DESK), 'alarm', '01_Detection', 'tree')
TOOLS = os.path.join(TREE, 'team', 'RESEARCH', 'tools')
RECORDS = (('GRADE', os.path.join(TOOLS, 'event_outcomes', 'RELEASE_event_outcomes_GM2.json')),
           ('MONTH', os.path.join(TOOLS, 'alarm_process', 'RELEASE_event_outcomes_GM2_MONTH.json')))


def check():
    sys.path.insert(0, TOOLS)
    from labcore import release as R      # noqa: E402  (the repo's own copy)
    out = {}
    for w, p in RECORDS:
        try:
            R.check(p, TREE); out[w] = 'OK'
        except R.ReleaseRefused as e:
            out[w] = 'REFUSED %s' % e
    return out


def main():
    out = check()
    for w, _ in RECORDS:
        print('RELEASE %s %s' % (w, out[w]))
    return 0 if all(v == 'OK' for v in out.values()) else 3


if __name__ == '__main__':
    sys.exit(main())
