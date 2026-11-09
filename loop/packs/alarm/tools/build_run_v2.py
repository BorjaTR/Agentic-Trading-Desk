#!/usr/bin/env python3
"""build_run_v2.py (SCO-A182 for SCOUT, learning series V2; PLAYGROUND, TEST). From build_run_v1.py (twin build_run_v1.py.pre_SCO-A182_*).
Builds the hunter prompt of one V2 run = the launch_v1 brief word for word + the SERIES RUN PART of HUNTER_PROMPT_TEMPLATE_V2.md with
its {SLOTS} filled from SERIES_V2_CONFIG.json (windows, yardstick, paths, state split) and from the arm:
  L (learning): the KNOWLEDGE page, the adopted PROMPT_ADD rows (V1 file, then PROMPT_ADD_V2.tsv), earlier L runs, series views with no C row.
  C (control):  the same text, an EMPTY knowledge page (ops/KNOWLEDGE_EMPTY_V1.tsv, header only; loop_check needs the KNOWLEDGE_<SEAT>_V<n> name and prints VERDICT FAIL 'no live rows' by design), no PROMPT_ADD rows, no earlier runs, no
                series files, no TRIED grep and no loop_find (the tried table only through the pipeline's own copy search).
Subcommands:
  build --arm L|C --run N --task SCT-A<300+N|400+N> --brief <BRIEF.md> --out <HUNTER_PROMPT.md> [--runf D] [--config F] [--dry-test]
  fill --file <text with slots> --config F [--dry-test]           prints the text with the config slots filled (GOAL/PASS_RULE V2)
  env --arm L|C --run N --config F [--dry-test]                    prints shell lines TASK= RUN_ID= RUNF= RK= ... for part_a_v2.sh
  check-launch --arm L|C --run N --config F [--behind] [--dry-test] the order rule and the seat job limit (exit 0 GO, 2 STOP)
Build checks (any failure: REFUSED <word>, exit 2, nothing written): config READY (or --dry-test); task id of the arm; every slot filled;
no em or en dash; every absolute path exists (except what the run makes); the closed-month scan (drill K blindfold_scan_k.py) on the part,
with --allow-def-last <windows.def_last_day> (SCO-A184: that one value passes only as the DEF field "last"; DEF_LAST_DAY refuses a
missing or malformed value or a part that does not carry it in that field);
no scout_only window words in the part; FORECAST_R1, FORECAST_R2, FORECAST_R3 and the sealing line present; arm C: no knowledge (no K1- kid,
no KNOWLEDGE table, series file, tried table path, PROMPT_ADD row id or earlier run path in the part or the brief: C_LEAK); writes O_EXCL."""
import argparse, csv, glob, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
H = os.path.expanduser('~'); _M = H + '/mnt' if os.path.isdir(H + '/mnt') else H  # C27: Mac host has no mnt (VM layout)
FR = _M + '/dev/TradingPlatform_repo/volat-agent/forensics'; R = _M + '/volat_release'
LSD = FR + '/team/SCOUT/loop_day_20261105/learning_series'
SCAN = FR + '/team/SCOUT/loop_day_20261105/drills/drillK/ops/blindfold_scan_k.py'
EXCL = ('MAKERTIDE, BOTHFLUSH, WICKBACK, LEGSTRETCH, MIDJOLT, HLCROWD, WIDESWEEP, WIDEBLOCKS, FDAOI, FDAOIV, FUOI, FUOIV, FDONLY, FDAOIS, '
        'ENGINEHOUR, CROWDDRAG (drill K)')
UNSET = ('SET_AT_V26',)
BEGIN, END = '<!-- SERIES RUN PART BEGIN', '<!-- SERIES RUN PART END -->'


def h(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def refuse(word, why):
    print('REFUSED %s %s' % (word, why)); sys.exit(2)


def tsv(p):
    if not os.path.isfile(p):
        return []
    return list(csv.DictReader(open(p, newline='', encoding='utf-8'), delimiter='\t'))


def expand(v, ls):
    if isinstance(v, str):
        return v.replace('@R@', R).replace('@FR@', FR).replace('@HOME@/mnt', _M).replace('@HOME@', H).replace('@LS@', ls)
    if isinstance(v, list):
        return [expand(x, ls) for x in v]
    if isinstance(v, dict):
        return {k: expand(x, ls) for k, x in v.items()}
    return v


def unset_keys(v, path=''):
    out = []
    if isinstance(v, str) and v in UNSET:
        out.append(path)
    elif isinstance(v, dict):
        for k, x in v.items():
            out += unset_keys(x, path + '.' + k)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            out += unset_keys(x, '%s[%d]' % (path, i))
    return out


def load_cfg(path, ls, dry):
    c = expand(json.load(open(path, encoding='utf-8')), ls)
    if not dry:
        if c.get('status') != 'READY':
            refuse('CONFIG_NOT_READY', 'status %s in %s (V26 not landed; a dry test passes --dry-test)' % (c.get('status'), path))
        u = unset_keys(c)
        if u:
            refuse('CONFIG_UNSET', ' '.join(u))
    return c


def ids(arm, n, cfg, ls, runf=None):
    if arm not in cfg['arms']:
        refuse('BAD_ARM', arm)
    if not 1 <= n <= 99:
        refuse('BAD_RUN', str(n))
    rid = '%s%02d' % (arm, n)
    task = 'SCT-A%d' % (cfg['arms'][arm]['task_base'] + n)
    return rid, task, runf or os.path.join(ls, 'runs_v2', rid)


def alarm_marker_current(jl):
    cur = jl['alarm_current']
    try:
        tgt = os.readlink(cur)
    except OSError:
        tgt = ''
    return jl['marker'] in tgt or os.path.isfile(os.path.join(cur, 'RELEASE_%s.json' % jl['marker']))


def seat_jobs(jl, seat='SCOUT'):
    seen, jobs = set(), []
    for root in jl['job_roots']:
        if not os.path.isdir(root):
            continue
        rr = os.path.realpath(root)
        if rr in seen:
            continue
        seen.add(rr)
        for q in sorted(glob.glob(os.path.join(root, 'Q_*'))):
            hb = os.path.join(q, 'runner.heartbeat')
            age = (datetime.now(timezone.utc).timestamp() - os.path.getmtime(hb)) if os.path.isfile(hb) else 1e9
            if os.path.exists(os.path.join(q, 'runner.stop')) and age > 600:
                for f in sorted(glob.glob(os.path.join(q, 'RUN', '*_judge_%s_*' % seat))):
                    print('  STALE (stopped queue, heartbeat %d s old, not counted) %s/RUN/%s' % (age, os.path.basename(q), os.path.basename(f)))
                continue
            for sub in ('IN', 'RUN'):
                for f in sorted(glob.glob(os.path.join(q, sub, '*_judge_%s_*' % seat))):
                    if sub == 'IN' and not f.endswith('.job.sh'):
                        continue
                    jobs.append('%s/%s/%s' % (os.path.basename(q), sub, os.path.basename(f)))
    return jobs


def open_runs(ls, me=None):
    out = []
    for d in sorted(glob.glob(os.path.join(ls, 'runs_v2', '[LC][0-9][0-9]'))):
        if me and os.path.basename(d) == me:
            continue
        started = os.path.isdir(os.path.join(d, 'ops'))                       # in Part A or prepared or running
        failed = os.path.isfile(os.path.join(d, 'ops', 'PART_A_FAILED.txt'))  # a Part A that stopped holds no slot
        ended = bool(glob.glob(os.path.join(d, 'work', 'RESULT_*.md')))       # the hunter closed: its jobs are done
        if started and not failed and not ended:
            out.append(os.path.basename(d))
    return out


def series_rows(ls, name='SERIES_V2.tsv'):
    return tsv(os.path.join(ls, name))


def cmd_check_launch(a, cfg, ls):
    rid, task, runf = ids(a.arm, a.run, cfg, ls, a.runf)
    o, stop = cfg['order'], []
    prep = lambda r: os.path.isfile(os.path.join(ls, 'runs_v2', r, 'ops', 'PART_A_DONE_UTC.txt'))
    if o.get('alternate'):
        if a.arm == 'C' and not prep('L%02d' % a.run):
            stop.append('ORDER: C%02d needs L%02d prepared first (%s)' % (a.run, a.run, o['alternate_rule']))
        if a.arm == 'L' and a.run > 1 and (a.run - 1) <= int(cfg.get('n_controls', 5)) and not prep('C%02d' % (a.run - 1)):
            stop.append('ORDER: L%02d needs C%02d prepared first' % (a.run, a.run - 1))
    if o.get('l_waits_prev_l_curated') and a.arm == 'L' and a.run > 1:
        prev = 'L%02d' % (a.run - 1)
        if not any(r.get('kind') == 'RUN' and r.get('run_id') == prev for r in series_rows(ls)):
            stop.append('ORDER: L%02d needs the SERIES_V2 RUN row of %s (curated)' % (a.run, prev))
    jl = cfg['job_limit']
    cur = alarm_marker_current(jl)
    limit = (jl['limit_after_behind'] if a.behind else jl['limit_after']) if cur else jl['limit_before']
    jobs, opn = seat_jobs(jl), open_runs(ls, rid)
    spr = jl['slots_per_run']
    used = max(len(jobs), len(opn) * spr)          # SCOUT jobs now in IN/RUN, or the slots the open runs hold, the larger
    free = limit - used
    print('JOB_LIMIT %d (%s current: %s%s); SCOUT jobs in IN/RUN %d; open runs %d %s (hold %d slots); used %d, free %d, this run needs %d' % (
        limit, jl['marker'], 'yes' if cur else 'no', ', --behind' if a.behind and cur else '',
        len(jobs), len(opn), ','.join(opn) or '-', len(opn) * spr, used, free, spr))
    for j in jobs:
        print('  JOB ' + j)
    if free < spr:
        stop.append('JOB LIMIT: free %d slots of %d, a run needs %d (open runs %d, SCOUT jobs %d)' % (free, limit, spr, len(opn), len(jobs)))
    if os.path.exists(runf):
        stop.append('RUN FOLDER EXISTS %s' % runf)
    for s in stop:
        print('STOP ' + s)
    print('CHECK_LAUNCH %s %s %s' % (rid, task, 'STOP' if stop else 'GO'))
    return 2 if stop else 0


def slots_common(cfg):
    w, y, ss = cfg['windows'], cfg['yardstick_design_sepjan'], cfg['state_split']   # C58: the Sep-Jan yardstick (the pooled Sep-Mar one is in the orchestrator-only yardstick_sepmar_file, C225)
    yu = cfg['yardstick_design_sepjan_up']
    cmd_ok = ss.get('cmd') not in (None, '', 'SET_WHEN_RELEASED') and os.path.isdir(ss['release_dir'])
    st = ('CURRENT at build %s: %s (owner %s)' % (now(), ss['cmd'], ss['owner'])) if cmd_ok else \
         ('NOT CURRENT at build %s (no released Alarm/state_split command; owner %s)' % (now(), ss['owner']))
    return {'{DESIGN_LABEL}': w['design_label'], '{DESIGN_MONTHS}': str(w['design_months']), '{DESIGN_GATE}': w['design_gate'],
            '{DESIGN_INPUT}': w['design_input'], '{DESIGN_BLOCK}': w['design_block'], '{LOOK_NOTE}': w['look_note'],
            '{YARD_NAME}': y['name'], '{YARD_LEAD15}': '+%.2f' % y['lead15'], '{YARD_T15}': '+%.2f' % y['t15'],
            '{YARD_LEAD1H}': '+%.2f' % y['lead1h'], '{YARD_MONTHS_PASS}': str(y['months_pass']), '{YARD_WAVES}': str(y['waves']), '{YARD_MONTHS}': str(y.get('months', 5)), '{YARD_WINDOW}': 'Sep 2025 to Jan 2026 (%s)' % y.get('window', ''),
            '{YARD_T_MIN}': str(y['t_min_better']), '{YARD_RECEIPT}': y['receipt'], '{YARD_SHA16}': y.get('receipt_sha16', 'in receipt'),
            '{SPLIT_STATUS}': st, '{SPLIT_CMD}': ss['cmd'] if cmd_ok else 'NOT CURRENT', '{SPLIT_DIR}': ss['release_dir'],
            '{SPLIT_OWNER}': ss['owner'], '{SPLIT_JOBT}': ss['job_template'], '{SPLIT_JOBT_SHA16}': h(ss['job_template']),
            '{DEF_LAST_DAY}': w.get('def_last_day', ''),
            '{Y15}': '%.2f' % y['lead15'], '{Y1H}': '%.2f' % y['lead1h'], '{YU15}': '%.2f' % yu['lead15'], '{YU1H}': '%.2f' % yu['lead1h'],
            '{JOB_ALLOC}': cfg['job_alloc']['vm']}


def forbidden_numbers(cfg):
    """C58: numbers that pool or are the held-out months (the Sep-Mar yardstick, the Feb-Mar block): never in a hunter prompt"""
    out = set()
    blocks = {k: cfg.get(k) for k in ('yardstick', 'yardstick_heldout_febmar')}
    hf = (cfg.get('yardstick_heldout_file') or {}).get('path')     # C95: the Feb-Mar block lives in an orchestrator-only file
    if hf:
        if not os.path.isfile(hf):
            refuse('HELDOUT_FILE_MISSING', '%s (config yardstick_heldout_file): the held-out scan needs it' % hf)
        blocks['yardstick_heldout_febmar'] = json.load(open(hf, encoding='utf-8')).get('yardstick_heldout_febmar')
    sf = (cfg.get('yardstick_sepmar_file') or {}).get('path')       # C225: the pooled Sep-Mar yardstick lives in an orchestrator-only file
    if sf:
        if not os.path.isfile(sf):
            refuse('SEPMAR_FILE_MISSING', '%s (config yardstick_sepmar_file): the held-out scan needs it' % sf)
        blocks['yardstick'] = json.load(open(sf, encoding='utf-8')).get('yardstick')
    for k in ('yardstick', 'yardstick_heldout_febmar'):
        y = blocks.get(k) or {}
        for f in ('lead15', 'lead1h'):           # leads and waves only: small t values (0.69) also occur in harmless text
            if isinstance(y.get(f), (int, float)): out.add('%.2f' % y[f])
        if isinstance(y.get('waves'), int): out.add('%d waves' % y['waves'])
    return sorted(out)


MASK = '<withheld: pools held-out months>'


def mask_forbidden(text, cfg):
    n = 0
    for x in forbidden_numbers(cfg):
        text, k = re.subn(r'(?<![0-9.])[+-]?' + re.escape(x) + r'(?![0-9])', MASK, text); n += k
    return text, n


def forbidden_scan(text, cfg):
    return [x for x in forbidden_numbers(cfg) if re.search(r'(?<![0-9.])' + re.escape(x) + r'(?![0-9])', text)]


def fill(text, S):
    for k, v in S.items():
        text = text.replace(k, v)
    return text


def cmd_fill(a, cfg, ls):
    t = open(a.file, encoding='utf-8').read()
    t = fill(t, slots_common(cfg))
    left = re.findall(r'(?<!\$)\{[A-Z][A-Z0-9_]*\}', t)
    if left:
        refuse('SLOT', str(sorted(set(left))))
    sys.stdout.write(t)
    return 0


def cmd_env(a, cfg, ls):
    rid, task, runf = ids(a.arm, a.run, cfg, ls, a.runf)
    q = lambda s: "'" + str(s).replace("'", "'\\''") + "'"
    rk = os.environ.get('SERIES_RUN_KEY') or 'SCOUT_' + datetime.now(timezone.utc).strftime('%Y%m%d')  # C27: keep one run key across days
    for k, v in (('RUN_ID', rid), ('TASK', task), ('TASKNUM', task[5:]), ('RUNF', runf), ('RK', rk), ('PACKV', cfg['pack_version']),
                 ('KITPY', cfg['run_kit']), ('LV', cfg['launch_v1']), ('START_RUN', cfg['start_run']), ('SET', cfg['seat_settings']),
                 ('PST', cfg['pipe_settings_template']), ('GATEWIN', cfg['windows']['design_gate'])):
        print('%s=%s' % (k, q(v)))
    return 0


def views_for_L(ls, runf, n):
    """the L hunter's series views (snapshot at build, sha16 in the prompt): V1 curated rows and V2 rows of arm L only"""
    os.makedirs(os.path.join(runf, 'ops'), exist_ok=True)
    cols = ['cid', 'run', 'arm', 'utc', 'item_kind', 'item_ref', 'text', 'verdict', 'reason', 'receipt', 'mistake_key', 'knowledge_kid']
    rows = [dict(r, arm='V1') for r in tsv(os.path.join(ls, 'CURATED_SERIES.tsv'))]
    rows += [r for r in tsv(os.path.join(ls, 'CURATED_SERIES_V2.tsv')) if r.get('arm') == 'L']
    cv = os.path.join(runf, 'ops', 'CURATED_VIEW.tsv')
    with os.fdopen(os.open(cv, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter='\t', extrasaction='ignore', lineterminator='\n'); w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, 'none') for c in cols})
    srows = [r for r in series_rows(ls) if r.get('arm') == 'L' and r.get('kind') == 'RUN']
    hdr = open(os.path.join(ls, 'SERIES_V2.tsv'), encoding='utf-8').readline().rstrip('\n').split('\t')
    sv = os.path.join(runf, 'ops', 'SERIES_VIEW.tsv')
    with os.fdopen(os.open(sv, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=hdr, delimiter='\t', extrasaction='ignore', lineterminator='\n'); w.writeheader()
        for r in srows:
            w.writerow(r)
    return cv, sv


def brief_for_L(ls, runf):
    """arm L only (C17, DOCS-K1): snapshot of knowledge_v1/KNOWLEDGE_BRIEF.md into RUNF/ops (sha16 in the prompt); None when not built yet"""
    src = os.path.join(ls, 'knowledge_v1', 'KNOWLEDGE_BRIEF.md')
    if not os.path.isfile(src):
        return None
    dst = os.path.join(runf, 'ops', 'KNOWLEDGE_BRIEF.md')
    data = open(src, 'rb').read()
    hl = heldout_scan(data.decode('utf-8', 'replace'))
    if hl:
        refuse('HELDOUT', 'knowledge brief: ' + '; '.join(hl)[:600])
    with os.fdopen(os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644), 'wb') as f:
        f.write(data)
    return dst


def earlier_L(ls, n):
    er, ideas = [], []
    for k in range(1, n):
        d = os.path.join(ls, 'runs_v2', 'L%02d' % k)
        res = sorted(glob.glob(os.path.join(d, 'work', 'RESULT_*.md')))
        er.append('L%02d %s' % (k, '%s (%s)' % (res[0], h(res[0])) if res else 'no RESULT file (read its SERIES_VIEW.tsv row and CURATED_VIEW.tsv rows)'))
        for p in sorted(glob.glob(os.path.join(d, 'work', 'INPUT_*_V[0-9]*.json'))):
            m = re.match(r'INPUT_(.+)_V\d+\.json$', os.path.basename(p))
            if m and m.group(1) not in ideas:
                ideas.append(m.group(1))
    return er, ideas


def prompt_adds(ls, n):
    last, order = {}, []
    for src, v2 in (('PROMPT_ADD.tsv', False), ('PROMPT_ADD_V2.tsv', True)):
        for r in tsv(os.path.join(ls, src)):
            k = r.get('add_id')
            if k not in last:
                order.append(k)
            last[k] = dict(r, _v2=v2)
    out = []
    for k in order:
        r = last[k]
        if r.get('status') not in ('ADOPTED', 'ADOPT'):  # C21: curators wrote ADOPT for V2AL05-01, V2AL06-01
            continue
        if r['_v2'] and not (r.get('applies_from_run', '').isdigit() and int(r['applies_from_run']) <= n):
            continue
        out.append(r)
    return out


LEAK = [(r'\bK1-\d+\b', 'knowledge kid'), (r'KNOWLEDGE_SCOUT_V1', 'KNOWLEDGE table'), (r'TRIED_ALARMS_V1', 'tried table path'),
        (r'CURATED_SERIES|CURATED_VIEW|SERIES_VIEW|SERIES_V2\.tsv|/SERIES\.tsv|TRIED_BY\.tsv|UNTESTED\.md|KNOW_PAGE_START|PROMPT_ADD(_V2)?\.tsv|KNOWLEDGE_BRIEF|knowledge_v1', 'series file'),
        (r'\bA\d+-\d\d\b|\bV2A\d+-\d\d\b', 'PROMPT_ADD row id'), (r'runs_v2/L\d\d|learning_series/run_\d', 'earlier run path'),
        (r'\bloop_find\b(?! ?(on|row)\b)', 'loop_find use'), (r'grep TRIED', 'tried table grep')]


NA_ARM = 'not available in this arm (the knowledge page, series files, earlier runs and tried-table reads; the tried table is reached only through the pipeline\'s own copy search, steps 02 and 03)'


def neutralize_brief(br):
    """arm C: the launch_v1 brief word for word except (1) a knowledge kid token becomes 'an earlier row' (the yardstick numbers stay) and
    (2) a line that names the knowledge table, a series file, the tried table, an earlier run path, a PROMPT_ADD id or loop_find keeps
    its leading label and says NA_ARM. Returns the text and the changed line numbers."""
    out, changed = [], []
    for i, line in enumerate(br.split('\n'), 1):
        new = re.sub(r'\bK1-\d+\b', 'an earlier row', line)
        parts = re.split(r'(?<=[.])\s+(?=[A-Z(])', new) if leak_scan(new) else [new]
        if len(parts) > 1:                       # a paragraph: only its leaking sentences go
            new = ' '.join(('(' + NA_ARM + '.)') if leak_scan(s) else s for s in parts)
        if leak_scan(new):
            m = re.match(r'^(\s*(?:#+\s+|[-*]\s+)?(?:\([a-z]\)\s+|\d+\.\s+|[A-Z_]+ = )?)', new)
            new = (m.group(1) if m else '') + NA_ARM
        if new != line:
            changed.append(i)
        out.append(new)
    return '\n'.join(out), changed


HELDOUT_RX = re.compile(r'lead_260[23]|yardstick_heldout_febmar|HANDOFF_FEBMAR|T8_HOLDOUT|hold_lead15\s*[=:]?\s*[+-]?\d|'
                        r'(?i:feb(?:ruary)?[- ](?:to )?mar(?:ch)?(?: 2026)?)[^\n]{0,30}?[+-]\d+\.\d+')


def heldout_scan(text):
    """C24: any held-out (Feb-Mar 2026) marker or number in a prompt or brief refuses the build, both arms"""
    return sorted(set(m.group(0) for m in HELDOUT_RX.finditer(text)))


def leak_scan(text):
    hits = []
    for rx, what in LEAK:
        for m in re.finditer(rx, text):
            hits.append('%s:%s' % (what, m.group(0)))
    return hits


def cmd_build(a, cfg, ls):
    N, T, arm = a.run, a.task, a.arm
    rid, task, runf = ids(arm, N, cfg, ls, a.runf)
    if T != task:
        refuse('BAD_TASK', '%s for arm %s run %d (expected %s)' % (T, arm, N, task))
    if os.path.exists(a.out):
        refuse('OUT_EXISTS', a.out)
    br = open(a.brief, encoding='utf-8').read()
    if not br.startswith('# Brief %s:' % T) or not br.endswith('\n'):
        refuse('BRIEF_TASK', 'the brief does not start with "# Brief %s:"' % T)
    nbr = []
    # C58b: the launch brief stays word for word (the run kit refuses a changed brief: BRIEF_NOT_FROM_PACK_PROMPT); its Sep-Mar yardstick
    # lines come from the released pack prompt (M044, needs a release); the pinned rules page and the launch prompt override them
    if arm == 'C':
        br, nbr = neutralize_brief(br)
        os.makedirs(os.path.join(runf, 'prep'), exist_ok=True)
        cb = os.path.join(runf, 'prep', 'BRIEF_ARM_C.md')
        if os.path.exists(cb):
            if open(cb, encoding='utf-8').read() != br:
                refuse('ARM_C_BRIEF_DIFFERS', cb)
        else:
            with os.fdopen(os.open(cb, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644), 'w', encoding='utf-8') as fh:
                fh.write(br)
    tplp = os.path.join(ls, 'HUNTER_PROMPT_TEMPLATE_V2.md')
    tpl = open(tplp, encoding='utf-8').read()
    i, j = tpl.find(BEGIN), tpl.find(END)
    if i < 0 or j < 0:
        refuse('NO_PART', 'markers')
    part = tpl[i:j + len(END)] + '\n'
    jobt = os.path.join(ls, 'PIPE_MAC_JOB_TEMPLATE_V2.sh')
    jt = open(jobt, encoding='utf-8').read()
    bad = re.findall(r'(?<![\w.-])(rm|rmdir|dd|git|sudo)(?![\w.-])', jt)
    if bad:
        refuse('JOB_WORDS', str(bad))
    os.makedirs(os.path.join(runf, 'ops'), exist_ok=True)
    know = cfg['know']
    tried = FR + '/team/RESEARCH/PROCESS/2_ALARMS/TRIED_ALARMS_V1.tsv'
    if arm == 'C':
        kp = os.path.join(runf, 'ops', 'KNOWLEDGE_EMPTY_V1.tsv')
        hdr = open(know, encoding='utf-8').readline()
        if os.path.exists(kp):
            if open(kp, encoding='utf-8').read() != hdr:
                refuse('EMPTY_KNOW_NOT_EMPTY', kp)
        else:
            with os.fdopen(os.open(kp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644), 'w', encoding='utf-8') as f:
                f.write(hdr)
        krows, adds, er, eideas, kb = 0, [], [], [], None
        A = {'{KNOW_PATH}': kp, '{START_FILES}': 'none for this run',
             '{PROMPT_ADD_BLOCK}': '- none apply to this run',
             '{SERIES_SO_FAR}': 'No earlier runs and no series files are given for this run: write in $RK_WORK/R00_QUESTIONS.md the line "SERIES: none given".',
             '{MISTAKES_LINE}': 'Write in $RK_WORK/R00_QUESTIONS.md a section "Mistakes not to repeat" from the pack pages you read in (a) only, one line each with how you will avoid it, or the line "none given".',
             '{FIND_LINE}': 'The tried table is read only by the pipeline\'s own copy search (steps 02 and 03 of your first Mac job): do not grep it and do not search the process tables by hand.',
             '{STUCK_PRE_SCOPE}': 'what the pack pages and the outside research suggest a first try could miss, and what could make a forced-selling alarm fail',
             '{EXCLUDED_IDEAS}': EXCL, '{EARLIER_IDEAS_LINE}': ''}
    else:
        kp = know
        krows = len(tsv(know))
        cv, sv = views_for_L(ls, runf, N)
        kb = brief_for_L(ls, runf)
        adds = prompt_adds(ls, N)
        er, eideas = earlier_L(ls, N)
        v1ideas = [r['idea'] for r in tsv(os.path.join(ls, 'SERIES.tsv')) if r.get('idea') and r['idea'] not in ('none', '-')]
        blk = '\n'.join('- %s (from run %s, %s): %s [evidence: %s]' % (r['add_id'], r['from_run'], r['kind'], r['text'], r['evidence']) for r in adds) \
            or '- none yet (no adopted row applies to this run)'
        sfiles = ('%s/UNTESTED.md, %s/TRIED_BY.tsv, %s/SERIES.tsv (runs 1 to 7 of V1), %s (%s, the series rows of earlier L runs), %s (%s, every curated item of V1 and of earlier L runs)'
                  % (ls, ls, ls, sv, h(sv), cv, h(cv)))
        sfiles = (('%s (%s, the knowledge brief: read it first; cite its F and Q ids in CLAIMS), ' % (kb, h(kb))) if kb
                  else 'knowledge brief: none built yet, ') + sfiles
        A = {'{KNOW_PATH}': kp, '{START_FILES}': sfiles, '{PROMPT_ADD_BLOCK}': blk,
             '{SERIES_SO_FAR}': ('%s/UNTESTED.md and %s/TRIED_BY.tsv (which untested questions earlier runs took); the series so far: %s/SERIES.tsv, %s and %s, and each earlier L run\'s result: %s.'
                                 % (ls, ls, ls, sv, cv, '; '.join(er) if er else 'none (this is the first L run of the block)')),
             '{MISTAKES_LINE}': 'Write in $RK_WORK/R00_QUESTIONS.md a section "Mistakes not to repeat": every mistake_key of %s (item_kind MISTAKE) with one line how you will avoid it.' % cv,
             '{FIND_LINE}': 'Use row T00-01 (loop_find) on your candidate words and grep TRIED (%s) for them before you pick.' % tried,
             '{STUCK_PRE_SCOPE}': 'what the earlier runs of the series have not tried, which knowledge rows are untested, which mistakes repeat (SERIES FILES above)',
             '{EXCLUDED_IDEAS}': EXCL + (', ' + ', '.join(v1ideas) if v1ideas else ''),
             '{EARLIER_IDEAS_LINE}': 'Every idea of an earlier run is excluded too: %s.' % (', '.join(eideas) if eideas else 'no earlier L run idea yet')}
    S = {'{RUN_ID}': rid, '{TASK}': T, '{UTC}': now(), '{HOME}': H, '{FR}': FR, '{R}': R, '{RUNF}': runf, '{LS}': ls,
         '{KNOW_SHA16}': h(kp), '{KNOW_ROWS}': str(krows), '{IDEA_SUFFIX}': rid,
         '{MAP_SHA16}': h(R + '/Alarm/alarm_pipeline/current/tree/team/RESEARCH/LEAD/MECHANISM_20261106/MECHANISM_MAP_V1.md'),
         '{STUCK_SHA16}': h(R + '/Skills/research-learning-loop/STUCK_CHECK.md'), '{PACK_VERSION}': cfg['pack_version'],
         '{PACK_DIR}': cfg['pack_dir'], '{PACK_START}': cfg['pack_start'], '{PACK_QUESTIONS}': cfg['pack_questions'],
         '{PIPEV}': cfg['pipev'], '{PIPELINE_EDITION}': cfg['pipeline_edition'], '{JOBT}': jobt, '{JOBT_SHA16}': h(jobt),
         '{RUN_KEY}': a.run_key or 'SCOUT_' + datetime.now(timezone.utc).strftime('%Y%m%d')}
    S.update(A); S.update(slots_common(cfg))
    part = fill(fill(part, {'{EARLIER_IDEAS_LINE} ': S['{EARLIER_IDEAS_LINE}'] + ' ' if S['{EARLIER_IDEAS_LINE}'] else ''}), S)
    left = re.findall(r'(?<!\$)\{[A-Z][A-Z0-9_]*\}', part)
    if left:
        refuse('SLOT', str(sorted(set(left))))
    text = br + part
    fb = forbidden_scan(part, cfg)            # C58b: the series part only (the brief is the release's text, word for word)
    if fb:
        refuse('HELDOUT', 'Sep-Mar or Feb-Mar yardstick numbers in the prompt: %s (C58)' % fb)
    if '—' in text or '–' in text:
        refuse('DASH', 'em or en dash')
    sj = open(cfg['state_split']['job_template'], encoding='utf-8').read()
    if re.findall(r'(?<![\w.-])(rm|rmdir|dd|git|sudo)(?![\w.-])', sj):
        refuse('JOB_WORDS', cfg['state_split']['job_template'])
    for k in ('FORECAST_R1.md', 'FORECAST_R2', 'FORECAST_R3', 'FORECASTS.tsv', 'BEFORE the round\'s first Mac job'):
        if k not in part:
            refuse('NO_FORECAST', k)
    w = cfg['windows']
    dl = str(w.get('def_last_day', ''))
    if not re.fullmatch(r'20[0-9]{6}', dl):
        refuse('DEF_LAST_DAY', 'windows.def_last_day %r is not an 8-digit day' % dl)
    if ('"last": "%s"' % dl) not in part:
        refuse('DEF_LAST_DAY', 'the part does not carry the DEF field "last": "%s"' % dl)
    hl = heldout_scan(text)
    if hl:
        refuse('HELDOUT', '; '.join(hl)[:600])
    for k in ('scout_only_look', 'scout_only_never'):
        if w.get(k) and w[k] in part:
            refuse('SCOUT_ONLY_WINDOW', k)
    if arm == 'C':
        lk = leak_scan(part) + ['brief ' + x for x in leak_scan(br)]
        if lk:
            refuse('C_LEAK', '; '.join(sorted(set(lk)))[:600])
    future = (runf + '/work', runf + '/pipe', runf + '/jobs', runf + '/ops/RUN_ENV.sh', runf + '/ops/RUN_PROMPT.md',
              FR + '/team/RESEARCH/ALARM_DESIGN/runs/' + S['{RUN_KEY}'], cfg['state_split']['release_dir'])   # SPLIT is checked by the hunter at run time
    miss = []
    for p in sorted(set(re.findall(re.escape(H) + r'/[^\s,;)`"\'<>]+', part))):
        p = p.rstrip('.:')
        if '$' in p or '*' in p or '<' in p or p.startswith(future):
            continue
        if not os.path.exists(p):
            miss.append(p)
    if miss:
        refuse('PATH', ' '.join(miss))
    scan = a.out + '.part_scan'
    with os.fdopen(os.open(scan, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644), 'w', encoding='utf-8') as f:
        f.write(re.sub(r'orch1_\d{8}', 'orch1_FOLDER', part))
    sc = subprocess.run([sys.executable, '-B', SCAN, '--allow-def-last', dl, scan], capture_output=True, text=True)
    if sc.returncode != 0:
        refuse('CLOSED_MONTH', sc.stdout.strip()[-300:])
    with os.fdopen(os.open(a.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644), 'w', encoding='utf-8') as f:
        f.write(text)
    print('BUILT %s sha16 %s arm %s run %s task %s know %s rows %d prompt_add %d earlier %d brief_lines_neutralized %d template %s config %s split %s kbrief %s' % (
        a.out, h(a.out), arm, rid, T, kp, krows, len(adds), len(er), len(nbr), h(tplp), h(a.config),
        'CURRENT' if S['{SPLIT_CMD}'] != 'NOT CURRENT' else 'NOT_CURRENT', h(kb) if kb else 'none'))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['build', 'fill', 'env', 'check-launch'])
    ap.add_argument('--arm'); ap.add_argument('--run', type=int); ap.add_argument('--task'); ap.add_argument('--brief'); ap.add_argument('--out')
    ap.add_argument('--runf'); ap.add_argument('--file'); ap.add_argument('--run-key')
    ap.add_argument('--ls', default=LSD); ap.add_argument('--config')
    ap.add_argument('--behind', action='store_true'); ap.add_argument('--dry-test', action='store_true')
    a = ap.parse_args()
    a.config = a.config or os.path.join(a.ls, 'SERIES_V2_CONFIG.json')
    cfg = load_cfg(a.config, a.ls, a.dry_test)
    need = {'build': ('arm', 'run', 'task', 'brief', 'out'), 'fill': ('file',), 'env': ('arm', 'run'), 'check-launch': ('arm', 'run')}[a.cmd]
    for k in need:
        if getattr(a, k) is None:
            refuse('USAGE', '--' + k.replace('_', '-') + ' needed for ' + a.cmd)
    return {'build': cmd_build, 'fill': cmd_fill, 'env': cmd_env, 'check-launch': cmd_check_launch}[a.cmd](a, cfg, a.ls)


if __name__ == '__main__':
    sys.exit(main())
