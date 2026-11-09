#!/usr/bin/env python3
"""messy_triage_v1.py (SCOUT 2026-11-08, C171; part P29 improvement loop). Sorts every OPEN line of MESSY.tsv into one class, so each
reported line reaches an owner and nothing is lost (scorecard "After the 4 packets": the improvement loop row). It changes nothing: it
writes MESSY_TRIAGE.tsv (one row per open line) and prints the class counts and the 15 largest still-open clusters.
Classes (checked in this order):
  NO_FILE         the line names no file ("-")
  DRILL_MATERIAL  a drill key, planted answer, planted result or planted state (drills_v2/GOLDEN/*/key|GOLD, T3_RESULTS, a planted NOW copy):
                  closed by the next key or task version, owner: the drill author
  REPLACED_FILE   the file is retired (RUN_PROMPT, HUNTER_PROMPT, *_V2 step pages, LEAN_RUN_V1): owner none, no action
  NO_LIVE_FILE    the named file does not exist (moved, renamed, never there): someone finds the file first (C218, review B3)
  QUOTE_GONE      the quoted words are no longer in the live file: likely fixed by a later change (a person or agent confirms)
  QUOTE_PRESENT   the quoted words are still in the live file: still open, owner = the live file's part
  NO_QUOTE        the live file exists but the line quotes nothing checkable
Drill copies (drills_v2/GOLDEN/K*/BASE|NEW*/, runs_v2/<run>/ops/) map to their live file by name (MAP below).
Usage: python3 -B messy_triage_v1.py [--registers DIR] [--series DIR]"""
import argparse, csv, os, re, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
MAP = {'HUNTER_RULES.md': 'lean_v1/HUNTER_RULES_V2.md', 'HUNTER_RULES_V2.md': 'lean_v1/HUNTER_RULES_V2.md',
       'HUNTER_LAUNCH.md': 'lean_v1/HUNTER_LAUNCH_V1.md', 'HUNTER_LAUNCH_V1.md': 'lean_v1/HUNTER_LAUNCH_V1.md',
       'JOB_SHEET.md': 'lean_v1/JOB_SHEET_V1.md', 'JOB_SHEET_V1.md': 'lean_v1/JOB_SHEET_V1.md',
       'ASSESSOR_STEP.md': 'ASSESSOR_STEP_V3.md', 'ASSESSOR_STEP_V3.md': 'ASSESSOR_STEP_V3.md',
       'CURATOR_STEP.md': 'CURATOR_STEP_V3.md', 'CURATOR_STEP_V3.md': 'CURATOR_STEP_V3.md',
       'ASSESSOR_SKILL.md': '~/.claude/skills/volat-assessor/SKILL.md', 'CURATOR_SKILL.md': '~/.claude/skills/volat-curator/SKILL.md',
       'HUNTER_SKILL.md': '~/.claude/skills/volat-hunter/SKILL.md', 'ORCHESTRATOR_SKILL.md': '~/.claude/skills/volat-orchestrator/SKILL.md',
       'LEARNING_LOOP_V3.md': 'LEARNING_LOOP_V3.md', 'PROCESS_IMPROVEMENT_V1.md': 'drills_v2/PROCESS_IMPROVEMENT_V1.md',
       'DOCUMENT_PROCESS_V1.md': 'drills_v2/DOCUMENT_PROCESS_V1.md', 'REPORT_TEMPLATE_V1.md': 'drills_v2/REPORT_TEMPLATE_V1.md',
       'REPORT_TEMPLATE.md': 'drills_v2/REPORT_TEMPLATE_V1.md', 'PROOF_RULES_V2.md': 'PROOF_RULES_V2.md',
       'HELDOUT.md': 'release_staging/LEARNING_LOOP_V2/alarm_pack/HELDOUT.md', 'FAILURES_LOG.tsv': 'lean_v1/FAILURES_LOG.tsv',
       'HOTFIX_LOG.tsv': 'lean_v1/HOTFIX_LOG.tsv', 'CARD_TEMPLATE.md': 'lean_v1/templates/CARD.md', 'CLAIMS_TEMPLATE.md': 'lean_v1/templates/CLAIMS.md',
       'FORECASTS_TEMPLATE.tsv': 'lean_v1/templates/FORECASTS.tsv', 'KNOWLEDGE_BRIEF.md': 'knowledge_v1/KNOWLEDGE_BRIEF.md',
       'STUCK_CHECK.md': '~/.claude/skills/research-learning-loop/STUCK_CHECK.md', 'ADOPTED_RULES.md': 'lean_v1/ADOPTED_NOTES.tsv',
       'REGISTERS_README.md': 'drills_v2/registers/README.md'}
if os.environ.get('LL_TRIAGE_MAP'):   # RC2: a seat's own file-name map (TSV: name, path under {SEAT_ROOT} or ~); default: the SCOUT map above
    MAP = dict(l.rstrip('\n').split('\t')[:2] for l in open(os.environ['LL_TRIAGE_MAP'], encoding='utf-8') if '\t' in l and not l.startswith('#'))
RETIRED = re.compile(r'(^|/)(RUN_PROMPT\.md|HUNTER_PROMPT(_TEMPLATE)?(_V2)?\.md|ASSESSOR_STEP(_V2)?\.md\.pre|ASSESSOR_STEP_V2\.md|CURATOR_STEP_V2\.md|LEAN_RUN_V1\.md|LEARNING_LOOP_V2\.md)$')
DRILL = re.compile(r'(GOLDEN/K\d/(key|GOLD)/|T3_RESULTS\.md|GOLDEN/K4/(BASE|NEW\d*)/NOW_SCOUT\.md|KEYCHECK/|SCORING/)')

def latest(rows):
    last = {}
    for r in rows: last[r['mess_id'].rstrip('abcdefghijklmnopqrstuvwxyzL')] = r      # a status row is the id plus a letter (reg.py)
    return list(last.values())

def live_path(f, series):
    f = f.strip().strip('`')
    base = os.path.basename(f)
    cand = MAP.get(base)
    if cand is None:
        cand = re.sub(r'^.*' + re.escape(os.environ.get('LL_SEAT_ROOT_NAME', 'learning_series')) + '/', '', f)   # RC2: the seat root's folder name
    p = os.path.expanduser(cand) if cand.startswith('~') else os.path.join(series, cand)
    return cand, p

def quotes(q):
    parts = [x.strip(' ."\'') for x in re.split(r'\.\.\.|…|"', q or '') if len(x.strip(' ."\'')) >= 12]
    return sorted(parts, key=len, reverse=True)

def norm(s):
    return re.sub(r'\s+', ' ', s.replace('`', '').replace('\\', '')).strip().lower()

def classify(r, series):
    f = (r.get('file') or '').strip()
    if f in ('', '-'): return 'NO_FILE', '-'
    if DRILL.search(f): return 'DRILL_MATERIAL', f
    if RETIRED.search(f) or os.path.basename(f) in ('RUN_PROMPT.md', 'HUNTER_PROMPT.md'): return 'REPLACED_FILE', f
    cand, p = live_path(f, series)
    if not os.path.isfile(p): return 'NO_LIVE_FILE', cand   # C218 (B3): was NO_QUOTE, whose text says the file exists
    qs = quotes(r.get('line_quoted', ''))
    if not qs: return 'NO_QUOTE', cand
    text = norm(open(p, errors='replace').read())
    hit = any(norm(q) in text for q in qs[:3])
    return ('QUOTE_PRESENT' if hit else 'QUOTE_GONE'), cand

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('--registers', default=os.environ.get('LL_REGISTERS', HERE))
    ap.add_argument('--series', default=os.environ.get('LL_SEAT_ROOT', os.path.dirname(os.path.dirname(HERE))))
    a = ap.parse_args(argv)
    rows = latest(list(csv.DictReader(open(os.path.join(a.registers, 'MESSY.tsv')), delimiter='\t')))
    opn = [r for r in rows if (r.get('status') or '').lower() == 'open']
    out, cnt, clus = [], Counter(), defaultdict(list)
    for r in opn:
        c, live = classify(r, a.series); cnt[c] += 1
        out.append([r['mess_id'].rstrip('abcdefghijklmnopqrstuvwxyzL'), c, live, (r.get('kind') or ''), (r.get('line_quoted') or '')[:120].replace('\t', ' ')])
        if c == 'QUOTE_PRESENT': clus[live].append(r['mess_id'].rstrip('abcdefghijklmnopqrstuvwxyzL'))
    with open(os.path.join(a.registers, 'MESSY_TRIAGE.tsv'), 'w', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n'); w.writerow(['mess_id', 'class', 'live_file', 'kind', 'quote']); w.writerows(out)
    print('TRIAGE open %d: %s' % (len(opn), ', '.join('%s %d' % kv for kv in cnt.most_common())))
    for live, ids in sorted(clus.items(), key=lambda kv: -len(kv[1]))[:15]:
        print('STILL_OPEN %3d %s (%s)' % (len(ids), live, ' '.join(ids[:6])))
    return 0

if __name__ == '__main__':
    sys.exit(main())
