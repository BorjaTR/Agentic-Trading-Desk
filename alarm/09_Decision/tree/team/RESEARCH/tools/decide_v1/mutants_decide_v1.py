"""mutants_decide_v1.py (DECIDE seat, 26 Oct 2026; SCOUT 2 Nov, ALARM_V1_20: copyfile, so copies from a read-only install can be edited): each mutant changes one rule in a copy of the code; tests_decide_v1.py must fail on
every one. The unchanged copy must pass first (else every mutant would look killed). The copy's tests read the real universe and registry
from the forensics root (DECIDE_FORENSICS), since the copy does not sit under it.
  python3 -B mutants_decide_v1.py -> one line per mutant, exit 1 if any survives."""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.realpath(__file__))
FILES = ('decide_rules_v1.py', 'decide_v1.py', 'tests_decide_v1.py', 'edges_decide_v1.py', 'EDGES_DECIDE_V1.tsv', 'SETTINGS_DECIDE_V1.tsv')
MUTANTS = [
    ('R01 fade is with the push', 'decide_rules_v1.py', "{'FADE': -push_side, 'FOLLOW': push_side", "{'FADE': push_side, 'FOLLOW': push_side"),
    ('R02 last true line decides', 'decide_rules_v1.py', "    for ln in active_lines(rb, mode):\n        if values", "    for ln in reversed(active_lines(rb, mode)):\n        if values"),
    ('R03 data gate skipped', 'decide_rules_v1.py', "        if k != 'STATE':\n            return out('SKIP', 1", "        if False:\n            return out('SKIP', 1"),
    ('R04 paper mode uses candidates', 'decide_rules_v1.py', "'paper': ('DEFAULT', 'FROZEN')", "'paper': ('DEFAULT', 'CANDIDATE', 'FROZEN')"),
    ('R05 failed lines decide', 'decide_rules_v1.py', "ACTIVE = {'research': ('DEFAULT', 'CANDIDATE', 'FROZEN')", "ACTIVE = {'research': ('DEFAULT', 'CANDIDATE', 'FROZEN', 'FAILED')"),
    ('R06 evidence not needed', 'decide_rules_v1.py', "    if status == 'DEFAULT':\n        return", "    if True:\n        return"),
    ('R07 four active lines allowed', 'decide_rules_v1.py', 'MAX_SKIP_LINES = 3', 'MAX_SKIP_LINES = 4'),
    ('R08 off days ignored', 'decide_rules_v1.py', "    if str(day) in [str(d) for d in sf['off_days']]:", "    if False:"),
    ('R09 off states ignored', 'decide_rules_v1.py', "        if values[o['field']] in o['off_if']:", "        if False:"),
    ('R10 regime gate before data gate', 'decide_rules_v1.py', "    for f, (st, rs) in used_fields(rb, sf, mode).items():", "    for f, (st, rs) in ([] if str(day) in [str(d) for d in sf['off_days']] else used_fields(rb, sf, mode).items()):"),
    ('R11 any rulebook alarm accepted', 'decide_rules_v1.py', "if rb.get('alarm_id') not in ('*', alarm_id):", "if False:"),
    ('R12 entry not checked against lab tools', 'decide_rules_v1.py', "_item('entry', rb.get('entry'), sorted(tools['entry'] | {UNSET}))", "_item('entry', rb.get('entry'), None)"),
    ('R13 mechanism not needed', 'decide_rules_v1.py', "            if not str(ln.get('mechanism') or '').strip():", "            if False:"),
    ('R14 skip_if may equal states', 'decide_rules_v1.py', "not set(ln['skip_if']) < set(ln['states'])", "not set(ln['skip_if']) <= set(ln['states'])"),
    ('R15a the prefix guess put back (undeclared NO_/NOT_ words read as reasons)', 'decide_rules_v1.py', "    return 'REASON' if matches(v, reasons) else 'UNDECLARED'",
     "    return 'REASON' if (matches(v, reasons) or v.startswith(('UNKNOWN', 'HOLE', 'NO_', 'NOT_'))) else 'UNDECLARED'"),
    ('R15b the prefix guess put back (states may not start with NO_/NOT_)', 'decide_rules_v1.py', "    hit = [s for s in states if matches(s, reasons)]",
     "    hit = [s for s in states if matches(s, reasons) or s.startswith(('NO_', 'NOT_'))]"),
    ('R17 a state that is also a declared reason accepted', 'decide_rules_v1.py', "    if hit:\n", "    if False:\n"),
    ('R18 an undeclared word is bad data, not a refusal', 'decide_rules_v1.py', "        if k == 'UNDECLARED':\n            raise", "        if False:\n            raise"),
    ('R19 reasons not required', 'decide_rules_v1.py', "not {'id', 'field', 'states', 'reasons', 'skip_if', 'status'} <= set(ln)", "not {'id', 'field', 'states', 'skip_if', 'status'} <= set(ln)"),
    ('R16 push side 0 traded', 'decide_rules_v1.py', "    if push_side not in (1, -1):", "    if push_side not in (1, -1, 0):"),
    ('V01 undeclared words accepted', 'decide_v1.py', "    if bad:\n        raise Refused('UNDECLARED_VALUE'", "    if False:\n        raise Refused('UNDECLARED_VALUE'"),
    ('V02 duplicate card rows kept', 'decide_v1.py', "            if k in out:\n                raise Refused", "            if False:\n                raise Refused"),
    ('V03 research window not checked', 'decide_v1.py', "    if not (w0 <= a.first <= a.last <= w1):", "    if False:"),
    ('V04 coin filter ignored', 'decide_v1.py', "        if coins is not None and k[1] not in coins:", "        if False:"),
    ('V05 TAKE list gets the skips', 'decide_v1.py', "                if d['action'] == act:", "                if True:"),
    ('V06 missing row read as a state', 'decide_v1.py', "vals[f] = DR.NO_CARD_ROW; uncovered.append((f, k))", "vals[f] = 'ABOUT'"),
    ('V07 other alarms rows joined', 'decide_v1.py', "            if r[kc[0]] != alarm_id:\n                continue", "            if False:\n                continue"),
    ('V09 evidence not checked', 'decide_v1.py', "        if not os.path.isfile(p) or sha16(p) != want:", "        if not os.path.isfile(p):"),
    ('V08 out folder reused', 'decide_v1.py', "    if os.path.exists(a.out):", "    if False:"),
    ('V10 lab tool ids not looked up in the release code', 'decide_v1.py', "            if lost:\n", "            if False:\n"),
    ('V11 release code sha16 not checked', 'decide_v1.py', "if not os.path.isfile(q) or sha16(q) != h:", "if not os.path.isfile(q):"),
    ('V12 decisions header depends on the rulebook', 'decide_v1.py', "w.writerow(DECISIONS_HEAD)", "w.writerow(DECISIONS_HEAD[:-1] + sorted(used))"),
    ('V13 event rows lose the alarm id', 'decide_v1.py', "w.writerow([k[0], k[1], k[2], k[3], on, trig, eid])", "w.writerow(['', k[1], k[2], k[3], on, trig, eid])"),
    ('K01 dates not checked as real days', 'decide_v1.py', "        dt.datetime.strptime(s, '%Y%m%d')", "        pass"),
    ('K02 fractional numbers rounded', 'decide_v1.py', "    if not s.lstrip('+-').isdigit():", "    if False:"),
    ('K03 side 2 kept', 'decide_v1.py', "    if k[3] not in (-1, 0, 1):", "    if False:"),
    ('K04 a weight of inf kept', 'decide_v1.py', "        if not (math.isfinite(w) and w > 0):", "        if not (w > 0):"),
    ('K05 a card file not named by its release kept', 'decide_v1.py', "    if not any(h in t for t in texts):", "    if False:"),
    ('K06 release record sha16 not checked', 'decide_v1.py', "    if not os.path.isfile(rel) or sha16(rel) != lib['sha16']:", "    if not os.path.isfile(rel):"),
    ('K07 receipt sha16 not checked', 'decide_v1.py', "        if not os.path.isfile(rp) or sha16(rp) != rc['sha16']:", "        if not os.path.isfile(rp):"),
    ('K08 source list sha16 not checked', 'decide_v1.py', "    if not os.path.isfile(src_here) or sha16(src_here) != src_sha:", "    if not os.path.isfile(src_here):"),
    ('K09 fires missing from the source list kept', 'decide_v1.py', "    if lost:\n        raise Refused('SOURCE_MISMATCH'", "    if False:\n        raise Refused('SOURCE_MISMATCH'"),
    ('K10 event_id not copied', 'decide_v1.py', "(r.get('event_id') or '').strip())", "'')"),
    ('K11 missing status column allowed', 'decide_v1.py', "        if sr and f + sr['suffix'] not in fields[pre]:", "        if False:"),
    ('K12 a status not admitted is used', 'decide_v1.py', "    if bad_status:", "    if False:"),
    ('K13 a fire with no card row is bad data, not a refusal', 'decide_v1.py', "    if uncovered:", "    if False:"),
    ('K14 an empty used cell is bad data, not a refusal', 'decide_v1.py', "    if empty:", "    if False:"),
    ('K15 inputs not rechecked before writing', 'decide_v1.py', "    changed = [k for k, p in files.items() if sha16(p) != at_admission[k]]\n    if changed:\n        raise", "    changed = []\n    if changed:\n        raise"),
    ('K16 verify ignores edited files', 'decide_v1.py', "    if bad:\n        raise Refused('RUN_CHANGED_AFTER_COMMIT'", "    if False:\n        raise Refused('RUN_CHANGED_AFTER_COMMIT'"),
    ('K17 verify ignores stray or missing files', 'decide_v1.py', "    if set(outs) != set(OUTPUTS) or present != set(OUTPUTS):", "    if False:"),
    ('K18 verify accepts an uncommitted folder', 'decide_v1.py', "    if not os.path.isfile(rp):\n        raise Refused('RUN_NOT_COMMITTED'", "    if False:\n        raise Refused('RUN_NOT_COMMITTED'"),
]


def main():
    env = dict(os.environ, DECIDE_FORENSICS=os.environ.get('DECIDE_FORENSICS') or os.path.realpath(os.path.join(HERE, '..', '..', '..', '..')))
    d = tempfile.mkdtemp()
    try:
        for f in FILES:
            shutil.copyfile(os.path.join(HERE, f), os.path.join(d, f))
        r = subprocess.run([sys.executable, '-B', os.path.join(d, 'tests_decide_v1.py')], capture_output=True, text=True, timeout=120, env=env)
        if r.returncode != 0:
            print('BASELINE FAILS: the unchanged copy does not pass, no mutant can be judged'); print(r.stdout[-2000:]); return 1
        print('BASELINE passes')
    finally:
        shutil.rmtree(d)
    alive = 0
    for name, fn, old, new in MUTANTS:
        d = tempfile.mkdtemp()
        try:
            for f in FILES:
                shutil.copyfile(os.path.join(HERE, f), os.path.join(d, f))
            src = open(os.path.join(d, fn)).read()
            if src.count(old) != 1:
                print('BROKEN', name, '(pattern found %d times)' % src.count(old)); alive += 1; continue
            open(os.path.join(d, fn), 'w').write(src.replace(old, new))
            r = subprocess.run([sys.executable, '-B', os.path.join(d, 'tests_decide_v1.py')], capture_output=True, text=True, timeout=120, env=env)
            if r.returncode == 0:
                alive += 1; print('SURVIVED', name)
            else:
                print('KILLED', name)
        finally:
            shutil.rmtree(d)
    print('%d/%d mutants killed' % (len(MUTANTS) - alive, len(MUTANTS)))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main())
