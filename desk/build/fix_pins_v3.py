#!/usr/bin/env python3
"""fix_pins_v3.py (SCOUT, 4 Nov 2026): the third build step, after fix_pins_v2.py. Two engine tests read the interpreter pin that
fix_pins_v2 dropped (E1); this step makes them read the same rule labcore's release check uses, keeps every pin true and writes
PIN_MAP_V3.tsv beside itself.

  python3 -B desk/build/fix_pins_v3.py <alarm folder>            dry
  python3 -B desk/build/fix_pins_v3.py <alarm folder> --write    write (a twin of every changed file first)

 E4 event_outcomes/test_gm1.py Releases.test_release_graph_checks: it ran only when the GM1 record's interpreter pin equals this
    interpreter, so in this repo (pin '<PYTHON>') the engine's own release check of GRADE and MONTH was always SKIPPED; after E1 the
    lookup raised KeyError (job 20268328, the one FAIL). Now: runs when the record pins no interpreter or pins this one (labcore's rule:
    a manifest without the key is not checked on it). So the clean repo's test run checks the GRADE and MONTH release graphs for real.
 E5 labcore/tests/test_release_v1.py test_R5 asserted the scrubbed pin '<PYTHON>'; now asserts no interpreter pin (not in TESTS.tsv;
    kept true anyway).
Then fix_pins_v2's chain: every file naming an old sha of a changed file gets the new one, until nothing changes; pages keep theirs."""
import os, shutil, sys, time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fix_pins_v2 as V2      # noqa: E402

EDITS = [
    ('E4', '01_Detection/tree/team/RESEARCH/tools/event_outcomes/test_gm1.py',
     "'RELEASE_event_outcomes_GM1.json')))['runtime']['interpreter']\n                         == sys.executable, 'release.check pins the Mac interpreter: runs in the runner job')",
     "'RELEASE_event_outcomes_GM1.json')))['runtime'].get('interpreter', sys.executable)\n                         == sys.executable, 'release.check pins another interpreter here')"),
    ('E5', '01_Detection/tree/team/RESEARCH/tools/labcore/tests/test_release_v1.py',
     "    assert man['runtime']['interpreter'] == '<PYTHON>'",
     "    assert 'interpreter' not in man.get('runtime', {})          # the desk build (desk/build/fix_pins_v2.py E1) drops the lab's path pin"),
]


def main(argv):
    if not argv:
        print(__doc__); return 2
    root = os.path.abspath(argv[0]); write = '--write' in argv
    texts = {p: open(p, encoding='utf-8').read() for p in V2.files(root)}
    new = dict(texts); why = {}
    for tag, rel, old, rep in EDITS:
        p = os.path.join(root, rel)
        if new[p].count(old) != 1:
            raise SystemExit('%s: %s holds the old text %d times (want 1): refused' % (tag, rel, new[p].count(old)))
        new[p] = new[p].replace(old, rep); why[p] = [tag]
    rounds = V2.chain(texts, new, why, ({}, {}))
    rows = [(os.path.relpath(p, root), V2.sha(texts[p].encode())[:16], V2.sha(new[p].encode())[:16], ','.join(why.get(p, ['PIN'])))
            for p in sorted(new) if new[p] != texts[p]]
    print('rounds %d, files changed %d (%s)' % (rounds, len(rows), ', '.join('%s %s' % (r[3], r[0].split('/')[-1]) for r in rows[:12])))
    if not write:
        return 0
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    repo = os.path.dirname(root); tw = os.path.join(repo, '.twins', 'fix_pins_v3_' + stamp)
    for p in sorted(new):
        if new[p] != texts[p]:
            d = os.path.join(tw, os.path.relpath(p, repo)); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy2(p, d)
    for p in sorted(new):
        if new[p] != texts[p]:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(new[p])
    with open(os.path.join(HERE, 'PIN_MAP_V3.tsv'), 'x') as f:
        f.write('# PIN_MAP_V3.tsv (fix_pins_v3.py, %s): every file of alarm/ this step changed; twins in .twins/fix_pins_v3_%s\n' % (stamp, stamp))
        f.write('file\tbefore_sha16\tafter_sha16\twhy\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    for w, v in sorted(V2.check(root).items()):
        print('release check %s: %s' % (w, v[:600]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
