"""add_row: append one LESSONS, RESULTS, TRIED, GAPS, CHANGES or PROMPTS row safely (twin first, clock stamp, column check, unique id).

Usage:
  python3 add_row.py <file.tsv> key=value [key=value ...]
The stamp column (date_utc or utc) is filled from the clock when not given. Creates the file with its header if missing.
"""
import csv, os, re, shutil, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from common import (LESSON_COLS, RESULT_COLS, TRIED_COLS, GAP_COLS, CHANGE_COLS, PROMPT_COLS, STAMP, STATUSES, VERDICTS, TRIED_VERDICTS, FAIL_LAYERS,
                    GAP_KINDS, GAP_STATUSES, CHANGE_STATUSES, PROMPT_STATUSES, find_root, ledger_ids, load_config, now_utc, read_tsv)


WARNINGS = []


def FAIL(msg):
    """playground work is never blocked (owner rule): its row is written with a warning; anything else is refused"""
    if PLAYGROUND[0]:
        WARNINGS.append(msg)
        print('WARN (playground, row still written): ' + msg)
        return
    sys.exit(msg)


PLAYGROUND = [False]


def check_design_quote(text):
    """a change to a tool quotes the rule it keeps: design=<file>; rule="<words>"; the words must be in that file, so the file was opened"""
    m = re.match(r'^design=(.+?); rule="(.{20,})"$', text.strip())
    if not m:
        FAIL('a tool change: closest_existing must be design=<file>; rule="<at least 20 characters copied from it>"')
        return
    f = os.path.expanduser(m.group(1))
    if not os.path.isfile(f):
        FAIL(f'a tool change: design file not found: {f}')
        return
    words = ' '.join(open(f, errors='replace').read().split())
    if ' '.join(m.group(2).split()) not in words:
        FAIL(f'a tool change: the quoted rule is not in {f}: copy it exactly')


def check_tried(path, rec):
    """the loop's own rules: every field answered, a failure names its stage and layer, a test that read outcomes names its ledger row"""
    empty = [k for k, v in rec.items() if not v.strip()]
    if empty:
        FAIL(f'empty fields {empty}: write none, or unknown, never leave a question blank')
    if rec['verdict'] not in TRIED_VERDICTS:
        FAIL(f'verdict must be one of {sorted(TRIED_VERDICTS)}: a test that passed its bar is WORKED, one that missed it is FAILED')
    if rec['fail_layer'] not in FAIL_LAYERS:
        FAIL(f'fail_layer must be one of {sorted(FAIL_LAYERS)}')
    here = os.path.dirname(os.path.abspath(path))
    root = find_root(here)
    cfg = load_config(root) if root else None
    if cfg and rec['process'] not in cfg['roster']:
        FAIL(f'process {rec["process"]} is not in the roster of {root}/LOOP.json')
    if rec['process'] == (cfg or {}).get('tools_process', '7_TOOLS'):
        check_design_quote(rec['closest_existing'])
    if cfg and cfg['ledger'] and rec['months_read'] != 'none':
        known = {i for _, i in ledger_ids(cfg)[0]}
        if rec['ledger_row'] == 'UNREGISTERED':  # outcomes read with no registration first: recorded, never counted as evidence
            if rec['verdict'] != 'INVALID_TEST' or rec['fail_layer'] != 'PROCESS':
                FAIL('ledger_row UNREGISTERED: the try read outcomes with no registration, so verdict INVALID_TEST and fail_layer PROCESS')
            known.add('UNREGISTERED')
        bad = [x.strip() for x in rec['ledger_row'].split(',') if x.strip() not in known]
        if bad:
            FAIL(f'ledger_row {bad} not in the ledger {cfg["ledger"]}: name the result id the ledger holds, not a registration')
    thought = os.path.join(here, rec['thought_file'])
    if not os.path.isfile(thought) or os.path.getsize(thought) == 0:
        FAIL(f'thought_file {rec["thought_file"]} missing or empty beside {path}: write the thought process first')
    if rec['verdict'] in ('FAILED', 'INVALID_TEST', 'NOT_MEASURABLE', 'STOPPED'):
        if rec['fail_layer'] == 'NONE' or rec['why'] in ('none', 'unknown'):
            FAIL('a try that did not work names its fail_layer and why (UNEXPLAINED: <what was checked> is allowed)')
        stages = {r[0] for r in read_tsv(os.path.join(here, 'STAGES.tsv'))[1]}
        if rec['failed_stage'] not in stages:
            FAIL(f'failed_stage must be one of {sorted(stages)}')
    if rec['verdict'] == 'PLANNED' and rec['months_read'] != 'none':
        FAIL('PLANNED means no outcome was read')
    _st = os.stat(os.path.join(here, rec["thought_file"]))   # st_birthtime exists on macOS only; Linux falls back to the last change (SCOUT 4 Nov: add_row crashed on Linux)
    print(f'minutes since the thought file was started: {(time.time() - getattr(_st, "st_birthtime", _st.st_mtime)) / 60:.0f}')
    if rec['verdict'] == 'INVALID_TEST' and rec['fail_layer'] == 'PREMISE':
        FAIL('an invalid test says nothing about the premise: name the layer that broke')
    if rec['months_read'] != 'none' and rec['ledger_row'] == 'none':
        FAIL('months were read: name the TRIES_LEDGER row')
    if rec['fail_layer'] == 'PROMPT' and rec['prompt_fix'] == 'none':
        FAIL('a prompt failure needs prompt_fix')
    for k in ('minutes_active', 'minutes_waiting', 'minutes_blocked'):
        if rec[k] != 'unknown' and not rec[k].replace('.', '', 1).isdigit():
            FAIL(f'{k} is minutes or unknown; unknown is not zero')


def main():
    path, pairs = sys.argv[1], sys.argv[2:]
    kind = os.path.basename(path).split('_')[0]
    cols = {'LESSONS': LESSON_COLS, 'RESULTS': RESULT_COLS, 'TRIED': TRIED_COLS, 'GAPS': GAP_COLS, 'CHANGES': CHANGE_COLS, 'PROMPTS': PROMPT_COLS}.get(kind)
    if cols is None:
        sys.exit('file name must start with LESSONS_, RESULTS_, TRIED_, GAPS_, CHANGES_ or PROMPTS_')
    rec = dict(p.split('=', 1) for p in pairs)
    stamp_col = 'date_utc' if kind == 'LESSONS' else 'utc'
    rec.setdefault(stamp_col, now_utc())
    unknown = set(rec) - set(cols)
    if unknown:
        sys.exit(f'unknown columns {sorted(unknown)}; allowed {cols}')
    missing = [c for c in cols if c not in rec]
    if missing:
        sys.exit(f'missing columns {missing}')
    if not STAMP.match(rec[stamp_col]):
        sys.exit(f'stamp {rec[stamp_col]!r} is not a clock stamp YYYY-MM-DDTHH:MM:SSZ; leave it out to use the clock')
    if rec[stamp_col] > now_utc():
        sys.exit(f'stamp {rec[stamp_col]} is after the clock: typed by hand; leave it out to use the clock')
    if kind == 'LESSONS' and rec['status'] not in STATUSES:
        sys.exit(f'status must be one of {sorted(STATUSES)}')
    if kind == 'LESSONS' and rec['status'] == 'CLOSED' and not rec['check_id']:
        sys.exit('CLOSED needs a check_id')
    if kind == 'RESULTS' and rec['verdict'] not in VERDICTS:
        sys.exit(f'verdict must be one of {sorted(VERDICTS)}')
    if kind == 'TRIED':
        PLAYGROUND[0] = rec.get('playground_ref', 'none').strip() not in ('', 'none') and rec.get('months_read', 'none') == 'none'
        check_tried(path, rec)
    if kind == 'LESSONS' and not {'scope:general', 'scope:project'} & {t.strip() for t in rec['tags'].split(',')}:
        sys.exit('a lesson says whether it holds everywhere or only here: add tag scope:general or scope:project')
    for k, col, allowed in (('GAPS', 'kind', GAP_KINDS), ('GAPS', 'status', GAP_STATUSES), ('CHANGES', 'status', CHANGE_STATUSES), ('PROMPTS', 'status', PROMPT_STATUSES)):
        if kind == k and rec[col] not in allowed:
            sys.exit(f'{col} must be one of {sorted(allowed)}')
    if kind == 'PROMPTS' and rec['status'] == 'CURRENT' and rec['eval_ref'] in ('', 'none'):
        sys.exit('a CURRENT prompt names the test that earned it (eval_ref)')
    if any('\t' in v or '\n' in v for v in rec.values()):
        sys.exit('values may not contain tabs or new lines')
    if os.path.exists(path):
        head, body = read_tsv(path)
        if head != cols:
            sys.exit(f'header of {path} is {head}, want {cols}')
        if rec['id'] in {r[0] for r in body}:
            sys.exit(f'id {rec["id"]} already used')
        shutil.copy2(path, f'{path}.pre_{rec[stamp_col].replace("-", "").replace(":", "")}')
        mode = 'a'
    else:
        mode = 'w'
    with open(path, mode, newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        if mode == 'w':
            w.writerow(cols)
        w.writerow([rec[c] for c in cols])
    print(f'added {rec["id"]} to {path}')


if __name__ == '__main__':
    main()
