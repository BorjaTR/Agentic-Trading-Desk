"""Shared formats for the research learning loop (V1). One place for the column lists, so every script agrees."""
import csv, datetime, json, os, re

LESSON_COLS = ['id', 'date_utc', 'seat', 'tags', 'what_happened', 'root_cause', 'cost_hours', 'rule_now', 'check_id', 'status', 'evidence']
RESULT_COLS = ['id', 'utc', 'seat', 'step', 'scheme', 'window', 'fires', 'waves', 'days', 'result', 'interval', 'verdict', 'ledger_row', 'evidence']
CHECK_COLS = ['check_id', 'lesson_id', 'plant_cmd', 'owner']
TRIED_COLS = ['id', 'utc', 'process', 'seat', 'run', 'what_tried', 'thought_file', 'expected', 'actual', 'verdict', 'failed_stage', 'fail_layer', 'why',
              'went_well', 'failed', 'slowed', 'gaps', 'improve', 'faster_next', 'not_waste', 'minutes_active', 'minutes_waiting', 'minutes_blocked',
              'closest_existing', 'tools_used', 'playground_ref', 'receipts', 'ledger_row', 'months_read', 'prompt_id', 'prompt_fix', 'model', 'next_action', 'lesson_id', 'reviewed_by']
GAP_COLS = ['id', 'utc', 'process', 'kind', 'what_missing', 'needed_for', 'why_existing_fails', 'playground_ref', 'status', 'evidence']
CHANGE_COLS = ['id', 'utc', 'process', 'what_changed', 'from_lesson', 'measure', 'before', 'after', 'status', 'evidence']
PROMPT_COLS = ['id', 'utc', 'prompt', 'version', 'process', 'file', 'sha16', 'model', 'parent', 'what_changed', 'why', 'eval_ref', 'before', 'after', 'status']
TRIED_VERDICTS = {'PLANNED', 'WORKED', 'FAILED', 'INVALID_TEST', 'NOT_MEASURABLE', 'UNSURE', 'STOPPED'}
FAIL_LAYERS = {'NONE', 'PREMISE', 'MEASURE', 'RULE', 'DATA', 'TOOL', 'PROCESS', 'PROMPT', 'COST'}
GAP_KINDS = {'METRIC', 'TOOL', 'DATA', 'TEST', 'PROCESS', 'SKILL', 'PROMPT'}
GAP_STATUSES = {'OPEN', 'PLAYGROUND', 'CLOSED', 'WONT_DO'}
CHANGE_STATUSES = {'PROPOSED', 'IN_FORCE', 'HELPED', 'NO_HELP', 'UNDONE'}
PROMPT_STATUSES = {'CANDIDATE', 'CURRENT', 'RETIRED', 'HISTORY'}
REPEAT_TAG = 'repeat:'  # a lesson tagged repeat:<old id> is the same mistake happening again
AGENT_KEYS = ['seat', 'updated_utc', 'read_first', 'goal', 'windows', 'tools', 'rules', 'status', 'handover']
HANDOVER_KEYS = ['doing', 'next', 'blocked_on', 'files']
STATUSES = {'OPEN', 'CLOSED', 'RETIRED'}
VERDICTS = {'PASS', 'FAIL', 'UNSURE', 'VOID'}
STAMP = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

ALWAYS_ON = [
    'coverage table first: every month and store you read has data (a quiet month is usually a hole)',
    'right windows from agent.json (find / check / blind); nothing past the seal',
    'rules, groups and thresholds frozen (sha16) with a PREREG ledger row before any check month is read',
    'count by wave (any coin within 30 min = one), never by fire',
    'no fixed minimum sizes: fires, waves, days and an interval; thin = gather more, not stop',
    'P&L only from raw stored prices with the full cost of trading (fees, spread, funding); a sign test in the tool',
    'no look-ahead: a value known after the decision time is a label, never an input',
    'no bucketing all fires with one changed setting; group by mechanism first',
    'CPU rules and a dry run for any multi-job launcher',
    '"nothing left to try" is never a conclusion: write the next idea',
    'every metric you use: read its card and quote what it must never be used as and what EMPTY means',
]


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def read_tsv(path):
    with open(path, newline='') as f:
        rows = list(csv.reader(f, delimiter='\t'))
    return (rows[0], rows[1:]) if rows else ([], [])


CONFIG = 'LOOP.json'  # at the loop root: {roster, tools_process, ledger, ledger_id_col, ledger_from, ledger_result_col, ledger_result_value}


def find_root(start, depth=3):
    """the loop root is the nearest folder holding LOOP.json, at most `depth` levels up; never a tree walk"""
    d = os.path.abspath(start)
    for _ in range(depth + 1):
        if os.path.isfile(os.path.join(d, CONFIG)):
            return d
        d = os.path.dirname(d)
    return ''


def load_config(root):
    """refuse a config that could pass an empty or partial check"""
    p = os.path.join(root, CONFIG)
    if not os.path.isfile(p):
        return None
    cfg = json.load(open(p))
    if not cfg.get('roster') or len(set(cfg['roster'])) != len(cfg['roster']):
        raise ValueError(f'{p}: roster must be a non-empty list of distinct folder names')
    if cfg.get('ledger') and not (cfg.get('ledger_id_col') and re.match(r'^\d{8}$', str(cfg.get('ledger_from', '')))):
        raise ValueError(f'{p}: a ledger needs ledger_id_col and ledger_from YYYYMMDD')
    cfg['ledger'] = os.path.expanduser(cfg.get('ledger', '')) if cfg.get('ledger') else ''
    if cfg['ledger'] and not os.path.isabs(cfg['ledger']):
        cfg['ledger'] = os.path.join(root, cfg['ledger'])
    return cfg


def ledger_ids(cfg):
    """the ids of the trial ledger, in file order, with their date (first 8 characters of the first column)"""
    with open(cfg['ledger']) as f:
        lines = [l.rstrip('\n').split('\t') for l in f if not l.startswith('#')]
    head = lines[0]
    k = head.index(cfg['ledger_id_col'])
    rc, rv = cfg.get('ledger_result_col', ''), cfg.get('ledger_result_value', '')
    j = head.index(rc) if rc else -1
    keep = [l for l in lines[1:] if len(l) > max(k, j) and l[k].strip()]
    if j >= 0:  # only result rows must be logged; a registration is not a try
        keep = [l for l in keep if l[j] == rv]
    return [(l[0][:8], l[k]) for l in keep], len([l for l in lines[1:] if not (j >= 0 and len(l) > j and l[j] != rv)])
