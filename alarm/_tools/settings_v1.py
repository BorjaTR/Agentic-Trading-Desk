"""settings_v1.py (SCOUT, 30 Oct 2026): where the data lives on this machine, for every tool of the Alarm package.

the owner, 30 Oct 2026 10:46-10:48 Berlin: "if now I clone the repository in another machine. That machine should be able to execute
everything as well with a settings file" ... "within the Alarm folder it is okay to share calling tools. The alarm folder is one
package on its own ... outside the alarm folder only data should be outside ... the settings folder would set where the data is".
Format: the team's tool protocol V4.12 (rule H4), as in tools/ctx_grade: one settings file per machine, settings/SETTINGS_<MACHINE>.env,
KEY=VALUE lines read as text (no quotes, no $variables, no ~, nothing executed); '#' lines and blank lines skipped; the keys are the
ones settings/SETTINGS_EXAMPLE.env documents, each at most once, no other key; a value is empty (not set on this machine) or an
absolute path outside the Alarm folder (only data lives outside). The settings file is always named on the command line.

  python3 -B _tools/settings_v1.py check <settings file> [KEY,...]   each key (or those named): OK, MISSING (no such path here) or EMPTY
                                                                     exit 0 all OK, 3 some MISSING or EMPTY, 2 refused
  python3 -B _tools/settings_v1.py get <settings file> KEY           print the value (exit 2: refused, or the key is empty)
In Python:  sys.path.insert(0, <Alarm>/_tools); import settings_v1 as S; S.get(<settings file>, 'LAB_DAYS')
            S.alarm_root(__file__) finds <Alarm> from any file inside it.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALARM = os.path.dirname(HERE)
EXAMPLE = os.path.join(ALARM, 'settings', 'SETTINGS_EXAMPLE.env')
LINE_RE = re.compile(r'([A-Z][A-Z0-9_]*)=(.*)')


class Refused(Exception):
    pass


def alarm_root(start):
    """the Alarm folder holding `start` (a file or folder inside it): the nearest parent with _tools/settings_v1.py and settings/"""
    d = os.path.dirname(os.path.abspath(start)) if os.path.isfile(start) else os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(d, 'settings')):
            return d
        up = os.path.dirname(d)
        if up == d:
            raise Refused('NOT INSIDE AN ALARM PACKAGE %s' % start)
        d = up


def read_env(path):
    """{key: value} of one KEY=VALUE file, in file order; refuses a missing file, a line that is not KEY=VALUE, a key twice"""
    if not os.path.isfile(path):
        raise Refused('NO SETTINGS FILE %s (copy settings/SETTINGS_EXAMPLE.env to settings/SETTINGS_<MACHINE>.env and set the values)' % path)
    rows = {}
    with open(path, encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip('\r\n')
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            m = LINE_RE.fullmatch(line)
            if not m:
                raise Refused('NOT KEY=VALUE %s line %d' % (path, n))
            if m.group(1) in rows:
                raise Refused('KEY TWICE %s (%s line %d)' % (m.group(1), path, n))
            rows[m.group(1)] = m.group(2)
    return rows


def keys():
    """the keys every settings file must have: the example's, in its order"""
    return list(read_env(EXAMPLE))


def inside(path, root):
    path, root = os.path.realpath(path), os.path.realpath(root)
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def load(path):
    """{key: value} of a machine's settings file: every example key, no other; each value empty or an absolute path outside Alarm"""
    want, got = keys(), read_env(path)
    miss = [k for k in want if k not in got]
    extra = [k for k in got if k not in want]
    if miss:
        raise Refused('KEYS MISSING %s in %s' % (','.join(miss), path))
    if extra:
        raise Refused('UNKNOWN KEYS %s in %s' % (','.join(extra), path))
    out = {}
    for k in want:
        v = got[k]
        if v and (v != v.strip() or not os.path.isabs(v)):
            raise Refused('NOT AN ABSOLUTE PATH %s=%r (no quotes, spaces, ~ or $variables)' % (k, v))
        if v and inside(v, ALARM):
            raise Refused('DATA INSIDE ALARM %s=%s (only data lives outside the Alarm folder; code lives inside)' % (k, v))
        out[k] = os.path.normpath(v) if v else ''
    return out


def get(path, key):
    s = load(path)
    if key not in s:
        raise Refused('NO SUCH KEY %s (keys: %s)' % (key, ','.join(s)))
    if not s[key]:
        raise Refused('EMPTY %s in %s (not set on this machine)' % (key, path))
    return s[key]


def check(path, names=None):
    """[(key, 'OK' / 'MISSING' / 'EMPTY', value)] for every key or the ones named"""
    s = load(path)
    names = list(s) if not names else names
    bad = [k for k in names if k not in s]
    if bad:
        raise Refused('NO SUCH KEY %s (keys: %s)' % (','.join(bad), ','.join(s)))
    return [(k, 'EMPTY' if not s[k] else ('OK' if os.path.exists(s[k]) else 'MISSING'), s[k]) for k in names]


def main(argv):
    if len(argv) < 2 or argv[0] not in ('get', 'check') or (argv[0] == 'get' and len(argv) != 3) or len(argv) > 3:
        print(__doc__)
        return 2
    try:
        if argv[0] == 'get':
            print(get(argv[1], argv[2]))
            return 0
        rows = check(argv[1], argv[2].split(',') if len(argv) == 3 else None)
    except Refused as e:
        print('REFUSED %s' % e, file=sys.stderr)
        return 2
    for k, st, v in rows:
        print('%-8s %-16s %s' % (st, k, v))
    print('settings %s: %d keys, %d not OK' % (os.path.abspath(argv[1]), len(rows), sum(1 for r in rows if r[1] != 'OK')))
    return 3 if any(r[1] != 'OK' for r in rows) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
