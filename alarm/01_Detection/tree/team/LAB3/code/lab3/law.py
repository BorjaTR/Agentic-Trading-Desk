"""lab3/law.py (LAB4 proposal days_proof v3, 22 Oct 2026; LAB1 review 08:46:18Z: ONE table): the research law, the one table both lab3.days
(the guard by purpose) and lab3.reader (Reader.law) answer from; neither keeps its own day constants. Standard Python only (lab3.reader
stays numpy- and pyarrow-free). The rows are lab3/days.py 734d38d4's RESEARCH_REFUSED plus PROOF_SEALED.
PROOF_SEALED (LAB1 08:33:24Z (2); the owner 08:43 Berlin 22 Oct: Jan-Mar 2026 is the one-look proof): research refuses 1 Jan to 9 Mar 2026
too (10 Mar on was refused already). PROOF_OPEN: the days the 'proof' purpose of lab3.days reads besides what research reads.
LAB1 23 Oct 2026 (the owner 05:45Z: "even if we open September to March we still have 6 months of blind data"): research reads
Sep 2025 to 31 Mar 2026; from 1 Apr 2026 refused (BLIND). The owner 06:01Z: "they can use data from September 2025 to May 2026":
research reads to 31 May 2026; from 1 Jun 2026 refused (BLIND)."""

import datetime

# BLIND RELEASE SCHEDULE (LAB1 23 Oct 2026, LEAD PROCESS_CHANGES_V1 OXP1-02; frozen BEFORE the first CHECK open; data only, it opens nothing):
# the blind span opens ONE month at a time, in this order, and only when a frozen card's CHECK has passed and LAB1 names that card;
# each release moves PROOF_OPEN to cover that month (a new law.py version, twin kept, a board line). Days after 22 Oct 2026 are the
# forward record: proof only (the owner 11:16Z: 'every day there is a new day'), never find data for research.
BLIND_SCHEDULE = ((20260601, 20260630), (20260701, 20260731), (20260801, 20260831), (20260901, 20260930), (20261001, 20261022))
PROOF_OPEN = (0, 0)       # LAB1 23 Oct 05:5xZ: nothing open to 'proof' now; Jun-Oct 2026 opens one month at a time, only for a frozen card (LAB1 names it)
RESEARCH_REFUSED = ((20260601, 99999999, 'BLIND (the owner 06:01Z 23 Oct: find window Sep 2025 to May 2026; Jun to Oct 2026 blind)'),)
# 05:52Z to 06:0xZ 23 Oct the row was (20260401, on, BLIND, the owner 05:45Z); the owner widened it at 06:01Z.
# Rows before 23 Oct (history, no longer read): (20260101, 20260309, PROOF_SEALED), (20260310, 20260405, NOT_YET_OPEN),
# (20260406, 20260705, KEPT_ASIDE), (20260706, 20260719, JUL_UNSEEN), (20260920, 20261007, FINAL_BLOCK), (20260706, on, reading law).


def _valid_day(day):
    """YYYYMMDD and a real calendar day, else ValueError (OUTSIDE D04-03: 20260230 was accepted)"""
    text = str(day)
    if len(text) != 8 or not text.isdigit():
        raise ValueError('day %r: must be YYYYMMDD' % (day,))
    datetime.date(int(text[:4]), int(text[4:6]), int(text[6:]))
    return int(text)


def research_refusal(day):
    """the first row's reason holding day, else None"""
    d = _valid_day(day)
    for lo, hi, why in RESEARCH_REFUSED:
        if lo <= d <= hi:
            return why
    return None


# QUARANTINE (LAB1 23 Oct 2026, STRATEGY-134049, CHECK_WINDOW_RULE_V3; ALARM 13:39:00Z disclosed): parts holding COMPUTED, unread
# OUTCOME labels of the CHECK months. Every purpose but 'proof' (freeze_judge's logged open, one run) is refused, whatever the seal says.
# (part name prefix, first day, last day, why). The data stays where it is (no move); the reader is the lock.
QUARANTINE = (('ADES.N2V1', 20260301, 20260531, 'QUARANTINE: ALARM N2V1 outcome labels of the CHECK months (STRATEGY-134049)'),
              ('ADES.N3V1', 20260301, 20260531, 'QUARANTINE: ALARM N3V1 outcome labels of the CHECK months (STRATEGY-134049)'))
# EPI.* was added 14:37Z on LAB1's WRONG description ('after-fire fields') and removed 15:2xZ: giveback and growth are cut AT the alarm
# (episode_blocks; test_alarm_profile plants 1e12 after the alarm), so EPI is known at the fire and is not an outcome (QUANT 15:17:26Z).


# STORES (LAB1 23 Oct 2026, STRATEGY-160923): raw stores outside lab_days that hold BUILD, CHECK and BLIND months. No tool reads them
# directly: a reader is written first, it reads through lab3 (a lab_days part) or calls store_refusal(store, day, purpose) before any
# file is opened. CHECK months (1 Mar to 31 May 2026): values for build/check/live; OUTCOMES only through freeze_judge 'proof'.
# BLIND (1 Jun 2026 on): research refused (RESEARCH_REFUSED), proof only for a named frozen card.
STORES = (('hl_node_data', '<ARCHIVE_DISK>/volat_archive/hl_node_data', 'HL node misc_events_by_block + node_fills_by_block (STRATEGY, the owner 16:05Z)'),
          ('hl_node_cols', '<ARCHIVE_DISK>/volat_archive/hl_node_cols', 'hl_node_read V1 converted columns (LAB1 24 Oct, labcore V2_5)'),
          ('candidate_days', '<DATA_ROOT>/candidate_days', 'the 5 HL candidate producers X1 parts (owner 07:35:18Z: on the Mac; labcore V2_5)'))


def store_refusal(store, day, purpose):
    """the reason a registered raw store may not be read on day for purpose, else None; an unregistered store is refused"""
    if store not in {s[0] for s in STORES}:
        return 'UNREGISTERED STORE %r: register it in law.STORES first' % (store,)
    if purpose == 'proof':
        return proof_refusal(day)
    if purpose == 'research':
        return research_refusal(day)
    _valid_day(day)
    return None


def quarantine_refusal(part, day):
    """the reason a part of a day is quarantined, else None"""
    d = _valid_day(day)
    for pre, lo, hi, why in QUARANTINE:
        if str(part).startswith(pre) and lo <= d <= hi:
            return why
    return None


def proof_refusal(day):
    """the proof purpose: PROOF_OPEN days, else what research may read"""
    d = _valid_day(day)
    if PROOF_OPEN[0] <= d <= PROOF_OPEN[1]:
        return None
    return research_refusal(d)
