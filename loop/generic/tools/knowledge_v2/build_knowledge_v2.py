#!/usr/bin/env python3
"""build_knowledge_v2.py - generic knowledge store of a learning loop; every seat-only setting comes from a pack file.
why: the owner 2026-11-08 16:31Z "let's then start making the generic version" (playground, no release); P35 SPLIT.tsv D20-D22, D25.
v2 = build_knowledge_v1.py with every alarm-only constant moved to --pack <file.json> (README.md: the contract, every key).
packs/alarm.json reproduces v1 byte for byte (golden test). Same store format as v1: a store written by v1 is read by v2.
commands (each needs --pack <file.json> and --dir <store folder>):
  init                       write empty store files (headers only) where missing
  check                      schema, eids exist, no control (arm C) eid in findings, statuses recomputed vs stored
  brief                      write KNOWLEDGE_BRIEF.md (deterministic: same inputs -> same bytes)
  op --who W --op OP ...     apply one delta op and log it in OPS_LOG.tsv
     OP = ADD --set k=v ...            (new finding; fid given or next free; status computed)
          UPDATE --target F --set k=v  (status_rule/status/n_* recomputed after)
          MERGE --target F --into G    (F RETIRED, superseded_by G; F eids appended to G)
          RETIRE --target F --into G   (F RETIRED, superseded_by G)
          EVIDENCE --set k=v ...       (append one EVIDENCE row; append only)
          HOLDOUT_SAME_SIGN --target F (orchestrator: held-out read same sign; word only, no numbers)
          QUESTION --set action=ADD --set question=... --set would_move_fid=F --set priority=1|2|3 ...
          QUESTION --target Q --set action=TAKE
          QUESTION --target Q --set action=ANSWER --set answered_by_eid=E  (eid must exist)
          MOVE --target <move> --set mechanism=M --set eid=E --set beat_r1=1|0 --set gain_vs_r1=x
               --set gain_vs_forecast=y --set fail=1|0 [--set note=...]
mechanism names: only the pack's (mechanisms list or mechanisms_file); check and every op refuse any other
  name (UNKNOWN_MECHANISM). A new mechanism is a line in the pack's list or file, never a code edit.
sides: the pack's sides; each side has its yardstick name; a mechanism belongs to the side that lists it, else
  to the side with mechanisms "*". BEST SO FAR: per side the eligible VARIANT row with the largest margin
  (minus_fdonly15 as stored, i.e. measure minus the side's yardstick; wrong_yardstick_note rows skipped).
status rules (numbers from the pack's status_bars; TB = t_bar):
  eligible evidence: arm != C, notes without outside_window_note, window inside design_window.
  eff_t: SPLIT_STATE -> t; VARIANT -> t, but 0 when minus_fdonly15 <= 0; YARDSTICK -> not used;
         VARIANT with wrong_yardstick_note -> unknown (None).
  RETIRED  T1 superseded_by set
  REFUTED  R1 any eligible eff_t <= -TB
  CONFIRMED C1 eff_t >= TB in >= confirmed_min_runs runs AND >= confirmed_min_mechanisms mechanisms AND (when
           confirmed_needs_holdout) a HOLDOUT_SAME_SIGN op in OPS_LOG (else SUPPORTED, rule S1+C1WAIT)
  SUPPORTED S1 eff_t >= TB and waves >= supported_min_waves in one run; S2 (when s2_fitted_beats_select) a fitted-round
           variant beats its run's select-round variant and the yardstick
  REFUTED  R2 >= refuted_min_runs runs with a known eff_t and none |eff_t| >= TB
  HYPOTHESIS H1 otherwise
A status bar set to "TODO" in the pack: check, brief and finding ops are refused until the owner sets it.
"""
import csv, os, re, sys, shutil, argparse, datetime, json

HERE = os.path.dirname(os.path.abspath(__file__))
EV_COLS = ["eid","utc","run","arm","mechanism","alarm","variant","test_kind","statement","window",
           "lead15","minus_fdonly15","lead1h","t","waves","months_up","months_total","job","source_file","notes"]
FI_COLS = ["fid","type","statement","scope_mechanisms","status","status_rule","evidence_eids","n_runs",
           "n_mechanisms","best_effect","cited_by_runs","cited_runs_margin","next_test","superseded_by",
           "last_utc","last_op"]
MV_COLS = ["move","mechanism","n","n_beat_r1","mean_gain_vs_r1","mean_gain_vs_forecast","n_fail","eids","notes"]
OQ_COLS = ["qid","question","would_move_fid","test_sketch","priority","source_run","status","answered_by_eid"]
OP_COLS = ["utc","who","op","target","old_new","reason"]
ARMS = {"L","C","V1"}
KINDS = {"VARIANT","SPLIT_STATE","YARDSTICK"}
TYPES = {"STATE","MECHANISM","CONDITION_EFFECT","NON_SEPARATOR","MOVE","ARCHETYPE"}
STATUSES = ["CONFIRMED","SUPPORTED","HYPOTHESIS","REFUTED","RETIRED"]
OPS = {"ADD","UPDATE","MERGE","RETIRE"}
OQ_STATUS = {"OPEN","TAKEN","ANSWERED"}
LINE_CAP = 260   # C127: was 300; keeps the brief under the 30 KB read limit (format, not a pack setting)
MORE = " ... (more in FINDINGS.tsv)"
FILES = {"EVIDENCE.tsv":EV_COLS,"FINDINGS.tsv":FI_COLS,"MOVES.tsv":MV_COLS,
         "OPEN_QUESTIONS.tsv":OQ_COLS,"OPS_LOG.tsv":OP_COLS}

# ---- pack settings (README.md: the --pack contract) ----
REQUIRED = {"pack_name": str, "brief_title": str, "design_window": str, "window_label": str,
            "outside_window_note": str, "outside_window_label": str, "wrong_yardstick_note": str,
            "sides": list, "measure_label": str, "rounds": dict, "status_bars": dict, "base_rates": dict,
            "intro_lines": list, "definitions": (dict, type(None))}
NESTED = {"rounds": ("select", "fitted", "placebo"),
          "status_bars": ("t_bar", "supported_min_waves", "confirmed_min_runs", "confirmed_min_mechanisms",
                          "confirmed_needs_holdout", "refuted_min_runs", "s2_fitted_beats_select"),
          "base_rates": ("pass_margin", "pass_t", "measure_word", "pass_line", "extra_lines")}
SIDE_KEYS = ("key", "label", "yardstick", "mechanisms")
DEF_KEYS = ("team_up", "runs_dir", "glob", "show_prefix")
BOOL_BARS = ("confirmed_needs_holdout", "s2_fitted_beats_select")
TODO = "TODO"
PACK = None; PACK_PATH = ""; MECHANISMS = set(); DESIGN = ("", ""); SIDES = []; DEFAULT_SIDE = ""
BARS = {}; ROUNDS = {}; MEAS = ""; OUT_NOTE = ""; OUT_LABEL = ""; WRONG_NOTE = ""

def refuse_pack(msg): raise SystemExit(f"REFUSED pack {PACK_PATH or '(none)'}: {msg} (README.md: the --pack contract)")

def load_pack(path):
    """read and check one pack file; sets the module settings. Refuses a missing key, a wrong type, a bad window."""
    global PACK, PACK_PATH, MECHANISMS, DESIGN, SIDES, DEFAULT_SIDE, BARS, ROUNDS, MEAS, OUT_NOTE, OUT_LABEL, WRONG_NOTE
    PACK_PATH = path
    try:
        with open(path, encoding="utf-8") as fh: pk = json.load(fh)
    except (OSError, ValueError) as e: refuse_pack(f"cannot read as JSON ({e})")
    if not isinstance(pk, dict): refuse_pack("top level is not an object")
    miss = [k for k in REQUIRED if k not in pk]
    miss += [f"{k}.{s}" for k, subs in NESTED.items() if isinstance(pk.get(k), dict) for s in subs if s not in pk[k]]
    if isinstance(pk.get("definitions"), dict): miss += [f"definitions.{s}" for s in DEF_KEYS if s not in pk["definitions"]]
    if ("mechanisms" in pk) == ("mechanisms_file" in pk): miss.append("exactly one of mechanisms / mechanisms_file")
    if miss: refuse_pack("missing required key(s) " + ", ".join(miss))
    for k, ty in REQUIRED.items():
        if not isinstance(pk[k], ty): refuse_pack(f"key {k} has the wrong type")
    if not re.fullmatch(r"\d{8}:\d{8}", pk["design_window"]): refuse_pack("design_window must be YYYYMMDD:YYYYMMDD")
    if "mechanisms_file" in pk:
        mf = os.path.join(os.path.dirname(os.path.abspath(path)), pk["mechanisms_file"])
        try:
            with open(mf, encoding="utf-8") as fh:
                mechs = [x.strip() for x in fh if x.strip() and not x.strip().startswith("#")]
        except OSError as e: refuse_pack(f"mechanisms_file not readable ({e})")
    else: mechs = pk["mechanisms"]
    if not mechs or not all(isinstance(m, str) and re.fullmatch(r"[A-Z0-9_]+", m) for m in mechs):
        refuse_pack("mechanism names must be a non-empty list of UPPER_CASE ids")
    for s in pk["sides"]:
        if not isinstance(s, dict) or any(x not in s for x in SIDE_KEYS): refuse_pack("every side needs " + ", ".join(SIDE_KEYS))
        if s["mechanisms"] != "*" and (not isinstance(s["mechanisms"], list) or any(m not in mechs for m in s["mechanisms"])):
            refuse_pack(f"side {s.get('key')}: mechanisms must be \"*\" or a list of the pack's mechanism names")
    if [s["mechanisms"] for s in pk["sides"]].count("*") != 1: refuse_pack("exactly one side must have mechanisms \"*\"")
    for k, v in pk["status_bars"].items():
        if v == TODO: continue
        if k in BOOL_BARS and not isinstance(v, bool): refuse_pack(f"status_bars.{k} must be true, false or \"TODO\"")
        if k not in BOOL_BARS and (isinstance(v, bool) or not isinstance(v, (int, float))): refuse_pack(f"status_bars.{k} must be a number or \"TODO\"")
    PACK = pk; MECHANISMS = set(mechs); DESIGN = tuple(pk["design_window"].split(":"))
    SIDES = pk["sides"]; DEFAULT_SIDE = [s["key"] for s in SIDES if s["mechanisms"] == "*"][0]
    BARS = pk["status_bars"]; ROUNDS = pk["rounds"]; MEAS = pk["measure_label"]
    OUT_NOTE, OUT_LABEL, WRONG_NOTE = pk["outside_window_note"], pk["outside_window_label"], pk["wrong_yardstick_note"]
    return pk

def need(section, keys):
    if PACK is None: raise SystemExit("REFUSED no pack loaded (--pack <file.json>)")
    todo = [f"{section}.{k}" for k in keys if PACK[section][k] == TODO]
    if todo: refuse_pack("TODO value(s) " + ", ".join(todo) + " (the owner sets them before check, brief or finding ops)")

def bad_mechs(v):
    return [m for m in (x.strip() for x in (v or "").split(",")) if m and m not in MECHANISMS]

def p(d, name): return os.path.join(d, name)

def read(d, name):
    path = p(d, name)
    if not os.path.exists(path): return [], None
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh, delimiter="\t"))
    if not rows: return [], None
    hdr = rows[0]
    return [dict(zip(hdr, r + [""]*(len(hdr)-len(r)))) for r in rows[1:] if r], hdr

def clean(v): return str(v).replace("\t"," ").replace("\n"," ").strip()

def write(d, name, cols, rows):
    tmp = p(d, name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows: fh.write("\t".join(clean(r.get(c,"")) for c in cols) + "\n")
    os.replace(tmp, p(d, name))

def append(d, name, cols, row):
    path = p(d, name); new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as fh:
        if new: fh.write("\t".join(cols) + "\n")
        fh.write("\t".join(clean(row.get(c,"")) for c in cols) + "\n")

def fnum(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def eligible(r):
    if r.get("arm") == "C" or OUT_NOTE in r.get("notes",""): return False
    w = r.get("window","").split(":")
    return len(w) == 2 and w[0] >= DESIGN[0] and w[1] <= DESIGN[1]

def eff_t(r):
    k = r.get("test_kind")
    if k == "YARDSTICK": return None
    t, m = fnum(r.get("t")), margin(r)
    if k == "VARIANT" and WRONG_NOTE in r.get("notes", ""): return None
    if k == "VARIANT" and m is not None and m <= 0: return 0.0
    return t

def margin(r):
    """minus_fdonly15 (measure minus the side's yardstick), or None when the row's notes carry wrong_yardstick_note"""
    if WRONG_NOTE in r.get("notes", ""): return None
    return fnum(r.get("minus_fdonly15"))

def holdouts(ops):
    """C218 (review B2): a HOLDOUT_SAME_SIGN row counts only for a finding added before it, and only when no later op changed that
    finding's evidence_eids (ADD, an UPDATE that sets evidence_eids, a MERGE into it); OPS_LOG order decides"""
    added, hold = set(), set()
    for o in ops:
        op, t = o.get("op"), o.get("target", "")
        if op == "ADD": added.add(t); hold.discard(t)
        elif op == "UPDATE" and "evidence_eids=" in o.get("old_new", ""): hold.discard(t)
        elif op == "MERGE":
            m = re.search(r"\(into ([^)]+)\)", o.get("old_new", ""))
            if m: hold.discard(m.group(1))
        elif op == "HOLDOUT_SAME_SIGN" and t in added: hold.add(t)
    return hold

def window_ok(w):
    """C218: YYYYMMDD:YYYYMMDD, real days, first <= last"""
    if not re.fullmatch(r"\d{8}:\d{8}", w or ""): return False
    try: a, b = (datetime.datetime.strptime(x, "%Y%m%d") for x in w.split(":"))
    except ValueError: return False
    return a <= b

def fitted_beats(r, ev_all):
    """S2: a fitted-round VARIANT (variant starts with rounds.fitted) beats its run's select-round VARIANT and the yardstick"""
    if r.get("test_kind") != "VARIANT" or not r.get("variant","").startswith(ROUNDS["fitted"]): return False
    m, lead = margin(r), fnum(r.get("lead15"))
    if m is None or m <= 0 or lead is None: return False
    for q in ev_all:
        if (q["run"] == r["run"] and q["alarm"] == r["alarm"] and q["test_kind"] == "VARIANT"
                and q["variant"].startswith(ROUNDS["select"]) and eligible(q)):
            l1 = fnum(q.get("lead15"))
            if l1 is not None and lead > l1: return True
    return False

def compute(f, ev_by, ev_all, hold):
    """returns (status, rule, n_runs, n_mechanisms)"""
    need("status_bars", NESTED["status_bars"]); tb = BARS["t_bar"]
    eids = [e for e in f.get("evidence_eids","").split(",") if e]
    rows = [ev_by[e] for e in eids if e in ev_by and eligible(ev_by[e])]
    n_runs = len({r["run"] for r in rows}); n_mech = len({r["mechanism"] for r in rows})
    if f.get("superseded_by"): return "RETIRED","T1",n_runs,n_mech
    effs = [(r, eff_t(r)) for r in rows]
    known = [(r, e) for r, e in effs if e is not None]
    if any(e <= -tb for _, e in known): return "REFUTED","R1",n_runs,n_mech
    strong = [r for r, e in known if e >= tb]
    if (len({r["run"] for r in strong}) >= BARS["confirmed_min_runs"]
            and len({r["mechanism"] for r in strong}) >= BARS["confirmed_min_mechanisms"]):
        if f["fid"] in hold or not BARS["confirmed_needs_holdout"]: return "CONFIRMED","C1",n_runs,n_mech
        return "SUPPORTED","S1+C1WAIT",n_runs,n_mech
    s1 = any((fnum(r.get("waves")) or 0) >= BARS["supported_min_waves"] for r in strong)
    s2 = BARS["s2_fitted_beats_select"] and any(fitted_beats(r, ev_all) for r in rows)
    if s1 or s2: return "SUPPORTED", "+".join(x for x, y in (("S1",s1),("S2",s2)) if y), n_runs, n_mech
    if len({r["run"] for r, _ in known}) >= BARS["refuted_min_runs"] and not any(abs(e) >= tb for _, e in known):
        return "REFUTED","R2",n_runs,n_mech
    return "HYPOTHESIS","H1",n_runs,n_mech

def load(d):
    ev,_ = read(d,"EVIDENCE.tsv"); fi,_ = read(d,"FINDINGS.tsv"); ops,_ = read(d,"OPS_LOG.tsv")
    return ev, {r["eid"]: r for r in ev}, fi, ops

def check(d, out=sys.stdout):
    need("status_bars", NESTED["status_bars"])   # check recomputes every status
    errs, mism = [], []
    for name, cols in FILES.items():
        rows, hdr = read(d, name)
        if hdr is None: errs.append(f"MISSING {name}"); continue
        if hdr != cols: errs.append(f"SCHEMA {name}: header differs")
    ev, ev_by, fi, ops = load(d)
    if len(ev_by) != len(ev): errs.append("DUP eid")
    for r in ev:
        if r["arm"] not in ARMS: errs.append(f"ARM {r['eid']} {r['arm']}")
        if r["test_kind"] not in KINDS: errs.append(f"KIND {r['eid']}")
        if r["mechanism"] not in MECHANISMS: errs.append(f"UNKNOWN_MECHANISM {r['eid']} {r['mechanism']}")
    fids = [f["fid"] for f in fi]
    if len(set(fids)) != len(fids): errs.append("DUP fid")
    hold = holdouts(ops)
    for f in fi:
        if f["type"] not in TYPES: errs.append(f"TYPE {f['fid']}")
        for m in bad_mechs(f["scope_mechanisms"]): errs.append(f"UNKNOWN_MECHANISM {f['fid']} {m}")
        if f["status"] not in STATUSES: errs.append(f"STATUS {f['fid']}")
        if f["last_op"] not in OPS: errs.append(f"LAST_OP {f['fid']}")
        eids = [e for e in f["evidence_eids"].split(",") if e]
        if not eids: errs.append(f"NO_EVIDENCE {f['fid']}")
        for e in eids:
            if e not in ev_by: errs.append(f"UNKNOWN_EID {f['fid']} {e}")
            elif ev_by[e]["arm"] == "C": errs.append(f"CONTROL_EVIDENCE {f['fid']} {e}")
        if f["superseded_by"] and f["superseded_by"] not in fids: errs.append(f"SUPERSEDED_BY {f['fid']}")
        st, rule, _, _ = compute(f, ev_by, ev, hold)
        if st != f["status"] or rule != f["status_rule"]:
            mism.append(f"MISMATCH {f['fid']} stored {f['status']}/{f['status_rule']} computed {st}/{rule}")
    mv,_ = read(d,"MOVES.tsv")
    for m in mv:
        if m["mechanism"] not in MECHANISMS: errs.append(f"UNKNOWN_MECHANISM move {m['move']} {m['mechanism']}")
        for e in [x for x in m["eids"].split(",") if x]:
            if e not in ev_by: errs.append(f"UNKNOWN_EID move {m['move']} {e}")
            elif ev_by[e]["arm"] == "C": errs.append(f"CONTROL_EVIDENCE move {m['move']} {e}")
    oq,_ = read(d,"OPEN_QUESTIONS.tsv")
    for q in oq:
        if q["status"] not in OQ_STATUS: errs.append(f"OQ_STATUS {q['qid']}")
        if q["priority"] not in {"1","2","3"}: errs.append(f"OQ_PRIORITY {q['qid']}")
        if q["status"] == "ANSWERED" and q["answered_by_eid"] not in ev_by: errs.append(f"OQ_ANSWER_EID {q['qid']}")
    for line in errs + mism: print(line, file=out)
    cnt = {s: sum(1 for f in fi if f["status"] == s) for s in STATUSES}
    print(f"CHECK {'PASS' if not errs and not mism else 'FAIL'} errors {len(errs)} mismatch {len(mism)} "
          f"evidence {len(ev)} findings {len(fi)} " + " ".join(f"{k} {v}" for k, v in cnt.items()), file=out)
    return errs, mism

def ev_ref(e, ev_by):
    r = ev_by.get(e)
    if r is None: return e + "(missing)"
    if r["arm"] == "C": return e + "(control)"
    if not eligible(r): return e + f"({OUT_LABEL} only, not counted)"
    return e

SEPMAR_NUM = re.compile(r"(?<![A-Za-z0-9.])[-+]?\d+\.\d+|(?<![A-Za-z0-9.])[-+]?\d+ pct")
def heldout_mask(text, eids, ev_by):
    """C48: an evidence row outside the design window pools held-out months, so the numbers its text carries never
    reach a hunter: decimals and 'N pct' are withheld in the brief."""
    if any(ev_by.get(e) is not None and ev_by[e].get("arm") != "C" and not eligible(ev_by[e])
           for e in (eids or "").split(",") if e):
        rep = f"<withheld: {OUT_LABEL}>"
        return SEPMAR_NUM.sub(lambda _m: rep, text)
    return text

def side(r):
    m = r.get("mechanism")
    for s in SIDES:
        if s["mechanisms"] != "*" and m in s["mechanisms"]: return s["key"]
    return DEFAULT_SIDE

def yardstick(mech):
    k = side({"mechanism": mech})
    return [s["yardstick"] for s in SIDES if s["key"] == k][0]

def best_variant(rows):
    """the one definition of 'best': eligible VARIANT row with the largest margin over its same-side
    yardstick (wrong_yardstick_note rows skipped); ties -> lower eid. Returns (margin, row) or None"""
    best = None
    for r in rows:
        if r.get("test_kind") != "VARIANT" or not eligible(r): continue
        m = margin(r)
        if m is None: continue
        if best is None or m > best[0] or (m == best[0] and r["eid"] < best[1]["eid"]): best = (m, r)
    return best

def best_so_far(ev):
    """per side (pack order) the eligible VARIANT row with the largest margin over its same-side yardstick; ties -> lower eid"""
    out = []
    for s in SIDES:
        b = best_variant([r for r in ev if side(r) == s["key"]])
        if not b: out.append(f"- {s['label']} vs {s['yardstick']}: none"); continue
        m, r = b
        out.append(f"- {s['label']} vs {s['yardstick']}: {r['alarm']} {r['variant']} {MEAS} {r['lead15']}, margin {m:+.2f}, "
                   f"t {r['t'] or 'n/a'}, {r['waves'] or 'n/a'} waves, {r['eid']}")
    return out

def cap(s, n=LINE_CAP):
    return s if len(s) <= n else s[:n - len(MORE)].rstrip() + MORE

def conflict_of(f):
    m = re.search(r"conflicts? with (F\d{4})", f.get("statement","") + " " + f.get("next_test",""))
    return m.group(1) if m else ""

def runs_t(f, ev_by):
    rows = [ev_by[e] for e in f["evidence_eids"].split(",") if e in ev_by and eligible(ev_by[e])]
    return ", ".join(f"{r['run']} t {r['t'] or 'n/a'}" for r in rows) or "none counted"

def finding_rows(f, ev_by):
    return [ev_by[e] for e in f["evidence_eids"].split(",") if e in ev_by and eligible(ev_by[e])]

def mech_best(f, ev_by):
    """per mechanism (sorted) the best numbers: best_variant; a mechanism with only split rows -> largest split t"""
    rows = finding_rows(f, ev_by); out = []
    for mech in sorted({r["mechanism"] for r in rows}):
        mr = [r for r in rows if r["mechanism"] == mech]
        b = best_variant(mr)
        if b:
            m, r = b
            out.append(f"{mech}: {MEAS} {r['lead15'] or 'n/a'}, margin {m:+.2f} vs {yardstick(mech)}, "
                       f"t {r['t'] or 'n/a'}, {r['waves'] or 'n/a'} waves, {r['eid']}"
                       + (f", window {r['window']} only" if r.get("window") != ":".join(DESIGN) else ""))  # C48: say when not the design window
            continue
        sp = [r for r in mr if r.get("test_kind") == "SPLIT_STATE" and fnum(r.get("t")) is not None]
        if sp:
            r = sorted(sp, key=lambda r: (-fnum(r["t"]), r["eid"]))[0]
            out.append(f"{mech}: split only, better state {MEAS} {r['lead15'] or 'n/a'}, t {r['t']}, "
                       f"{r['waves'] or 'n/a'} waves, {r['eid']}")
        else:
            out.append(f"{mech}: no margin vs {yardstick(mech)} yet")
    return "; ".join(out) or "none counted"

def base_rates(ev):
    """C29: per memory run, the select-round measure and best fitted-round measure (eligible VARIANT rows only), the
    fitted gain, and the class means a forecast starts from; round names, pass bars and extra lines from the pack"""
    need("base_rates", ("pass_margin", "pass_t")); B = PACK["base_rates"]
    S, F, P = ROUNDS["select"], ROUNDS["fitted"], ROUNDS["placebo"] or None
    runs = {}
    for r in ev:
        if r.get("arm") != "L" or r.get("test_kind") != "VARIANT" or not eligible(r): continue
        v = r.get("variant", ""); lead = fnum(r.get("lead15"))
        if lead is None: continue
        rnd = ("S" if v.startswith(S) else ("P" if P and v.startswith(P)
               else ("F" if re.match(re.escape(F) + r"\s", v) else None)))   # C65: the placebo is not the fitted round
        if rnd is None: continue
        d = runs.setdefault(r["run"], {"mech": r.get("mechanism", "")})
        if rnd not in d or lead > d[rnd]: d[rnd] = lead; d[rnd + "_tw"] = (r.get("t") or "n/a", r.get("waves") or "n/a"); d[rnd + "_m"] = fnum(r.get("minus_fdonly15"))
    rows = [(k, d) for k, d in sorted(runs.items()) if "S" in d]
    out = [f"## BASE RATES (computed; start every forecast here, then adjust; {PACK['window_label']} {MEAS})"]
    if not rows: return out + ["- none yet"]
    for k, d in rows:
        g = ("%+.2f" % (d["F"] - d["S"])) if "F" in d else "n/a"
        t1, w1 = d.get("S_tw", ("n/a", "n/a"))
        se = ("%.2f" % (d["S"] / fnum(t1))) if fnum(t1) else "n/a"
        out.append("- %s %s: %s %+.2f (t %s, %s waves, se %s), best %s %s, %s gain vs %s %s%s" % (k, d["mech"], S, d["S"], t1, w1, se, F, ("%+.2f" % d["F"]) if "F" in d else "n/a", F, S, g,
                   ("; placebo %s %+.2f (gain %+.2f; not in the %s mean)" % (P, d["P"], d["P"] - d["S"], F)) if "P" in d else ""))
    r1 = [d["S"] for _, d in rows]; gs = [d["F"] - d["S"] for _, d in rows if "F" in d]
    out.append("- %s %s: mean %+.2f, range %+.2f to %+.2f (n %d)" % (S, B["measure_word"], sum(r1) / len(r1), min(r1), max(r1), len(r1)))
    ok = [k for k, d in rows if d.get("S_m") is not None and d["S_m"] >= B["pass_margin"] and (fnum(d.get("S_tw", ("", ""))[0]) or 0) >= B["pass_t"]]   # C126 (H02-R2a)
    out.append(B["pass_line"].format(n=len(ok), total=len(rows), runs=", ".join(ok) or "none"))
    if gs:
        out.append("- %s gain vs %s: mean %+.2f, range %+.2f to %+.2f (n %d): shrink a predicted %s gain toward the mean of its own move in MOVES (this pooled mean only when the move has n < 2)" % (F, S, sum(gs) / len(gs), min(gs), max(gs), len(gs), F))
    out += list(B["extra_lines"])
    return out

def definitions(ev, fi, d):
    """C31: the exact definition file of every variant cited by a CONFIRMED, SUPPORTED or open-state finding; only files
    that exist; where to look from the pack's definitions block (null: the section says so)"""
    import glob
    out = ["## DEFINITIONS (exact conditions with metric codes: open only these files, never the receipts beside them)"]
    D = PACK["definitions"]
    if D is None: return out + ["- not set in this pack"]
    team = os.path.abspath(os.path.join(d, *([".."] * int(D["team_up"]))))
    root = os.path.join(team, D["runs_dir"])
    ev_by = {r["eid"]: r for r in ev}; want = set()
    for f in fi:
        if f["status"] in ("CONFIRMED", "SUPPORTED") or (f["status"] == "HYPOTHESIS" and f["type"] in ("STATE", "CONDITION_EFFECT")):
            for e in [x for x in f["evidence_eids"].split(",") if x in ev_by]:
                r = ev_by[e]
                if r.get("test_kind") != "VARIANT" or r.get("arm") == "C": continue
                m = re.search(r"\bV(\d+)\b", r.get("variant", ""))
                if m and r.get("alarm"): want.add((r["alarm"], "V" + m.group(1)))
    for alarm, v in sorted(want):
        hits = sorted(glob.glob(os.path.join(root, D["glob"].replace("{alarm}", alarm).replace("{v}", v))))
        if hits: out.append("- %s %s: %s/%s" % (alarm, v, D["show_prefix"], os.path.relpath(hits[-1], team)))
    return out if len(out) > 1 else out + ["- none found"]

def brief(d):
    need("status_bars", NESTED["status_bars"]); need("base_rates", ("pass_margin", "pass_t"))
    ev, ev_by, fi, ops = load(d); hold = holdouts(ops)
    mv,_ = read(d,"MOVES.tsv"); oq,_ = read(d,"OPEN_QUESTIONS.tsv")
    fi = sorted(fi, key=lambda f: f["fid"]); st_by = {f["fid"]: f["status"] for f in fi}
    S, F = ROUNDS["select"], ROUNDS["fitted"]
    def line(f, nxt=True):
        eids = ",".join(ev_ref(e, ev_by) for e in f["evidence_eids"].split(",") if e)
        _, _, nr, nm = compute(f, ev_by, ev, hold)
        names = ", ".join(sorted({r["mechanism"] for r in finding_rows(f, ev_by)})) or "none"
        s = (f"- {f['fid']} {f['status']} ({f['status_rule']}) | runs {nr}, mechanisms {nm} ({names}) | "
             f"best: {mech_best(f, ev_by)} | [{f['type']}] {cap(heldout_mask(f['statement'], f['evidence_eids'], ev_by))} | eids {eids} | "
             + (f"next: {f['next_test'] or 'none'}" if nxt else "next: see FINDINGS.tsv (C126: a REFUTED finding's next text is kept in the store)"))
        if f["superseded_by"]: s += f" | superseded by {f['superseded_by']}"
        return s
    out = [PACK["brief_title"], "",
           f"## BEST SO FAR (computed: best eligible VARIANT by margin over its same-side yardstick, {PACK['window_label']})"]
    out += best_so_far(ev) + [""]
    out += base_rates(ev) + [""]
    out += definitions(ev, fi, d) + [""]
    out += [x.replace("{LINE_CAP}", str(LINE_CAP)) for x in PACK["intro_lines"]] + [""]
    # C23: open states lead the brief, so a weak-t state is not buried under strong archetypes
    opn = [f for f in fi if f["status"] == "HYPOTHESIS" and f["type"] in ("STATE","CONDITION_EFFECT") and not f["superseded_by"]]
    out += [f"## OPEN STATES TO TEST ({len(opn)}) (a state seen in a split, not yet SUPPORTED; each is a ready {S} or {F} test; full line under HYPOTHESIS)"]
    out += [f"- {f['fid']} [{f['type']}] {cap(heldout_mask(f['statement'], f['evidence_eids'], ev_by))} | best: {mech_best(f, ev_by)} | next: {f['next_test'] or 'none'}" for f in opn] or ["- none"]
    out += [""]
    for title, sts in (("CONFIRMED",{"CONFIRMED"}),("SUPPORTED",{"SUPPORTED"})):
        rows = [f for f in fi if f["status"] in sts]
        out += [f"## {title} ({len(rows)})"] + ([line(f) for f in rows] or ["- none"]) + [""]
    conf = [f for f in fi if f["status"] == "HYPOTHESIS" and conflict_of(f)]
    hyp = [f for f in fi if f["status"] == "HYPOTHESIS" and not conflict_of(f)]
    out += [f"## HYPOTHESIS ({len(hyp)})"] + ([line(f) for f in hyp] or ["- none"]) + [""]
    out += [f"## CONFLICTS TO RESOLVE ({len(conf)}) (HYPOTHESIS against another finding)"]
    out += ([f"- {f['fid']} vs {conflict_of(f)} ({st_by.get(conflict_of(f), 'unknown')}): " + line(f)[2:]
             for f in conf] or ["- none"]) + [""]
    dnr = [f for f in fi if f["status"] == "REFUTED"]
    out += [f"## DO NOT RETRY ({len(dnr)}) (status REFUTED by the numbers)"]
    out += ([line(f, nxt=False) + f" | runs: {runs_t(f, ev_by)}"
             for f in dnr] or ["- none"]) + [""]
    def mline(m):
        return (f"- {m['move']} on {m['mechanism']}: n {m['n']}, beat {S} {m['n_beat_r1']}, mean gain vs {S} "
                f"{m['mean_gain_vs_r1'] or 'none'}, vs forecast {m['mean_gain_vs_forecast'] or 'none'}, fails "
                f"{m['n_fail']} | eids {','.join(ev_ref(e, ev_by) for e in m['eids'].split(',') if e)} | {cap(heldout_mask(m['notes'], m['eids'], ev_by), 300)}")
    mv = sorted(mv, key=lambda m: (m["move"], m["mechanism"]))
    def n(m): return int(fnum(m["n"]) or 0)
    def nf(m): return int(fnum(m["n_fail"]) or 0)
    works = [m for m in mv if n(m) >= 2 and nf(m) == 0 and (fnum(m["mean_gain_vs_r1"]) or 0) > 0]
    fails = [m for m in mv if m not in works and nf(m) >= 1]
    single = [m for m in mv if m not in works and m not in fails]
    out += [f"## MOVES THAT WORK ({len(works)}) (n >= 2, no fail, mean gain vs {S} > 0)"] + ([mline(m) for m in works] or ["- none"]) + [""]
    out += [f"## MOVES THAT FAIL ({len(fails)})"] + ([mline(m) for m in fails] or ["- none"]) + [""]
    out += [f"## MOVES NOT YET A RULE ({len(single)}) (n < 2 or no counted try)"] + ([mline(m) for m in single] or ["- none"]) + [""]
    oqs = sorted([q for q in oq if q["status"] != "ANSWERED"], key=lambda q: (q["priority"], q["qid"]))
    def qline(q):
        ts = q['test_sketch']
        n = 420 if q['priority'] == "1" else 100   # C127: priority 1 long, 2-3 short; the full test stays in OPEN_QUESTIONS.tsv
        test = ts if len(ts) <= n else ts[:n].rsplit(' ', 1)[0] + " ... (full test in OPEN_QUESTIONS.tsv)"
        s = f"- {q['qid']} (priority {q['priority']}, {q['status']}, moves {q['would_move_fid']}, from {q['source_run']}) {q['question'] if q['priority'] == '1' else cap(q['question'], 200)} | test: {test}"
        for x in [x for x in re.split(r"[ ,;]+", q["would_move_fid"]) if st_by.get(x) == "REFUTED"]:
            s += f" (retries refuted {x}: needs new evidence named)"
        return s
    out += [f"## OPEN QUESTIONS ({len(oqs)})"]
    out += [qline(q) for q in oqs] or ["- none"]
    data = "\n".join(out) + "\n"
    with open(p(d,"KNOWLEDGE_BRIEF.md"), "w", encoding="utf-8", newline="") as fh: fh.write(data)
    return data

def question_op(d, who, target, sets, reason, utc):
    oq,_ = read(d,"OPEN_QUESTIONS.tsv"); ev,_ = read(d,"EVIDENCE.tsv"); eids = {r["eid"] for r in ev}
    act = sets.get("action","").upper(); by = {q["qid"]: q for q in oq}
    if act == "ADD":
        qid = sets.get("qid") or "Q%03d" % (max([int(q["qid"][1:]) for q in oq] or [0]) + 1)
        if qid in by: raise SystemExit(f"REFUSED duplicate qid {qid}")
        q = {c: sets.get(c, "") for c in OQ_COLS}; q["qid"], q["status"], q["answered_by_eid"] = qid, "OPEN", ""
        if q["priority"] not in {"1","2","3"}: raise SystemExit("REFUSED priority")
        if not q["question"]: raise SystemExit("REFUSED empty question")
        oq.append(q); old_new = "- -> OPEN"
    elif act in ("TAKE","ANSWER"):
        if target not in by: raise SystemExit(f"REFUSED unknown qid {target}")
        q = by[target]; qid = target; old = q["status"]
        if old == "ANSWERED": raise SystemExit(f"REFUSED {qid} already ANSWERED")
        if act == "TAKE": q["status"] = "TAKEN"; old_new = f"{old} -> TAKEN"
        else:
            e = sets.get("answered_by_eid","")
            if e not in eids: raise SystemExit(f"REFUSED answered_by_eid {e or '(empty)'} not in EVIDENCE")
            q["status"], q["answered_by_eid"] = "ANSWERED", e; old_new = f"{old} -> ANSWERED ({e})"
    else: raise SystemExit("REFUSED QUESTION action (ADD|TAKE|ANSWER)")
    twin(d,"OPEN_QUESTIONS.tsv","QUESTION")
    write(d,"OPEN_QUESTIONS.tsv",OQ_COLS,sorted(oq, key=lambda q: q["qid"]))
    append(d,"OPS_LOG.tsv",OP_COLS,{"utc":utc,"who":who,"op":"QUESTION","target":qid,"old_new":old_new,"reason":reason})
    return qid

def twin(d, name, tag):
    src = p(d, name)
    if os.path.exists(src):
        os.makedirs(p(d,"twins"), exist_ok=True)
        dst = p(d, os.path.join("twins", f"{name}.pre_{tag}_{now().replace(':','')}"))
        k = 0
        while os.path.exists(dst): k += 1; dst = dst.rsplit(".", 1)[0] + f".{k}" if k > 1 else dst + ".1"
        shutil.copy2(src, dst)

def refresh(f, ev_by, ev, hold):
    st, rule, nr, nm = compute(f, ev_by, ev, hold)
    f["status"], f["status_rule"], f["n_runs"], f["n_mechanisms"] = st, rule, str(nr), str(nm)

def apply_op(d, who, op, target="", sets=None, into="", reason="", utc=None):
    if PACK is None: raise SystemExit("REFUSED no pack loaded (--pack <file.json>)")
    sets = sets or {}; utc = utc or now()
    if op == "QUESTION": return question_op(d, who, target, sets, reason, utc)
    ev, ev_by, fi, ops = load(d); hold = holdouts(ops)
    if op == "EVIDENCE":
        row = {c: sets.get(c, "") for c in EV_COLS}
        if not row["eid"]: row["eid"] = "E%04d" % (len(ev) + 1)
        if row["eid"] in ev_by: raise SystemExit(f"REFUSED duplicate eid {row['eid']}")
        if row["arm"] not in ARMS or row["test_kind"] not in KINDS: raise SystemExit("REFUSED arm/test_kind")
        if row["mechanism"] not in MECHANISMS: raise SystemExit(f"REFUSED UNKNOWN_MECHANISM {row['mechanism'] or '(empty)'} (allowed: {', '.join(sorted(MECHANISMS))})")
        for k in ("t", "waves"):   # C218: numbers or empty (K6)
            v = row[k].strip(); x = fnum(v)
            if v and (x is None or x != x or x in (float("inf"), float("-inf"))): raise SystemExit(f"REFUSED NOT_A_NUMBER {k}={v}")
        if not window_ok(row["window"]): raise SystemExit(f"REFUSED BAD_WINDOW {row['window'] or '(empty)'}: YYYYMMDD:YYYYMMDD, real days, first <= last")
        row["utc"] = row["utc"] or utc
        append(d,"EVIDENCE.tsv",EV_COLS,row)
        append(d,"OPS_LOG.tsv",OP_COLS,{"utc":utc,"who":who,"op":"EVIDENCE","target":row["eid"],"old_new":"- -> appended","reason":reason})
        return row["eid"]
    if op == "HOLDOUT_SAME_SIGN":
        need("status_bars", NESTED["status_bars"])
        if target not in {f["fid"] for f in fi}: raise SystemExit(f"REFUSED UNKNOWN_FID {target or '(empty)'}: the held-out word names an existing finding (C218)")
        append(d,"OPS_LOG.tsv",OP_COLS,{"utc":utc,"who":who,"op":op,"target":target,"old_new":"- -> same sign","reason":reason})
        ops.append({"op":op,"target":target}); hold = holdouts(ops)
        by = {f["fid"]: f for f in fi}
        if target in by:
            old = by[target]["status"]; twin(d,"FINDINGS.tsv",op); refresh(by[target], ev_by, ev, hold)
            by[target]["last_utc"], by[target]["last_op"] = utc, "UPDATE"
            write(d,"FINDINGS.tsv",FI_COLS,fi)
            append(d,"OPS_LOG.tsv",OP_COLS,{"utc":utc,"who":who,"op":"UPDATE","target":target,"old_new":f"status {old} -> {by[target]['status']}","reason":"recomputed after HOLDOUT_SAME_SIGN"})
        return target
    if op == "MOVE": return move_op(d, who, target, sets, reason, utc, ev_by)
    if op not in OPS: raise SystemExit(f"REFUSED op {op}")
    need("status_bars", NESTED["status_bars"])
    for m in bad_mechs(sets.get("scope_mechanisms","")): raise SystemExit(f"REFUSED UNKNOWN_MECHANISM {m} (allowed: {', '.join(sorted(MECHANISMS))})")
    by = {f["fid"]: f for f in fi}
    for e in [x for x in sets.get("evidence_eids","").split(",") if x]:
        if e not in ev_by: raise SystemExit(f"REFUSED UNKNOWN_EID {e}")
        if ev_by[e]["arm"] == "C": raise SystemExit(f"REFUSED CONTROL_EVIDENCE {e}")
    if op == "UPDATE" and "evidence_eids" in sets: hold = hold - {target}   # C218 (B2): evidence changed, an earlier held-out word no longer counts
    if op == "MERGE": hold = hold - {into}
    twin(d,"FINDINGS.tsv",op)
    if op == "ADD":
        fid = sets.get("fid") or "F%04d" % (len(fi) + 1)
        if fid in by: raise SystemExit(f"REFUSED duplicate fid {fid}")
        if not sets.get("evidence_eids"): raise SystemExit("REFUSED NO_EVIDENCE")
        f = {c: sets.get(c, "") for c in FI_COLS}; f["fid"] = fid
        f["last_utc"], f["last_op"] = utc, "ADD"; refresh(f, ev_by, ev, hold); fi.append(f)
        old_new = f"- -> {f['status']}/{f['status_rule']}"; target = fid
    else:
        if target not in by: raise SystemExit(f"REFUSED unknown fid {target}")
        f = by[target]; old = f"{f['status']}/{f['status_rule']}"
        if op == "UPDATE":
            for k, v in sets.items():
                if k in ("fid","status","status_rule","last_utc","last_op"): continue
                f[k] = v
        else:
            if into not in by: raise SystemExit(f"REFUSED unknown --into {into}")
            f["superseded_by"] = into
            if op == "MERGE":
                g = by[into]; ge = [x for x in g["evidence_eids"].split(",") if x]
                for e in f["evidence_eids"].split(","):
                    if e and e not in ge: ge.append(e)
                g["evidence_eids"] = ",".join(ge); refresh(g, ev_by, ev, hold)
                g["last_utc"], g["last_op"] = utc, "MERGE"
        refresh(f, ev_by, ev, hold); f["last_utc"], f["last_op"] = utc, op
        old_new = f"{old} -> {f['status']}/{f['status_rule']}" + (f" (into {into})" if into else "") \
                  + ("".join(f"; {k}={v}" for k, v in sets.items()) if op == "UPDATE" else "")
    write(d,"FINDINGS.tsv",FI_COLS,fi)
    append(d,"OPS_LOG.tsv",OP_COLS,{"utc":utc,"who":who,"op":op,"target":target,"old_new":old_new,"reason":reason})
    return target

def move_op(d, who, target, sets, reason, utc, ev_by):
    mech, e = sets.get("mechanism",""), sets.get("eid","")
    if not target: raise SystemExit("REFUSED MOVE needs --target <move name>")
    if mech not in MECHANISMS: raise SystemExit(f"REFUSED UNKNOWN_MECHANISM {mech or '(empty)'} (allowed: {', '.join(sorted(MECHANISMS))})")
    eids = [x for x in e.split(",") if x]
    if not eids: raise SystemExit("REFUSED MOVE needs --set eid=E")
    for x in eids:
        if x not in ev_by: raise SystemExit(f"REFUSED UNKNOWN_EID {x}")
        if ev_by[x]["arm"] == "C": raise SystemExit(f"REFUSED CONTROL_EVIDENCE {x}")
    def flag(k):
        v = sets.get(k, "")
        if v not in ("0","1"): raise SystemExit(f"REFUSED {k} must be 0 or 1")
        return int(v)
    beat, fail = flag("beat_r1"), flag("fail")
    g1, gf = fnum(sets.get("gain_vs_r1","")), fnum(sets.get("gain_vs_forecast",""))
    if g1 is None or gf is None: raise SystemExit("REFUSED gain_vs_r1 and gain_vs_forecast must be numbers")
    mv,_ = read(d,"MOVES.tsv")
    row = next((m for m in mv if m["move"] == target and m["mechanism"] == mech), None)
    if row and any(x in row["eids"].split(",") for x in eids): raise SystemExit(f"REFUSED DUP_MOVE_EID {e} already counted for {target}/{mech}")
    twin(d,"MOVES.tsv","MOVE")
    if row is None:
        row = {c: "" for c in MV_COLS}; row.update(move=target, mechanism=mech, n="0", n_beat_r1="0",
            mean_gain_vs_r1="0", mean_gain_vs_forecast="0", n_fail="0"); mv.append(row); old = "-"
    else: old = f"n {row['n']}"
    n = int(row["n"] or 0)
    row["mean_gain_vs_r1"] = "%.2f" % (((fnum(row["mean_gain_vs_r1"]) or 0) * n + g1) / (n + 1))
    row["mean_gain_vs_forecast"] = "%.2f" % (((fnum(row["mean_gain_vs_forecast"]) or 0) * n + gf) / (n + 1))
    row["n"] = str(n + 1); row["n_beat_r1"] = str(int(row["n_beat_r1"] or 0) + beat)
    row["n_fail"] = str(int(row["n_fail"] or 0) + fail)
    row["eids"] = ",".join([x for x in row["eids"].split(",") if x] + eids)
    if sets.get("note"): row["notes"] = (row["notes"] + "; " if row["notes"] else "") + sets["note"]
    write(d,"MOVES.tsv",MV_COLS,sorted(mv, key=lambda m: (m["move"], m["mechanism"])))
    append(d,"OPS_LOG.tsv",OP_COLS,{"utc":utc,"who":who,"op":"MOVE","target":f"{target}/{mech}","old_new":f"{old} -> n {row['n']}","reason":reason})
    return f"{target}/{mech}"

def init(d):
    os.makedirs(d, exist_ok=True)   # C218: a missing store folder is made (was a traceback)
    for name, cols in FILES.items():
        if not os.path.exists(p(d, name)): write(d, name, cols, [])

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["check","brief","op","init"])
    ap.add_argument("--pack", required=True, help="pack settings JSON (README.md: the --pack contract)")
    ap.add_argument("--dir", required=True, help="the seat's own store folder")
    ap.add_argument("--who", default="CURATOR")
    ap.add_argument("--op", default=""); ap.add_argument("--target", default=""); ap.add_argument("--into", default="")
    ap.add_argument("--set", action="append", default=[]); ap.add_argument("--reason", default="")
    a = ap.parse_args(argv)
    load_pack(a.pack)
    if a.cmd == "init": init(a.dir); return 0
    if a.cmd == "check":
        errs, mism = check(a.dir); return 1 if errs or mism else 0
    if a.cmd == "brief":
        brief(a.dir); print("BRIEF", p(a.dir,"KNOWLEDGE_BRIEF.md")); return 0
    sets = dict(s.split("=", 1) for s in a.set)
    print(apply_op(a.dir, a.who, a.op, a.target, sets, a.into, a.reason)); return 0

if __name__ == "__main__":
    sys.exit(main())
