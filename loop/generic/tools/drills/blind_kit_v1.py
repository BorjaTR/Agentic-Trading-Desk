#!/usr/bin/env python3
"""blind_kit_v1.py (SCOUT 2026-11-08; why: team/RESEARCH/plans/PLAN_PROCESS_QUALITY_SYSTEM_20261108.md, fairness rules:
blind scorers, gold items, two scorers, scorer never the author). Builds a blind scoring kit for one judged drill:
  make:  copies the outputs to score and the gold items into <kit>/items/ under random names (I01, I02, ...), writes
         <kit>/SCORER_TASK.md (key + rubric + items, one TSV out per scorer) and a PRIVATE map <kit>/../<kit name>_MAP.tsv
         (outside the kit folder: scorers never read it). Order is shuffled with a seed from the kit name (sorted, stable).
         C223: refuses with REFUSED NO_GOLD (no --gold) or REFUSED BAD_GOLD (a --gold without =<known total>), exit 2.
  score: after the scorers ran: agreement (build/agreement_v1.py) + gold check (each scorer within --gold-tol of each gold's
         known total) + de-blinded totals per original output (mean of scorers, adjudication list). C223: a map with no gold row
         prints GOLD NONE and GOLD_CHECK FAIL, exit 3.
  python3 -B blind_kit_v1.py make --kit <dir> --key <KEY.md> [--rubric <file>] --item <path> ... --gold <path>=<known total> ...
  python3 -B blind_kit_v1.py score --kit <dir> --scorers <A.tsv> <B.tsv> [--gold-tol 1]"""
import argparse, csv, hashlib, os, random, re, shutil, subprocess, sys
REPORT_TEMPLATE = os.environ.get('LL_REPORT_TEMPLATE', '<LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series/drills_v2/REPORT_TEMPLATE_V1.md')   # RC2: the seat's REPORT template (generic copy: {GENERIC}/REPORT_TEMPLATE_V1.md); default as in the source
HERE = os.path.dirname(os.path.abspath(__file__))

def key_elements(key):
    """C97 (BLIND-H04-R1v3: one scorer split I1 into I1_trap and I1_kill, the other did not, so no rows matched): the scored element ids
    of a key, from lines that start with an id and a point count, e.g. 'MOVE (1):' or 'I1 (3):'; [] when the key has none in that form."""
    out = []
    for ln in open(key, encoding='utf-8'):
        m = re.match(r'^([A-Z][A-Z0-9_]{0,15}) \((\d+(?:\.\d+)?)\)', ln)
        if m and m.group(1) not in out: out.append(m.group(1))
    return out

def gold_arg(g):
    """C223 (review RC3 N1): one --gold value is <path>=<known total>; (path, total text) or None when the total is missing or not a number"""
    p, sep, known = g.rpartition('=')
    if not sep or not p:
        return None
    try:
        float(known)
    except ValueError:
        return None
    return p, known.strip()

def make(a):
    if not a.gold:                                                            # C223 (N1): a kit with no gold item checks nothing
        print('REFUSED NO_GOLD: give at least one --gold <path>=<known total>'); return 2
    golds = [gold_arg(g) for g in a.gold]
    for g, v in zip(a.gold, golds):
        if v is None:
            print('REFUSED BAD_GOLD %s: a --gold value is <path>=<known total>' % g); return 2
    kit = os.path.abspath(a.kit); os.makedirs(os.path.join(kit, 'items'), exist_ok=True); os.makedirs(os.path.join(kit, 'OUT'), exist_ok=True)
    src = [(p, 'item', '') for p in a.item] + [(p, 'gold', known) for p, known in golds]
    seed = int(hashlib.sha256(os.path.basename(kit).encode()).hexdigest()[:8], 16)
    order = sorted(src); random.Random(seed).shuffle(order)
    mp = os.path.join(os.path.dirname(kit), os.path.basename(kit) + '_MAP.tsv')
    with open(mp, 'w') as m:
        m.write('blind_id\tsource\tkind\tknown_total\n')
        for i, (p, kind, known) in enumerate(order, 1):
            bid = 'I%02d' % i; txt = open(p).read()
            lines = txt.splitlines(True)                                      # blind: drop a title line, redact agent ids anywhere
            body = ''.join(lines[1:] if lines and lines[0].startswith('# ') else lines)
            body = re.sub(r'\b(R\d[a-z]?V\d_[ab]|HID_[ab]|RD\d?_[ab]|scorer[A-Z]|r\d[a-z]?\b|SCT-A\d+)', '<id>', body)
            open(os.path.join(kit, 'items', bid + '.md'), 'w').write('# Item %s\n' % bid + body); m.write('\t'.join([bid, p, kind, known]) + '\n')
    rub = ('Rubric: ' + os.path.abspath(a.rubric) + '\n') if a.rubric else ''
    els = [e.strip() for e in a.elements.split(',')] if a.elements else key_elements(a.key)
    el_txt = ('Use exactly these element ids, one row each: %s.' % ', '.join(els)) if els else '(item = the key\'s element id, e.g. P1 or Q3)'
    task = f"""Blind scorer (paper research). You score {len(order)} outputs of one drill against its answer key. You did not write them and you do not know who did; do not guess.
Read ONLY: the key {os.path.abspath(a.key)}
{rub}and every file in {kit}/items/ (I01.md ...). No other file, no search outside these.
For each item and each scored element of the key, give the points the key allows (use the key's own scale; half points only where the key allows them), with a quote of at most 15 words from the item as evidence. An element with no evidence scores 0.
Write ONLY {kit}/OUT/<your id>.tsv and {kit}/OUT/<your id>_REPORT.md. The .tsv is tab-separated, header: run	item	points	evidence
(run = the item id I01..; item = the element id). {el_txt} Then one row per item: <I..>	TOTAL	<sum>	<one line: weakest element>.
Then write {kit}/OUT/<your id>_REPORT.md with the REPORT block of {REPORT_TEMPLATE} (MESSY lines for any key or rubric line you found unclear or two-way; WASTE; at most one PROPOSE; NONE where empty).
Max {10 + 2 * len(order)} tool calls. Reply with one line: the file path and the totals per item.
"""
    open(os.path.join(kit, 'SCORER_TASK.md'), 'w').write(task)
    print('KIT %s items %d (gold %d) map %s' % (kit, len(order), len(a.gold), mp)); return 0

def score(a):
    kit = os.path.abspath(a.kit); mp = os.path.join(os.path.dirname(kit), os.path.basename(kit) + '_MAP.tsv')
    m = {r['blind_id']: r for r in csv.DictReader(open(mp), delimiter='\t')}
    subprocess.run([sys.executable, '-B', os.path.join(HERE, 'agreement_v1.py')] + a.scorers)
    tot = {}
    for f in a.scorers:
        for r in csv.DictReader(open(f), delimiter='\t'):
            if r['item'] == 'TOTAL' and r['run'] in m:
                try: tot.setdefault(r['run'], {})[os.path.basename(f)] = float(r['points'])
                except ValueError: pass
    bad = 0
    for bid, r in sorted(m.items()):
        t = tot.get(bid, {}); mean = sum(t.values()) / len(t) if t else float('nan')
        if r['kind'] == 'gold':
            off = {k: v - float(r['known_total']) for k, v in t.items()}
            ok = len(t) == len(a.scorers) and all(abs(x) <= a.gold_tol for x in off.values())   # C218 (B1): a total from every scorer
            if not ok: bad += 1
            print('GOLD %s known %s scored %s -> %s' % (bid, r['known_total'], t, 'OK' if ok else ('NO_SCORES %d of %d scorers' % (len(a.scorers) - len(t), len(a.scorers)) if len(t) < len(a.scorers) else 'SCORER_OFF')))
        elif not t:
            bad += 1; print('ITEM %s %s NO_SCORES' % (bid, r['source']))   # C218 (B1): an item no scorer totalled is a failure
        else:
            spread = (max(t.values()) - min(t.values())) if t else float('nan')
            print('ITEM %s %s mean %.2f spread %.2f%s' % (bid, r['source'], mean, spread, ' ADJUDICATE' if spread > 1 else ''))
    if not any(r['kind'] == 'gold' for r in m.values()):                  # C223 (N1): no gold row = nothing was checked = a failure
        print('GOLD NONE: the kit has no gold item'); bad += 1
    print('GOLD_CHECK %s' % ('PASS' if not bad else 'FAIL %d' % bad)); return 0 if not bad else 3

def main(argv=None):
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    mk = sp.add_parser('make'); mk.add_argument('--kit', required=True); mk.add_argument('--key', required=True); mk.add_argument('--rubric')
    mk.add_argument('--item', action='append', default=[]); mk.add_argument('--gold', action='append', default=[]); mk.add_argument('--elements', help='comma list of element ids (default: read from the key)')
    sc = sp.add_parser('score'); sc.add_argument('--kit', required=True); sc.add_argument('--scorers', nargs='+', required=True); sc.add_argument('--gold-tol', type=float, default=1)
    a = ap.parse_args(argv)
    return make(a) if a.cmd == 'make' else score(a)

if __name__ == '__main__':
    sys.exit(main())
