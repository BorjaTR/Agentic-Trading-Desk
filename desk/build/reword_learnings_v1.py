#!/usr/bin/env python3
"""reword_learnings_v1.py: the kit's learning tables (LEARNINGS_V5.tsv, LEARNINGS_V6.tsv of the release) shipped as starting knowledge
in loop/, reworded mechanically: scrub_v1's path and name rules, then agent and seat names to neutral words and found-alarm ids to
'a found alarm'. Every row and column is kept (the sources column is the evidence, with paths scrubbed). Owner decision 3 Nov 2026 21:34Z:
ship our lessons as starting knowledge; found alarms, registry and data stay out. MECHANICAL, NOT REVIEWED BY HAND.

  python3 -B desk/build/reword_learnings_v1.py <release folder> <loop folder>"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scrub_v1  # noqa: E402

SRC = {'KIT_LEARNINGS_V5.tsv': 'Agentic/tree/ALARM_DESIGN/KIT_V5/LEARNINGS_V5.tsv', 'KIT_LEARNINGS_V6.tsv': 'Agentic/tree/ALARM_DESIGN/KIT_V6/LEARNINGS_V6.tsv'}
WORDS = [
    (r'\b(?:AD|GPT|DESKA?)[0-9]{1,2}_[A-Z]+_[A-Z0-9]+\b', 'a found alarm'),          # alarm ids of the lab registry
    (r'\bKNOWN_[A-Z0-9]+\b', 'a found alarm'),
    (r'\b(?:CODEX|CLAUDE|OXCODE|CODE)[0-9]+\b', 'an agent'),
    (r'\bGPT[0-9]*\b', 'an outside reviewer'),
    (r'\bSCOUT\b', 'the kit owner'),
    (r'\b(?:LAB[1-4]|LEAD|STRATEGY|QUANT|DSK|LAYERS|LIVE[45]|BUILD[1-5]|TEST[12]|CONDUCTOR|RELEASE|EDGE[12]|BED|TREE|ALARMLIB|FIND)\b', 'a lab seat'),
    (r'\bAD[0-9]{1,2}\b(?=[ ,.;:)])', 'an agent'),                                  # school agents AD1..; R1, R2 are the pass rules and stay (SCOUT 3 Nov 22:4xZ: the old pattern turned them into 'an agent')
    (r'\bhb/[A-Za-z0-9_]+(?:\.txt)?', 'the lab board'),
]
COMPILED = [(re.compile(a), b) for a, b in WORDS]


def reword(t):
    t = scrub_v1.scrub_text(t)
    for rx, b in COMPILED:
        t = rx.sub(b, t)
    return t


def main(argv):
    if len(argv) != 2:
        print(__doc__); return 2
    rel, loop = argv
    for out, rp in SRC.items():
        p = os.path.join(loop, out)
        if os.path.exists(p):
            print('REFUSED: %s exists' % p); return 2
        t = reword(open(os.path.join(rel, rp), encoding='utf-8').read())
        lines = t.split('\n')
        lines.insert(0, '# %s: %s of the released Alarm package, reworded by desk/build/reword_learnings_v1.py (mechanical, not reviewed by hand)' % (out, rp))
        with open(p, 'x', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print('WROTE %s: %d lines' % (p, len(lines)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
