"""loop_init: start a learning loop for any project. Writes LOOP.json and one folder per process with its empty registers. Never overwrites.

Usage: python3 loop_init.py <loop root> --roster 1_IDEAS,2_TESTS[,...] [--tools-process 9_TOOLS] [--ledger <tsv> --ledger-id-col <col> --ledger-from YYYYMMDD
       [--ledger-result-col <col> --ledger-result-value <value>]]
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import CHANGE_COLS, GAP_COLS, LESSON_COLS, PROMPT_COLS, TRIED_COLS, CONFIG


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--roster', required=True)
    ap.add_argument('--tools-process', default='')
    ap.add_argument('--ledger', default='')
    ap.add_argument('--ledger-id-col', default='')
    ap.add_argument('--ledger-from', default='')
    ap.add_argument('--ledger-result-col', default='')
    ap.add_argument('--ledger-result-value', default='')
    a = ap.parse_args()
    roster = [x.strip() for x in a.roster.split(',') if x.strip()]
    if a.tools_process and a.tools_process not in roster:
        roster.append(a.tools_process)
    cfg = {'roster': roster, 'tools_process': a.tools_process, 'ledger': a.ledger, 'ledger_id_col': a.ledger_id_col, 'ledger_from': a.ledger_from,
           'ledger_result_col': a.ledger_result_col, 'ledger_result_value': a.ledger_result_value}
    os.makedirs(a.root, exist_ok=True)
    p = os.path.join(a.root, CONFIG)
    if os.path.exists(p):
        sys.exit(f'{p} exists: edit it by hand, with a twin')
    json.dump(cfg, open(p, 'w'), indent=1)
    for name in roster:
        d = os.path.join(a.root, name)
        short = name.split('_', 1)[-1]
        os.makedirs(os.path.join(d, 'thoughts'), exist_ok=True)
        for n, cols in (('TRIED', TRIED_COLS), ('LESSONS', LESSON_COLS), ('GAPS', GAP_COLS), ('CHANGES', CHANGE_COLS)):
            f = os.path.join(d, f'{n}_{short}_V1.tsv')
            if not os.path.exists(f):
                open(f, 'w').write('\t'.join(cols) + '\n')
        for f, text in (('STAGES.tsv', 'stage\tquestion\n'), ('START_HERE.md', f'# {name}: start here\nGoal, stages (STAGES.tsv), tools.\n')):
            if not os.path.exists(os.path.join(d, f)):
                open(os.path.join(d, f), 'w').write(text)
    os.makedirs(os.path.join(a.root, 'PROMPTS', 'files'), exist_ok=True)
    reg = os.path.join(a.root, 'PROMPTS', 'PROMPTS_V1.tsv')
    if not os.path.exists(reg):
        open(reg, 'w').write('\t'.join(PROMPT_COLS) + '\n')
    print(f'loop ready at {a.root}: {len(roster)} processes; fill each STAGES.tsv and START_HERE.md')


if __name__ == '__main__':
    main()
