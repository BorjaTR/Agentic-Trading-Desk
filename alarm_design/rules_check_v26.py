#!/usr/bin/env python3
# rules_check_v26.py (SCO-A183, SCOUT 2026-11-07, PLAYGROUND, TEST, NOT REVIEWED, PROVISIONAL): rules_check_v25.py 7bc505f8acc07681 with this head line and the usage name; no rule changed. Its head follows.
# rules_check_v25.py (SCO-A171, SCOUT 2026-11-07, PLAYGROUND, TEST, NOT REVIEWED, PROVISIONAL): rules_check_v24.py 3ec3633c984905f5 with this head line and the usage name; no rule changed. Its head follows.
# rules_check_v24.py (SCO-A169, SCOUT 2026-11-07, PLAYGROUND, TEST, NOT REVIEWED, PROVISIONAL): rules_check_v23.py 0b49570f0cdf89e2 with this head line and the usage name; no rule changed. Its head follows.
# rules_check_v23.py (SCO-A162, SCOUT 2026-11-06, PLAYGROUND, TEST, NOT REVIEWED, PROVISIONAL): rules_check_v22.py 641d71a63e04ea57 with this head line and the usage name; no rule changed. Its head follows.
# rules_check_v22.py (SCO-A163, SCOUT 2026-11-06, PLAYGROUND, TEST, NOT REVIEWED, PROVISIONAL): rules_check_v21.py b97666f9a45ec1d0 with this head line and the usage name; no rule changed. Its head follows.
# rules_check_v21.py (SCO-A160, SCOUT 2026-11-06, PLAYGROUND, TEST, NOT REVIEWED, PROVISIONAL): rules_check_v20.py 289c0ad19f6b9a0e with this head line and the usage name; no rule changed. Its head follows.
# rules_check_v20.py (SCO-A157, SCOUT 2026-11-06, PLAYGROUND, TEST, NOT REVIEWED, PROVISIONAL): rules_check_v19.py 9fce4eab4b6b0c7c with this head line, the usage name and the bridge words mac_desk_v49 / bridge v49 (the released MAC_DESK_V49); no other rule changed. Its head follows.
# rules_check_v19.py (SCO-A154, SCOUT 2026-11-06, PLAYGROUND, TEST, NOT REVIEWED, CANDIDATE): rules_check_v18.py f8e20ea2d90ddc11 with this head line and the usage name only; no rule changed. Its head follows.
# rules_check_v18.py (SCO-A153, SCOUT 2026-11-06, PLAYGROUND tool, TEST, NOT REVIEWED, CANDIDATE): rules_check_v17.py 79a05d9ea3b46df6
# (made by make_v18.py) for the V18 shape: the tools run the process (alarm_pipeline_v1), the agent has six steps. Removed (the steps they
# checked are pipeline steps now, checked by the pipeline's tests t01-t41): SEAL_LABEL, FIRSTLOOK, MECHANISM, UNDERSTAND_CARD, and the
# DRY_WALK line of rule TOOLS. New: AGENT_STEPS (gates steps and close_requires are exactly QUESTIONS, CLAIM, RUN, ANALYZE, CARD_REVIEW,
# PROPOSE), PIPELINE (one "2. RUN:" line naming alarm_pipeline_v1.py with its sha16 and "no hand step"; with --root that sha16 is the
# file's; a "## Pipeline steps" section lists "- P<nn> <NAME>" lines equal to the pipeline's STEPS), HANDOFF (CARD_REVIEW receipt words
# ALARM_CARD_, HANDOFF.json, INDEX.tsv; the "4. CARD_REVIEW:" line names team/RESEARCH/LEAD/ALARM_CARDS/INDEX.tsv).
# Usage: python3 -B rules_check_v18.py <folder> <manifest.tsv> [--root <forensics root>] [--release <volat_release folder>].
# Exit 0 PASS, 1 FAIL, 2 usage. The head of rules_check_v17.py follows.
# rules_check_v17.py (SCO-A147, SCOUT 2026-11-06, PLAYGROUND tool, TEST, NOT REVIEWED, SHADOW, not adopted): rules_check_v16.py
# 8269c0589a1b1f79 (made by make_rules_v17.py) reading the TOOLS table in the PACK_TEMPLATE_V3 columns (row_id, step, tool, status, sha16,
# path, command, output, analysis_rule, next_input; tool = <name> [edition: E; route: R; allow: A]), mapped back to the V16 fields so rule
# TOOLS checks what it checked; rule TIME_LOG names time_log_v4 (str_gap4/a_time_log, 89dc6123dd89d4bc); rule CLOSE_ROUTE also refuses a
# loop_v9.py CLOSE row (FORMAT_V2: it cannot find a START that loop.py wrote); new rule ANALYSIS: every row has an analysis_rule and a
# next_input, next_input names rows of the table or says none: <why>, a NO TOOL rule starts NO TOOL:, NO RULE rows printed as one INFO line.
# Usage: python3 -B rules_check_v17.py <folder> <manifest.tsv> [--root <forensics root>] [--release <volat_release folder>].
# Exit 0 PASS, 1 FAIL, 2 usage. The head of rules_check_v16.py follows.
# rules_check_v16.py (SCO-A137, SCOUT 2026-11-06, PLAYGROUND tool, TEST, NOT REVIEWED, SHADOW, not adopted): rules_check_v15.py
# 9a1bff5081a30242 (made by make_rules_v16.py) plus rule NO_TOOL_REQUIRED (no NO TOOL row on a step close requires or close_if names, nor
# on EVERY, LAUNCH or CLOSE) and rule CLOSE_ROUTE (one loop.py close row and one close_check_v2 row with --ops among the CLOSE rows; no
# loop_v2.py or close_check_v1.py row); UNDERSTAND_CARD now pins alarm_understand_v1 e5fd46f920baae53. The other 11 rules are those of
# rules_check_v15.py. Usage: python3 -B rules_check_v16.py <folder> <manifest.tsv> [--root <forensics root>] [--release <volat_release folder>].
# Exit 0 PASS, 1 FAIL, 2 usage. The head of rules_check_v15.py follows.
# rules_check_v15.py (SCO-A134, SCOUT 2026-11-06, PLAYGROUND tool, TEST, NOT REVIEWED, SHADOW, not adopted): rules_check_v14.py
# 229993642f7b6735 (made by make_rules_v15.py) plus rule TOOLS (the manifest names one TOOLS_V<n>.tsv of role tools with the
# 12 columns; every process step has a row, a NO TOOL row names its owner and "do not build inside a run"; each step block names
# exactly its rows with "Tools (TOOLS_V<n>.tsv): <ids>."; EVERY, LAUNCH and CLOSE rows are named outside the steps; the rule
# "never build a tool inside a run" is a process line; DRY_WALK checks every row and its allow-list; with --root (team/ paths)
# and --release (INSTALL/ and RELEASE/ paths) each row's file has its sha16 and each bridge row is on mac_desk_v48's allow-list)
# and rule UNDERSTAND_CARD (one 12a line between 12 NOVELTY and 13 CLASSIFY, CANDIDATE, never blocking, a description only,
# naming alarm_understand_v1 689f595ddb255d9e and the owner D202611051304_4bb5, with its TOOLS row; not a gates step).
# The 9 rules below are byte equal to rules_check_v14.py. Usage: python3 -B rules_check_v15.py <folder> <manifest.tsv>
# [--root <forensics root>] [--release <volat_release folder>]. Exit 0 PASS, 1 FAIL, 2 usage. Its head follows.
# rules_check_v14.py (SCO-A121, SCOUT 2026-11-06, PLAYGROUND tool, SHADOW, not adopted): rules_check_v13.py 1aead3a037746d7b
# (made by make_rules_v14.py) plus rule MECHANISM: the process file holds exactly one line led by "4b. MECHANISM (CANDIDATE", right
# after the 4a line and before step 5, naming MECHANISM_MAP_V1.md with its sha16 2f1131b39bd554a5, the word NONE, the as-of share at
# GRADE as a description only, and no threshold (no ">=" and no 0.<digits> number on it); MECHANISM is not a gates step.
# The 8 rules below are byte equal to rules_check_v13.py. Its head follows.
# rules_check_v12.py (SCO-A106, SCOUT 2026-11-06, PLAYGROUND tool, SHADOW, not adopted): the pack-own rule checks of ALARM_BUILD,
# role "rules" in its MANIFEST (not a shared template tool). Made by make_rules_v12.py from rules_check_v11.py (db322d51ddf8fda5, SCO-A104):
# only this head, rule_read_once and the usage name changed. rule_read_once accepts the read-once sentence on the step 0 line itself
# (the V10 position) or on a pack-own line led by "Step 0 also:" inside the step 0 block (after the one "0. QUESTIONS:" line, before the
# next numbered step or "## " heading), because PACK_TEMPLATE_V1 keeps step 0 as a shared line; it still fails when the sentence is
# absent from both. The other 7 rule checks are byte equal to rules_check_v11.py (so to route_check_v10.py lines 21 to 134).
# Rules, each printing RULE <name> OK or FAIL RULE <name> <why>: QUESTIONS binding and qids, SLOWDOWNS words, TIME_LOG pin,
# SEAL_LABEL word, READ_ONCE, FIRSTLOOK step, CLOSED_MONTHS only in the holdout guard, NO_EM_DASH. A rule checks the library text,
# never that a task follows it. Routes are not checked here (the shared route tool does that).
# Usage: python3 -B rules_check_v12.py <folder> <manifest.tsv> [--root <forensics root>]   (manifest columns: role, file, sha16;
# with --root the time_log_v3 sha16 named in the files is also checked against the file). Exit 0 PASS, 1 FAIL, 2 usage.
import sys, os, re, hashlib, json
def sha16(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
# ---- V10 rule checks (SCO-A95). Each rule returns a list of failure strings; an empty list is OK. ----
CAUSE_WORDS = ('CODED', 'DATA_COMPUTE', 'DIDNT_KNOW_METRIC', 'DIDNT_KNOW_TOOL', 'TOOL_REFUSED_OR_BROKE', 'VM_LIMITS', 'DOC_READING', 'REWORK', 'WAITING')
TIME_LOG = 'team/SCOUT/loop_day_20261105/str_gap4/a_time_log/time_log_v4.py'   # V17: was team/SCOUT/tools/time_log_v3/time_log_v3.py
MON = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
MONL = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
def _by_role(man, role, r):
    fs = [f for f in man if role.get(f) == r]
    return fs[0] if len(fs) == 1 else None
def _text(D, f):
    if not f: return None
    try: return open(os.path.join(D, f), encoding='utf-8').read()
    except (OSError, UnicodeError): return None
def _gates(D, man, role):
    t = _text(D, _by_role(man, role, 'gates'))
    if t is None: return None, 'no single readable gates file in the manifest'
    try: return json.loads(t), None
    except ValueError as e: return None, 'gates file does not parse: %s' % e
def rule_questions(D, man, role, root):
    g, err = _gates(D, man, role)
    if err: return [err]
    spec = g.get('questions') or {}; q = spec.get('file', '')
    if not re.fullmatch(r'QUESTIONS_V[0-9]+\.md', q) or q not in man: return ['gates questions file %r is not a manifest QUESTIONS_V<n>.md' % q]
    try: data = open(os.path.join(D, q), 'rb').read()
    except OSError: return ['questions file %s missing' % q]
    out = []
    if hashlib.sha256(data).hexdigest() != spec.get('sha256'): out.append('%s sha256 differs from the gates binding' % q)
    t = data.decode('utf-8', 'replace'); ids = re.findall(r'^## (Q[0-9]+)\b', t, re.M)
    if not ids or len(ids) != len(set(ids)): out.append('qids missing or duplicated (%d headings, %d distinct)' % (len(ids), len(set(ids))))
    blocks = re.split(r'^## (Q[0-9]+)\b', t, flags=re.M)
    for i in range(1, len(blocks), 2):
        m = re.search(r'```json\n(.*?)\n```', blocks[i + 1], re.S)
        if not m: out.append('%s has no json block' % blocks[i]); continue
        try: d = json.loads(m.group(1))
        except ValueError: out.append('%s json block does not parse' % blocks[i]); continue
        if d.get('qid') != blocks[i]: out.append('%s heading differs from its json qid %r' % (blocks[i], d.get('qid')))
    mm = re.search(r'\b(\d+) qids\b', _text(D, _by_role(man, role, 'start')) or '')
    if not mm or int(mm.group(1)) != len(ids): out.append('the start file names %s qids, the questions file has %d' % (mm.group(1) if mm else 'no', len(ids)))
    return out
def _has_line(t, words):
    for l in (t or '').split('\n'):
        if all(re.search(r'(?<![A-Za-z0-9_])' + re.escape(w) + r'(?![A-Za-z0-9_])', l) for w in words): return True
    return False
def rule_slowdowns(D, man, role, root):
    out = []
    for r in ('prompt', 'start'):
        f = _by_role(man, role, r); t = _text(D, f)
        if t is None: out.append('no readable %s file' % r); continue
        if not _has_line(t, ('slowdowns', 'minutes', 'evidence', 'tool to release', 'required') + CAUSE_WORDS):
            out.append('%s has no one line requiring slowdowns with minutes, evidence, the tool to release and the nine cause words' % f)
    return out
def rule_time_log(D, man, role, root):
    out = []; pat = re.compile(re.escape(TIME_LOG) + r' \(([0-9a-f]{16})\)')
    for r in ('process', 'prompt', 'start'):
        f = _by_role(man, role, r); hs = set(pat.findall(_text(D, f) or ''))
        if not hs: out.append('%s does not name %s with its sha16' % (f, TIME_LOG)); continue
        if len(hs) != 1: out.append('%s names %s with %d different sha16' % (f, TIME_LOG, len(hs))); continue
        if root:
            p = os.path.join(root, TIME_LOG)
            if not os.path.isfile(p): out.append('%s missing under --root' % TIME_LOG)
            elif sha16(p) not in hs: out.append('%s is %s, %s names %s' % (TIME_LOG, sha16(p), f, ''.join(hs)))
    return out
def rule_seal(D, man, role, root):
    g, err = _gates(D, man, role)
    if err: return [err]
    out = []; seal = [s for s in g.get('steps', []) if s.get('id') == 'SEAL']
    if len(seal) != 1 or 'card_true_label' not in (seal[0].get('receipt_must_contain') or []): out.append('gates SEAL step lacks the receipt word card_true_label')
    t = _text(D, _by_role(man, role, 'process'))
    if not [l for l in (t or '').split('\n') if l.startswith('8. SEAL:') and 'card_true_label' in l and 'before the VARIANTS row' in l and 'count of 0 stops the seal' in l]:
        out.append('process step 8 SEAL does not seal card_true_label before the VARIANTS row with a stop on count 0')
    return out
def rule_read_once(D, man, role, root):
    out = []; t = _text(D, _by_role(man, role, 'process'))
    ls = (t or '').split('\n'); words = lambda l: 'READ_ONCE.tsv' in l and 'Read each source once' in l
    ok = bool([l for l in ls if l.startswith('0. QUESTIONS:') and words(l)])
    s0 = [i for i, l in enumerate(ls) if l.startswith('0. QUESTIONS:')]
    if not ok and len(s0) == 1:
        j = s0[0] + 1
        while j < len(ls) and not re.match(r'[0-9]+[a-z]?\. ', ls[j]) and not ls[j].startswith('## '):
            if ls[j].startswith('Step 0 also:') and words(ls[j]): ok = True
            j += 1
    if not ok: out.append('process step 0 does not log each source read once in READ_ONCE.tsv')
    if 'READ_ONCE.tsv' not in (_text(D, _by_role(man, role, 'prompt')) or ''): out.append('prompt does not name READ_ONCE.tsv')
    return out
def rule_firstlook(D, man, role, root):
    g, err = _gates(D, man, role)
    if err: return [err]
    out = []
    if any(s.get('id') == 'FIRSTLOOK' for s in g.get('steps', [])): out.append('FIRSTLOOK is a gates step; it stays CANDIDATE, not gated')
    t = _text(D, _by_role(man, role, 'process')) or ''
    ls = [l for l in t.split('\n') if l.startswith('11a. FIRSTLOOK (CANDIDATE')]
    if len(ls) != 1 or 'after DECIDE' not in ls[0] or 'NEEDS MORE MONTHS' not in ls[0] or 'never SIZE from Sep-Dec alone' not in ls[0]: out.append('process has no single step 11a FIRSTLOOK (CANDIDATE) after DECIDE that keeps Sep-Dec at NEEDS MORE MONTHS')
    else:
        lines = t.split('\n'); i = lines.index(ls[0])
        if not (lines[i - 1].startswith('11. DECIDE') and lines[i + 1].startswith('12. NOVELTY')): out.append('step 11a is not between steps 11 and 12')
    return out
def _closed_tokens(g):
    toks = set()
    for h in g.get('holdout', []):
        a, b = h['window'].split(':'); y, m = int(a[:4]), int(a[5:7]); y2, m2 = int(b[:4]), int(b[5:7])
        while (y, m) <= (y2, m2):
            toks |= {'%04d-%02d' % (y, m), '%04d%02d' % (y, m), '%s %04d' % (MON[m - 1], y), '%s %04d' % (MONL[m - 1], y), '%02d%02d' % (y % 100, m)}
            m += 1
            if m == 13: y, m = y + 1, 1
    return toks
def rule_closed_months(D, man, role, root):
    g, err = _gates(D, man, role)
    if err: return [err]
    out = []; toks = sorted(_closed_tokens(g)); gf = _by_role(man, role, 'gates')
    if not toks: return ['gates has no holdout guard']
    for f in man:
        if role.get(f) == 'carried_table': continue
        t = _text(D, f) or ''
        if f == gf:
            g2 = dict(g); g2.pop('holdout', None); t = json.dumps(g2)
        for k in toks:
            if re.search(r'(?<![0-9A-Za-z])' + re.escape(k) + r'(?![0-9A-Za-z])', t): out.append('%s names a closed month outside the holdout guard' % f); break
    return out
def rule_no_em_dash(D, man, role, root):
    return ['%s has an em dash' % f for f in man if chr(0x2014) in (_text(D, f) or '')]
MAP_NAME, MAP_SHA = 'MECHANISM_MAP_V1.md', '2f1131b39bd554a5'
def rule_mechanism(D, man, role, root):
    g, err = _gates(D, man, role)
    if err: return [err]
    out = []
    if any(s.get('id') == 'MECHANISM' for s in g.get('steps', []) if isinstance(s, dict)): out.append('MECHANISM is a gates step; it stays CANDIDATE, not gated')
    t = _text(D, _by_role(man, role, 'process')) or ''
    lines = t.split('\n'); ls = [i for i, l in enumerate(lines) if l.startswith('4b. MECHANISM (CANDIDATE')]
    if len(ls) != 1: return out + ['process has %d lines led by "4b. MECHANISM (CANDIDATE", expected 1' % len(ls)]
    i = ls[0]; l = lines[i]
    for w in (MAP_NAME, MAP_SHA, 'NONE', 'at CLAIM', 'at GRADE', 'as-of share', 'description only', 'no threshold'):
        if w not in l: out.append('the 4b MECHANISM line does not name %r' % w)
    if '>=' in l or re.search(r'(?<![0-9A-Za-z.])0\.[0-9]+', l): out.append('the 4b MECHANISM line holds a threshold')
    if not (i > 0 and lines[i - 1].startswith('4a. ') and i + 1 < len(lines) and lines[i + 1].startswith('5. DEFINE')): out.append('step 4b is not between steps 4a and 5')
    return out
# ---- V15 rules (SCO-A134, brief team/SCOUT/loop_day_20261105/briefs/SCO-A134_ALARM_BUILD_V15_TOOLS.md f75e0e41ed7dd13a) ----
RELEASE = None   # set by main from --release <the volat_release folder>; INSTALL rows resolve under it by the START pin
TOOLS_HDR = ['row', 'step', 'name', 'status', 'edition', 'sha16', 'path', 'command', 'route', 'allow', 'receipt', 'note']
TOOLS_STATUS = ('RELEASED', 'PLAYGROUND, TEST NOT REVIEWED', 'KIT COMMAND', 'NO TOOL')
TOOLS_ROUTES = ('own shell', 'parent shell', 'bridge v49 rel', 'bridge v49 reldry', 'bridge v49 relwait', 'bridge v49 kitq', 'bridge v49 opdone', 'none admitted', '-')
TOOLS_OUTSIDE = {'EVERY': 'EV', 'LAUNCH': 'LA', 'CLOSE': 'CL'}
TOOLS_PTR = re.compile(r'Tools \((TOOLS_V[0-9]+\.tsv)\): ([A-Za-z0-9, -]+?)\.(?=\s|$)')
TOOLS_ID = re.compile(r'^T([0-9]{2}[a-z]?|EV|LA|CL)-[0-9]{2}$')
def _step_code(s):
    if s in TOOLS_OUTSIDE: return TOOLS_OUTSIDE[s]
    m = re.match(r'^([0-9]+)([a-z]?)$', s)
    return ('%02d%s' % (int(m.group(1)), m.group(2))) if m else None
def _steps_blocks(t):
    # numbered step lines "N. " or "Na. " under "## Steps"; a block runs to the next numbered line or "## " heading
    ls = t.split('\n'); sec = False; blocks = []; cur = None
    for i, l in enumerate(ls):
        if l.startswith('## '):
            sec = (l.strip() == '## Steps'); cur = None; continue
        m = re.match(r'^([0-9]+[a-z]?)\. ', l) if sec else None
        if m: cur = [m.group(1), i, [l]]; blocks.append(cur)
        elif cur is not None: cur[2].append(l)
    return ls, blocks
# V17 (SCO-A147): the PACK_TEMPLATE_V3 columns; each row mapped back to the V16 fields (row, name, edition, route, allow, receipt, note)
TOOLS_V17_HDR = ['row_id', 'step', 'tool', 'status', 'sha16', 'path', 'command', 'output', 'analysis_rule', 'next_input']
TOOLCELL = re.compile(r'^(.*) \[edition: (.*?); route: (.*?); allow: (.*?)\]$')
def _tools_rows(D, f):
    t = _text(D, f)
    if t is None: return None, ['tools file %s missing or unreadable' % f]
    rows, out, hdr = [], [], None
    for n, l in enumerate(t.split('\n'), 1):
        if not l.strip() or l.startswith('#'): continue
        if hdr is None:
            hdr = l.split('\t')
            if hdr != TOOLS_V17_HDR: out.append('%s header is not the %d PACK_TEMPLATE_V3 columns %s' % (f, len(TOOLS_V17_HDR), ' '.join(TOOLS_V17_HDR)))
            continue
        r = l.split('\t')
        if len(r) != len(TOOLS_V17_HDR): out.append('%s line %d has %d fields, not %d' % (f, n, len(r), len(TOOLS_V17_HDR))); continue
        d = dict(zip(TOOLS_V17_HDR, r), line=n); m = TOOLCELL.match(d['tool'])
        if not m: out.append('%s line %d tool cell is not <name> [edition: E; route: R; allow: A]' % (f, n)); continue
        d.update(row=d['row_id'], name=m.group(1), edition=m.group(2), route=m.group(3), allow=m.group(4), receipt=d['output'], note=d['analysis_rule'])
        rows.append(d)
    if hdr is None: out.append('%s has no header' % f)
    return rows, out
def _install_rel(D, man, role):
    m = re.search(r'INSTALL = \S*/volat_release/(\S+?) \(pinned\)', _text(D, _by_role(man, role, 'start')) or '')
    return m.group(1) if m else None
def _resolve(path, root, irel):
    if path.startswith('team/'): return os.path.join(root, path) if root else None
    if path.startswith('INSTALL/'): return os.path.join(RELEASE, irel, path[len('INSTALL/'):]) if (RELEASE and irel) else None
    if path.startswith('RELEASE/'): return os.path.join(RELEASE, path[len('RELEASE/'):]) if RELEASE else None
    return None
def rule_tools(D, man, role, root):
    tf = [f for f in man if role.get(f) == 'tools']
    if len(tf) != 1: return ['the manifest has %d rows of role tools, expected 1 (TOOLS_V<n>.tsv)' % len(tf)]
    tf = tf[0]
    if not re.fullmatch(r'TOOLS_V[0-9]+\.tsv', tf): return ['the tools file %s is not named TOOLS_V<n>.tsv' % tf]
    rows, out = _tools_rows(D, tf)
    if rows is None: return out
    pt = _text(D, _by_role(man, role, 'process')) or ''
    ls, blocks = _steps_blocks(pt); psteps = [b[0] for b in blocks]
    ids = {}
    for r in rows:
        rid, st = r['row'], r['step']; w = '%s row %s' % (tf, rid)
        if rid in ids: out.append('%s: duplicate row id' % w); continue
        ids[rid] = r
        m = TOOLS_ID.match(rid)
        if st not in psteps and st not in TOOLS_OUTSIDE: out.append('%s: step %r is not a process step nor one of %s' % (w, st, ', '.join(TOOLS_OUTSIDE)))
        elif not m or m.group(1) != _step_code(st): out.append('%s: id does not carry its step %s (T%s-nn)' % (w, st, _step_code(st)))
        s = r['status']
        if s not in TOOLS_STATUS: out.append('%s: status %r is not one of %s' % (w, s, ' | '.join(TOOLS_STATUS))); continue
        if s == 'NO TOOL':
            if not r['name'].startswith('NO TOOL: '): out.append('%s: a NO TOOL row names what is missing as "NO TOOL: <what>"' % w)
            if 'do not build inside a run' not in r['note'] or 'owner' not in r['note']: out.append('%s: a NO TOOL row note names the owner and "do not build inside a run"' % w)
            if r['sha16'] != '-' or r['path'] != '-' or r['route'] != '-' or r['edition'] != '-': out.append('%s: a NO TOOL row has edition, sha16, path and route "-"' % w)
            continue
        if s == 'RELEASED' and r['edition'] in ('', '-'): out.append('%s: a RELEASED row names its edition' % w)
        if not re.fullmatch(r'[0-9a-f]{16}', r['sha16']): out.append('%s: sha16 %r is not 16 hex' % (w, r['sha16']))
        if not re.match(r'^(INSTALL|RELEASE)/|^team/', r['path']): out.append('%s: path %r is not INSTALL/, RELEASE/ or team/' % (w, r['path']))
        rt, al = r['route'], r['allow']
        if rt not in TOOLS_ROUTES or rt == '-': out.append('%s: route %r is not one of %s' % (w, rt, ' | '.join(TOOLS_ROUTES[:-1]))); continue
        need = {'bridge v49 rel': r'rel [a-z0-9_]+', 'bridge v49 reldry': r'rel [a-z0-9_]+', 'bridge v49 kitq': r'kitq [A-Z]+', 'bridge v49 relwait': r'relwait', 'bridge v49 opdone': r'opdone'}.get(rt, r'-')
        if not re.fullmatch(need, al): out.append('%s: allow %r does not fit route %s (%s)' % (w, al, rt, need))
    for st in psteps:
        if not [r for r in rows if r['step'] == st]: out.append('process step %s has no TOOLS row (write a NO TOOL row)' % st)
    named = {}
    for bi, (st, i, bl) in enumerate(blocks):
        got = [m for l in bl for m in TOOLS_PTR.finditer(l)]
        if len(got) != 1: out.append('process step %s block has %d "Tools (TOOLS_V<n>.tsv): <ids>." pointers, expected 1' % (st, len(got))); continue
        f, idl = got[0].group(1), [x.strip() for x in got[0].group(2).split(',')]
        if f != tf: out.append('process step %s points to %s, the manifest tools file is %s' % (st, f, tf))
        for x in idl:
            named[x] = named.get(x, 0) + 1
            if x not in ids: out.append('process step %s names %s, not a row of %s' % (st, x, tf))
            elif ids[x]['step'] != st: out.append('process step %s names %s, a row of step %s' % (st, x, ids[x]['step']))
        miss = sorted(rid for rid, r in ids.items() if r['step'] == st and rid not in idl)
        if miss: out.append('process step %s does not name its rows %s' % (st, ' '.join(miss)))
    blines = set(i2 for b in blocks for i2 in range(b[1], b[1] + len(b[2])))
    for i, l in enumerate(ls):
        if i in blines: continue
        for m in TOOLS_PTR.finditer(l):
            if m.group(1) != tf: out.append('process line %d points to %s, the manifest tools file is %s' % (i + 1, m.group(1), tf))
            for x in [y.strip() for y in m.group(2).split(',')]:
                named[x] = named.get(x, 0) + 1
                if x not in ids: out.append('process line %d names %s, not a row of %s' % (i + 1, x, tf))
                elif ids[x]['step'] not in TOOLS_OUTSIDE: out.append('process line %d (outside the steps) names %s, a row of step %s' % (i + 1, x, ids[x]['step']))
    for rid, r in ids.items():
        if r['step'] in TOOLS_OUTSIDE and rid not in named: out.append('row %s (%s) is named by no process line' % (rid, r['step']))
    for b in blocks:
        for m in (m for l in b[2] for m in TOOLS_PTR.finditer(l)):
            for x in [y.strip() for y in m.group(2).split(',')]:
                if x in ids and ids[x]['step'] in TOOLS_OUTSIDE: out.append('process step %s names %s, a row of %s (name it outside the steps)' % (b[0], x, ids[x]['step']))
    if not [l for l in ls if 'never build a tool inside a run' in l and 'NO TOOL' in l and 'TOOLS_V' in l]: out.append('process has no line with the rule "never build a tool inside a run" and NO TOOL')
    if root:
        irel = _install_rel(D, man, role)
        for rid, r in ids.items():
            if r['status'] == 'NO TOOL': continue
            p = _resolve(r['path'], root, irel)
            if p is None: continue
            if not os.path.isfile(p): out.append('row %s path %s missing' % (rid, r['path']))
            elif sha16(p) != r['sha16']: out.append('row %s path %s is sha16 %s, the row says %s' % (rid, r['path'], sha16(p), r['sha16']))
        br = [r for r in ids.values() if r['route'].startswith('bridge v49')]
        bs = [r for r in ids.values() if r['name'] == 'mac_desk_v49']
        if br and len(bs) != 1: out.append('%d bridge rows and %d rows named mac_desk_v49 (expected 1)' % (len(br), len(bs)))
        elif br:
            bp = _resolve(bs[0]['path'], root, irel); bt = _text('', bp) if bp and os.path.isfile(bp) else None
            if bt is None: out.append('bridge file %s not readable under --root' % bs[0]['path'])
            else:
                km = re.search(r'^KIT_KINDS = \(([^)]*)\)', bt, re.M); kinds = re.findall(r"'([A-Z]+)'", km.group(1)) if km else []
                for r in br:
                    sub = r['route'].split()[-1]
                    if ("a[:1] == ['%s']" % sub) not in bt: out.append('row %s: bridge subcommand %s is not on the allow-list of %s' % (r['row'], sub, bs[0]['path']))
                    a2 = r['allow'].split()
                    if a2[0] == 'rel' and len(a2) == 2 and ("    '%s': {'script'" % a2[1]) not in bt: out.append('row %s: rel tool %s is not on the allow-list of %s' % (r['row'], a2[1], bs[0]['path']))
                    if a2[0] == 'kitq' and len(a2) == 2 and a2[1] not in kinds: out.append('row %s: kitq kind %s is not on the allow-list (KIT_KINDS) of %s' % (r['row'], a2[1], bs[0]['path']))
    return out
AU_NAME, AU_SHA, AU_OWNER = 'alarm_understand_v1', 'e5fd46f920baae53', 'D202611051304_4bb5'   # V16: was 689f595ddb255d9e
def rule_understand_card(D, man, role, root):
    g, err = _gates(D, man, role)
    if err: return [err]
    out = []
    if any('UNDERSTAND' in str(s.get('id', '')) for s in g.get('steps', []) if isinstance(s, dict)): out.append('UNDERSTAND is a gates step; step 12a stays CANDIDATE, never blocking')
    lines = (_text(D, _by_role(man, role, 'process')) or '').split('\n')
    ls = [i for i, l in enumerate(lines) if l.startswith('12a. UNDERSTAND CARD (CANDIDATE')]
    if len(ls) != 1: return out + ['process has %d lines led by "12a. UNDERSTAND CARD (CANDIDATE", expected 1' % len(ls)]
    i = ls[0]; l = lines[i]
    for w in (AU_NAME, AU_SHA, AU_OWNER, 'mandatory=false', 'never blocking', 'description only'):
        if w not in l: out.append('the 12a UNDERSTAND CARD line does not name %r' % w)
    if not (i > 0 and lines[i - 1].startswith('12. NOVELTY') and i + 1 < len(lines) and lines[i + 1].startswith('13. CLASSIFY')): out.append('step 12a is not between steps 12 NOVELTY and 13 CLASSIFY')
    tf = [f for f in man if role.get(f) == 'tools']
    rows = _tools_rows(D, tf[0])[0] if len(tf) == 1 else None
    if not rows or not [r for r in rows if r['step'] == '12a' and r['name'] == AU_NAME and r['sha16'] == AU_SHA]: out.append('the TOOLS file has no step 12a row %s %s' % (AU_NAME, AU_SHA))
    return out
# ---- V16 rules (SCO-A137, brief team/SCOUT/loop_day_20261105/briefs/SCO-A137_V16_FIX_GAPS.md 6586bc82e5031556) ----
def _tools_of(D, man, role):
    tf = [f for f in man if role.get(f) == 'tools']
    if len(tf) != 1: return None, ['the manifest has %d rows of role tools, expected 1' % len(tf)]
    return _tools_rows(D, tf[0])
def rule_no_tool_required(D, man, role, root):
    # GV15-01, GV15-06: a NO TOOL row stops its step (PROCESS rule line), so none may sit on a step close requires or close_if names,
    # nor on EVERY, LAUNCH or CLOSE; a CANDIDATE step (not a gates step) may keep one (it writes UNANSWERED)
    g, err = _gates(D, man, role)
    if err: return [err]
    rows, out = _tools_of(D, man, role)
    if rows is None: return out
    req = set(g.get('close_requires', [])) | set(c.get('then') for c in g.get('close_if', []) if isinstance(c, dict))
    ls, blocks = _steps_blocks(_text(D, _by_role(man, role, 'process')) or '')
    name = {}
    for st, i, bl in blocks:
        m = re.match(r'^[0-9]+[a-z]?\. ([A-Z][A-Z0-9_]*)', bl[0]); name[st] = m.group(1) if m else None
    out = []
    for r in rows:
        if r['status'] != 'NO TOOL': continue
        if r['step'] in TOOLS_OUTSIDE: out.append('row %s is NO TOOL on %s: every run needs it' % (r['row'], r['step']))
        elif name.get(r['step']) in req: out.append('row %s is NO TOOL on step %s %s, which close requires (close_requires or close_if): a run cannot pass it' % (r['row'], r['step'], name.get(r['step'])))
    return out
def rule_close_route(D, man, role, root):
    # GV15-02: one admissible close, the tools trials E, F, H and I ran: loop.py close and close_check_v2 with the typed ledger
    rows, out = _tools_of(D, man, role)
    if rows is None: return out
    cl = [r for r in rows if r['step'] == 'CLOSE']; out = []
    for r in cl:
        if re.search(r'(^|/)(loop_v2|loop_v9|close_check_v1)\.py$', r['path']): out.append('row %s names %s: not the close route trials could run (V16, V17: loop.py close, close_check_v2; loop_v9 reads FORMAT_V2 and finds no loop.py START)' % (r['row'], r['path']))
    lp = [r for r in cl if r['path'].endswith('/loop.py') and ' close ' in r['command']]
    cc = [r for r in cl if r['path'].endswith('/close_check_v2.py')]
    if len(lp) != 1: out.append('%d CLOSE rows run loop.py close, expected 1' % len(lp))
    if len(cc) != 1: out.append('%d CLOSE rows run close_check_v2, expected 1' % len(cc))
    elif '--ops ' not in cc[0]['command']: out.append('row %s close_check_v2 has no --ops (the typed ledger)' % cc[0]['row'])
    return out
# ---- V17 rule (SCO-A147): tool -> output -> analysis -> next tool, every row ----
NEXT_ID = re.compile(r'\bT(?:[0-9]{2}[a-z]?|EV|LA|CL)-[0-9]{2}\b')
def rule_analysis(D, man, role, root):
    rows, out = _tools_of(D, man, role)
    if rows is None: return out
    out = list(out); ids = set(r['row'] for r in rows); nr = []
    for r in rows:
        a, ni, w = r['analysis_rule'].strip(), r['next_input'].strip(), 'row %s' % r['row']
        rule = re.split(r'(?:^|\s)V16 note: ', a, 1)[0].strip()
        if not rule: out.append('%s has no analysis_rule' % w)
        if r['status'] == 'NO TOOL' and not rule.startswith('NO TOOL: '): out.append('%s is NO TOOL: its analysis_rule does not start NO TOOL: (the owner and what to report)' % w)
        if 'NO RULE:' in rule: nr.append(r['row'])
        if not ni: out.append('%s has no next_input' % w); continue
        named = NEXT_ID.findall(ni)
        if ni.startswith('none: '):
            if len(ni) < 12: out.append('%s next_input none: gives no why' % w)
        elif not named: out.append('%s next_input names no row id and is not none: <why>' % w)
        for x in named:
            if x not in ids: out.append('%s next_input names %s, not a row of the table' % (w, x))
    print('INFO RULE ANALYSIS rows %d; NO RULE rows %d: %s' % (len(rows), len(nr), ' '.join(nr) or 'none'))
    return out
# ---- V18 rules (SCO-A153) ----
AGENT = ['QUESTIONS', 'CLAIM', 'RUN', 'ANALYZE', 'CARD_REVIEW', 'PROPOSE']
PIPE_REL = 'team/SCOUT/pack_kit/alarm_pipeline_v1/alarm_pipeline_v1.py'
def rule_agent_steps(D, man, role, root):
    g, err = _gates(D, man, role)
    if err: return [err]
    out = []; ids = [s.get('id') for s in g.get('steps', []) if isinstance(s, dict)]
    if ids != AGENT: out.append('gates steps are %s, not the six agent steps %s' % (','.join(map(str, ids)), ','.join(AGENT)))
    if list(g.get('close_requires', [])) != AGENT: out.append('close_requires is %s, not the six agent steps' % g.get('close_requires'))
    return out
def rule_pipeline(D, man, role, root):
    t = _text(D, _by_role(man, role, 'process')) or ''; ls = t.split('\n'); out = []
    run = [l for l in ls if l.startswith('2. RUN:')]
    if len(run) != 1: return ['process has %d "2. RUN:" lines, expected 1' % len(run)]
    m = re.search(r'alarm_pipeline_v1\.py \(([0-9a-f]{16})\)', run[0])
    if not m: out.append('the 2. RUN line does not name alarm_pipeline_v1.py (<sha16>)')
    if 'no hand step' not in run[0]: out.append('the 2. RUN line does not say no hand step')
    sec = False; got = []
    for l in ls:
        if l.startswith('## '): sec = (l.strip() == '## Pipeline steps'); continue
        mm = re.match(r'^- P([0-9]{2}) ([A-Z_]+)\b', l) if sec else None
        if mm: got.append((int(mm.group(1)), mm.group(2)))
    want = None
    if root and os.path.isfile(os.path.join(root, PIPE_REL)):
        pt = open(os.path.join(root, PIPE_REL), encoding='utf-8').read()
        if m and sha16(os.path.join(root, PIPE_REL)) != m.group(1): out.append('the 2. RUN line names %s, %s is %s' % (m.group(1), PIPE_REL, sha16(os.path.join(root, PIPE_REL))))
        sm = re.search(r'^STEPS = \[(.*?)\]$', pt, re.M | re.S)
        want = [(int(a), b) for a, b in re.findall(r"\(([0-9]+), '([A-Z_]+)'", sm.group(1))] if sm else None
    elif root: out.append('%s missing under --root' % PIPE_REL)
    if want is None: want = [(i, x) for i, x in got] if len(got) == 22 else [(0, 'TWENTY_TWO_STEPS')]
    if got != want: out.append('the "## Pipeline steps" lines %s are not the pipeline STEPS %s' % (got, want))
    return out
def rule_handoff(D, man, role, root):
    g, err = _gates(D, man, role)
    if err: return [err]
    out = []; cr = [s for s in g.get('steps', []) if isinstance(s, dict) and s.get('id') == 'CARD_REVIEW']
    words = cr[0].get('receipt_must_contain', []) if len(cr) == 1 else []
    for w in ('ALARM_CARD_', 'HANDOFF.json', 'INDEX.tsv'):
        if w not in words: out.append('gates CARD_REVIEW receipt_must_contain lacks %s' % w)
    t = _text(D, _by_role(man, role, 'process')) or ''
    if not [l for l in t.split('\n') if l.startswith('4. CARD_REVIEW:') and 'team/RESEARCH/LEAD/ALARM_CARDS/INDEX.tsv' in l]: out.append('the 4. CARD_REVIEW line does not name team/RESEARCH/LEAD/ALARM_CARDS/INDEX.tsv')
    return out
RULES = [('QUESTIONS', rule_questions), ('SLOWDOWNS', rule_slowdowns), ('TIME_LOG', rule_time_log),
         ('READ_ONCE', rule_read_once), ('CLOSED_MONTHS', rule_closed_months), ('NO_EM_DASH', rule_no_em_dash),
         ('TOOLS', rule_tools), ('NO_TOOL_REQUIRED', rule_no_tool_required), ('CLOSE_ROUTE', rule_close_route), ('ANALYSIS', rule_analysis),
         ('AGENT_STEPS', rule_agent_steps), ('PIPELINE', rule_pipeline), ('HANDOFF', rule_handoff)]
def main(a):
    global RELEASE
    root = None; rest = list(a[3:]); a = a[:3]
    while len(rest) >= 2 and rest[0] in ('--root', '--release'):
        if rest[0] == '--root': root = rest[1]
        else: RELEASE = rest[1]
        rest = rest[2:]
    if len(a) != 3 or rest: print('usage: rules_check_v26.py <folder> <manifest.tsv> [--root <forensics root>] [--release <volat_release folder>]'); return 2
    D, M = a[1], a[2]
    if not os.path.isdir(D) or not os.path.isfile(M): print('usage: missing folder or manifest'); return 2
    rows = [l.split('\t') for l in open(M, encoding='utf-8').read().splitlines() if l and not l.startswith('#')]
    if rows and rows[0][:3] == ['role', 'file', 'sha16']: rows = rows[1:]
    man = {}; role = {}
    for r in rows:
        man[r[1]] = r[2]; role[r[1]] = r[0]
    rule_fails = 0
    for name, fn in RULES:
        got = fn(D, man, role, root)
        for w in got: print('FAIL RULE %s %s' % (name, w))
        if not got: print('RULE %s OK' % name)
        rule_fails += len(got)
    print('SUMMARY rules %d rule_fails %d -> %s' % (len(RULES), rule_fails, 'PASS' if rule_fails == 0 else 'FAIL'))
    return 0 if rule_fails == 0 else 1
if __name__ == '__main__': sys.exit(main(sys.argv))
