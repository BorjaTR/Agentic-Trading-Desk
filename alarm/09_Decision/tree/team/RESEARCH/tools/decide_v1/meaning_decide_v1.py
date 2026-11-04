"""meaning_decide_v1.py (DECIDE seat, 26 Oct 2026): the meaning loop of decision tool V1. It does NOT import decide_v1 or decide_rules_v1.
It re-reads the raw files with plain line splitting, recomputes every decision from the rulebook JSON, and checks that each written word
means what it says:
  Q1 every DECISIONS row equals the recomputed action, slot, reason, detail and trade side (0 differences allowed)
  Q2 the rows are exactly the universe fires of that alarm and window, once each; TAKE + SKIP lists partition them
  Q3 every used field value on a row equals the raw card value (or the card row is really absent)
  Q4 VALUE_COUNTS equal a direct count over the raw cards of the selected fires
  Q5 the weight of each wave sums to 1 over its fires, so tally weights count waves
  Q6 every number of 3 or more digits, or with a decimal point, in an evidence cell is in ONE line of the cited source file, and the
     file is at its sha16 (short numbers such as "+8c" or "1 h" are not checked here; the reviewer reads those by hand)
  Q7 RUN.json sha16s equal the files on disk, found from the roots given here (not from the paths the run machine wrote)
  Q8 the output headers are the fixed pipeline headers, the fire key alarm_id, coin, t, side first (written out here, not imported)
  Q9 every TAKE and SKIP event row carries the onset_t, trigger and event_id of its fire in the alarm's source event list, unchanged
States and reasons: a word is a state only when the line declares it, a reason only when the line declares it (exact, or a 'WORD*' family);
nothing is judged by how a word is spelled.
  python3 -B meaning_decide_v1.py <forensics> <profile cards root> <runs folder> [volumes root]  -> MEANING_DECIDE_V1.txt in the runs folder
The volumes root is where the Mac's /Volumes is on this machine: /Volumes on the Mac (the default), $HOME/mnt on the VM. A run made on the
other machine wrote its paths there; they are moved to this one (V1.0.1, so the checker runs on the Mac too)."""
import hashlib, json, os, re, sys, datetime as dt

def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]

def rows(p):
    L = [l.rstrip('\n') for l in open(p) if not l.startswith('#')]
    h = L[0].split('\t')
    return [dict(zip(h, l.split('\t'))) for l in L[1:] if l]

HEADS = {'DECISIONS.tsv': 'alarm_id coin t side utc parent_id cluster_id weight action slot reason detail trade_side entry exit size card_ctx card_prof card_pmm used_values',
         'TAKE_EVENTS.tsv': 'alarm_id coin t side onset_t trigger event_id', 'SKIP_EVENTS.tsv': 'alarm_id coin t side onset_t trigger event_id',
         'VALUE_COUNTS.tsv': 'alarm_id field value kind fires'}

def declared(v, states, reasons):
    if v in states: return 'STATE'
    if v == 'NO_CARD_ROW': return 'MISSING_ROW'
    if v == 'NO_VALUE': return 'EMPTY'
    for r in reasons:
        if v == r or (r[-1:] == '*' and v[:len(r) - 1] == r[:-1]):
            return 'REASON'
    return 'UNDECLARED'

def main(F, P, O, V='/Volumes'):
    L = F + '/team/RESEARCH/LIBRARY'; D = F + '/team/RESEARCH/tools/decide_v1'
    out = []; bad = 0
    def say(ok, msg):
        nonlocal bad
        bad += 0 if ok else 1
        out.append(('PASS ' if ok else 'FAIL ') + msg)
    uni = rows(L + '/UNIVERSE_ALARMS_V1.tsv')
    shorts = {'ALM_C_V1': 'C', 'ALM_M_V1': 'M', 'ALM_H0_V1': 'H0', 'ALM_S2B0_V1': 'S2B0', 'ALM_S2R1_V1': 'S2R1', 'ALM_S3W_V1': 'S3W'}
    def here(inp):
        # the run machine's path -> this machine's: by the path relative to the forensics root, or under the profile cards root
        if inp.get('root_rel'):
            return os.path.join(F, inp['root_rel'])
        if '/cards_v5_1/' in inp['path']:
            return os.path.join(P, inp['path'].split('/cards_v5_1/', 1)[1])
        p = inp['path']
        if not os.path.exists(p) and p.startswith('/Volumes/'):
            p = os.path.join(V, p[len('/Volumes/'):])
        elif not os.path.exists(p) and '/mnt/' in p:
            p = os.path.join(V, p.split('/mnt/', 1)[1])
        return p
    for run in sorted(d for d in os.listdir(O) if os.path.isdir(os.path.join(O, d))):
        R = os.path.join(O, run); info = json.load(open(R + '/RUN.json')); a = info['alarm_id']
        moved = [k for k in ('rulebook', 'safety') if not os.path.isfile(here(info['inputs'][k])) or sha16(here(info['inputs'][k])) != info['inputs'][k]['sha16']]
        if moved:     # the run was made from another version of these files: nothing below can be recomputed from today's
            say(False, '%s Q7 %s changed since this run was made (recompute skipped)' % (run, ', '.join(moved))); continue
        rb = json.load(open(here(info['inputs']['rulebook']))); sf = json.load(open(here(info['inputs']['safety'])))
        act = ('DEFAULT', 'CANDIDATE', 'FROZEN') if info['mode'] == 'research' else ('DEFAULT', 'FROZEN')
        lines = [x for x in rb['skip_rules'] if x['status'] in act and x['status'] != 'DEFAULT']
        used = {x['field']: (x['states'], x['reasons']) for x in lines + sf['off_states']}
        # Q8
        say(all(open(os.path.join(R, n)).readline().rstrip('\n').split('\t') == h.split() for n, h in HEADS.items()),
            '%s Q8 the 4 output headers are the fixed pipeline headers' % run)
        # raw cards, keyed by (coin, t, side)
        cards = {'ctx.': {}, 'prof.': {}, 'pmm.': {}}
        src = {'ctx.': [(L + '/context_split/runs_v41/commit_974f4eeb79487e91/STATE_CARDS_%s_V41.tsv' % a, 't')],
               'prof.': [(P + '/%s/CARDS_%s.tsv' % (s, a), 'emission_t') for s in 'abc'],
               'pmm.': [(L + '/cause_lib/run_v1_2/PMM_%s.tsv' % shorts[a], 'emission_t')]}
        for pre, fl in src.items():
            for p, tcol in fl:
                for r in rows(p):
                    if r['registry_id'] == a:
                        cards[pre][(r['coin'].upper(), int(r[tcol]), int(r['side']))] = r
        fires = [r for r in uni if r['alarm_id'] == a and info['first'] <= dt.datetime.fromtimestamp(int(r['t']), dt.timezone.utc).strftime('%Y%m%d') <= info['last']]
        dec = rows(R + '/DECISIONS.tsv')
        # Q2
        fk = sorted((r['coin'].upper(), int(r['t']), int(r['side'])) for r in fires)
        dk = sorted((r['coin'], int(r['t']), int(r['side'])) for r in dec)
        tk = rows(R + '/TAKE_EVENTS.tsv'); sk = rows(R + '/SKIP_EVENTS.tsv')
        part = sorted([(r['coin'], int(r['t']), int(r['side'])) for r in tk + sk])
        say(fk == dk == part and len(set(dk)) == len(dk) and all(r['alarm_id'] == a for r in dec + tk + sk), '%s Q2 rows = universe fires once each (%d), TAKE %d + SKIP %d' % (run, len(fk), len(tk), len(sk)))
        # Q1, Q3
        diff = 0; vdiff = 0; counts = {}; undeclared = 0
        for r in dec:
            k = (r['coin'], int(r['t']), int(r['side']))
            vals = {}
            for f in used:
                pre = f[:f.index('.') + 1]; c = cards[pre].get(k)
                vals[f] = 'NO_CARD_ROW' if c is None else ((c.get(f[len(pre):]) or '').strip() or 'NO_VALUE')
                counts[(f, vals[f])] = counts.get((f, vals[f]), 0) + 1
                undeclared += declared(vals[f], *used[f]) == 'UNDECLARED'
            written = dict(x.split('=', 1) for x in r['used_values'].split(';') if x)
            if written != vals:
                vdiff += 1
            day = dt.datetime.fromtimestamp(k[1], dt.timezone.utc).strftime('%Y%m%d')
            side = {'FADE': -k[2], 'FOLLOW': k[2], 'UNSET': 0}[rb['side']['value']]
            exp = None
            if k[2] not in (1, -1):
                exp = ('SKIP', '1', 'BAD_DATA', 'push_side=%s' % k[2], '0')
            for f in used:
                if exp is None and declared(vals[f], *used[f]) != 'STATE':
                    exp = ('SKIP', '1', 'BAD_DATA', '%s=%s' % (f, vals[f]), '0'); break
            if exp is None and day in [str(x) for x in sf['off_days']]:
                exp = ('SKIP', '2', 'OFF_STATE', 'off_day=%s' % day, '0')
            if exp is None:
                for o in sf['off_states']:
                    if vals[o['field']] in o['off_if']:
                        exp = ('SKIP', '2', 'OFF_STATE', '%s:%s=%s' % (o['id'], o['field'], vals[o['field']]), '0'); break
            if exp is None and rb['side']['status'] not in act:
                exp = ('SKIP', '3', 'SIDE_NOT_ACTIVE', 'side status %s in %s mode' % (rb['side']['status'], info['mode']), '0')
            if exp is None:
                for x in lines:
                    if vals[x['field']] in x['skip_if']:
                        exp = ('SKIP', '4', 'SKIP_RULE', '%s:%s=%s' % (x['id'], x['field'], vals[x['field']]), str(side)); break
            if exp is None:
                exp = ('TAKE', '4', 'NO_SKIP_LINE_TRUE', '', str(side))
            got = (r['action'], r['slot'], r['reason'], r['detail'], r['trade_side'])
            if got != exp:
                diff += 1
        say(diff == 0, '%s Q1 recomputed decisions: %d rows, %d differ' % (run, len(dec), diff))
        say(vdiff == 0 and undeclared == 0, '%s Q3 used field values equal the raw cards: %d rows differ, %d undeclared words' % (run, vdiff, undeclared))
        # Q4
        vc = {(r['field'], r['value']): int(r['fires']) for r in rows(R + '/VALUE_COUNTS.tsv')}
        kinds_ok = all(r['kind'] == declared(r['value'], *used[r['field']]) and r['alarm_id'] == a for r in rows(R + '/VALUE_COUNTS.tsv'))
        say(vc == counts and kinds_ok, '%s Q4 value counts equal a direct count (%s)' % (run, ', '.join('%s=%d' % (v, n) for (f, v), n in sorted(counts.items())) or 'no field used'))
        # Q5
        w = {}
        for r in fires:
            w[r['cluster_id']] = w.get(r['cluster_id'], 0.0) + float(r['weight'])
        tot = sum(t['weight'] for t in info['tally'].values())
        say(all(abs(v - 1) < 1e-6 for v in w.values()) and abs(tot - len(w)) < 1e-3, '%s Q5 waves %d, every wave weighs 1, tally weight %.3f' % (run, len(w), tot))
        # Q6
        evs = [('side', rb['side'].get('evidence'))] + [(x['id'], x.get('evidence')) for x in rb['skip_rules']]
        for who, ev in evs:
            if not ev:
                continue
            src_lines = open(os.path.join(F, ev['source'])).read().split('\n')
            nums = re.findall(r'[+-]?\d[\d,]*\.?\d*', ev['cell'])
            nums = [n.rstrip('.,') for n in nums if len(n.strip('+-').replace(',', '').rstrip('.')) >= 3 or '.' in n.rstrip('.')]
            best = max(range(len(src_lines)), key=lambda i: sum(n in src_lines[i] for n in nums))
            missing = [n for n in nums if n not in src_lines[best]]
            say(not missing and sha16(os.path.join(F, ev['source'])) == ev['sha16'],
                '%s Q6 %s evidence numbers in one line (%d) of %s: %s%s' % (run, who, best + 1, os.path.basename(ev['source']), ' '.join(nums), (' MISSING ' + ' '.join(missing)) if missing else ''))
        # Q9
        sl = {}
        for r in rows(here(info['inputs']['source_events'])):
            sl[(r['coin'].upper(), int(r['t']), int(r['side']))] = (r['onset_t'], r['trigger'], r['event_id'])
        idiff = sum(sl.get((r['coin'], int(r['t']), int(r['side']))) != (r['onset_t'], r['trigger'], r['event_id']) for r in tk + sk)
        say(idiff == 0, '%s Q9 event identity equals the source list (%d rows, %d differ, triggers %s)'
            % (run, len(tk + sk), idiff, ','.join(sorted({r['trigger'] for r in tk + sk}))))
        # Q7
        ok = all(sha16(os.path.join(R, n)) == h for n, h in info['outputs'].items()) and all(sha16(here(v)) == v['sha16'] for v in info['inputs'].values())
        say(ok, '%s Q7 RUN.json sha16s equal disk' % run)
    out.append('%d checks, %d failed' % (len(out), bad))
    open(os.path.join(O, 'MEANING_DECIDE_V1.txt'), 'w').write('\n'.join(out) + '\n')
    print('\n'.join(out))
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:5]))
