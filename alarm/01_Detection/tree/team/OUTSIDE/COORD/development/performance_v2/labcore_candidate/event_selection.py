"""Apply the shared resolver's dated membership to original event identities.

The consumer must call the reviewed resolver against verified roster/group files;
a stored manifest is not an admission or execution permission by itself.
"""
import datetime as dt
import hashlib
import json


def _midnight(day):
    if not isinstance(day, str) or len(day) != 8 or not day.isdigit():
        raise ValueError('resolver interval needs YYYYMMDD dates')
    parsed = dt.datetime.strptime(day, '%Y%m%d').replace(tzinfo=dt.timezone.utc)
    epoch = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    return (parsed - epoch).days * 86400 * 1_000_000


def select_events(population, manifest):
    """Return every selected original event, preserving source-file order."""
    if manifest.get('schema_version') != 2:
        raise ValueError('unsupported resolver schema')
    payload = {key: value for key, value in manifest.items() if key != 'cache_key'}
    identity = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'),
                                         ensure_ascii=True, allow_nan=False).encode()).hexdigest()
    if manifest.get('cache_key') != identity:
        raise ValueError('resolver manifest identity mismatch')
    expected_reference = {'subject': population.subject, 'source_sha256': population.source_sha256}
    if manifest.get('population_reference') != expected_reference:
        raise ValueError('resolver not bound to original event population')
    requested = manifest['requested']
    if requested['timezone'] != 'UTC' or requested['endpoints'] != 'date_inclusive':
        raise ValueError('unsupported resolver time convention')
    first = _midnight(requested['first'])
    end = _midnight(requested['last']) + 86400 * 1_000_000
    next_start = first
    selected = []
    for interval in manifest['resolved']['intervals']:
        lo = _midnight(interval['first'])
        hi = _midnight(interval['last']) + 86400 * 1_000_000
        if lo != next_start or hi <= lo or hi > end:
            raise ValueError('membership intervals must exactly partition requested dates')
        next_start = hi
        status = interval['membership_status']
        if status not in ('DEFINED', 'GROUP_NOT_EFFECTIVE'):
            raise ValueError('unknown membership status')
        if status == 'GROUP_NOT_EFFECTIVE' and interval['coins']:
            raise ValueError('undefined group interval cannot supply members')
        selected.extend(population.select(coins=interval['coins'], first_us=lo, end_us=hi))
    if next_start != end:
        raise ValueError('membership intervals do not cover requested dates')
    return tuple(sorted(selected, key=lambda event: event['source_ordinal']))
