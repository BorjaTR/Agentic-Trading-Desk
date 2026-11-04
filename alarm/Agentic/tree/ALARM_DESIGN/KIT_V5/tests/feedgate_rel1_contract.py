#!/usr/bin/env python3
"""feedgate_rel1_contract.py (SCOUT K12, 31 Oct 2026; TEST, NOT REVIEWED): THE contract of the feed-gate editions of GRADE's and MONTH's Outcomes
step (SCOUT 31 Oct ~06:40Z: "take the feed-gate dev path out of GRADE and MONTH") from the old files of an Alarm folder, each by listed,
counted text replacements only (test_feedgate_rel1.py re-applies the same list to the old file and compares byte for byte):
  event_outcomes_rel1.py      = event_outcomes.py 7332c1f005e958ef + the gate from FEED_GATE, the research days from RESEARCH_STORE,
                                RUN_PARALLEL run_parallel_rel1.py, RELEASE RELEASE_event_outcomes_V3_REL1.json
  run_parallel_rel1.py        = run_parallel.py c48230fb71f55090 + EO event_outcomes_rel1.py, run_lab's gate from FEED_GATE
  event_outcomes_aw1_rel1.py  = event_outcomes_aw1.py a66240b3332ddf00 + event_outcomes_rel1's changes, RELEASE ..._AW1_REL1.json
  RELEASE_event_outcomes_V3_REL1.json  = V3_CANDIDATE with the two editions in place of event_outcomes.py and run_parallel.py
  RELEASE_event_outcomes_AW1_REL1.json = AW1 with event_outcomes_aw1_rel1.py in place of event_outcomes_aw1.py and V3_REL1 in place of
                                         V3_CANDIDATE
Stage 2 (sha16s from stage 1): alarm_grade_chain_v2_0_3_to20251231.sh (v2_0_2 + Outcomes event_outcomes_rel1, RESEARCH_STORE),
  alarm_grade_chain_v2_2_3_to20260430.sh (v2_2_2 + event_outcomes_aw1_rel1), JOB_GRADE_V8 and JOB_MONTH_V8 (V7 + the new chain, RESEARCH_STORE
  given to it) and queue_job_v6.py (v5 + the V8 templates and the job placeholder @@RESEARCH_STORE@@).
build(al) makes the ten texts in memory (test_feedgate_rel1.py compares them with the files of the release, byte for byte); the
command writes each once (opened 'x') under OUT at its path in the Alarm folder and prints path, sha16, bytes. Never deletes.
  python3 -B feedgate_rel1_contract.py <Alarm folder (old files)> <OUT>"""
import hashlib, json, os, sys

T01 = os.path.join('01_Detection', 'tree', 'team', 'RESEARCH', 'tools')
EO_OLD = os.path.join(T01, 'event_outcomes', 'event_outcomes.py')
EO_NEW = os.path.join(T01, 'event_outcomes', 'event_outcomes_rel1.py')
RP_OLD = os.path.join(T01, 'event_profile', 'run_parallel.py')
RP_NEW = os.path.join(T01, 'event_profile', 'run_parallel_rel1.py')
AW_OLD = os.path.join(T01, 'alarm_process', 'event_outcomes_aw1.py')
AW_NEW = os.path.join(T01, 'alarm_process', 'event_outcomes_aw1_rel1.py')
V3_OLD = os.path.join(T01, 'event_outcomes', 'RELEASE_event_outcomes_V3_CANDIDATE.json')
V3_NEW = os.path.join(T01, 'event_outcomes', 'RELEASE_event_outcomes_V3_REL1.json')
AR_OLD = os.path.join(T01, 'alarm_process', 'RELEASE_event_outcomes_AW1.json')
AR_NEW = os.path.join(T01, 'alarm_process', 'RELEASE_event_outcomes_AW1_REL1.json')
OLD_SHA = {EO_OLD: '7332c1f005e958ef', RP_OLD: 'c48230fb71f55090', AW_OLD: 'a66240b3332ddf00', V3_OLD: '2dd498a3b2c1a61e',
           AR_OLD: '0de68ccfca3a7376'}

HELPERS = '''

def feed_gate():
    """K12 rel1: the feed's stop gate is the environment FEED_GATE (the settings key FEED_GATE; the job gives it to the chain, the chain to
    this run and its workers). It must be set: unset is refused NO_FEED_GATE (never the built-in team path of labcore.jobgate); empty =
    no gate (a machine without the feed), the rule of detect_v2's --gate"""
    if 'FEED_GATE' not in os.environ:
        raise Refused('NO_FEED_GATE', 'set FEED_GATE to the feed stop gate file (the settings key FEED_GATE), or to empty for no gate')
    return os.environ['FEED_GATE']


def gate_wait(log=print):
    """K12 rel1: labcore.jobgate.gate_wait on the FEED_GATE file (as before: blocks while its first line is not RUN; a missing file reads
    PAUSE); no gate (FEED_GATE empty): 0 at once, nothing read"""
    g = feed_gate()
    return jobgate.gate_wait(gate=g, log=log) if g else 0


def research_store(lab_root):
    """K12 rel1: the research days are the environment RESEARCH_STORE (the settings key RESEARCH_STORE) when it is set and not empty,
    else (as before) research_days beside the lab days"""
    return os.environ.get('RESEARCH_STORE') or os.path.join(os.path.dirname(os.path.abspath(lab_root)), 'research_days')
'''
REFUSED_CLASS = '''class Refused(PermissionError):
    """a refusal by name: nothing is read or written after it"""
    def __init__(self, code, text):
        super().__init__('%s: %s' % (code, text)); self.code = code
'''
CHANGES_EO = '''  - the feed's stop gate is the environment FEED_GATE (the settings key; the job and the chain set it): it must be set (unset: refused
    NO_FEED_GATE); empty = no gate (a machine without the feed), as detect_v2's --gate; a gate file is waited on with
    labcore.jobgate.gate_wait(gate=FEED_GATE) at the run start, the build start and between days, as before (the old file waited on
    labcore.jobgate's built-in GATE, the Mac dev tree's team/FEED/stops/BACKFILL_GATE.txt; on another machine that file is missing, reads
    PAUSE, and the run waited for ever); feed_gate(), gate_wait() and research_store() follow the class Refused;
  - the research days are the environment RESEARCH_STORE (the settings key) when it is set and not empty, else research_days beside the
    lab days, as before;
  - RUN_PARALLEL is event_profile/run_parallel_rel1.py (its outcomes workers run event_outcomes_rel1.py; run_parallel.py's ran the old file);
'''
EO_EDITS = [
    ('"""event_outcomes.py: OUTCOMES, code VERSION 3 (',
     '"""event_outcomes_rel1.py: new edition by SCOUT K12 for the clean release (31 Oct 2026; TEST, NOT REVIEWED; SCOUT 31 Oct: "take the\n'
     'feed-gate dev path out of GRADE and MONTH"). Old file: event_outcomes.py 7332c1f005e958ef (VERSION 3), never edited. Changed, nothing else:\n'
     + CHANGES_EO +
     '  - its release record is RELEASE_event_outcomes_V3_REL1.json (V3_CANDIDATE with this file and run_parallel_rel1.py in place of the old).\n'
     'VERSION, every value, rule, seal and output format are event_outcomes.py\'s. The rest of this text is event_outcomes.py\'s.\n'
     'event_outcomes.py: OUTCOMES, code VERSION 3 (', 1),
    ("RELEASE = os.path.join(HERE, 'RELEASE_event_outcomes_V3_CANDIDATE.json')",
     "RELEASE = os.path.join(HERE, 'RELEASE_event_outcomes_V3_REL1.json')         # K12 rel1: this edition's release record", 1),
    ("RUN_PARALLEL = os.path.join(TOOLS, 'event_profile', 'run_parallel.py')",
     "RUN_PARALLEL = os.path.join(TOOLS, 'event_profile', 'run_parallel_rel1.py')   # K12 rel1: its outcomes workers run this edition", 1),
    ('jobgate.gate_wait(log=log)', 'gate_wait(log=log)', 3),
    ("os.path.join(os.path.dirname(os.path.abspath(lab_root)), 'research_days')", 'research_store(lab_root)', 2),
    (REFUSED_CLASS, REFUSED_CLASS + HELPERS, 1),                   # last: the helpers hold the old research-days expression
]
AW_EDITS = [
    ('# event_outcomes_aw1.py, aw1 (STRATEGY 28 Oct 2026',
     '# event_outcomes_aw1_rel1.py (SCOUT K12, 31 Oct 2026; TEST, NOT REVIEWED): event_outcomes_aw1.py a66240b3332ddf00, never edited, with\n'
     "# event_outcomes_rel1.py's changes and nothing else: the feed's stop gate is the environment FEED_GATE (must be set: unset refused\n"
     '# NO_FEED_GATE; empty = no gate), never labcore.jobgate\'s built-in dev-tree GATE; the research days are RESEARCH_STORE when set;\n'
     '# RUN_PARALLEL is run_parallel_rel1.py (only named in the code inventory: aw1 runs Outcomes in its own process, run 0); its release\n'
     "# record is RELEASE_event_outcomes_AW1_REL1.json. The rest of this file is event_outcomes_aw1.py's.\n"
     '# event_outcomes_aw1.py, aw1 (STRATEGY 28 Oct 2026', 1),
    ("RELEASE = os.path.join(HERE, 'RELEASE_event_outcomes_AW1.json')   # aw1",
     "RELEASE = os.path.join(HERE, 'RELEASE_event_outcomes_AW1_REL1.json')   # aw1; K12 rel1: this edition's release record", 1),
    ("RUN_PARALLEL = os.path.join(TOOLS, 'event_profile', 'run_parallel.py')",
     "RUN_PARALLEL = os.path.join(TOOLS, 'event_profile', 'run_parallel_rel1.py')   # K12 rel1 (only in the code inventory: run 0)", 1),
    ('jobgate.gate_wait(log=log)', 'gate_wait(log=log)', 3),
    ("os.path.join(os.path.dirname(os.path.abspath(lab_root)), 'research_days')", 'research_store(lab_root)', 2),
    (REFUSED_CLASS, REFUSED_CLASS + HELPERS, 1),                   # last: the helpers hold the old research-days expression
]
RP_HELPER = '''

def feed_gate_wait(jobgate, log):
    """K12 rel1: run_lab's gate is the environment FEED_GATE (the settings key): it must be set (unset: refused NO_FEED_GATE, never the
    built-in team path of labcore.jobgate); empty = no gate; a gate file: labcore.jobgate.gate_wait(gate=FEED_GATE), as before"""
    if 'FEED_GATE' not in os.environ:
        raise Refusal('NO_FEED_GATE', 'set FEED_GATE to the feed stop gate file (the settings key FEED_GATE), or to empty for no gate')
    g = os.environ['FEED_GATE']
    return jobgate.gate_wait(gate=g, log=log) if g else 0
'''
REFUSAL_CLASS = '''class Refusal(Exception):
    def __init__(self, code, msg):
        super().__init__('%s: %s' % (code, msg)); self.code = code
'''
RP_EDITS = [
    ('"""run_parallel.py: run Profile (event_profile), Context (alarm_context ed2), Outcomes (event_outcomes) or Cause (event_cause) over a date',
     '"""run_parallel_rel1.py: new edition by SCOUT K12 for the clean release (31 Oct 2026; TEST, NOT REVIEWED). Old file: run_parallel.py\n'
     'c48230fb71f55090, never edited. Changed, nothing else: the Outcomes workers run event_outcomes/event_outcomes_rel1.py (EO); the gate\n'
     'run_lab waits on (Profile, Context) is the environment FEED_GATE (feed_gate_wait: it must be set, unset is refused NO_FEED_GATE; empty =\n'
     "no gate), never labcore.jobgate's built-in dev-tree GATE. The rest of this text is run_parallel.py's.\n"
     'run_parallel.py: run Profile (event_profile), Context (alarm_context ed2), Outcomes (event_outcomes) or Cause (event_cause) over a date', 1),
    ("EO = os.path.join(HERE, '..', 'event_outcomes', 'event_outcomes.py')",
     "EO = os.path.join(HERE, '..', 'event_outcomes', 'event_outcomes_rel1.py')   # K12 rel1: the workers run the rel1 edition", 1),
    ('waited = jobgate.gate_wait(log=lambda s: print(s, flush=True))', 'waited = feed_gate_wait(jobgate, log=lambda s: print(s, flush=True))', 1),
    (REFUSAL_CLASS, REFUSAL_CLASS + RP_HELPER, 1),
]
EDITS = ((EO_OLD, EO_NEW, EO_EDITS), (RP_OLD, RP_NEW, RP_EDITS), (AW_OLD, AW_NEW, AW_EDITS))


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def apply(text, edits, name):
    """the listed replacements, each found exactly its count of times in the old text (else refused)"""
    for old, new, n in edits:
        c = text.count(old)
        if c != n:
            raise SystemExit('REFUSED: %s: %r found %d times, want %d' % (name, old[:70], c, n))
        text = text.replace(old, new)
    return text


def tree_rel(p):
    """a path of the Alarm folder relative to the detection tree (the release records' 'team/...' keys)"""
    return os.path.relpath(p, os.path.join('01_Detection', 'tree'))


def v3_record(old, eo_sha, rp_sha):
    d = json.loads(old); files = {}
    for k, v in d['files'].items():
        if k == tree_rel(EO_OLD):
            files[tree_rel(EO_NEW)] = {'role': 'event_outcomes VERSION 3, release edition rel1 (K12: the gate from FEED_GATE, the research days '
                                               'from RESEARCH_STORE)', 'sha16': eo_sha}
        elif k == tree_rel(RP_OLD):
            files[tree_rel(RP_NEW)] = {'role': 'the shared launcher (outcomes branch) run executes, release edition rel1 (K12: workers run '
                                               'event_outcomes_rel1.py; run_lab\'s gate from FEED_GATE)', 'sha16': rp_sha}
        else:
            files[k] = v
    d['files'] = files
    d['by'] = 'SCOUT K12 feedgate_rel1_contract.py, 31 Oct 2026'
    d['release'] = 'event_outcomes_V3_REL1'
    d['reason'] = ('the clean release (K12, SCOUT 31 Oct: the feed-gate dev path out of GRADE and MONTH): RELEASE_event_outcomes_V3_CANDIDATE.json '
                   '2dd498a3b2c1a61e with event_outcomes_rel1.py and run_parallel_rel1.py in place of event_outcomes.py and run_parallel.py; '
                   'every other file, release, runtime and finding the same')
    d['replaces'] = 'none (V3_CANDIDATE stays for the chains that run event_outcomes.py)'
    d['status'] = 'TEST, NOT REVIEWED (SCOUT K12; V3_CANDIDATE: CANDIDATE: NOT APPROVED; independent re-review of A51-01..07 pending)'
    return json.dumps(d, indent=1) + '\n'


def aw1_record(old, aw_sha, v3_sha):
    d = json.loads(old); files = {}
    for k, v in d['files'].items():
        if k == tree_rel(AW_OLD):
            files[tree_rel(AW_NEW)] = {'role': 'event_outcomes V3 with the alarm kit window classes (aw1), release edition rel1 (K12: the gate '
                                               'from FEED_GATE, the research days from RESEARCH_STORE)', 'sha16': aw_sha}
        else:
            files[k] = v
    d['files'] = files
    d['releases'] = {(tree_rel(V3_NEW) if r == tree_rel(V3_OLD) else r): (v3_sha if r == tree_rel(V3_OLD) else s)
                     for r, s in d['releases'].items()}
    d['release'] = 'event_outcomes_AW1_REL1'
    d['status'] = 'TEST, NOT REVIEWED (SCOUT K12; aw1: STRATEGY, ALARM_DESIGN kit)'
    d['by'] = 'SCOUT K12 feedgate_rel1_contract.py, 31 Oct 2026'
    d['reason'] = ('the clean release (K12, SCOUT 31 Oct: the feed-gate dev path out of GRADE and MONTH): RELEASE_event_outcomes_AW1.json '
                   '0de68ccfca3a7376 with event_outcomes_aw1_rel1.py in place of event_outcomes_aw1.py and RELEASE_event_outcomes_V3_REL1.json '
                   'in place of V3_CANDIDATE; the window table the same')
    d['replaces'] = 'none (AW1 stays for the chains that run event_outcomes_aw1.py)'
    return json.dumps(d, indent=1) + '\n'


# ---------------------------------------------------------------- stage 2: the chains, the job templates and the queue (sha16s from stage 1)
C_OLD = os.path.join('03_Grading', 'tree', 'tools', 'alarm_process', 'alarm_grade_chain_v2_0_2_to20251231.sh')
C_NEW = os.path.join('03_Grading', 'tree', 'tools', 'alarm_process', 'alarm_grade_chain_v2_0_3_to20251231.sh')
M_OLD = os.path.join('03_Grading', 'tree', 'tools', 'month_parts', 'alarm_grade_chain_v2_2_2_to20260430.sh')
M_NEW = os.path.join('03_Grading', 'tree', 'tools', 'month_parts', 'alarm_grade_chain_v2_2_3_to20260430.sh')
KJ = os.path.join('Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'jobs')
G7, G8 = os.path.join(KJ, 'JOB_GRADE_V7.job.sh.txt'), os.path.join(KJ, 'JOB_GRADE_V8.job.sh.txt')
M7, M8 = os.path.join(KJ, 'JOB_MONTH_V7.job.sh.txt'), os.path.join(KJ, 'JOB_MONTH_V8.job.sh.txt')
Q5 = os.path.join('Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'tools', 'queue_job_v5.py')
Q6 = os.path.join('Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'tools', 'queue_job_v6.py')
OLD_SHA.update({C_OLD: '3628339f9fefb7cd', M_OLD: 'd2bc556e5adaa1a4', G7: '66d2e78a3a3b37bf', M7: '0d5038a444250202', Q5: '51864a030f5cfb20'})
GATE_ABS = '[ -z "$FEED_GATE" ] || [ "${FEED_GATE#/}" != "$FEED_GATE" ] || { echo "NO_FEED_GATE: FEED_GATE is not an absolute path: $FEED_GATE"; exit 2; }\n'
STORE_CHECK = ('# K12 (v2_0_3, v2_2_3): the research days (settings RESEARCH_STORE) must be set, an absolute path; Outcomes reads them and the gate\n'
               '# from the environment, so both are exported\n'
               '[ -n "${RESEARCH_STORE:-}" ] && [ "${RESEARCH_STORE#/}" != "$RESEARCH_STORE" ] || { echo "NO_RESEARCH_STORE: set RESEARCH_STORE to the '
               'research days, an absolute path (the job fills it from the settings file)"; exit 2; }\n'
               'export FEED_GATE RESEARCH_STORE\n')


def chain_edits(m):
    head = ('#!/bin/bash\n'
            '# alarm_grade_chain_v2_0_3_to20251231.sh (SCOUT K12, 31 Oct 2026, home team/RESEARCH/tools/alarm_process; TEST, NOT REVIEWED):\n'
            '# alarm_grade_chain_v2_0_2_to20251231.sh 3628339f9fefb7cd with only Outcomes (step 5) changed (SCOUT 31 Oct: "take the feed-gate dev\n'
            '# path out of GRADE and MONTH"): event_outcomes_rel1.py (%s: event_outcomes.py with the feed\'s stop gate from FEED_GATE, never\n'
            '# labcore.jobgate\'s built-in dev-tree GATE, and the research days from RESEARCH_STORE), its workers run_parallel_rel1.py (%s), its\n'
            '# release record RELEASE_event_outcomes_V3_REL1.json (%s); the three checked by sha16 before any step and named in INPUTS_<V>.txt (4\n'
            '# lines appended: outcomes, launcher, release, research); the caller gives RESEARCH_STORE (the settings key: an absolute path) as it\n'
            '# gives FEED_GATE, and the chain exports both to Outcomes. The rest of this header is v2_0_2\'s.\n'
            '#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> RESEARCH_STORE=<research days> [LEAN=..] [BASE=..] [SCREEN=1] '
            'bash alarm_grade_chain_v2_0_3_to20251231.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]\n') % (m[EO_NEW], m[RP_NEW], m[V3_NEW])
    return [('#!/bin/bash\n', head, 1),
            (GATE_ABS, GATE_ABS + STORE_CHECK, 1),
            ('PINS_SHA=17f89bef42400d38   # K12: detect_v2.py, idea_to_grade_rel1.py, I2G_PINS_V2_REL1.json\n',
             'PINS_SHA=17f89bef42400d38   # K12: detect_v2.py, idea_to_grade_rel1.py, I2G_PINS_V2_REL1.json\n'
             'EO_SHA=%s; RP_SHA=%s; REL_SHA=%s   # K12 v2_0_3: event_outcomes_rel1.py, run_parallel_rel1.py, RELEASE_event_outcomes_V3_REL1.json\n'
             % (m[EO_NEW], m[RP_NEW], m[V3_NEW]), 1),
            ('ckf $DET $DET_SHA; ckf $I2G $I2G_SHA; ckf $PINS $PINS_SHA\n',
             'ckf $DET $DET_SHA; ckf $I2G $I2G_SHA; ckf $PINS $PINS_SHA\n'
             'EO=$T/event_outcomes/event_outcomes_rel1.py; RP=$T/event_profile/run_parallel_rel1.py; REL=$T/event_outcomes/RELEASE_event_outcomes_V3_REL1.json\n'
             'ckf $EO $EO_SHA; ckf $RP $RP_SHA; ckf $REL $REL_SHA\n', 1),
            ('"$PINS_SHA" "$PINS" "${FEED_GATE:-none}" >> "$W/INPUTS_${V}.txt"\n',
             '"$PINS_SHA" "$PINS" "${FEED_GATE:-none}" >> "$W/INPUTS_${V}.txt"\n'
             'printf \'outcomes\\t%s\\t%s\\nlauncher\\t%s\\t%s\\nrelease\\t%s\\t%s\\nresearch\\t%s\\n\' "$EO_SHA" "$EO" "$RP_SHA" "$RP" "$REL_SHA" "$REL" '
             '"$RESEARCH_STORE" >> "$W/INPUTS_${V}.txt"\n', 1),
            ('$PY -B $T/event_outcomes/event_outcomes.py run 1 ', '$PY -B $EO run 1 ', 1)]


def month_edits(m):
    head = ('#!/bin/bash\n'
            '# alarm_grade_chain_v2_2_3_to20260430.sh (SCOUT K12, 31 Oct 2026, home team/RESEARCH/tools/month_parts; TEST, NOT REVIEWED):\n'
            '# alarm_grade_chain_v2_2_2_to20260430.sh d2bc556e5adaa1a4 with only Outcomes (step 5) changed (SCOUT 31 Oct: "take the feed-gate dev\n'
            '# path out of GRADE and MONTH"): event_outcomes_aw1_rel1.py (%s: event_outcomes_aw1.py with the feed\'s stop gate from\n'
            '# FEED_GATE, never labcore.jobgate\'s built-in dev-tree GATE, and the research days from RESEARCH_STORE; run 0 as before) with its\n'
            '# release record RELEASE_event_outcomes_AW1_REL1.json (%s); both checked by sha16 and named in INPUTS_<V>.txt, which also gets a\n'
            '# research line; the caller gives RESEARCH_STORE (the settings key: an absolute path) as it gives FEED_GATE, and the chain exports\n'
            '# both to Outcomes. The rest of this header is v2_2_2\'s.\n'
            '#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> RESEARCH_STORE=<research days> [PARTS=2..26] [LEAN=..] '
            '[BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_2_3_to20260430.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]\n') % (m[AW_NEW], m[AR_NEW])
    return [('#!/bin/bash\n', head, 1),
            (GATE_ABS, GATE_ABS + STORE_CHECK, 1),
            ('EO_SHA=a66240b3332ddf00; REL_SHA=0de68ccfca3a7376', 'EO_SHA=%s; REL_SHA=%s' % (m[AW_NEW], m[AR_NEW]), 1),
            ('EO=$AP/event_outcomes_aw1.py;', 'EO=$AP/event_outcomes_aw1_rel1.py;', 1),
            ('ckf event_outcomes_aw1.py $EO_SHA; ckf RELEASE_event_outcomes_AW1.json $REL_SHA',
             'ckf event_outcomes_aw1_rel1.py $EO_SHA; ckf RELEASE_event_outcomes_AW1_REL1.json $REL_SHA', 1),
            ('"$EO_SHA" "$EO" "$REL_SHA" "$AP/RELEASE_event_outcomes_AW1.json" >> "$W/INPUTS_${V}.txt"\n',
             '"$EO_SHA" "$EO" "$REL_SHA" "$AP/RELEASE_event_outcomes_AW1_REL1.json" >> "$W/INPUTS_${V}.txt"\n', 1),
            ('printf \'gate\\t%s\\n\' "${FEED_GATE:-none}" >> "$W/INPUTS_${V}.txt"\n',
             'printf \'gate\\t%s\\n\' "${FEED_GATE:-none}" >> "$W/INPUTS_${V}.txt"\nprintf \'research\\t%s\\n\' "$RESEARCH_STORE" >> "$W/INPUTS_${V}.txt"\n', 1)]


def grade8_edits(m):
    return [('(ALARM_DESIGN KIT_V5 JOB_GRADE_V7, template @@TPLSHA@@): 10 Sep-31 Dec 2025 grade of @@IDEA@@, variants @@ITEMS_LIST@@, against 3 '
             'matched random moments per fire (alarm_grade_chain_v2_0_2_to20251231: v2_0_1',
             '(ALARM_DESIGN KIT_V5 JOB_GRADE_V8, template @@TPLSHA@@): 10 Sep-31 Dec 2025 grade of @@IDEA@@, variants @@ITEMS_LIST@@, against 3 '
             'matched random moments per fire (alarm_grade_chain_v2_0_3_to20251231: v2_0_2 with Outcomes event_outcomes_rel1, the feed gate from '
             'FEED_GATE and the research days from RESEARCH_STORE, SCOUT K12; v2_0_2: v2_0_1', 1),
            ('the feed gate FEED_GATE included (JOB_GRADE_V6 with only its chain changed,',
             'the feed gate FEED_GATE and the research days RESEARCH_STORE included (JOB_GRADE_V7 with only its chain changed and RESEARCH_STORE '
             'given to it; V7: JOB_GRADE_V6 with only its chain changed,', 1),
            ('ck $CH/alarm_grade_chain_v2_0_2_to20251231.sh 3628339f9fefb7cd', 'ck $CH/alarm_grade_chain_v2_0_3_to20251231.sh %s' % m[C_NEW], 1),
            ('FEED_GATE=@@FEED_GATE@@ LEAN=$L bash $CH/alarm_grade_chain_v2_0_2_to20251231.sh',
             'FEED_GATE=@@FEED_GATE@@ RESEARCH_STORE=@@RESEARCH_STORE@@ LEAN=$L bash $CH/alarm_grade_chain_v2_0_3_to20251231.sh', 1),
            ('"chain v2_0_2 Sep-Dec, lean $L"', '"chain v2_0_3 Sep-Dec, lean $L"', 1)]


def month8_edits(m):
    return [('(ALARM_DESIGN KIT_V5 JOB_MONTH_V7, template @@TPLSHA@@; chain v2_2_2 in 26 coin parts: v2_2_1',
             '(ALARM_DESIGN KIT_V5 JOB_MONTH_V8, template @@TPLSHA@@; chain v2_2_3 in 26 coin parts: v2_2_2 with Outcomes event_outcomes_aw1_rel1, '
             'the feed gate from FEED_GATE and the research days from RESEARCH_STORE, SCOUT K12; v2_2_2: v2_2_1', 1),
            ('SCOUT K12; JOB_MONTH_V6 with only its chain changed, CLEAN_RELEASE_V1:',
             'SCOUT K12; JOB_MONTH_V7 with only its chain changed and RESEARCH_STORE given to it; V7: JOB_MONTH_V6 with only its chain changed, '
             'CLEAN_RELEASE_V1:', 1),
            ('every machine path from the settings file, the feed gate FEED_GATE included):',
             'every machine path from the settings file, the feed gate FEED_GATE and the research days RESEARCH_STORE included):', 1),
            ('ck $MP/alarm_grade_chain_v2_2_2_to20260430.sh d2bc556e5adaa1a4', 'ck $MP/alarm_grade_chain_v2_2_3_to20260430.sh %s' % m[M_NEW], 1),
            ('FEED_GATE=@@FEED_GATE@@ PARTS=26 LEAN=$L bash $MP/alarm_grade_chain_v2_2_2_to20260430.sh',
             'FEED_GATE=@@FEED_GATE@@ RESEARCH_STORE=@@RESEARCH_STORE@@ PARTS=26 LEAN=$L bash $MP/alarm_grade_chain_v2_2_3_to20260430.sh', 1),
            ('"chain v2_2_2 Sep-Apr in 26 coin parts, lean $L"', '"chain v2_2_3 Sep-Apr in 26 coin parts, lean $L"', 1)]


def queue_edits(m):
    return [('"""queue_job_v5.py (SCOUT for ALARM_DESIGN KIT_V5, 30 Oct 2026; TEST, NOT REVIEWED).',
             '"""queue_job_v6.py (SCOUT K12 for ALARM_DESIGN KIT_V5, 31 Oct 2026; TEST, NOT REVIEWED): queue_job_v5.py 51864a030f5cfb20 with only\n'
             'GRADE and MONTH moved to JOB_GRADE_V8 (%s) and JOB_MONTH_V8 (%s), whose chains v2_0_3 and v2_2_3 run Outcomes with the feed\'s\n'
             'stop gate from FEED_GATE and the research days from RESEARCH_STORE, and the job path placeholder @@RESEARCH_STORE@@ (the settings key\n'
             'RESEARCH_STORE of the machine that runs the job: now one of the keys --job-settings must have). The rest of this text is\n'
             'queue_job_v5.py\'s.\n'
             'queue_job_v5.py (SCOUT for ALARM_DESIGN KIT_V5, 30 Oct 2026; TEST, NOT REVIEWED).' % (m[G8], m[M8]), 1),
            ("'GRADE': '66d2e78a3a3b37bf', 'MONTH': '0d5038a444250202',", "'GRADE': '%s', 'MONTH': '%s'," % (m[G8], m[M8]), 1),
            ("'GRADE': 'JOB_GRADE_V7.job.sh.txt',", "'GRADE': 'JOB_GRADE_V8.job.sh.txt',", 1),
            ("'MONTH': 'JOB_MONTH_V7.job.sh.txt',", "'MONTH': 'JOB_MONTH_V8.job.sh.txt',", 1),
            ("# refused UNPINNED_MODULE); a KIND without one is NOT CLEAN YET",
             "# refused UNPINNED_MODULE; GRADE V8 and MONTH V8: chains v2_0_3 and v2_2_3, Outcomes with the gate from FEED_GATE and the research\n"
             "# days from RESEARCH_STORE, SCOUT K12, 31 Oct); a KIND without one is NOT CLEAN YET", 1),
            ("JOB_NEED = ('PYTHON', 'LAB_DAYS', 'SCRATCH', 'RESEARCH_ROOT')",
             "JOB_NEED = ('PYTHON', 'LAB_DAYS', 'SCRATCH', 'RESEARCH_ROOT', 'RESEARCH_STORE')", 1),
            ("PATHS = ('ALARM', 'PYTHON', 'RESEARCH_ROOT', 'SCRATCH', 'LAB_DAYS', 'FEED_GATE')",
             "PATHS = ('ALARM', 'PYTHON', 'RESEARCH_ROOT', 'SCRATCH', 'LAB_DAYS', 'FEED_GATE', 'RESEARCH_STORE')", 1),
            ('(run queue_job_v5.py from the Alarm folder)', '(run queue_job_v6.py from the Alarm folder)', 1),
            ("'settings_v1_of_queue_job_v5'", "'settings_v1_of_queue_job_v6'", 1),
            ("raise Refused('USAGE queue_job_v5.py ", "raise Refused('USAGE queue_job_v6.py ", 1),
            ('  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v5.py --settings <file>',
             '  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v6.py --settings <file>', 1)]


STAGE2 = ((C_OLD, C_NEW, chain_edits), (M_OLD, M_NEW, month_edits), (G7, G8, grade8_edits), (M7, M8, month8_edits), (Q5, Q6, queue_edits))

def sha16_text(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()[:16]


def build(al):
    """{path in the Alarm folder: text} of the ten new files, made in memory from the old files of the Alarm folder al (each old file
    checked by its sha16 first); nothing is written"""
    for p, s in OLD_SHA.items():
        if sha16(os.path.join(al, p)) != s:
            raise SystemExit('REFUSED: %s is %s, not %s' % (p, sha16(os.path.join(al, p)), s))
    rd = lambda p: open(os.path.join(al, p), encoding='utf-8').read()
    texts, m = {}, {}
    for old, new, edits in EDITS:
        texts[new] = apply(rd(old), edits, old); m[new] = sha16_text(texts[new])
    texts[V3_NEW] = v3_record(rd(V3_OLD), m[EO_NEW], m[RP_NEW]); m[V3_NEW] = sha16_text(texts[V3_NEW])
    texts[AR_NEW] = aw1_record(rd(AR_OLD), m[AW_NEW], m[V3_NEW]); m[AR_NEW] = sha16_text(texts[AR_NEW])
    for old, new, edits in STAGE2:                                   # in order: each one's edits name the sha16s made before it
        texts[new] = apply(rd(old), edits(m), old); m[new] = sha16_text(texts[new])
    return texts


def main(a):
    al, out = a
    for p, t in build(al).items():
        q = os.path.join(out, p); os.makedirs(os.path.dirname(q), exist_ok=True)
        with open(q, 'x', encoding='utf-8') as f:
            f.write(t)
        print('%s\t%s\t%d' % (p, sha16(q), os.path.getsize(q)))
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1:]))
