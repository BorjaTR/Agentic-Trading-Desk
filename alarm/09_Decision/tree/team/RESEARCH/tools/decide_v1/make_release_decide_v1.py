"""make_release_decide_v1.py (DECIDE seat, 26 Oct 2026): writes the release record of decision tool V1 from disk, so no sha16 is typed
by hand (kit row 17). Every listed file is hashed here; every listed run is checked with decide_v1.verify_run() and its outputs copied
from its RUN.json. The record names the steps covered and the receipts. --check re-hashes a written record and lists any file that moved.
  python3 -B make_release_decide_v1.py <forensics> <runs folder> <second runs folder> <new record path> [release name]
  python3 -B make_release_decide_v1.py --check <forensics> <record>"""
import datetime as dt, json, os, sys
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import decide_v1 as DV

REL = 'team/RESEARCH/tools/decide_v1/'
FILES = ['decide_rules_v1.py', 'decide_v1.py', 'tests_decide_v1.py', 'mutants_decide_v1.py', 'edges_decide_v1.py', 'meaning_decide_v1.py',
         'make_release_decide_v1.py', 'EDGES_DECIDE_V1.tsv', 'SETTINGS_DECIDE_V1.tsv', 'ADMITTED_INPUTS_V1.json', 'LAB_TOOLS_V1.json',
         'SAFETY_V1.json', 'LAB_TOOLS_INVENTORY_V1.md', 'CARD_DECIDE_V1.md', 'SCOPE_DECIDE_V1.md', 'SPEED_BUDGET_DECIDE_V1.md',
         'README_DECIDE_V1.md', 'KIT_DECIDE_V1.md', 'run_decide_all_v1.sh', 'rulebooks/RULES_DEFAULT_V1.json', 'rulebooks/RULES_ALM_M_V1.json',
         'rulebooks/RULES_ALM_S3W_V1.json', 'receipts_kit_v1/TESTS.txt', 'receipts_kit_v1/MUTANTS.txt', 'receipts_kit_v1/EDGES.txt',
         'receipts_kit_v1/PROBE_KIT_OLD_VS_NEW.txt', 'receipts_kit_v1/probe_kit_old_vs_new_v1.py', 'receipts_kit_v1/split_tamper_old_vs_new.txt', 'receipts_kit_v1/split_uncommitted_v1.txt', 'receipts_kit_v1/MUTANTS_FIRST_AFTER_REWRITE.txt',
         'loop_v1/split_groups_v1.py', 'loop_v1/decide_loop_read_v1.py', 'loop_v1/test_decide_loop_read_v1.py',
         'loop_v1/DECIDE_LOOP_SETTINGS_V1.json', 'loop_v1/DECIDE_LOOP_PREREG_V1.md', 'loop_v1/run_decide_loop_v1.sh',
         'loop_v1/DECIDE_LOOP_PREREG_V1_1.md', 'loop_v1/DECIDE_LOOP_PREREG_V1_1_ADDENDUM_1.md', 'loop_v1/run_decide_loop_v1_1.sh',
         'loop_v1/summarize_decide_loop_v1_1.py', 'FINAL_NOTE_DECIDE_V1.md']
STEPS = {'lean step 1 card': 'CARD_DECIDE_V1.md (five parts, SETTINGS and EDGES as data)',
         'lean step 2 build': 'decide_rules_v1.py, decide_v1.py',
         'lean step 3 T1 edges through the tool': 'edges_decide_v1.py on EDGES_DECIDE_V1.tsv, 33 of 33',
         'lean step 3 T2 independent reading': 'meaning_decide_v1.py (imports nothing from the tool) and the reviewer recompute',
         'lean step 3 T3 real data': 'the 8 runs on the six frozen alarms',
         'lean step 3 T4 stamps': 'RUN.json: code, inputs, admitting releases, source list, phase times; verify_run()',
         'lean step 3 T5 same bytes': 'the 8 runs made twice, every output identical',
         'lean step 3 T6 scale': 'SPEED_BUDGET_DECIDE_V1.md',
         'scope and acceptance': 'SCOPE_DECIDE_V1.md A1-A13',
         'speed budget': 'SPEED_BUDGET_DECIDE_V1.md (written after the first runs, said so)',
         'test kit 25 Oct': 'KIT_DECIDE_V1.md, one line per row 1-17 and 6b',
         'meaning loop': 'MEANING_DECIDE_V1.txt in the first runs folder',
         'outcome loop': 'loop_v1_1_run on ALM_M_V1 (V1.0.1): NOTHING PAYS, S1 FAILED in 0 of 22 cells; audit AUDIT_DECIDE_LOOP_V1_1_INDEP.md 972a812dea5bb3c2'}


def main(F, runs, runs2, out, name='DECIDE_V1_CANDIDATE'):
    if os.path.exists(out):
        sys.exit('REFUSED: %s exists' % out)
    files = {REL + f: DV.sha16(os.path.join(F, REL, f)) for f in FILES}
    rec = {'release': name, 'by': 'DECIDE seat (thread Build decision tool V1)',
           'made_utc': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'files': files, 'steps_covered': STEPS, 'runs': {}}
    same = 0; total = 0
    for n in sorted(d for d in os.listdir(runs) if os.path.isdir(os.path.join(runs, d))):
        info = DV.verify_run(os.path.join(runs, n)); info2 = DV.verify_run(os.path.join(runs2, n))
        total += len(info['outputs']); same += sum(info['outputs'][k] == info2['outputs'].get(k) for k in info['outputs'])
        rec['runs'][n] = {'fires': info['fires'], 'tally': info['tally'], 'outputs': info['outputs'], 'timing_s': info['timing_s'],
                          'RUN.json': DV.sha16(os.path.join(runs, n, 'RUN.json'))}
    rec['runs_folder'] = runs; rec['second_runs_folder'] = runs2
    rec['same_bytes'] = '%d of %d outputs identical across the two folders' % (same, total)
    m = os.path.join(runs, 'MEANING_DECIDE_V1.txt')
    rec['meaning'] = {'file': m, 'sha16': DV.sha16(m), 'last_line': open(m).read().strip().splitlines()[-1]}
    if same != total:
        sys.exit('REFUSED: the two runs folders differ (%s)' % rec['same_bytes'])
    json.dump(rec, open(out, 'w'), indent=1, sort_keys=True)
    print(out, DV.sha16(out), rec['same_bytes'], rec['meaning']['last_line'])


def check(F, path):
    rec = json.load(open(path))
    moved = [p for p, h in rec['files'].items() if not os.path.isfile(os.path.join(F, p)) or DV.sha16(os.path.join(F, p)) != h]
    print('MOVED: %s' % moved if moved else 'every file at its sha16 (%d)' % len(rec['files']))
    return 1 if moved else 0


if __name__ == '__main__':
    if sys.argv[1] == '--check':
        sys.exit(check(*sys.argv[2:4]))
    main(*sys.argv[1:6])
