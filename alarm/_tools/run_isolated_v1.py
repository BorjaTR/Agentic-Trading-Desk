#!/usr/bin/env python3
"""run_isolated_v1.py (SCOUT 30 Oct 2026; the owner 09:52 Berlin: "prove that they can run only from their Alarm folder").
Runs one script of this repository (a test file or a tool) as __main__ and proves two things at the end:
  (1) every Python module it imported came from this Alarm folder or from the interpreter itself (its standard library and its
      installed packages such as numpy and pyarrow): none from the team's dev tree or anywhere else;
  (2) it opened no file under a forbidden root (default: the dev trees <DEV> and ~/mnt/dev), seen by a Python audit hook;
      files of the interpreter itself (its prefix, standard library and installed packages) do not count, because on the Mac the
      team's Python (<VENV>) lives inside the dev tree (fixed 30 Oct 2026 before the first commit).
Exit: the script's own exit code; 3 when (1) or (2) failed (the list is printed).
  python3 -B run_isolated_v1.py [--forbid <dir>]... <script.py> [args...]"""
import os, runpy, site, sys, sysconfig

ALARM = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(a):
    forbid = []
    while a and a[0] == '--forbid':
        forbid.append(os.path.realpath(a[1])); a = a[2:]
    if not a:
        raise SystemExit(__doc__.strip().split('\n')[-1])
    forbid = forbid or [os.path.realpath(p) for p in ('<DEV>', os.path.expanduser('~/mnt/dev')) if os.path.isdir(p)]
    script = os.path.realpath(a[0])
    if not script.startswith(ALARM + os.sep):
        raise SystemExit('NOT IN THIS ALARM FOLDER: %s' % script)
    lib = [sysconfig.get_paths()[k] for k in ('stdlib', 'platstdlib', 'purelib', 'platlib')]
    interp = [os.path.realpath(p) for p in lib + list(site.getsitepackages()) + [site.getusersitepackages()] + [sys.prefix, sys.base_prefix]]
    allowed = [ALARM] + interp
    opened = []

    def hook(event, args):
        if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
            p = os.path.realpath(os.fsdecode(args[0]))
            if any(p == f or p.startswith(f + os.sep) for f in forbid) and not any(p == r or p.startswith(r + os.sep) for r in interp):
                opened.append(p)
    sys.addaudithook(hook)
    sys.argv = [script] + a[1:]; sys.path[0] = os.path.dirname(script)
    code = 0
    try:
        runpy.run_path(script, run_name='__main__')
    except SystemExit as e:
        code = int(e.code) if isinstance(e.code, (int, bool)) else (0 if e.code is None else 1)
    config = {'sitecustomize', 'usercustomize'}                      # the interpreter's own start-up config (e.g. /etc/python3.10)
    outside = sorted({os.path.realpath(m.__file__) for k, m in list(sys.modules.items()) if getattr(m, '__file__', None) and k not in config
                      and not any(os.path.realpath(m.__file__).startswith(r + os.sep) for r in allowed)})
    if outside or opened:
        print('ISOLATION FAILED: modules from outside %s; files opened under %s: %s' % (outside, forbid, sorted(set(opened))[:20]))
        sys.exit(3)
    n = sum(1 for m in list(sys.modules.values()) if getattr(m, '__file__', None) and os.path.realpath(m.__file__).startswith(ALARM + os.sep))
    print('ISOLATION OK: %d modules from %s, the rest from the interpreter; no file opened under %s; script exit %s' % (n, ALARM, forbid, code))
    sys.exit(code)


if __name__ == '__main__':
    main(sys.argv[1:])
