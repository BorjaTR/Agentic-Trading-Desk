#!/usr/bin/env python3
"""run_isolated_v2.py (SCOUT 30 Oct 2026; the owner 22:21 Berlin: "Let's make sure everything can run from the release folder";
23:07: "All alarm tools should work from the release folder only"). The RUN proof of a clean tool on REAL data: run_isolated_v1
plus the machine's settings file. Runs one script of this Alarm folder as __main__ and proves, at the end:
  (1) every Python module it imported came from this Alarm folder or from the interpreter itself (as v1);
  (2) every file it opened under a forbidden root (--forbid, else the settings' FORBID) lies under a DATA key of the settings file and is no
      code: data keys are LAB_DAYS, RESEARCH_STORE, HL_FILLS, SCRATCH, RESEARCH_ROOT, RUNNER_QUEUES, BOARD and FEED_GATE (a file: the feed's gate) (those present);
      code is a .py, .pyc, .pyo, .sh, .so or .dylib file or a job template (.job.sh.txt). On the Mac the research data lives inside
      the dev tree (RESEARCH_ROOT), so v1 could not prove a real run; a dev tool's code is still refused, data under a key is not.
      The interpreter's own files do not count (as v1).
  (3) nothing it opened or imported lies in an archive/ folder of this Alarm folder: past editions are read only, never run
      (the owner 30 Oct 2026 23:51-23:54 Berlin: "move the past editions to an Archive folder"). An archive/ folder in the data is data.
Exit: the script's own exit code; 3 when (1) or (2) failed (the list is printed); 2 when refused (no settings file, a bad one, no
forbidden folder: neither --forbid nor the settings' FORBID, whose folders are split on ':' as run_all_tests_v1 does).
  python3 -B _tools/run_isolated_v2.py --settings <settings file> [--forbid <dir>]... <script.py> [args...]"""
import os, runpy, site, sys, sysconfig

HERE = os.path.dirname(os.path.abspath(__file__))
ALARM = os.path.realpath(os.path.dirname(HERE))
DATA_KEYS = ('LAB_DAYS', 'RESEARCH_STORE', 'HL_FILLS', 'SCRATCH', 'RESEARCH_ROOT', 'RUNNER_QUEUES', 'BOARD', 'FEED_GATE')
CODE_SUFFIX = ('.py', '.pyc', '.pyo', '.sh', '.so', '.dylib', '.job.sh.txt')


def under(p, roots):
    return any(p == r or p.startswith(r + os.sep) for r in roots)


def in_archive(p):
    """a file inside an archive/ folder of this Alarm folder (a past edition)"""
    return p.startswith(ALARM + os.sep) and 'archive' in os.path.relpath(p, ALARM).split(os.sep)[:-1]


def judge(opened, forbid, data, interp):
    """the opened files that break (2): under a forbidden root, not the interpreter's, and either outside every data root or code"""
    bad = []
    for p in sorted(set(opened)):
        if not under(p, forbid) or under(p, interp):
            continue
        if under(p, data) and not p.endswith(CODE_SUFFIX):
            continue
        bad.append(p)
    return bad


def settings_roots(path):
    """-> (the realpaths of the settings file's data keys, empty keys and keys this file lacks left out; its FORBID folders' realpaths)"""
    sys.path.insert(0, HERE)
    import settings_v1 as S
    sys.path.pop(0)
    s = S.load(path)
    return [os.path.realpath(s[k]) for k in DATA_KEYS if s.get(k)], [os.path.realpath(x) for x in (s.get('FORBID') or '').split(':') if x]


def main(a):
    forbid, settings = [], None
    while a and a[0] in ('--forbid', '--settings'):
        if len(a) < 2:
            print(__doc__.strip().split('\n')[-1]); return 2
        if a[0] == '--forbid':
            forbid.append(os.path.realpath(a[1]))
        else:
            settings = a[1]
        a = a[2:]
    if not a or settings is None:
        print(__doc__.strip().split('\n')[-1]); return 2
    try:
        data, fb = settings_roots(settings)
    except Exception as e:                      # settings_v1.Refused, or a file that cannot be read
        print('REFUSED SETTINGS: %s' % e); return 2
    forbid = forbid or fb                                      # no machine path written in: --forbid, else the settings' FORBID
    if not forbid:
        print('REFUSED: NO FORBIDDEN FOLDER: set FORBID in %s (the dev tree) or give --forbid' % settings); return 2
    script = os.path.realpath(a[0])
    if not script.startswith(ALARM + os.sep):
        print('NOT IN THIS ALARM FOLDER: %s' % script); return 2
    lib = [sysconfig.get_paths()[k] for k in ('stdlib', 'platstdlib', 'purelib', 'platlib')]
    interp = [os.path.realpath(p) for p in lib + list(site.getsitepackages()) + [site.getusersitepackages()] + [sys.prefix, sys.base_prefix]]
    allowed = [ALARM] + interp
    opened = []

    def hook(event, args):
        if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
            opened.append(os.path.realpath(os.fsdecode(args[0])))
    sys.addaudithook(hook)
    sys.argv = [script] + a[1:]; sys.path[0] = os.path.dirname(script)
    code = 0
    try:
        runpy.run_path(script, run_name='__main__')
    except SystemExit as e:
        code = int(e.code) if isinstance(e.code, (int, bool)) else (0 if e.code is None else 1)
    config = {'sitecustomize', 'usercustomize'}
    outside = sorted({os.path.realpath(m.__file__) for k, m in list(sys.modules.items()) if getattr(m, '__file__', None) and k not in config
                      and not under(os.path.realpath(m.__file__), allowed)})
    bad = judge(opened, forbid, data, interp)
    mods = {os.path.realpath(m.__file__) for k, m in list(sys.modules.items()) if getattr(m, '__file__', None)}
    arch = sorted(p for p in set(opened) | mods if in_archive(p))
    if outside or bad or arch:
        print('RUN ISOLATION FAILED: modules from outside %s; files under %s that are no data of the settings (or are code): %s; '
              'past editions (archive/) opened or imported: %s' % (outside, forbid, bad[:20], arch[:20]))
        return 3
    nd = len({p for p in opened if under(p, data)})
    print('RUN ISOLATION OK: modules from %s and the interpreter only; %d data files opened under the settings keys; no code and nothing '
          'else opened under %s; no past edition (archive/) opened; script exit %s' % (ALARM, nd, forbid, code))
    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
