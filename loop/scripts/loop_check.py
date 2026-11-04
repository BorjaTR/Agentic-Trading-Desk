"""loop_check: is the learning loop being used? Read only. Exit 1 on a problem.

Acceptance: python3 loop_check.py <loop root> --accept [--playground <folder>]
  Only this form can print VERDICT FULL_PASS: the roster, ledger and start come from <loop root>/LOOP.json and cannot be overridden.
End of one trial: --try <ledger id>: that id has a valid row. End of a release: --edition <name>: a valid tools row names it.
Diagnostics: python3 loop_check.py <loop root> [--playground <folder>] [--ledger <tsv> [--since YYYYMMDD]] [--speed]: prints SCOPED, never a pass.
Checks: every TRIED row's thought file; every prompt file's sha16; one CURRENT per prompt; every playground row names the closest released thing;
every outcome try in the ledger since --since has a TRIED row (the loop died once because nothing checked this).
"""
import argparse, glob, hashlib, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import FAIL_LAYERS, PROMPT_COLS, TRIED_COLS, TRIED_VERDICTS, ledger_ids, load_config, read_tsv


def rows(path, cols, problems):
    """fail closed: a wrong header or a row of the wrong width is a problem, never an empty file"""
    head, body = read_tsv(path)
    if cols and head != cols:
        problems.append(f'{path}: wrong header')
        return []
    for n, r in enumerate(body, 2):
        if len(r) != len(head):
            problems.append(f'{path} line {n}: {len(r)} fields, want {len(head)}')
    return [dict(zip(head, r)) for r in body if len(r) == len(head)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('process')
    ap.add_argument('--playground', default='')
    ap.add_argument('--ledger', default='')
    ap.add_argument('--since', default='')
    ap.add_argument('--speed', action='store_true')
    ap.add_argument('--accept', action='store_true')
    ap.add_argument('--try', dest='try_id', default='')
    ap.add_argument('--edition', default='')
    a = ap.parse_args()
    try:
        cfg = load_config(a.process)
    except ValueError as e:
        sys.exit(f'REFUSED\t{e}')
    if (a.accept or a.try_id or a.edition) and (a.since or a.ledger or not cfg):
        sys.exit('REFUSED\t--accept, --try and --edition read LOOP.json and take no --ledger or --since')
    problems, tried, warnings = [], [], []  # warnings: playground rows, never blocking (owner rule)
    names = cfg['roster'] if cfg else []
    if not cfg:
        problems.append('LOOP.json missing: the roster, ledger and start of this loop')
    print(f'PROCESSES\t{len(names)} checked')
    for name in names:
        d = os.path.join(a.process, name)
        short = name.split('_', 1)[-1]
        for need in ('START_HERE.md', 'STAGES.tsv', f'TRIED_{short}_V1.tsv', f'LESSONS_{short}_V1.tsv', f'GAPS_{short}_V1.tsv', f'CHANGES_{short}_V1.tsv'):
            if not os.path.isfile(os.path.join(d, need)):
                problems.append(f'{name}: {need} missing')
        p = os.path.join(d, f'TRIED_{short}_V1.tsv')
        if not os.path.isfile(p):
            continue
        got = rows(p, TRIED_COLS, problems)
        replaced = {r['what_tried'].split()[1].rstrip(':;,') for r in got if r['what_tried'].startswith('replaces ') and len(r['what_tried'].split()) > 1}
        replaced |= {r['id'].rsplit('_C', 1)[0] for r in got if re.search(r'_C\d+$', r['id'])}  # a correction row <id>_C1 also clears <id>
        for r in got:
            blank = [k for k, v in r.items() if not v.strip()]
            play = r['playground_ref'].strip() not in ('', 'none') and r['months_read'].strip() == 'none'
            if r['id'] not in replaced and (blank or r['verdict'] not in TRIED_VERDICTS or r['fail_layer'] not in FAIL_LAYERS):
                (warnings if play else problems).append(f'{r["id"]}: not a row add_row would accept (blank {blank[:3]}, verdict {r["verdict"]!r}, layer {r["fail_layer"]!r}); write rows with add_row; to correct it, add a row whose what_tried starts "replaces <id>"')
                continue
            t = os.path.join(d, r['thought_file'])
            if not os.path.isfile(t) or os.path.getsize(t) == 0:
                (warnings if play else problems).append(f'{r["id"]}: thought file missing or empty: {r["thought_file"]}')
            elif r['id'] not in replaced and r['id'] not in {x['id'] for x in tried}:
                tried.append(r)
    reg = os.path.join(a.process, 'PROMPTS', 'PROMPTS_V1.tsv')
    current, latest = {}, {}
    if not os.path.isfile(reg):
        problems.append('PROMPTS/PROMPTS_V1.tsv missing')
    for r in rows(reg, PROMPT_COLS, problems) if os.path.isfile(reg) else []:
        f = os.path.join(a.process, 'PROMPTS', r['file'])  # the kept copy under PROMPTS: a working file elsewhere moves on
        if not os.path.exists(f):
            problems.append(f'prompt {r["id"]}: file missing {f}')
        elif hashlib.sha256(open(f, 'rb').read()).hexdigest()[:16] != r['sha16']:
            problems.append(f'prompt {r["id"]}: file changed after registering: a new version is a new row')
        latest[(r['prompt'], r['version'])] = r  # a later row for the same version sets its status; old rows stay as written
    for r in latest.values():
        if r['status'] == 'CURRENT':
            current.setdefault(r['prompt'], []).append(r['id'])
    for name, path in ((cfg or {}).get('served_prompts') or {}).items():  # the text agents really get must be the CURRENT one
        f = os.path.expanduser(path)
        cur = [latest[x] for x in latest if x[0] == name and latest[x]['status'] == 'CURRENT']
        if not os.path.isfile(f):
            problems.append(f'served prompt {name}: file missing {f}')
        elif not cur or hashlib.sha256(open(f, 'rb').read()).hexdigest()[:16] not in {r['sha16'] for r in cur}:
            problems.append(f'served prompt {name} ({f}) is not the CURRENT registered version: register its text as a new version row')
    for name, ids in current.items():
        if len(ids) > 1:
            problems.append(f'prompt {name}: more than one CURRENT {ids}')
    if a.playground:
        for r in rows(os.path.join(a.playground, 'INDEX.tsv'), None, problems):
            if not r['closest_released'].strip() or not r['why_not_it'].strip():
                problems.append(f'playground {r["id"]}: names no closest released thing and why not')
            if not os.path.exists(os.path.join(a.playground, r['path'])):
                problems.append(f'playground {r["id"]}: path missing {r["path"]}')
    lcfg = dict(cfg or {})
    if a.ledger:
        lcfg.update(ledger=a.ledger, ledger_id_col=lcfg.get('ledger_id_col') or 'ask_id', ledger_from=a.since or lcfg.get('ledger_from', '0'))
    if lcfg.get('ledger'):
        ids, n = ledger_ids(lcfg)
        since = a.since or lcfg['ledger_from']
        if a.accept and not ids:
            problems.append('ledger has no rows: not a ledger to accept against')
        if len(ids) < n:
            problems.append(f'ledger: {n - len(ids)} lines with no id')
        logged = {x.strip() for r in tried for x in r['ledger_row'].split(',')}
        miss = [i for d, i in ids if d >= since and i not in logged]
        print(f'LEDGER\ttries since {since}: {len(miss)} with no TRIED row')
        problems += [f'ledger try with no TRIED row: {m}' for m in miss[:20]]
    if a.try_id:
        ok = [r for r in tried if r['id'] == a.try_id or a.try_id in {x.strip() for x in r['ledger_row'].split(',')}]
        print(f'TRY\t{a.try_id}\t{len(ok)} valid rows')
        if not ok:
            problems.append(f'trial {a.try_id}: no valid row; log it with add_row before the trial ends')
    if a.edition:
        tp = cfg.get('tools_process', '')
        ok = [r for r in tried if r['process'] == tp and a.edition in (r['what_tried'] + ' ' + r['tools_used'])]
        print(f'EDITION\t{a.edition}\t{len(ok)} rows in {tp}')
        if not ok:
            problems.append(f'edition {a.edition}: no row in {tp} names it; a code change is logged before it is released')
    if a.speed:
        by = {}
        for r in tried:
            by.setdefault(r['process'], []).append(r)
        for proc, rs in sorted(by.items()):
            act = [float(r['minutes_active']) for r in rs if r['minutes_active'] != 'unknown']
            wait = [float(r['minutes_waiting']) for r in rs if r['minutes_waiting'] != 'unknown']
            print(f'SPEED\t{proc}\ttries {len(rs)}\tmedian active {statistics.median(act) if act else "unknown"}\tmedian waiting {statistics.median(wait) if wait else "unknown"}')
    for m in warnings:
        print('WARN\tplayground, not blocking: ' + m)
    for m in problems:
        print('PROBLEM\t' + m)
    print(f'SUMMARY\ttried {len(tried)}\tproblems {len(problems)}')
    print('VERDICT\t' + ('FAIL' if problems else 'FULL_PASS' if a.accept else 'PASS' if (a.try_id or a.edition) else 'SCOPED: not an acceptance'))
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
