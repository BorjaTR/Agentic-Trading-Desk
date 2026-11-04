"""test_setup_python_v1.py (SCOUT helper K14, 31 Oct 2026; TEST, NOT REVIEWED): the Python setup step _tools/setup_python_v1.sh, with no
network. Each case plants its own machine in a new temporary folder: an Alarm folder holding a copy of the script and a packages file; a
PATH of fake python3 scripts (each answers the script's version probe and import probe from its own data folder; the venv it makes holds
another fake), a fake uname (the platform), a fake curl or wget (a planted download) and links to the few system tools the script uses (no real
python3, curl or wget on it). One class runs this test's own interpreter on a planted distribution, so the probes' Python is proved too.
The script runs under /bin/bash when there is one (macOS's bash 3.2 on a Mac), else the bash on PATH.
  python3 -B _tools/tests/test_setup_python_v1.py      (from Alarm; no data, no network)
It never deletes: its temporary folders stay under TMPDIR (run_all_tests_v1 gives each test its own TMPDIR and removes it after)."""
import io
import itertools
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ALARM = os.path.dirname(TOOLS)
SCRIPT = os.path.join(TOOLS, 'setup_python_v1.sh')
SHIPPED = os.path.join(ALARM, 'settings', 'PYTHON_PACKAGES.txt')
BASH = '/bin/bash' if os.path.isfile('/bin/bash') else shutil.which('bash')
BASE = tempfile.mkdtemp(prefix='setup_python_v1_test_')
COUNT = itertools.count(1)

# The pinned table as read from the release (python-build-standalone 20261026, its SHA256SUMS): the script must give exactly this.
RELEASE = 'https://github.com/astral-sh/python-build-standalone/releases/download/20261026/'
PINNED = {
    'aarch64-apple-darwin': 'cba3455e18516fbe8668cff2820c9b6a53447c552d612443c2b2fb60d390a908',
    'x86_64-apple-darwin': 'a85474bcc78a98ca6b0070d8d615b0494b912b960239e6f18cc12d648f2dc270',
    'x86_64-unknown-linux-gnu': 'a87ee63646c8f8438b7af3954b2135ed2af91d033c631f12a8f20af903046d06',
    'aarch64-unknown-linux-gnu': 'a344c887b04a309f292cac1ef7c7a85e39e11932ec301d635258c569d830861b',
}
UNAMES = [('Darwin', 'arm64', 'aarch64-apple-darwin'), ('Darwin', 'x86_64', 'x86_64-apple-darwin'),
          ('Linux', 'x86_64', 'x86_64-unknown-linux-gnu'), ('Linux', 'aarch64', 'aarch64-unknown-linux-gnu'),
          ('Linux', 'arm64', 'aarch64-unknown-linux-gnu')]
PACKS = 'numpy==2.2.6\npyarrow==25.0.1\npytest>=8.3.3\nscipy>=1.15.3\norjson>=3.11.9\n'
SPECS = PACKS.split()
GOOD = {'numpy': '2.2.6', 'pyarrow': '25.0.1', 'pytest': '8.3.3', 'scipy': '1.15.3', 'orjson': '3.11.9'}
SYS_TOOLS = {t: shutil.which(t) for t in ('sh', 'cat', 'cp', 'mkdir', 'tr', 'uname', 'tar', 'gzip', 'shasum', 'sha256sum', 'openssl', 'perl')
             if shutil.which(t)}

FAKE_PY = r'''#!/bin/sh
# a fake python3 of test_setup_python_v1 (planted): it answers setup_python_v1.sh's probes from the files of its data folder
D=$(cat "${0%/*}/fake_data")
case "$*" in
  *'probe: version'*) echo "VERSION" >> "$D/calls.log"; cat "$D/version"; exit 0 ;;
  *'probe: import'*)
    for a in "$@"; do last=$a; done
    echo "IMPORT $last" >> "$D/calls.log"
    while read -r n rest; do
      if [ "$n" = "$last" ]; then echo "IMPORT $n $rest"; exit 0; fi
    done < "$D/packages"
    echo "IMPORT $last NO $last ModuleNotFoundError"; exit 0 ;;
  '-m venv '*)
    echo "VENV $3" >> "$D/calls.log"
    if [ -f "$D/venv_rc" ]; then exit "$(cat "$D/venv_rc")"; fi
    mkdir -p "$3/bin" && cp "$0" "$3/bin/python3" && echo "$D/venv" > "$3/bin/fake_data" && echo "home = ${0%/*}" > "$3/pyvenv.cfg"
    exit $? ;;
  '-m pip '*)
    echo "$*" >> "$D/pip.log"
    if [ -f "$D/pip_rc" ]; then exit "$(cat "$D/pip_rc")"; fi
    exit 0 ;;
esac
echo "fake python3: unexpected call: $*" >&2
exit 9
'''
FAKE_UNAME = '#!/bin/sh\n# a fake uname (planted)\ncase "$1" in -m) echo @M@ ;; *) echo @S@ ;; esac\n'
FAKE_CURL = r'''#!/bin/sh
# a fake curl (or wget) of test_setup_python_v1 (planted): it logs its arguments and writes the planted payload to its @O@ file
D='@D@'
echo "$*" >> "$D/curl.log"
out=''; prev=''
for a in "$@"; do if [ "$prev" = "@O@" ]; then out=$a; fi; prev=$a; done
cp "$D/payload" "$out"
'''


def asset(p):
    return 'cpython-3.11.18+20261026-%s-install_only.tar.gz' % p


def url(p):
    return RELEASE + asset(p).replace('+', '%2B')


def read(path, mode='r'):
    with open(path, mode) as f:
        return f.read()


def write(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb' if isinstance(text, bytes) else 'w') as f:
        f.write(text)
    if mode:
        os.chmod(path, mode)
    return path


def make_data(dd, version, packages, pip_rc=None, venv_rc=None, venv=None, raw_version=None):
    """a fake python3's data folder: its answer to the version probe, its packages ({name: version, or None when not importable}),
    pip's and venv's exit codes, and the data folder of the venv it makes (venv: (version, packages, pip_rc))"""
    write(os.path.join(dd, 'version'), raw_version if raw_version is not None else 'PYTHON %s\n' % version)
    write(os.path.join(dd, 'packages'), ''.join('%s NO %s ModuleNotFoundError\n' % (n, n) if v is None else '%s OK %s %s\n' % (n, n, v)
                                                for n, v in packages.items()))
    if pip_rc is not None:
        write(os.path.join(dd, 'pip_rc'), '%d\n' % pip_rc)
    if venv_rc is not None:
        write(os.path.join(dd, 'venv_rc'), '%d\n' % venv_rc)
    if venv is not None:
        make_data(os.path.join(dd, 'venv'), venv[0], venv[1], pip_rc=venv[2])
    return dd


def lines(out, start):
    return [l for l in out.splitlines() if l.startswith(start)]


def item(out, status, name):
    """the line of item `name` (python3 or a package line) with that status, or None"""
    for l in out.splitlines():
        f = l.split()
        if len(f) >= 2 and f[0] == status and f[1] == name:
            return l
    return None


class World:
    """one planted machine: <d>/Alarm (a copy of the script, settings/PYTHON_PACKAGES.txt), <d>/bin (the fakes), <d>/sys (system tools)"""
    def __init__(self, name, packages=PACKS, uname=None):
        self.d = os.path.join(BASE, '%s_%d' % (name, next(COUNT)))
        self.alarm = os.path.join(self.d, 'Alarm')
        self.script = os.path.join(self.alarm, '_tools', 'setup_python_v1.sh')
        os.makedirs(os.path.dirname(self.script))
        shutil.copyfile(SCRIPT, self.script)
        self.pkgs = os.path.join(self.alarm, 'settings', 'PYTHON_PACKAGES.txt')
        if packages is not None:
            write(self.pkgs, packages)
        else:
            os.makedirs(os.path.dirname(self.pkgs))
        self.bin = os.path.join(self.d, 'bin')
        self.sys = os.path.join(self.d, 'sys')
        os.makedirs(self.bin)
        os.makedirs(self.sys)
        for t, p in SYS_TOOLS.items():
            os.symlink(p, os.path.join(self.sys, t))
        if uname:
            write(os.path.join(self.bin, 'uname'), FAKE_UNAME.replace('@S@', uname[0]).replace('@M@', uname[1]), 0o755)
        self.curl_log = os.path.join(self.d, 'curl.log')

    def fake_py(self, key, version, packages, bindir=None, **kw):
        """a fake python3 in bindir (default: this machine's bin, on its PATH); returns (its path, its data folder)"""
        dd = make_data(os.path.join(self.d, 'data_' + key), version, packages, **kw)
        bindir = bindir or self.bin
        write(os.path.join(bindir, 'fake_data'), dd + '\n')
        return write(os.path.join(bindir, 'python3'), FAKE_PY, 0o755), dd

    def fake_curl(self, payload, name='curl'):
        """a fake curl (or wget: name='wget') on PATH that 'downloads' the payload; it logs its arguments in <d>/curl.log"""
        write(os.path.join(self.d, 'payload'), payload)
        write(os.path.join(self.bin, name), FAKE_CURL.replace('@D@', self.d).replace('@O@', '-o' if name == 'curl' else '-O'), 0o755)

    def tarball(self):
        """a real .tar.gz like the pinned one: python/bin/python3 (a fake that says 3.11.18) and its data"""
        src = os.path.join(self.d, 'tar_src', 'python', 'bin')
        dd = make_data(os.path.join(self.d, 'data_tarball'), '3.11.18', GOOD, venv=('3.11.18', GOOD, None))
        write(os.path.join(src, 'fake_data'), dd + '\n')
        write(os.path.join(src, 'python3'), FAKE_PY, 0o755)
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode='w:gz') as t:
            t.add(os.path.join(self.d, 'tar_src', 'python'), arcname='python')
        return buf.getvalue()

    def run(self, *args, cwd=None, env=None):
        e = dict(os.environ)
        e.update({'PATH': self.bin + os.pathsep + self.sys, 'LC_ALL': 'C'})
        e.update(env or {})
        p = subprocess.run([BASH, self.script] + list(args), cwd=cwd or self.d, env=e, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           stdin=subprocess.DEVNULL, text=True, timeout=120)
        return p.returncode, p.stdout


class Case(unittest.TestCase):
    def world(self, **kw):
        return World(self.id().split('.')[-1], **kw)


class T01Static(Case):
    def test_the_header_names_the_release_page_and_its_sums(self):
        head = read(SCRIPT).split('\nset -u\n')[0]
        self.assertIn('https://github.com/astral-sh/python-build-standalone/releases/tag/20261026', head)
        self.assertIn('https://github.com/astral-sh/python-build-standalone/releases/download/20261026/SHA256SUMS', head)

    def test_the_table_is_the_release_table(self):
        src = read(SCRIPT)
        self.assertEqual(sorted(re.findall(r'PIN_URL=(https://\S+)', src)), sorted(url(p) for p in PINNED))
        self.assertEqual(sorted(re.findall(r'PIN_SHA256=([0-9a-f]{64}) ', src)), sorted(PINNED.values()))

    def test_bash_3_2_only(self):
        """nothing newer than macOS's bash 3.2 in the code (comment lines skipped)"""
        newer = [(r'\b(declare|typeset|local)\s+-[a-zA-Z]*[An]', 'associative array or name reference'),
                 (r'\$\{[A-Za-z_][A-Za-z0-9_]*(\[[^]]*\])?(,,?|\^\^?)\}', 'case change'), (r'\breadlink\s+-f\b', 'readlink -f'),
                 (r'\b(mapfile|readarray|coproc)\b', 'bash 4 builtin'), (r'\|&', '|&'), (r'&>>', '&>>'), (r';;&', ';;&'),
                 (r'\bshopt\s+-s\s+(globstar|lastpipe|autocd)\b', 'bash 4 shopt'), (r'\[\[\s+-v\b', '[[ -v'),
                 (r'\$\{[A-Za-z_][A-Za-z0-9_]*@[QEPAa]\}', '${x@Q}'), (r'\bwait\s+-n\b', 'wait -n'), (r'\bEPOCH(SECONDS|REALTIME)\b', 'bash 5')]
        code = [(n, l) for n, l in enumerate(read(SCRIPT).splitlines(), 1) if not l.lstrip().startswith('#')]
        found = [(n, why) for n, l in code for pat, why in newer if re.search(pat, l)]
        self.assertEqual(found, [])

    def test_it_never_deletes_or_moves(self):
        code = [l for l in read(SCRIPT).splitlines() if not l.lstrip().startswith('#')]
        self.assertEqual([l for l in code if re.search(r'(^|[\s;&|(`])(rm|rmdir|unlink|shred|mv)\s', l)], [])

    def test_the_shipped_packages_file_is_read(self):
        """the release's own settings/PYTHON_PACKAGES.txt: each package line is read and checked (an all-good fake)"""
        text = read(SHIPPED)
        specs = [re.match(r'([A-Za-z0-9._-]+)(==|>=)(\S+)$', l.strip()).groups() for l in text.splitlines() if l.strip() and not l.startswith('#')]
        self.assertGreaterEqual(len(specs), 5)
        w = self.world(packages=text)
        w.fake_py('good', '3.11.3', {n: v for n, op, v in specs})
        rc, out = w.run('--check')
        self.assertEqual(rc, 0, out)
        for n, op, v in specs:
            self.assertIsNotNone(item(out, 'OK', n + op + v), out)
        self.assertIn('CHECK OK: python3 3.11.3 (%s) and the %d packages of ' % (os.path.join(w.bin, 'python3'), len(specs)), out)


class T02Check(Case):
    def test_no_python3_on_path(self):
        w = self.world()
        rc, out = w.run('--check')
        self.assertEqual(rc, 1, out)
        self.assertIn('none on PATH', item(out, 'MISSING', 'python3'))
        for spec in SPECS:
            self.assertIsNotNone(item(out, 'UNCHECKED', spec), out)
        self.assertIn('CHECK FAILED: 6 of 6 items not OK: python3 %s (' % ' '.join(SPECS), out)

    def test_an_old_python3(self):
        w = self.world()
        py, dd = w.fake_py('old', '3.9.6', GOOD)
        rc, out = w.run('--check')
        self.assertEqual(rc, 1, out)
        self.assertIn('3.9.6 %s (PATH): older than 3.10' % py, item(out, 'WRONG', 'python3'))
        self.assertEqual(len(lines(out, 'UNCHECKED')), 5, out)
        self.assertEqual(read(os.path.join(dd, 'calls.log')).split(), ['VERSION'])     # no package asked of it

    def test_3_10_and_newer_are_enough(self):
        for v in ('3.10.0', '3.11.18', '3.13.1'):
            w = self.world()
            w.fake_py('py', v, GOOD)
            rc, out = w.run('--check')
            self.assertEqual(rc, 0, (v, out))
            self.assertIn(' %s ' % v, item(out, 'OK', 'python3'))

    def test_a_missing_package(self):
        w = self.world()
        w.fake_py('py', '3.11.3', dict(GOOD, orjson=None))
        rc, out = w.run('--check')
        self.assertEqual(rc, 1, out)
        self.assertIn('not importable: import orjson gives ModuleNotFoundError', item(out, 'MISSING', 'orjson>=3.11.9'))
        self.assertEqual(len(lines(out, 'OK ')), 5, out)
        self.assertIn('CHECK FAILED: 1 of 6 items not OK: orjson>=3.11.9 (', out)

    def test_each_package_is_asked_once_by_its_name(self):
        w = self.world()
        py, dd = w.fake_py('py', '3.11.3', GOOD)
        self.assertEqual(w.run('--check')[0], 0)
        self.assertEqual(read(os.path.join(dd, 'calls.log')).splitlines(), ['VERSION'] + ['IMPORT ' + n for n in GOOD])

    def test_exact_versions(self):
        cases = {'2.2.6': 'OK', '2.2.6.0': 'OK', '2.2.6+local1': 'OK', '2.2.5': 'WRONG', '2.3.0': 'WRONG', '2.2.6rc1': 'WRONG',
                 '2.2.6.post1': 'WRONG', '2.2.6.dev0': 'WRONG', '2.2.60': 'WRONG', '12.2.6': 'WRONG', '2.2': 'WRONG'}
        for found, want in cases.items():
            w = self.world()
            w.fake_py('py', '3.11.3', dict(GOOD, numpy=found))
            rc, out = w.run('--check')
            self.assertEqual(rc, 0 if want == 'OK' else 1, (found, out))
            self.assertIsNotNone(item(out, want, 'numpy==2.2.6'), (found, out))

    def test_minimum_versions_compare_as_numbers(self):
        cases = [('scipy', '1.15.10', 'OK'), ('scipy', '1.16.0', 'OK'), ('scipy', '1.15.3', 'OK'), ('scipy', '1.15.2', 'WRONG'),
                 ('scipy', '1.9.9', 'WRONG'), ('scipy', '1.16.0rc1', 'OK'), ('scipy', '1.15.3rc1', 'WRONG'), ('scipy', '1.15.3.post2', 'OK'),
                 ('pytest', '10.0.0', 'OK'), ('pytest', '8.3.2', 'WRONG'), ('pytest', '8.10', 'OK'), ('pytest', '8.3', 'WRONG'),
                 ('orjson', '3.11.10', 'OK'), ('orjson', '3.2', 'WRONG')]
        spec = {'scipy': 'scipy>=1.15.3', 'pytest': 'pytest>=8.3.3', 'orjson': 'orjson>=3.11.9'}
        for name, found, want in cases:
            w = self.world()
            w.fake_py('py', '3.11.3', dict(GOOD, **{name: found}))
            rc, out = w.run('--check')
            self.assertEqual(rc, 0 if want == 'OK' else 1, (name, found, out))
            self.assertIsNotNone(item(out, want, spec[name]), (name, found, out))

    def test_an_unknown_or_unreadable_version(self):
        w = self.world()
        w.fake_py('py', '3.11.3', dict(GOOD, numpy='?', scipy='banana'))
        rc, out = w.run('--check')
        self.assertEqual(rc, 1, out)
        self.assertIn('its version is not known', item(out, 'WRONG', 'numpy==2.2.6'))
        self.assertIn('banana installed: a version this check cannot read', item(out, 'WRONG', 'scipy>=1.15.3'))

    def test_a_broken_python3(self):
        w = self.world()
        w.fake_py('py', None, GOOD, raw_version='Traceback (most recent call last):\nboom\n')
        rc, out = w.run('--check')
        self.assertEqual(rc, 1, out)
        self.assertIn('the version probe failed: Traceback', item(out, 'WRONG', 'python3'))
        self.assertEqual(len(lines(out, 'UNCHECKED')), 5, out)

    def test_the_named_python_is_used(self):
        w = self.world()
        w.fake_py('path', '3.9.6', {})
        py, dd = w.fake_py('named', '3.11.3', GOOD, bindir=os.path.join(w.d, 'other'))
        rc, out = w.run('--check', '--python', py)
        self.assertEqual(rc, 0, out)
        self.assertIn('3.11.3 %s (--python;' % py, item(out, 'OK', 'python3'))
        self.assertFalse(os.path.exists(os.path.join(w.d, 'data_path', 'calls.log')))      # the PATH one was never asked
        rc, out = w.run('--check', '--python', 'other/python3')                            # relative to the current folder
        self.assertEqual(rc, 0, out)
        self.assertIn(os.path.realpath(py), item(out, 'OK', 'python3'))
        rc, out = w.run('--check', '--python', os.path.join(w.d, 'nope', 'python3'))
        self.assertEqual(rc, 1, out)
        self.assertIn('not an executable file', item(out, 'MISSING', 'python3'))

    def test_the_packages_file_is_read_line_by_line(self):
        text = '# a comment\n\n   \n  numpy == 2.2.6   # inline\r\npyarrow==25.0.1\r\n\tpytest>=8.3.3\nscipy>=1.15.3\norjson>=3.11.9'
        w = self.world(packages=text)
        w.fake_py('py', '3.11.3', GOOD)
        rc, out = w.run('--check')
        self.assertEqual(rc, 0, out)
        for spec in SPECS:
            self.assertIsNotNone(item(out, 'OK', spec), out)

    def test_a_line_that_is_not_name_op_version_is_refused(self):
        for bad in ('numpy', 'numpy~=2.2', 'numpy<3', 'numpy>2', 'numpy[x]==2.2.6', 'numpy==2.2.6,<3', 'numpy==2.2.6 ; python_version<"3.12"',
                    'git+https://example.org/x.git', '-r other.txt', '==2.2.6', 'numpy==', 'numpy===2.2.6', 'numpy==two'):
            w = self.world(packages='pytest>=8.3.3\n' + bad + '\n')
            py, dd = w.fake_py('py', '3.11.3', GOOD)
            for args in (('--check',), ('--install', os.path.join(w.d, 'py'), '--dry')):
                rc, out = w.run(*args)
                self.assertEqual(rc, 2, (bad, args, out))
                self.assertIn('REFUSED PACKAGES LINE 2 ', out, bad)
            self.assertFalse(os.path.exists(os.path.join(dd, 'calls.log')), bad)           # refused before any python is asked

    def test_no_packages_file(self):
        w = self.world(packages=None)
        w.fake_py('py', '3.11.3', GOOD)
        rc, out = w.run('--check')
        self.assertEqual(rc, 2, out)
        self.assertIn('REFUSED NO PACKAGES FILE', out)


class T03Usage(Case):
    def test_usage_exit_2(self):
        w = self.world()
        w.fake_py('py', '3.11.3', GOOD)
        dest = os.path.join(w.d, 'py')
        for args in ((), ('--nope',), ('check',), ('--dry',), ('--check', '--dry'), ('--install',), ('--install', '--dry'), ('--install', ''),
                     ('--check', '--python'), ('--check', '--python', '--dry'), ('--install', dest, '--python', 'x'),
                     ('--check', '--install', dest), ('--install', dest, '--check'), ('--check', '--python', 'a', '--python', 'b')):
            rc, out = w.run(*args)
            self.assertEqual(rc, 2, (args, out))
            self.assertTrue(out.startswith('USAGE '), (args, out))
        self.assertFalse(os.path.exists(dest))


class T04Refused(Case):
    def test_a_folder_inside_the_alarm_folder(self):
        w = self.world()
        w.fake_py('py', '3.11.3', GOOD, venv=('3.11.3', GOOD, None))
        link = os.path.join(w.d, 'link_into_alarm')
        os.symlink(os.path.join(w.alarm, 'settings'), link)
        tries = [w.alarm, os.path.join(w.alarm, 'py'), os.path.join(w.alarm, 'x', '..', 'py'), os.path.join(w.d, 'no', '..', 'Alarm', 'py'),
                 os.path.join(link, 'py'), link, os.path.join(w.alarm, '_tools', '..', '..', 'Alarm', 'venvs', 'py')]
        for dest in tries:
            for dry in ((), ('--dry',)):
                rc, out = w.run('--install', dest, *dry)
                self.assertEqual(rc, 2, (dest, out))
                self.assertIn('REFUSED FOLDER INSIDE THE ALARM FOLDER', out, dest)
        rc, out = w.run('--install', 'venvs/py', cwd=w.alarm)                         # a relative folder, from inside
        self.assertEqual(rc, 2, out)
        self.assertIn('REFUSED FOLDER INSIDE THE ALARM FOLDER %s/venvs/py' % os.path.realpath(w.alarm), out)
        self.assertEqual(sorted(os.listdir(w.alarm)), ['_tools', 'settings'])         # nothing made inside
        self.assertEqual(os.listdir(os.path.join(w.alarm, 'settings')), ['PYTHON_PACKAGES.txt'])

    def test_a_sibling_folder_is_not_inside(self):
        w = self.world()
        w.fake_py('py', '3.11.3', GOOD)
        rc, out = w.run('--install', w.alarm + '_python', '--dry')
        self.assertEqual(rc, 0, out)

    def test_a_folder_that_exists_and_is_not_empty(self):
        w = self.world()
        w.fake_py('py', '3.11.3', GOOD, venv=('3.11.3', GOOD, None))
        full = os.path.dirname(write(os.path.join(w.d, 'full', 'x.txt'), 'keep me\n'))
        dot = os.path.dirname(write(os.path.join(w.d, 'dot', '.hidden'), 'keep me\n'))
        dotdot = os.path.dirname(write(os.path.join(w.d, 'dotdot', '..x'), 'keep me\n'))
        sub = os.path.join(w.d, 'sub')
        os.makedirs(os.path.join(sub, 'venv'))
        afile = write(os.path.join(w.d, 'a_file'), 'keep me\n')
        dangling = os.path.join(w.d, 'dangling')
        os.symlink(os.path.join(w.d, 'no_such'), dangling)
        for dest, why in ((full, 'FOLDER EXISTS AND IS NOT EMPTY'), (dot, 'FOLDER EXISTS AND IS NOT EMPTY'), (dotdot, 'FOLDER EXISTS AND IS NOT EMPTY'),
                          (sub, 'FOLDER EXISTS AND IS NOT EMPTY'), (afile, 'NOT A FOLDER'), (dangling, 'NOT A FOLDER')):
            for dry in ((), ('--dry',)):
                rc, out = w.run('--install', dest, *dry)
                self.assertEqual(rc, 2, (dest, out))
                self.assertIn('REFUSED ' + why, out, dest)
        self.assertEqual((os.listdir(full), os.listdir(dot), os.listdir(dotdot), os.listdir(sub)), (['x.txt'], ['.hidden'], ['..x'], ['venv']))
        self.assertEqual(read(afile), 'keep me\n')
        self.assertFalse(os.path.exists(os.path.join(w.d, 'no_such')))

    def test_an_empty_folder_is_taken(self):
        w = self.world()
        w.fake_py('py', '3.11.3', GOOD, venv=('3.11.3', GOOD, None))
        empty = os.path.join(w.d, 'empty')
        os.makedirs(empty)
        rc, out = w.run('--install', empty, '--dry')
        self.assertEqual(rc, 0, out)
        self.assertIn('INSTALL  %s (an empty folder)' % os.path.realpath(empty), out)
        rc, out = w.run('--install', empty)
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-1], 'PYTHON=%s/venv/bin/python3' % os.path.realpath(empty))


class T05Dry(Case):
    def test_each_platform_gets_its_url_and_sha256(self):
        for s, m, p in UNAMES:
            w = self.world(uname=(s, m))
            w.fake_curl(b'never fetched')
            dest = os.path.join(w.d, 'new', 'py')
            rc, out = w.run('--install', dest, '--dry')
            self.assertEqual(rc, 0, (s, m, out))
            self.assertIn('PLATFORM %s (uname: %s %s)' % (p, s, m), out)
            self.assertEqual([l.split() for l in lines(out, 'URL ')], [['URL', url(p)]], out)
            self.assertEqual([l.split() for l in lines(out, 'SHA256 ')], [['SHA256', PINNED[p]]], out)
            d, f = os.path.realpath(dest), '%s/download/%s' % (os.path.realpath(dest), asset(p))
            steps = ['download %s to %s (curl)' % (url(p), f), 'sha256 of %s must be %s (the table)' % (f, PINNED[p]),
                     'unpack %s into %s/python (tar)' % (f, d), 'venv: %s/python/bin/python3 -m venv %s/venv' % (d, d),
                     'pip: %s/venv/bin/python3 -m pip install --disable-pip-version-check -r %s' % (d, os.path.realpath(w.pkgs)),
                     'check: --check --python %s/venv/bin/python3' % d, 'print the settings line PYTHON=%s/venv/bin/python3' % d]
            self.assertEqual([l.split(None, 1)[1].split(';')[0] if l.startswith('STEP     unpack') else l.split(None, 1)[1].split(' (for ')[0]
                              for l in lines(out, 'STEP ')], steps, out)
            self.assertEqual((out.splitlines()[0], out.splitlines()[-1]), ('DRY RUN: nothing is changed', 'DRY RUN: nothing was changed'))
            self.assertFalse(os.path.exists(os.path.join(w.d, 'new')))
            self.assertFalse(os.path.exists(w.curl_log))
            self.assertEqual(lines(out, 'PYTHON='), [])

    def test_no_pinned_build_for_this_machine(self):
        w = self.world(uname=('FreeBSD', 'amd64'))
        w.fake_curl(b'never fetched')
        rc, out = w.run('--install', os.path.join(w.d, 'py'), '--dry')
        self.assertEqual(rc, 1, out)
        self.assertIn("PLATFORM none pinned for uname 'FreeBSD amd64'", out)
        self.assertIn('FAILED plan: no python3 3.10 or 3.11 on PATH and no pinned build for this machine', out)
        w.fake_py('py', '3.11.3', GOOD)                                                   # a good python3 needs no build
        rc, out = w.run('--install', os.path.join(w.d, 'py'), '--dry')
        self.assertEqual(rc, 0, out)

    def test_a_python3_3_10_or_3_11_on_path_is_used_as_it_is(self):
        for v in ('3.10.12', '3.11.3'):
            w = self.world(uname=('Darwin', 'arm64'))
            py, dd = w.fake_py('py', v, GOOD)
            w.fake_curl(b'never fetched')
            rc, out = w.run('--install', os.path.join(w.d, 'py'), '--dry')
            self.assertEqual(rc, 0, out)
            self.assertIn('PYTHON3  %s %s on PATH: used as it is' % (py, v), out)
            self.assertEqual([l for l in lines(out, 'STEP ') if l.split()[1] in ('download', 'sha256', 'unpack')], [], out)
            self.assertIn('STEP     venv: %s -m venv ' % py, out)

    def test_other_versions_on_path_get_the_pinned_build(self):
        for v in ('3.9.6', '3.12.1', '3.14.0'):
            w = self.world(uname=('Linux', 'x86_64'))
            py, dd = w.fake_py('py', v, GOOD)
            w.fake_curl(b'never fetched')
            rc, out = w.run('--install', os.path.join(w.d, 'py'), '--dry')
            self.assertEqual(rc, 0, out)
            self.assertIn('%s %s on PATH: not 3.10 or 3.11' % (py, v), out)
            self.assertEqual([l.split()[2] for l in lines(out, 'STEP     download')], [url('x86_64-unknown-linux-gnu')], out)

    def test_no_downloader(self):
        w = self.world(uname=('Linux', 'aarch64'))                                      # no python3, no curl, no wget on PATH
        for dry in (('--dry',), ()):
            rc, out = w.run('--install', os.path.join(w.d, 'py'), *dry)
            self.assertEqual(rc, 1, out)
            self.assertIn('FAILED plan: neither curl nor wget is on PATH', out)
        self.assertFalse(os.path.exists(os.path.join(w.d, 'py')))


class T06Install(Case):
    def test_with_a_good_python3_on_path(self):
        w = self.world(uname=('Linux', 'x86_64'))
        w.fake_curl(b'never fetched')
        py, dd = w.fake_py('py', '3.11.3', dict(GOOD, orjson=None), venv=('3.11.3', GOOD, None))   # PATH's lacks orjson; the venv has all
        dest = os.path.join(w.d, 'new', 'py')
        rc, out = w.run('--install', dest)
        self.assertEqual(rc, 0, out)
        d = os.path.realpath(dest)
        self.assertEqual(out.splitlines()[-1], 'PYTHON=%s/venv/bin/python3' % d)
        self.assertEqual(read(os.path.join(dd, 'venv', 'pip.log')).split(),
                         ['-m', 'pip', 'install', '--disable-pip-version-check', '-r', os.path.realpath(w.pkgs)])
        self.assertEqual(read(os.path.join(dd, 'calls.log')).splitlines(), ['VERSION', 'VENV %s/venv' % d])
        self.assertIn('3.11.3 %s/venv/bin/python3 (the new venv;' % d, item(out, 'OK', 'python3'))
        for spec in SPECS:
            self.assertIsNotNone(item(out, 'OK', spec), out)
        self.assertFalse(os.path.exists(w.curl_log))
        self.assertEqual(sorted(os.listdir(d)), ['venv'])

    def test_a_relative_folder_is_printed_absolute(self):
        w = self.world()
        w.fake_py('py', '3.10.12', GOOD, venv=('3.10.12', GOOD, None))
        rc, out = w.run('--install', 'rel/py')
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines()[-1], 'PYTHON=%s/venv/bin/python3' % os.path.realpath(os.path.join(w.d, 'rel', 'py')))

    def test_pip_fails(self):
        w = self.world()
        w.fake_py('py', '3.11.3', GOOD, venv=('3.11.3', GOOD, 1))
        rc, out = w.run('--install', os.path.join(w.d, 'py'))
        self.assertEqual(rc, 1, out)
        self.assertEqual(len(lines(out, 'FAILED pip:')), 1, out)
        self.assertEqual(lines(out, 'PYTHON='), [])

    def test_the_new_venv_fails_its_check(self):
        w = self.world()
        w.fake_py('py', '3.11.3', GOOD, venv=('3.11.3', dict(GOOD, pyarrow='24.0.0'), None))
        rc, out = w.run('--install', os.path.join(w.d, 'py'))
        self.assertEqual(rc, 1, out)
        self.assertIsNotNone(item(out, 'WRONG', 'pyarrow==25.0.1'), out)
        self.assertEqual(len(lines(out, 'FAILED check: 1 items not OK')), 1, out)
        self.assertEqual(lines(out, 'PYTHON='), [])

    def test_venv_fails(self):
        w = self.world()
        w.fake_py('py', '3.11.3', GOOD, venv_rc=3)
        rc, out = w.run('--install', os.path.join(w.d, 'py'))
        self.assertEqual(rc, 1, out)
        self.assertEqual(len(lines(out, 'FAILED venv:')), 1, out)
        self.assertEqual(lines(out, 'PYTHON='), [])

    def test_a_download_with_another_sha256_is_never_unpacked(self):
        for (s, m, p), dl in zip(UNAMES, ('curl', 'curl', 'curl', 'curl', 'wget')):
            w = self.world(uname=(s, m))
            payload = w.tarball()
            w.fake_curl(payload, dl)
            dest = os.path.join(w.d, 'py')
            rc, out = w.run('--install', dest)
            self.assertEqual(rc, 1, out)
            d = os.path.realpath(dest)
            f = os.path.join(d, 'download', asset(p))
            self.assertEqual(len([l for l in lines(out, 'FAILED sha256: %s has ' % f) if 'the table says %s' % PINNED[p] in l]), 1, out)
            self.assertEqual(read(f, 'rb'), payload)                               # the download is left where it came
            self.assertEqual(sorted(os.listdir(d)), ['download'])                         # nothing unpacked, no venv
            self.assertEqual(read(w.curl_log).split()[-3:], ['-O' if dl == 'wget' else '-o', f, url(p)])   # the pinned URL of this platform
            self.assertIn('(%s)' % dl, lines(out, 'STEP     download')[0])
            self.assertEqual(lines(out, 'PYTHON='), [])


class T07RealPython(Case):
    """this test's own interpreter answers the real probes, on a distribution planted on PYTHONPATH whose module has another name"""
    def plant(self, w):
        site = os.path.join(w.d, 'site')
        write(os.path.join(site, 'k14probe_mod', '__init__.py'), '__version__ = "9.9.9"\n')
        di = os.path.join(site, 'k14_probe_dist-1.2.3.dist-info')
        write(os.path.join(di, 'METADATA'), 'Metadata-Version: 2.1\nName: k14-probe-dist\nVersion: 1.2.3\n')
        write(os.path.join(di, 'top_level.txt'), 'k14probe_mod\n')
        write(os.path.join(di, 'RECORD'), 'k14probe_mod/__init__.py,,\nk14_probe_dist-1.2.3.dist-info/METADATA,,\n')
        old = os.environ.get('PYTHONPATH')
        return {'PYTHONPATH': site + (os.pathsep + old if old else '')}

    def test_the_probes_on_a_real_python(self):
        ver = '%d.%d.%d' % tuple(sys.version_info[:3])
        w = self.world(packages='k14-probe-dist==1.2.3\nk14-probe-dist>=1.2\n')
        rc, out = w.run('--check', '--python', sys.executable, env=self.plant(w))
        self.assertEqual(rc, 0, out)
        self.assertIn('%s %s (--python;' % (ver, sys.executable), item(out, 'OK', 'python3'))
        self.assertEqual(item(out, 'OK', 'k14-probe-dist==1.2.3').split()[-1], '1.2.3')   # the distribution's version, not the module's
        self.assertEqual(item(out, 'OK', 'k14-probe-dist>=1.2').split()[-1], '1.2.3')
        w = self.world(packages='k14-probe-dist>=1.3\nk14-absent-dist==1.0\n')
        write(os.path.join(w.d, 'k14_absent_dist.py'), '__version__ = "1.0"\n')        # in the current folder: not a package
        rc, out = w.run('--check', '--python', sys.executable, env=self.plant(w))
        self.assertEqual(rc, 1, out)
        self.assertTrue(item(out, 'WRONG', 'k14-probe-dist>=1.3').endswith(' 1.2.3 installed'), out)
        self.assertIn('not importable: import k14_absent_dist gives ModuleNotFoundError', item(out, 'MISSING', 'k14-absent-dist==1.0'))
        self.assertIn('CHECK FAILED: 2 of 3 items not OK: k14-probe-dist>=1.3 k14-absent-dist==1.0 (', out)


if __name__ == '__main__':
    print('bash %s; python %s; temporary folder %s (left in place)' % (BASH, sys.version.split()[0], BASE), flush=True)
    r = unittest.main(exit=False, verbosity=1).result
    print('TESTS %d, failures %d, errors %d' % (r.testsRun, len(r.failures), len(r.errors)))
    sys.exit(0 if r.wasSuccessful() else 1)
