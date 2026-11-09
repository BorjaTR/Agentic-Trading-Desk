#!/usr/bin/env python3
"""card_v2.py (SCO-A154 for SCOUT, 6 Nov 2026: card_v1 dee1fe3d227ed63a with the INDEX version column; the INDEX header is
checked before anything is written in root. An INDEX with the 9th column version gets the mechanism tool name of the json (tool key,
mechanism_v1 when absent); an 8 column INDEX is written as before. card_v1 text follows.)
V1_3_2 (SCO-A170, 7 Nov 2026): "hypothesis at CLAIM" on the card comes from the meta json's hypothesis (the pipeline writes the sealed
INPUT mechanism_hypothesis there), never from the mechanism json (a result); '-' when the meta has none.
card_v1.py (SCO-A153 for SCOUT, 6 Nov 2026; PLAYGROUND, TEST, NOT REVIEWED; alarm_pipeline_v1 step 22 HANDOFF). THE ALARM CARD, one per
alarm, the deliverable of the alarm design process, handed to STRATEGY and filed by mechanism. Reads only finished card outputs (the
alarm_cards_v1 TSV and MD), the mechanism_v1 json and the pipeline's kit words; no market data.
  python3 -B card_v1.py --alarm A --cards-tsv ALARM_CARDS_<X>.tsv --cards-md ALARM_CARDS_<X>.md --mechanism-json MECHANISM.json
      --meta META.json --root <ALARM_CARDS root> --out <new local dir> [--rows-alarm A2,A3 (more alarm rows of the same alarm, e.g. a
      second block)]
Writes <out>/ALARM_CARD_<A>.md and .tsv (columns alarm, q, answer, number, source, sha16, strength), then copies both into
<root>/<MECHANISM>/<A>/ with HANDOFF.json (sha16s, source files, source jobs) and appends one row to <root>/INDEX.tsv (alarm, mechanism,
card_sha16, utc, role, card, handoff_sha16, source_jobs), twin INDEX.tsv.pre_SCO_<utc> first. Card rows: the 8 answers Q1..Q8 and GRADE
(copied from the card tool, never retyped), KIT (race, TRUE, novelty, first look: the kit's own words), MECHANISM (id, share, map sha16),
AFTER (the after-the-fire line), PARTB1.. (the card tool's Part B knowledge lines). The same handoff twice is EXISTS (rc 0, nothing
added); a different card for an alarm already filed goes to <root>/<MECHANISM>/<A>/v<utc>/. Refusals (rc 2, nothing written in root):
SIDE_WORD (a trade-side word on the card: alarm_cards_v1.side_hits, imported read-only), NO_ROWS (the alarm has no Q1..Q8 rows),
BAD_MECHANISM (json without mechanism or map_sha16), BAD_META."""
import sys
sys.dont_write_bytecode = True
import argparse, csv, fcntl, hashlib, importlib.util, json, os, shutil, subprocess

HERE = os.path.dirname(os.path.realpath(__file__))
AC = os.path.join(HERE, '..', '..', '..', 'RESEARCH', 'PLAYGROUND', 'tools', 'PG20261105_alarm_understand', 'code', 'alarm_cards_v1.py')
COLS = ('alarm', 'q', 'answer', 'number', 'source', 'sha16', 'strength')
ICOLS = ('alarm', 'mechanism', 'card_sha16', 'utc', 'role', 'card', 'handoff_sha16', 'source_jobs')
VCOL = 'version'
QS = ('Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'GRADE')


class Refused(Exception):
    def __init__(self, code, why):
        Exception.__init__(self, code); self.code, self.why = code, why


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def utc():
    return subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], stdout=subprocess.PIPE, universal_newlines=True, check=True).stdout.strip()


def side_hits_fn():
    path = os.environ.get('CARD_V1_ALARM_CARDS', AC)
    spec = importlib.util.spec_from_file_location('alarm_cards_v1_ro', path)
    m = importlib.util.module_from_spec(spec); sys.modules['alarm_cards_v1_ro'] = m; spec.loader.exec_module(m)
    return m.side_hits


def clean(s):
    return str(s).replace('\t', ' ').replace('\n', ' ').replace('|', '/')


def claim_hypothesis(meta):
    """V1_3_2 (SCO-A170, R1-11): the hypothesis at CLAIM is the run's sealed INPUT mechanism_hypothesis, carried by the pipeline in the
    meta json (HANDOFF_META hypothesis); never the mechanism json, which is a result (the card job's MECHANISM.json held null and the
    card printed None). Absent or empty in the meta: '-'."""
    h = meta.get('hypothesis')
    return '-' if h is None or str(h).strip() == '' else str(h)


def md_sections(md, alarms):
    """the '### <alarm> (' sections of the card tool's page, and its Part B lines"""
    L = open(md).read().splitlines()
    sec, cur, partb, inb = {}, None, [], False
    for l in L:
        if l.startswith('## Part B'):
            inb, cur = True, None; continue
        if inb:
            if l[:2] in ('1.', '2.', '3.', '4.', '5.'):
                partb.append(l)
            continue
        if l.startswith('### '):
            name = l[4:].split(' (')[0]
            cur = name if name in alarms else None
            if cur:
                sec.setdefault(cur, []).append(l)
            continue
        if cur:
            sec[cur].append(l)
    return sec, partb


def build(a):
    meta = json.load(open(a.meta))
    for k in ('kit', 'jobs', 'role'):
        if k not in meta:
            raise Refused('BAD_META', 'meta lacks %s' % k)
    M = json.load(open(a.mechanism_json))
    if 'mechanism' not in M or 'map_sha16' not in M:
        raise Refused('BAD_MECHANISM', a.mechanism_json)
    names = [a.alarm] + [x for x in a.rows_alarm.split(',') if x]
    src = list(csv.DictReader((l for l in open(a.cards_tsv) if not l.startswith('#')), delimiter='\t'))
    rows = [r for r in src if r['alarm'] in names and r['q'] in QS]
    if not [r for r in rows if r['q'].startswith('Q')]:
        raise Refused('NO_ROWS', 'no Q1..Q8 rows for %s in %s' % (','.join(names), a.cards_tsv))
    sec, partb = md_sections(a.cards_md, names)
    mech, share = M['mechanism'], M.get('share')
    k = meta['kit']
    kit_ans = 'race %s (decide_v6); TRUE %s (true_gate_v3); novelty %s (novelty_v5); first look %s' % (
        k.get('race', '-'), k.get('true', '-'), k.get('novelty', '-'), k.get('firstlook', '-'))
    shares = '; '.join('%s %s' % (m, v.get('share')) for m, v in sorted(M.get('shares', {}).items()))
    mech_ans = ('%s: as-of share %s of the fires where the map membership rule holds at the fire second (threshold %s); all shares: %s'
                % (mech, share, M.get('threshold', 0.9), shares))
    tsv = [COLS]
    for r in rows:
        tsv.append(tuple(clean(r[c]) for c in COLS))
    tsv.append((a.alarm, 'KIT', kit_ans, '-', 'pipeline step jsons', '-', '-'))
    tsv.append((a.alarm, 'MECHANISM', mech_ans, str(share), os.path.basename(a.mechanism_json), sha16(a.mechanism_json), '-'))
    after = []
    for nm in names:
        for l in sec.get(nm, []):
            if l.startswith('- after the fire (description):'):
                after.append((nm, l[len('- after the fire (description):'):].strip()))
    for nm, t in after:
        tsv.append((nm, 'AFTER', clean(t), '-', os.path.basename(a.cards_md), sha16(a.cards_md), '-'))
    for i, l in enumerate(partb, 1):
        tsv.append((a.alarm, 'PARTB%d' % i, clean(l[2:].strip()), '-', os.path.basename(a.cards_md), sha16(a.cards_md), '-'))
    md = ['# ALARM_CARD_%s' % a.alarm, '',
          '- the alarm card of the alarm design process (card_v1, alarm_pipeline_v1 step 22; PLAYGROUND, TEST, NOT REVIEWED). Knowledge only: answers describe the event, never a trade side.',
          '- role %s; mechanism **%s** (map %s, share %s); hypothesis at CLAIM: %s' % (meta['role'], mech, M['map_sha16'], share, claim_hypothesis(meta)),
          '- kit words: %s' % kit_ans,
          '- sources: card tool %s %s and %s %s; mechanism %s %s; jobs %s' % (os.path.basename(a.cards_tsv), sha16(a.cards_tsv),
              os.path.basename(a.cards_md), sha16(a.cards_md), os.path.basename(a.mechanism_json), sha16(a.mechanism_json),
              ', '.join('%s %s' % kv for kv in sorted(meta['jobs'].items())) or '-'), '']
    for nm in names:
        md += ['## %s' % nm, '', '| Q | answer | number | source sha16 | strength |', '|---|---|---|---|---|']
        for r in rows:
            if r['alarm'] == nm:
                md.append('| %s | %s | %s | %s %s | %s |' % (r['q'], clean(r['answer']), clean(r['number']), r['source'], r['sha16'], r['strength']))
        for x, t in after:
            if x == nm:
                md.append(''); md.append('- after the fire (description): ' + t)
        md.append('')
    md += ['## Mechanism', '', '- ' + mech_ans, '- card Q3: %s (%s)' % (M.get('q3', {}).get('answer', '-'), M.get('q3', {}).get('strength', '-')),
           '- card Q4: %s (%s)' % (M.get('q4', {}).get('answer', '-'), M.get('q4', {}).get('strength', '-')), '',
           '## Part B (knowledge lines of the card tool)', ''] + partb + ['']
    text_md = '\n'.join(md) + '\n'; text_tsv = '\n'.join('\t'.join(r) for r in tsv) + '\n'
    hits = side_hits_fn()(text_md + '\n' + text_tsv)
    if hits:
        raise Refused('SIDE_WORD', 'trade-side words on the card: %s' % ','.join(hits))
    return text_md, text_tsv, mech, meta


def main(argv=None):
    ap = argparse.ArgumentParser()
    for x in ('--alarm', '--cards-tsv', '--cards-md', '--mechanism-json', '--meta', '--root', '--out'):
        ap.add_argument(x, required=True)
    ap.add_argument('--rows-alarm', default='')
    a = ap.parse_args(argv)
    try:
        text_md, text_tsv, mech, meta = build(a)
    except Refused as r:
        print('REFUSED %s: %s' % (r.code, r.why)); return 2
    os.makedirs(a.out, exist_ok=True)
    lm = os.path.join(a.out, 'ALARM_CARD_%s.md' % a.alarm); lt = os.path.join(a.out, 'ALARM_CARD_%s.tsv' % a.alarm)
    for q, t in ((lm, text_md), (lt, text_tsv)):
        if os.path.exists(q) and open(q).read() != t:
            print('REFUSED OUT_DIFFERS: %s exists with other text' % q); return 2
        if not os.path.exists(q):
            open(q, 'x').write(t)
    cs = sha16(lm)
    os.makedirs(a.root, exist_ok=True)
    idx = os.path.join(a.root, 'INDEX.tsv')
    lock = open(os.path.join(a.root, '.INDEX.lock'), 'a'); fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        hdr = open(idx).readline().rstrip('\n').split('\t') if os.path.exists(idx) else list(ICOLS)
        if hdr not in (list(ICOLS), list(ICOLS) + [VCOL]):
            print('REFUSED BAD_INDEX: %s header' % idx); return 2
        dst = os.path.join(a.root, mech, a.alarm)
        dm = os.path.join(dst, os.path.basename(lm))
        if os.path.exists(dm) and sha16(dm) == cs:
            hj = os.path.join(dst, 'HANDOFF.json')
            print('HANDOFF %s %s card %s sha16 %s index %s EXISTS' % (a.alarm, mech, dm, cs, idx)); return 0
        now = utc()
        if os.path.exists(dm):
            dst = os.path.join(dst, 'v' + now.replace('-', '').replace(':', ''))
        os.makedirs(dst, exist_ok=True)
        dm = os.path.join(dst, os.path.basename(lm)); dt_ = os.path.join(dst, os.path.basename(lt))
        shutil.copyfile(lm, dm); shutil.copyfile(lt, dt_)
        h = dict(alarm=a.alarm, mechanism=mech, role=meta['role'], utc=now, card_md=dm, card_md_sha16=sha16(dm), card_tsv=dt_,
                 card_tsv_sha16=sha16(dt_), sources={p: sha16(p) for p in (a.cards_tsv, a.cards_md, a.mechanism_json, a.meta)},
                 source_jobs=meta['jobs'], kit=meta['kit'], tool='card_v2.py', tool_sha16=sha16(os.path.realpath(__file__)))
        hj = os.path.join(dst, 'HANDOFF.json')
        json.dump(h, open(hj, 'x'), indent=1, sort_keys=True)
        if os.path.exists(idx):
            shutil.copy2(idx, idx + '.pre_SCO_' + now.replace('-', '').replace(':', ''))
        else:
            open(idx, 'x').write('\t'.join(ICOLS) + '\n')
        row = (a.alarm, mech, cs, now, meta['role'], os.path.relpath(dm, a.root), sha16(hj), ','.join('%s' % v for k, v in sorted(meta['jobs'].items())) or '-')
        if len(hdr) == len(ICOLS) + 1:
            row = row + (os.path.splitext(str(json.load(open(a.mechanism_json)).get('tool') or 'mechanism_v1.py'))[0],)
        with open(idx, 'a') as f:
            f.write('\t'.join(row) + '\n')
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN); lock.close()
    print('HANDOFF %s %s card %s sha16 %s index %s' % (a.alarm, mech, dm, cs, idx))
    return 0


if __name__ == '__main__':
    sys.exit(main())
