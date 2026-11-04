#!/usr/bin/env python3
"""alarm_core V1.2 (ALARMLIB seat, 25 Oct 2026; V1.1 with the four shared rules taken from the ONE shared copy, alarm_contract_v1.py in
team/RESEARCH/tools/idea_to_grade, which the grading tool also imports: review F6 "two copies of the shared contract"). Same answers as
V1.1 (tests_alarm_core_v1_1.py with ALARM_IMPL=alarm_core_v1_2). The CONTRACT functions of ALARM_LIBRARY_SCOPE_ARCH_V2, pure Python (stdlib only).
It reads no data store, runs no producer and no tool. Every function is a rule of the design; tests_alarm_core_v1.py checks each rule,
including the 8 discriminating cases of the OX-DATA review (REVIEW_ALARM_LIBRARY_SCOPE_V1_OX-DATA.md).

Rules (each one a section of the V2 design):
  source   opening_share / closing_share (HF3: S11 = opened / (opened + closed), EMPTY when the denominator is 0);
           hit-account prior exposure (HLPOSM HM3) is NOT closed volume; a "wiped" claim reads closed volume only.
  side     side_of: +1 / -1 by the sign, UNKNOWN for 0 or missing. Never a guess.
  machine  AlarmMachine: one state machine per (coin, direction): IDLE -> RUNNING -> FADING -> ENDED, UNKNOWN on a gap
           (a gap never reads as fading or ended); causal running maximum; fade = below fade_frac x running max for fade_hold_s;
           reset = below reset level (direction-specific) AND min_gap_s since the last emission; onset only when the VALUE crosses the
           current cut (a cut that moved under an unchanged value is CUT_CHANGE, not an event); deterministic episode ids;
           snapshot / restore so a restart or a re-batch gives the same events and ids.
  clock    emission_time = the latest of (observation + source availability delay, every confirmation's known_at); no emission while
           a confirmation is missing; onset kept apart from emission.
  r1       detect_r1: break of the prior 24 h extreme (the level EXCLUDES the current observation), re-entry inside within 30 min after
           going at least depth beyond; emission at re-entry or at the confirmation's receipt, whichever is later.
  registry membership(cards): from the cards' literal definitions only; no outcome argument exists. Two cards merge only when their
           canonical definitions are identical.
  waves    Clusters: market clusters from ONE frozen universe of fires (id, version), gap chaining with an explicit max span, weights
           1/size fixed at build; any subgroup reads the frozen ids and weights, never recomputes them.
  controls control_eligible: as-of eligibility uses only fires up to AND AT the moment ([t - before_s, t], closed at t: a same-second
           fire excludes it, V1.1 C09); a later fire can only enter a
           separate retrospective sensitivity (mode 'retro').
  grading  HorizonBook: a horizon picked on TUNE outcomes is frozen (sha16) and only READ on CHECK; picking on CHECK is refused.
           first_touch: target and stop inside the same price bin = AMBIGUOUS, scored as the stop (never the favourable order);
           passive_fill: a resting order fills only when a later bin trades STRICTLY through its price; a touch is unfilled.
"""
import hashlib, json, os, sys
_TOOLS = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'tools', 'idea_to_grade'))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
import alarm_contract_v1 as C

UNKNOWN = 'UNKNOWN'


class Refused(Exception):
    """a request the contract forbids (the message names the rule)"""


# ---------------------------------------------------------------------------------------------------- source
def opening_share(s07, s08, s09, s10):
    """HF3: (opened long + opened short) / (opened + closed). UNKNOWN when any part is missing or nothing traded."""
    parts = (s07, s08, s09, s10)
    if any(p is None for p in parts): return UNKNOWN
    den = s07 + s08 + s09 + s10
    if den <= 0: return UNKNOWN
    return (s07 + s08) / den


def closing_share(s11):
    """closing share = 1 - S11, only when S11 is valued (S11 is EMPTY when its denominator is 0)."""
    if s11 is None or s11 == UNKNOWN: return UNKNOWN
    if not 0.0 <= s11 <= 1.0: raise Refused('S11 outside [0, 1]: %r' % (s11,))
    return 1.0 - s11


def hit_exposure_share(prior_qty, hit_accounts):
    """HLPOSM HM3: the prior side exposure belonging to accounts hit by a liquidation, over the prior side total. Each account once."""
    tot = sum(prior_qty.values())
    if tot <= 0: return UNKNOWN
    return sum(prior_qty[a] for a in set(hit_accounts) if a in prior_qty) / tot


def closed_share(prior_qty, closed_qty):
    """the share of the prior side exposure actually closed by liquidation fills (what a 'wiped' claim needs)."""
    tot = sum(prior_qty.values())
    if tot <= 0: return UNKNOWN
    return sum(min(q, prior_qty.get(a, 0.0)) for a, q in closed_qty.items()) / tot


def wiped_from_readings(prior_qty, hit_accounts, closed_qty, bar):
    return wiped(closed_share(prior_qty, closed_qty), bar)


def wiped(closed, bar):
    """'the side was wiped' is read from CLOSED volume only; UNKNOWN stays UNKNOWN."""
    if closed == UNKNOWN: return UNKNOWN
    return closed >= bar


# ---------------------------------------------------------------------------------------------------- side
def side_of(signed):
    if signed is None or signed == UNKNOWN or signed != signed: return UNKNOWN
    if signed > 0: return 1
    if signed < 0: return -1
    return UNKNOWN


# ---------------------------------------------------------------------------------------------------- machine
class AlarmMachine:
    """One alarm on one coin, both directions apart. feed(t, value, cut, reset) with value = the signed trigger reading (None = missing),
    cut / reset = the current cut and reset level for |value| (from the coin's own past, given by the caller with their vintage)."""
    PHASES = ('IDLE', 'RUNNING', 'FADING', 'ENDED', UNKNOWN)
    CUT_GUARD = True                                                        # onset needs the VALUE to cross the current cut

    def __init__(self, alarm, coin, fade_frac=0.5, fade_hold_s=60, min_gap_s=900, source_delay_s=0):
        self.alarm, self.coin = alarm, coin
        self.fade_frac, self.fade_hold_s, self.min_gap_s, self.source_delay_s = fade_frac, fade_hold_s, min_gap_s, source_delay_s
        self.st = {d: dict(phase='IDLE', armed=True, runmax=0.0, below_since=None, onset=None, last_emit=None, prev=None, seq=0)
                   for d in (1, -1)}
        self.events, self.diag = [], []

    def snapshot(self):
        return json.loads(json.dumps(dict(st={str(k): v for k, v in self.st.items()}, events=self.events, diag=self.diag)))

    def restore(self, snap):
        self.st = {int(k): dict(v) for k, v in snap['st'].items()}
        self.events, self.diag = list(snap['events']), list(snap['diag'])
        return self

    def episode_id(self, d, onset):
        return '%s:%s:%s:%d' % (self.alarm, self.coin, onset, d)

    def feed(self, t, value, cut, reset):
        if value is None or value == UNKNOWN or cut is None or reset is None:
            self.on_gap(t)
            return
        self.on_value(t, value, cut, reset)

    def on_gap(self, t):
        for d, s in self.st.items():
            if s['phase'] in ('RUNNING', 'FADING'):
                s['phase'] = UNKNOWN; self.diag.append((t, d, 'GAP'))       # never ENDED, never FADING on a gap
            s['below_since'] = None
            s['prev'] = None                                                # the next value cannot make an onset from a gap

    def on_value(self, t, value, cut, reset):
        for d, s in self.st.items():
            v = value * d                                                   # the reading on this direction's side
            prev = s['prev']; s['prev'] = v
            if s['phase'] == UNKNOWN:
                if v <= reset:
                    s['phase'] = 'ENDED'; self.diag.append((t, d, 'ENDED_AFTER_GAP'))
                else:
                    s['phase'] = 'RUNNING' if v >= s['runmax'] * self.fade_frac else 'FADING'
                    s['runmax'] = max(s['runmax'], v)
                    continue
            if s['phase'] in ('RUNNING', 'FADING'):
                s['runmax'] = max(s['runmax'], v)
                if v <= reset:
                    s['phase'] = 'ENDED'; s['below_since'] = None
                elif v < self.fade_frac * s['runmax']:
                    if s['below_since'] is None: s['below_since'] = t
                    if t - s['below_since'] >= self.fade_hold_s: s['phase'] = 'FADING'
                else:
                    s['below_since'] = None; s['phase'] = 'RUNNING'
            if s['phase'] in ('IDLE', 'ENDED'):
                gap_ok = s['last_emit'] is None or t - s['last_emit'] >= self.min_gap_s
                if v <= reset: s['armed'] = True
                if v >= cut and s['armed'] and gap_ok:
                    if self.CUT_GUARD and (prev is None or prev >= cut):                         # no valued step below the CURRENT cut: only the cut moved
                        self.diag.append((t, d, 'CUT_CHANGE' if prev is not None else 'NO_PRIOR_VALUE'))
                        s['armed'] = False
                        continue
                    s.update(phase='RUNNING', armed=False, runmax=v, below_since=None, onset=t, last_emit=t, seq=s['seq'] + 1)
                    self.events.append(dict(alarm=self.alarm, coin=self.coin, side=d, onset_t=t,
                                            emission_t=t + self.source_delay_s, episode_id=self.episode_id(d, t),
                                            stage='START', notice_seq=s['seq']))

    def phase(self, d):
        return self.st[d]['phase']


def run_stream(machine, rows):
    for r in rows: machine.feed(*r)
    return machine


# ---------------------------------------------------------------------------------------------------- clock
def emission_time(observed_t, source_delay_s, confirmations_known_at):
    """None while any confirmation is still missing (None); else the latest availability."""
    if any(k is None for k in confirmations_known_at): return None
    return max([observed_t + source_delay_s] + list(confirmations_known_at))


# ---------------------------------------------------------------------------------------------------- r1
def detect_r1(rows, confirm_known_at, depth=0.005, within_s=1800, lookback_s=86400, upto=None):
    """rows: [(t, px)] ascending. A break: px above the max of px over [t - lookback_s, t) (the current observation EXCLUDED).
    R1: after the break, the price went >= depth beyond the level, then came back to <= level within within_s of the break.
    Emission = max(re-entry t, confirmation receipt). Data after `upto` is not seen (prefix rule)."""
    rows = [r for r in rows if upto is None or r[0] <= upto]
    out, brk = [], None
    for i, (t, px) in enumerate(rows):
        prior = [p for (u, p) in rows[:i] if t - lookback_s <= u < t]
        if brk is None:
            if prior and px > max(prior):
                brk = dict(t=t, level=max(prior), far=px)
            continue
        brk['far'] = max(brk['far'], px)
        if t - brk['t'] > within_s: brk = None; continue
        if px <= brk['level'] and brk['far'] >= brk['level'] * (1 + depth):
            k = confirm_known_at(brk['t'], t)
            em = emission_time(t, 0, [k])
            if em is not None and (upto is None or em <= upto):
                out.append(dict(break_t=brk['t'], reentry_t=t, emission_t=em, level=brk['level']))
            brk = None
    return out


# ---------------------------------------------------------------------------------------------------- registry
def canonical(card):
    """the literal definition only (trigger, cuts, reset, clocks, sources and their editions); names and notes do not count."""
    keys = ('family', 'trigger', 'cuts', 'reset', 'clocks', 'sources', 'side_rule', 'confirmation')
    return hashlib.sha256(json.dumps({k: card.get(k) for k in keys}, sort_keys=True).encode()).hexdigest()[:16]


def membership_api(cards, overlap=None, outcome_corr=None):
    """the call consumers use: overlap and outcome correlation are ANNOTATIONS; they are accepted and ignored for membership."""
    return membership(cards)


def membership(cards):
    """{card id: (status, canonical id)}. Status comes from the literal meaning checks on the card, nothing else.
    Identical canonical definitions merge into the first id (EQUIVALENT_OF)."""
    seen, out = {}, {}
    for c in cards:
        k = canonical(c)
        if k in seen: out[c['id']] = ('EQUIVALENT_OF:' + seen[k], k); continue
        seen[k] = c['id']
        m = c.get('meaning', {})
        if m.get('literal') is False: st = 'DROPPED'
        elif m.get('literal') is True: st = 'RESEARCH_ONLY' if c.get('live_gaps') else 'MEMBER'
        else: st = 'NOT_READY'
        out[c['id']] = (st, k)
    return out


# ---------------------------------------------------------------------------------------------------- waves
class Clusters:
    """market clusters over ONE frozen universe: fires [(fire_id, coin, t)], chained when the gap to the previous fire is <= gap_s,
    split when the chain would exceed max_span_s (flagged CHAIN_SPLIT). Ids and weights are fixed here; subgroups only read them."""

    def __init__(self, fires, universe_id, gap_s=1800, max_span_s=4 * 3600):
        self.universe_id = universe_id
        fs = sorted(fires, key=lambda f: (f[2], f[0]))
        self.cid, self.flags, members = {}, {}, {}
        for (fid, coin, t), (k, flag) in zip(fs, C.chain([f[2] for f in fs], gap_s, max_span_s)):
            if flag: self.flags[k] = 'CHAIN_SPLIT'
            cur = '%s:W%05d' % (universe_id, k + 1)
            self.cid[fid] = cur; members.setdefault(cur, []).append(fid)
        self.size = {c: len(v) for c, v in members.items()}
        self.weight = {fid: 1.0 / self.size[c] for fid, c in self.cid.items()}

    def subgroup(self, fire_ids):
        """ids and weights of a subgroup: read from the frozen build. A fire outside the universe is refused."""
        miss = [f for f in fire_ids if f not in self.cid]
        if miss: raise Refused('fires outside the frozen universe %s: %s' % (self.universe_id, miss[:3]))
        return {f: (self.cid[f], self.weight[f]) for f in fire_ids}


# ---------------------------------------------------------------------------------------------------- controls
def control_eligible(t, fire_times, before_s=4 * 3600, after_s=1800, mode='asof'):
    """asof: a reference moment t is excluded only by a fire in [t - before_s, t] (V1.1: the fire moment itself is never a control; V1 used
    [t - before_s, t) and let t = a fire be its own control, OX-DATA C09). retro (sensitivity only): also (t, t + after_s]."""
    if C.asof_busy(t, sorted(fire_times), before_s): return False
    if mode == 'retro' and any(t < f <= t + after_s for f in fire_times): return False
    return True


# ---------------------------------------------------------------------------------------------------- grading
class HorizonBook:
    """a horizon chosen from outcomes is a TUNED setting: chosen once on TUNE, frozen, then only read on CHECK."""

    def __init__(self):
        self.frozen = {}

    def choose(self, alarm, curve, window):
        if window != 'tune': raise Refused('a horizon may be chosen on TUNE outcomes only (asked: %s)' % window)
        if alarm in self.frozen: raise Refused('horizon of %s already frozen: a new choice is a new version and a try' % alarm)
        h = max(sorted(curve), key=lambda k: curve[k])
        rec = dict(alarm=alarm, horizon=h, tuned=True)
        rec['sha16'] = hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:16]
        self.frozen[alarm] = rec
        return rec

    def evaluate(self, alarm, curve_check):
        if alarm not in self.frozen: raise Refused('no frozen horizon for %s' % alarm)
        h = self.frozen[alarm]['horizon']
        return h, curve_check.get(h)


def first_touch(bins, side, target, stop):
    """bins: [(t, high, low)] after the entry; side +1 long / -1 short; target, stop: prices. Both levels inside one bin = AMBIGUOUS,
    scored as STOP (the order inside a bin is not known)."""
    for t, hi, lo in bins:
        code = C.bin_exit(side, hi, lo, target, stop)
        if code == 'AMBIGUOUS_STOP': return ('AMBIGUOUS', t, 'STOP')
        if code is not None: return (code, t, code)
    return ('TIME', None, 'TIME')


def passive_fill(bins, side, limit, placed_t):
    """a resting buy (side +1) fills only when a bin STARTING after placed_t trades strictly below its limit (a sell: strictly above).
    A touch at the limit is unfilled (queue position unknown)."""
    for t, hi, lo in bins:
        if t <= placed_t: continue
        if C.trades_through(side, hi, lo, limit): return ('FILLED', t)
    return ('UNFILLED', None)
