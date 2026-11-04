"""home_kit isolation hook (home_kit V1.0, STRATEGY 30 Oct 2026; TEST, NOT REVIEWED; first built for ctx_grade V1.0, whose names it
keeps: CTXG_*). Source: team/RESEARCH/tools/home_kit/isolation/sitecustomize.py; every tool home holds an exact copy at
bin/isolation/sitecustomize.py. Python loads this file at start-up in every process of a run (the tool's entry script puts
bin/isolation first on PYTHONPATH and sets CTXG_ISOLATE=1), the spawned workers included. A Python audit hook then writes one line to
CTXG_ISOLATION_LOG for every file opened under a CTXG_FORBID root (the dev trees) that is not under a CTXG_ALLOW root (the tool's home,
the interpreter, the files the settings name). Imports are opens, so a module taken from the dev tree is caught too. Nothing else
changes: the hook only writes when it sees such an open. The entry script reads the log at the end (empty = ISOLATION OK).
V1.1 (CONDUCTOR 31 Oct 2026, C49, opt-in): when CTXG_OPEN_LOG is set, a second hook writes one line per distinct file opened by
this process (O<TAB>path), and NONPY<TAB>program when it starts a program that is not Python; unset, nothing changes.
V1.2 (STRATEGY 31 Oct 2026, SCOUT's C49 review M3 and M5): with CTXG_OPEN_LOG set, a Python child that will not write this log is NONPY
too (NONPY<TAB>program<TAB>why): its env lacks CTXG_ISOLATE=1, this CTXG_OPEN_LOG or this hook's folder on PYTHONPATH, or it starts with
-I, -E or -S; the os.spawn event's program is read after its mode. Each thread has its own busy flag (threading.local) in both hooks, so
an open in one thread while another thread is inside a hook is still checked and logged."""
import os
import sys

if os.environ.get('CTXG_ISOLATE') == '1':
    import site
    import sysconfig
    import threading

    def _roots(var):
        return [os.path.realpath(p) for p in os.environ.get(var, '').split(':') if p]

    _FORBID = _roots('CTXG_FORBID')
    _ALLOW = _roots('CTXG_ALLOW')
    for _p in [sys.prefix, sys.base_prefix, sys.exec_prefix] + [sysconfig.get_paths()[k] for k in ('stdlib', 'platstdlib', 'purelib', 'platlib')]:
        _ALLOW.append(os.path.realpath(_p))
    try:
        _ALLOW += [os.path.realpath(p) for p in site.getsitepackages()]
    except Exception:
        pass
    _LOG = os.environ.get('CTXG_ISOLATION_LOG', '')
    _BUSY = threading.local()   # V1.2 (M5): _BUSY.on is this thread's flag (V1.1: one list for all threads)

    def _under(p, roots):
        return any(p == r or p.startswith(r + os.sep) for r in roots)

    def _hook(event, args):
        if event != 'open' or getattr(_BUSY, 'on', 0) or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        _BUSY.on = 1
        try:
            p = os.path.realpath(os.path.abspath(os.fsdecode(args[0])))
            if _under(p, _FORBID) and not _under(p, _ALLOW):
                with open(_LOG, 'a') as fh:
                    fh.write('OPEN\t%d\t%s\t%s\n' % (os.getpid(), os.path.basename(sys.argv[0]) if sys.argv else '?', p))
        except Exception:
            pass
        finally:
            _BUSY.on = 0

    if _FORBID and _LOG:
        sys.addaudithook(_hook)

    _OPEN = os.environ.get('CTXG_OPEN_LOG', '')
    if _OPEN:
        _SEEN = set()
        _PY = {os.path.basename(sys.executable or 'python3')}
        _HOOK_DIR = os.path.dirname(os.path.realpath(__file__))

        def _put(line):
            _BUSY.on = 1
            try:
                with open(_OPEN, 'a') as fh:
                    fh.write(line)
            except Exception:
                pass
            finally:
                _BUSY.on = 0

        def _is_py(prog):
            b = os.path.basename(os.fsdecode(prog)) if prog else ''
            return b in _PY or b.startswith('python')

        def _no_log(argv, env):
            """V1.2 (M3): why a Python child will not write this open log ('' = it will): an option -I, -E or -S before -c, -m or the
            script (-W and -X take a value), or its env (None = this process's) without CTXG_ISOLATE=1, this CTXG_OPEN_LOG or this hook's
            folder on PYTHONPATH"""
            argv = os.fsdecode(argv).split() if isinstance(argv, (str, bytes)) else [os.fsdecode(a) for a in argv]
            i = 1
            while i < len(argv) and argv[i].startswith('-') and argv[i] not in ('-', '--'):
                a = argv[i]; i += 1
                if a.startswith('--'):
                    if a == '--check-hash-based-pycs':   # the one long option with a value
                        i += 1
                    continue
                for j, ch in enumerate(a[1:]):
                    if ch in 'IES':
                        return 'option -' + ch
                    if ch in 'cm':
                        i = len(argv)
                        break
                    if ch in 'WX':   # its value is the rest of this group, or the next argument
                        if j == len(a) - 2:
                            i += 1
                        break
            env = os.environ if env is None else env
            if env.get('CTXG_ISOLATE') != '1':
                return 'env without CTXG_ISOLATE=1'
            if env.get('CTXG_OPEN_LOG') != _OPEN:
                return 'env without this CTXG_OPEN_LOG'
            if _HOOK_DIR not in [os.path.realpath(p) for p in env.get('PYTHONPATH', '').split(os.pathsep) if p]:
                return 'env without the hook on PYTHONPATH'
            return ''

        def _hook2(event, args):
            if getattr(_BUSY, 'on', 0) or not args:
                return
            try:
                if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
                    p = os.path.realpath(os.path.abspath(os.fsdecode(args[0])))
                    if p not in _SEEN:
                        _SEEN.add(p); _put('O\t%s\n' % p)
                elif event in ('subprocess.Popen', 'os.posix_spawn', 'os.exec', 'os.spawn'):
                    if event == 'os.spawn':   # V1.2: (mode, path, args, env); the others start with the program
                        args = args[1:]
                    prog = args[0] if not isinstance(args[0], (list, tuple)) else (args[0][0] if args[0] else '')
                    if event == 'subprocess.Popen' and not prog and len(args) > 1 and args[1]:
                        a1 = args[1]; prog = a1 if isinstance(a1, (str, bytes)) else a1[0]
                    if isinstance(prog, (str, bytes)) and ' ' in os.fsdecode(prog):
                        prog = os.fsdecode(prog).split()[0]
                    if not _is_py(prog):
                        _put('NONPY\t%s\n' % os.fsdecode(prog))
                    else:   # V1.2 (M3): the args and env the event passes (Popen: program, args, cwd, env; the others: program, args, env)
                        why = _no_log(args[1], args[3] if event == 'subprocess.Popen' else args[2])
                        if why:
                            _put('NONPY\t%s\t%s\n' % (os.fsdecode(prog), why))
                elif event == 'os.system':
                    _put('NONPY\t%s\n' % os.fsdecode(args[0]).split()[0])
            except Exception:
                pass

        sys.addaudithook(_hook2)
