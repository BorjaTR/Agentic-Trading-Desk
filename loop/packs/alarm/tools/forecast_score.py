#!/usr/bin/env python3
"""Score hunter forecasts: Brier (p_beat_yardstick vs the pass rule: +2 over the same-side yardstick, t >= 3, 3 of 5 months; C50) + 80 pct coverage, per run.
Usage: python3 forecast_score.py [L02 L03 ...]  (default: every runs_v2/L* with work/FORECASTS.tsv)
Reads runs_v2/<L>/work/FORECASTS.tsv, pipe_r1/pipe_r3/pipe_r3p STEP_11_GRADE.json (the actual lead15, t, months; C145) or else runs_v2/<L>/CARD.md, SERIES_V2_CONFIG.json (yardstick_design_sepjan, _up). Writes FORECAST_SCORES.tsv here; with --print it writes nothing and prints the rows (assessors)."""
import csv, glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.environ.get('ALARM_SERIES_DIR', os.path.dirname(os.path.dirname(HERE)))   # RC2 copy: the series folder (runs_v2/, SERIES_V2_CONFIG.json)
_TOOL_DIR = HERE
RUNS = os.path.join(S, "runs_v2")
NUM = re.compile(r"[+-]?\d+(?:\.\d+)?")

def num(v):
    m = NUM.fullmatch(str(v).strip()) if v is not None else None
    return float(m.group()) if m else None

def yardsticks():
    """C113 (ASSESS-C04): the Sep-Jan yardsticks from SERIES_V2_CONFIG.json, so a control assessor never opens knowledge_v1"""
    import json
    _cf = os.path.join(S, "SERIES_V2_CONFIG.json"); c = json.load(open(_cf if os.path.isfile(_cf) else os.path.join(_TOOL_DIR, "SERIES_V2_CONFIG.json")))   # RC2: else the pack copy
    d, u = c["yardstick_design_sepjan"], c["yardstick_design_sepjan_up"]
    for y in (d, u): assert y["window"] == "20250910:20260131", y["name"]
    return float(d["lead15"]), float(u["lead15"])

PASS_MARGIN, PASS_T, PASS_MONTHS = 2.0, 3.0, 3   # C50: the R1 pass rule the hunter's p is about (HUNTER_RULES: +2 over the yardstick, t >= 3, 3 of 5 months)
def card(run):
    """lead15 per round from the card table, plus t and months up when the card has those columns (None when not)"""
    txt = open(os.path.join(RUNS, run, "CARD.md")).read()
    up = "FORCED_OUT_SHORTS" in txt.split("| round |")[0]
    lead, tt, mo, idx, var = {}, {}, {}, {}, {}
    for line in txt.splitlines():
        c = [x.strip() for x in line.split("|")]
        if len(c) > 2 and c[1] == "round": idx = {name: i for i, name in enumerate(c)}
        if len(c) > 5 and re.fullmatch(r"R[13]P?", c[1]):
            m = NUM.search(c[4])
            if m and c[1] not in lead:
                lead[c[1]] = float(m.group())
                vs = re.findall(r"\bV(\d+)\b", c[3]); var[c[1]] = vs[-1] if vs else None     # C145: the round's variant, to match its receipt
                if "t" in idx and idx["t"] < len(c): tt[c[1]] = num(NUM.search(c[idx["t"]]).group()) if NUM.search(c[idx["t"]]) else None
                mk = next((k for k in idx if k.startswith("months")), None)     # C101 (M071): 'months up' or 'months above +10.99'
                if mk and idx[mk] < len(c):
                    mm = re.match(r"\s*(\d+) of [45]", c[idx[mk]]); mo[c[1]] = int(mm.group(1)) if mm else None
    card.variants = var
    return up, lead, tt, mo

def passed(a, yard, t, months):
    """1 when the round meets the pass rule the forecast p is about; parts the card lacks are not counted against it"""
    return 1 if (a - yard >= PASS_MARGIN and (t is None or t >= PASS_T) and (months is None or months >= PASS_MONTHS)) else 0

PIPES = {"R1": "pipe_r1", "R3": "pipe_r3", "R3P": "pipe_r3p"}
def receipts(run, yard):
    """C145 (K2 packet: a planted card cell +14.84 vs STEP_11 14.34 reached the forecast error): lead15, t and months above the
    yardstick per round from pipe_<k>/STEP_11_GRADE.json (numbers.real, horizon 15m); a round with no receipt is left to the card"""
    import json
    out = {}
    for rnd, pipe in PIPES.items():
        f = os.path.join(RUNS, run, pipe, "STEP_11_GRADE.json")
        if not os.path.isfile(f): continue
        try: real = json.load(open(f))["numbers"]["real"]
        except (ValueError, KeyError, TypeError): continue
        r = next((x for x in real if x.get("horizon") == "15m"), None)
        if not r or num(r.get("lead")) is None: continue
        try: alarm = json.load(open(f)).get("alarm", "")
        except ValueError: alarm = ""
        m = re.search(r"_V(\d+)$", alarm or "")
        out[rnd] = (num(r["lead"]), num(r.get("t")), m.group(1) if m else None)
    return out

def forecasts(run):
    rows = list(csv.reader(open(os.path.join(RUNS, run, "work", "FORECASTS.tsv")), delimiter="\t"))
    hdr, out = rows[0], {}
    newfmt = "p_beat_yardstick" in hdr
    for r in rows[1:]:
        if not r or not r[0].strip(): continue
        rnd = re.match(r"R\dP?", r[0].strip())       # C60: R3P (placebo) is its own round, never R3 (M032)
        if not rnd: continue
        rnd = rnd.group()
        if newfmt or len(r) >= 8:      # round utc p net low high t months
            p, net, lo, hi = (num(r[i]) if i < len(r) else None for i in (2, 3, 4, 5))
        else:                           # old L02 format: round utc net t months
            p, net, lo, hi = None, num(r[2]), None, None
        if p is not None and not (0 <= p <= 1): p = None
        out[rnd] = dict(label=r[0].strip(), utc=r[1].strip(), p=p, net=net, lo=lo, hi=hi)   # last row of a round wins
    return out

def main(argv):
    show = '--print' in argv; argv = [x for x in argv if x != '--print']      # C98 (M066): --print writes nothing (assessors)
    fd, fu = yardsticks()
    runs = argv or sorted(os.path.basename(os.path.dirname(os.path.dirname(f))) for f in glob.glob(os.path.join(RUNS, "L*", "work", "FORECASTS.tsv")))
    rows, summ = [], []
    for run in runs:
        up, lead, tt, mo = card(run); yard = fu if up else fd; fc = forecasts(run)
        src = {k: "card" for k in lead}
        cv = getattr(card, "variants", {})
        for rnd, (a, t1, v) in receipts(run, yard).items():            # C145: the receipt's lead15 wins over the card cell
            if rnd not in lead: continue                                 # (t and months stay the card's: one change at a time)
            if v is None or cv.get(rnd) is None or v != cv.get(rnd):
                src[rnd] = "card (receipt variant %s, card V%s: not compared)" % (v, cv.get(rnd)); continue
            src[rnd] = "STEP_11" if abs(a - lead[rnd]) < 0.006 else "STEP_11 (card said %s)" % lead[rnd]
            lead[rnd] = a
            if tt.get(rnd) is None: tt[rnd] = t1
        bs, cov = [], []
        for rnd in ("R1", "R3", "R3P"):
            if rnd not in fc or rnd not in lead: continue
            f, a = fc[rnd], lead[rnd]; o = passed(a, yard, tt.get(rnd), mo.get(rnd))   # C50: was 'a > yard' (beats at all)
            b = (f["p"] - o) ** 2 if f["p"] is not None else None
            c = (1 if f["lo"] <= a <= f["hi"] else 0) if None not in (f["lo"], f["hi"]) else None
            if b is not None: bs.append(b)
            if c is not None: cov.append(c)
            rows.append([run, rnd, f["label"], f["utc"], "FUONLY" if up else "FDONLY", yard, f["p"], f["net"], f["lo"], f["hi"], a, o,
                         "" if b is None else round(b, 4), "" if c is None else c, "" if f["net"] is None else round(a - f["net"], 2), src.get(rnd, "card")])
        summ.append((run, len(bs), round(sum(bs) / len(bs), 4) if bs else None, sum(cov), len(cov)))
    with (open(os.devnull, "w") if show else open(os.path.join(HERE, "FORECAST_SCORES.tsv"), "w", newline="")) as fh:
        w = csv.writer(sys.stdout if show else fh, delimiter="\t")
        w.writerow(["run","round","forecast_row","utc","yardstick","yard15","p_beat","forecast15","low80","high80","actual15","beat","brier","covered","error15","actual_from"])
        w.writerows(rows)
    for run, n, b, c, nc in summ:
        print(f"{run}\tbrier {b} (n {n})\tcoverage {c}/{nc}")
    tb = [b for _, _, b, _, _ in summ if b is not None]
    pc, pn = sum(s[3] for s in summ), sum(s[4] for s in summ)
    print(f"ALL\tbrier falls run to run: {'yes' if all(x > y for x, y in zip(tb, tb[1:])) else 'no'}\tpooled coverage {pc}/{pn}")

if __name__ == "__main__": main(sys.argv[1:])
