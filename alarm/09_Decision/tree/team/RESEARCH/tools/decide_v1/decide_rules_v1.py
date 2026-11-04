"""decide_rules_v1.py (DECIDE seat, 26 Oct 2026): the pure rules of decision tool V1. No path, alarm, coin or date is held here.

One fire in, one decision out, in seven fixed slots:
  1 DATA GATE    a push side other than +1 / -1 -> SKIP BAD_DATA. Every field the active rules use must hold one of its declared
                 states. A declared reason of that field (the library's own words for "no reading", for example UNKNOWN:HOLE or
                 NO_HISTORY), a missing card row or an empty cell -> SKIP BAD_DATA. A word that is neither a declared state nor a
                 declared reason refuses (the declaration is incomplete). Each line declares its field's states AND reasons: nothing is
                 guessed from how a word is spelled. Fields no active rule uses never block.
  2 REGIME GATE  the safety file's off days and off states -> SKIP OFF_STATE. An empty safety file switches nothing off.
  3 SIDE         the rulebook's side (FADE = against the push, FOLLOW = with it, UNSET = not chosen: the grader shows both).
  4 SKIP RULES   at most 3 active lines "if field is one of skip_if -> SKIP"; the first true line decides; none true -> TAKE.
  5 SIZE         the rulebook's unit.
  6 ENTRY        a NAME of an existing lab tool setting ('tool:id', for example the grader's entry types), or UNSET. No default.
  7 EXIT         a NAME of an existing lab tool exit ('tool:id'), or UNSET. Fills, exits and money are the named tool's, never here.
                 The allowed names come from the lab tools file (each tool with its release sha16), so a rulebook cannot invent one.
A line counts only when its status is active for the mode: research uses CANDIDATE and FROZEN lines, paper uses FROZEN lines only.
FAILED and RETIRED lines stay in the file as a record and never decide. Every line except DEFAULT ones needs its evidence."""
import re

SCHEMA_RULEBOOK = 'DECIDE_RULEBOOK_V1'
SCHEMA_SAFETY = 'DECIDE_SAFETY_V1'
MODES = ('research', 'paper')
STATUSES = ('DEFAULT', 'CANDIDATE', 'FROZEN', 'FAILED', 'RETIRED')
ACTIVE = {'research': ('DEFAULT', 'CANDIDATE', 'FROZEN'), 'paper': ('DEFAULT', 'FROZEN')}
SIDES = ('FADE', 'FOLLOW', 'UNSET')
SCHEMA_LAB_TOOLS = 'DECIDE_LAB_TOOLS_V1'
UNSET = 'UNSET'
PREFIXES = ('ctx.', 'prof.', 'pmm.')                           # context library, profile library, pre-move library
MAX_SKIP_LINES = 3
NO_CARD_ROW = 'NO_CARD_ROW'                                    # this tool's own words: the fire has no card row / an empty cell
NO_VALUE = 'NO_VALUE'
TOOL_WORDS = (NO_CARD_ROW, NO_VALUE)
EVIDENCE_KEYS = ('source', 'sha16', 'cell')
SKIP_KEYS = {'id', 'field', 'states', 'reasons', 'skip_if', 'status', 'mechanism', 'evidence', 'note'}
RULEBOOK_KEYS = {'schema', 'alarm_id', 'version', 'side', 'skip_rules', 'entry', 'exit', 'size', 'note'}
ITEM_KEYS = {'value', 'status', 'evidence', 'mechanism', 'note'}
SAFETY_KEYS = {'schema', 'status', 'set_by', 'off_days', 'off_states', 'kill_limits', 'note'}
OFF_KEYS = {'id', 'field', 'states', 'reasons', 'off_if', 'note'}


class RuleError(ValueError):
    pass


def matches(v, reasons):
    """a declared reason is an exact word, or a family 'WORD*' (any word that starts with WORD, for example 'UNKNOWN:*')"""
    return any(v == r or (r.endswith('*') and v.startswith(r[:-1])) for r in reasons)


def kind_of(v, states, reasons):
    """STATE, REASON (declared), MISSING_ROW, EMPTY, or UNDECLARED"""
    if v in states:
        return 'STATE'
    if v == NO_CARD_ROW:
        return 'MISSING_ROW'
    if v == NO_VALUE:
        return 'EMPTY'
    return 'REASON' if matches(v, reasons) else 'UNDECLARED'


def _evidence(where, ev, status):
    if status == 'DEFAULT':
        return
    if not isinstance(ev, dict) or any(not str(ev.get(k) or '').strip() for k in EVIDENCE_KEYS):
        raise RuleError('%s: status %s needs evidence with %s' % (where, status, ', '.join(EVIDENCE_KEYS)))
    if not re.fullmatch(r'[0-9a-f]{16}', ev['sha16']):
        raise RuleError('%s: evidence sha16 %r is not 16 hex digits' % (where, ev['sha16']))


def _item(where, it, allowed):
    if not isinstance(it, dict) or set(it) - ITEM_KEYS or 'value' not in it or 'status' not in it:
        raise RuleError('%s: needs value and status, keys %s only' % (where, sorted(ITEM_KEYS)))
    if it['status'] not in STATUSES:
        raise RuleError('%s: status %r' % (where, it['status']))
    if allowed is not None and it['value'] not in allowed:
        raise RuleError('%s: value %r not in %s' % (where, it['value'], allowed))
    _evidence(where, it.get('evidence'), it['status'])


def _states(where, field, states, reasons):
    if not isinstance(field, str) or not field.startswith(PREFIXES) or len(field) <= 5:
        raise RuleError('%s: field %r must start with one of %s' % (where, field, PREFIXES))
    if not isinstance(states, list) or not states or len(set(states)) != len(states):
        raise RuleError('%s: states must be a non-empty list without repeats' % where)
    if not isinstance(reasons, list) or len(set(reasons)) != len(reasons):
        raise RuleError('%s: reasons must be a list (may be empty) without repeats' % where)
    for s in states + reasons:
        if not isinstance(s, str) or not s.strip() or s != s.strip() or s in TOOL_WORDS or s == '*':
            raise RuleError('%s: %r cannot be a state or a reason' % (where, s))
    hit = [s for s in states if matches(s, reasons)]
    if hit:
        raise RuleError('%s: states %s are also declared reasons' % (where, hit))


def check_lab_tools(lt):
    """{schema, entry: {tool: {release, sha16, ids}}, exit: {...}} -> {'entry': set('tool:id'), 'exit': set(...)}"""
    if not isinstance(lt, dict) or lt.get('schema') != SCHEMA_LAB_TOOLS:
        raise RuleError('lab tools schema must be %s' % SCHEMA_LAB_TOOLS)
    out = {}
    for part in ('entry', 'exit'):
        tools = lt.get(part)
        if not isinstance(tools, dict) or not tools:
            raise RuleError('lab tools: %s must name at least one tool' % part)
        names = set()
        for tool, d in tools.items():
            if ':' in tool or not isinstance(d, dict) or not str(d.get('release') or '').strip():
                raise RuleError('lab tools %s/%s: needs a release file' % (part, tool))
            if not re.fullmatch(r'[0-9a-f]{16}', str(d.get('sha16') or '')):
                raise RuleError('lab tools %s/%s: sha16 of the release file' % (part, tool))
            if not isinstance(d.get('ids'), list) or not d['ids']:
                raise RuleError('lab tools %s/%s: ids must be a non-empty list' % (part, tool))
            names |= {'%s:%s' % (tool, i) for i in d['ids']}
        out[part] = names
    return out


def check_rulebook(rb, alarm_id, tools):
    """refuse anything the engine would have to guess about -> the rulebook unchanged"""
    if not isinstance(rb, dict) or rb.get('schema') != SCHEMA_RULEBOOK:
        raise RuleError('rulebook schema must be %s' % SCHEMA_RULEBOOK)
    if set(rb) - RULEBOOK_KEYS:
        raise RuleError('rulebook: unknown keys %s' % sorted(set(rb) - RULEBOOK_KEYS))
    if rb.get('alarm_id') not in ('*', alarm_id):
        raise RuleError('rulebook is for %r, the run is for %r' % (rb.get('alarm_id'), alarm_id))
    _item('side', rb.get('side'), SIDES)
    _item('entry', rb.get('entry'), sorted(tools['entry'] | {UNSET}))
    _item('exit', rb.get('exit'), sorted(tools['exit'] | {UNSET}))
    _item('size', rb.get('size'), None)
    if not isinstance(rb['size']['value'], (int, float)) or isinstance(rb['size']['value'], bool) or not rb['size']['value'] > 0:
        raise RuleError('size: value must be a positive number')
    lines = rb.get('skip_rules')
    if not isinstance(lines, list):
        raise RuleError('skip_rules must be a list')
    ids = set(); open_lines = 0
    for n, ln in enumerate(lines):
        where = 'skip_rules[%d]' % n
        if not isinstance(ln, dict) or set(ln) - SKIP_KEYS or not {'id', 'field', 'states', 'reasons', 'skip_if', 'status'} <= set(ln):
            raise RuleError('%s: needs id, field, states, reasons, skip_if, status; keys %s only' % (where, sorted(SKIP_KEYS)))
        if ln['id'] in ids:
            raise RuleError('%s: id %r repeats' % (where, ln['id']))
        ids.add(ln['id'])
        _states(where, ln['field'], ln['states'], ln['reasons'])
        if not isinstance(ln['skip_if'], list) or not ln['skip_if'] or not set(ln['skip_if']) < set(ln['states']):
            raise RuleError('%s: skip_if must be a non-empty proper subset of states' % where)
        if ln['status'] not in STATUSES or ln['status'] == 'DEFAULT':
            raise RuleError('%s: status %r (a skip line is never DEFAULT)' % (where, ln['status']))
        _evidence(where, ln.get('evidence'), ln['status'])
        if ln['status'] in ('CANDIDATE', 'FROZEN'):
            if not str(ln.get('mechanism') or '').strip():
                raise RuleError('%s: an active line needs a written mechanism' % where)
            open_lines += 1
    if open_lines > MAX_SKIP_LINES:
        raise RuleError('skip_rules: %d active lines, at most %d' % (open_lines, MAX_SKIP_LINES))
    return rb


def check_safety(sf):
    if not isinstance(sf, dict) or sf.get('schema') != SCHEMA_SAFETY:
        raise RuleError('safety schema must be %s' % SCHEMA_SAFETY)
    if set(sf) - SAFETY_KEYS:
        raise RuleError('safety: unknown keys %s' % sorted(set(sf) - SAFETY_KEYS))
    days = sf.get('off_days')
    if not isinstance(days, list) or any(not re.fullmatch(r'\d{8}', str(d)) for d in days):
        raise RuleError('safety: off_days must be a list of YYYYMMDD')
    offs = sf.get('off_states')
    if not isinstance(offs, list):
        raise RuleError('safety: off_states must be a list')
    ids = set()
    for n, o in enumerate(offs):
        where = 'off_states[%d]' % n
        if not isinstance(o, dict) or set(o) - OFF_KEYS or not {'id', 'field', 'states', 'reasons', 'off_if'} <= set(o):
            raise RuleError('%s: needs id, field, states, reasons, off_if' % where)
        if o['id'] in ids:
            raise RuleError('%s: id %r repeats' % (where, o['id']))
        ids.add(o['id'])
        _states(where, o['field'], o['states'], o['reasons'])
        if not isinstance(o['off_if'], list) or not o['off_if'] or not set(o['off_if']) < set(o['states']):
            raise RuleError('%s: off_if must be a non-empty proper subset of states' % where)
    return sf


def active_lines(rb, mode):
    return [ln for ln in rb['skip_rules'] if ln['status'] in ACTIVE[mode] and ln['status'] != 'DEFAULT']


def used_fields(rb, sf, mode):
    """field -> (declared states, declared reasons), for every field an active line or an off state reads (one declaration per field)"""
    out = {}
    for ln in list(sf['off_states']) + active_lines(rb, mode):
        st = (tuple(ln['states']), tuple(ln['reasons']))
        if out.setdefault(ln['field'], st) != st:
            raise RuleError('field %s is declared with two different state or reason lists' % ln['field'])
    return out


def decide(values, push_side, day, rb, sf, mode):
    """values: field -> word for this fire (a missing field is NO_CARD_ROW); push_side +1 / -1; day YYYYMMDD
    -> dict(action, slot, reason, detail, trade_side, entry, exit, size)"""
    if mode not in MODES:
        raise RuleError('mode %r' % mode)
    def out(action, slot, reason, detail='', side=0):
        return dict(action=action, slot=slot, reason=reason, detail=detail, trade_side=side,
                    entry=rb['entry']['value'], exit=rb['exit']['value'], size=rb['size']['value'])
    # 1 data gate
    if push_side not in (1, -1):
        return out('SKIP', 1, 'BAD_DATA', 'push_side=%s' % push_side)
    for f, (st, rs) in used_fields(rb, sf, mode).items():
        v = values.get(f, NO_CARD_ROW)
        k = kind_of(v, st, rs)
        if k == 'UNDECLARED':
            raise RuleError('%s=%r is neither a declared state nor a declared reason of the field' % (f, v))
        if k != 'STATE':
            return out('SKIP', 1, 'BAD_DATA', '%s=%s' % (f, v))
    # 2 regime gate
    if str(day) in [str(d) for d in sf['off_days']]:
        return out('SKIP', 2, 'OFF_STATE', 'off_day=%s' % day)
    for o in sf['off_states']:
        if values[o['field']] in o['off_if']:
            return out('SKIP', 2, 'OFF_STATE', '%s:%s=%s' % (o['id'], o['field'], values[o['field']]))
    # 3 side
    side = rb['side']
    if side['status'] not in ACTIVE[mode]:
        return out('SKIP', 3, 'SIDE_NOT_ACTIVE', 'side status %s in %s mode' % (side['status'], mode))
    trade = {'FADE': -push_side, 'FOLLOW': push_side, 'UNSET': 0}[side['value']]
    # 4 skip rules, first true decides
    for ln in active_lines(rb, mode):
        if values[ln['field']] in ln['skip_if']:
            return out('SKIP', 4, 'SKIP_RULE', '%s:%s=%s' % (ln['id'], ln['field'], values[ln['field']]), trade)
    # 5 size, 6 entry, 7 exit come from the rulebook
    return out('TAKE', 4, 'NO_SKIP_LINE_TRUE', '', trade)
