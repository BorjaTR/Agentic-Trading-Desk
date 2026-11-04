"""SCOUT make_families_v2 (23 Oct 2026; SKEPTIC REVIEW 03-09/03-10): writes FAMILIES_V2.tsv. Changes from v1 (kept): NO exemption by words
(TOOL_CHECK / LABEL_CHECK only by try id in EXEMPT_V1.tsv, with evidence that no outcome was read, signed by LEAD); family_of_all returns EVERY
matching family (a try naming two alarms counts in both: the conservative side); matching is case-insensitive everywhere (one classifier,
imported by fairness_bar, never copied). v1 text follows. Alarm families are GENERATED from
team/RESEARCH/alarms/ALARMS_V1.tsv (one family per alarm id, never typed); a short HAND list holds only what is not an alarm id there
(chain card names of A02P, alarms not yet in ALARMS_V1, TOOL_CHECK, LABEL_CHECK, the unconfirmed 20 Oct door asks). Reads no outcome.
Rules: an id matches only as a whole token NOT followed by '.' or a word character (C4.S11 is a metric on the STOP list, X1.POSX a producer,
never an alarm); ids that are also row ids in a ledger source (M1-M6 in SCOUT_LEDGER_MODEL_V1) match in that source only when written
'alarm <id>' or as a card name (<id>_..._CARD). First matching row wins; the order is: TOOL_CHECK, LABEL_CHECK, HAND chain rows, generated
alarm rows (longest id first), DOOR_20OCT_TO_CONFIRM. Unmatched = UNMAPPED, printed by the census. Files written whole (tmp + replace).
  python3 -B make_families_v1.py [out]"""
import hashlib, os, re, sys

HERE = os.path.dirname(os.path.realpath(__file__))
ALARMS = os.path.realpath(os.path.join(HERE, '..', '..', 'alarms', 'ALARMS_V1.tsv'))
MODEL_ROW_IDS = {'M1', 'M2', 'M3', 'M4', 'M5', 'M6'}           # also row ids of SCOUT_LEDGER_MODEL_V1 (M1..M63)

HAND_FIRST = [
    (r'\b(A02P|A02N|BUCKETS?_A02P\w*|BUCKET_PROOF\w*|PRO_A02P\w*|S2_ONESIDED|FADE_THINBOOK|MONEY_S2\w*|CAUSE_A02P\w*|DOSSIER ?1|C5 crowd)\b(?![.\w])',
     'any', 'A02P', 'HAND: the A02N/A02P alarm (not an id in ALARMS_V1) and every card built on it'),
    (r'\b(D-WAVE|DWAVE)\b(?![.\w])', 'any', 'DWAVE', 'HAND: D-WAVE (not in ALARMS_V1; ALARM to add it, then this row retires)'),
    (r'\b(D-HL|DHL)\b(?![.\w])', 'any', 'DHL', 'HAND: D-HL (not in ALARMS_V1)'),
    (r'\b(EXHAUSTION|EXH)\b(?![.\w])', 'any', 'EXH', 'HAND: EXHAUSTION (not in ALARMS_V1)'),
    (r'\b(R-?B4)\b(?![.\w])', 'any', 'RB4', 'HAND: ALARM\'s R-B4 truth card (not in ALARMS_V1)'),
]
HAND_LAST = [
    (r'\b(fire-entry-probe|tool-smoke|rehearsal-smoke|code-probe|F1|I0[1-4]|I01xI02|BATCH-[0-9]+Z)\b(?![.\w])', 'ledger', 'DOOR_20OCT_TO_CONFIRM',
     '20 Oct door asks incl. the smoke and probe rows (they carry money columns, so they COUNT): subject NOT confirmed; the spool files name it'),
]


def alarm_ids(path=ALARMS):
    rows = [l.rstrip('\n').split('\t') for l in open(path) if not l.startswith('#')]
    i = rows[0].index('alarm')
    return sorted({r[i] for r in rows[1:] if len(r) > i and r[i].strip()}, key=lambda x: (-len(x), x))


def generated_rows(ids):
    out = []
    for a in ids:
        tok = re.escape(a)
        if a in MODEL_ROW_IDS:
            out.append((r'(alarm %s|\b%s_\w*CARD)(?![.\w])' % (tok, tok), 'model', a, 'GENERATED from ALARMS_V1; in the model ledger only as "alarm %s" or its card (M-row id clash)' % a))
            out.append((r'(?<![\w.])%s(?![.\w])' % tok, 'ledger|screen|try|results', a, 'GENERATED from ALARMS_V1'))
        else:
            out.append((r'(?<![\w.])%s(?![.\w])' % tok, 'any', a, 'GENERATED from ALARMS_V1'))
    return out


def exempt_ids(path=None):
    """{try id: family} from EXEMPT_V1.tsv (id, family TOOL_CHECK|LABEL_CHECK, evidence, signed_by); a row without evidence or signer is refused"""
    path = path or os.path.join(HERE, 'EXEMPT_V1.tsv'); out = {}
    if not os.path.exists(path):
        return out
    for l in open(path):
        if l.startswith('#') or l.startswith('id\t') or not l.strip():
            continue
        f = l.rstrip('\n').split('\t')
        if len(f) < 4 or f[1] not in ('TOOL_CHECK', 'LABEL_CHECK') or not f[2].strip() or not f[3].strip():
            raise ValueError('EXEMPT row refused (needs id, family, evidence, signer): %r' % l)
        out[f[0]] = f[1]
    return out


def family_of_all(text, source, rows, try_id=None, exempt=None):
    """every family whose row matches (case-insensitive), in row order; an exempt id gives only its exemption; none = ['UNMAPPED']"""
    if exempt and try_id in exempt:
        return [exempt[try_id]]
    out = []
    for pat, src, fam, _ in rows:
        if src != 'any' and source not in src.split('|'):
            continue
        if re.search(pat, text, re.I) and fam not in out:
            out.append(fam)
    return out or ['UNMAPPED']


def family_of(text, source, rows):
    for pat, src, fam, _ in rows:
        if src != 'any' and source not in src.split('|'):
            continue
        if re.search(pat, text, re.I):
            return fam
    return 'UNMAPPED'


def build(alarms_path=ALARMS):
    sha = hashlib.sha256(open(alarms_path, 'rb').read()).hexdigest()[:16]
    rows = HAND_FIRST + generated_rows(alarm_ids(alarms_path)) + HAND_LAST
    head = ['# FAMILIES_V2 (SCOUT, generated by make_families_v2.py; alarm rows from ALARMS_V1.tsv sha16 %s; LEAD co-signs the sha16 of this file)' % sha,
            '# EVERY matching row counts (a try in two families counts in both); case-insensitive; exemptions only by id (EXEMPT_V1.tsv); unmatched = UNMAPPED',
            'pattern\tsource\tfamily\twhy']
    return '\n'.join(head + ['\t'.join(r) for r in rows]) + '\n', rows


def main(a):
    out = a[0] if a else os.path.join(HERE, 'FAMILIES_V2.tsv')
    txt, rows = build()
    with open(out + '.tmp', 'w') as f:
        f.write(txt)
    os.replace(out + '.tmp', out)
    print('WROTE', out, hashlib.sha256(open(out, 'rb').read()).hexdigest()[:16], len(rows), 'rows')


if __name__ == '__main__':
    main(sys.argv[1:])
