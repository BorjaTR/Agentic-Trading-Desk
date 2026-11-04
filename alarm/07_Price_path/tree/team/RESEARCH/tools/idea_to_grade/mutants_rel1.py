#!/usr/bin/env python3
"""mutants_rel1.py (SCOUT, K6, 31 Oct 2026; TEST, NOT REVIEWED): planted bugs in every new line of the rel1 editions of the grader V3.2
speed twin S6 (owner STRATEGY/LEAD), its clean kernels alarm_stamp_ed1_1 and alarm_stamp_projection_v2, and markout_v1_2. Each bug is
planted in a COPY of the files the chain runs (copied from the tree root four folders above this file, in the team/ layout: the
files the two rel1 pins files name, the tables and the tests), then test_rel1_paths.py and the old test of that file's tool run on the
copy: every bug must make one of them fail (KILLED). Never edits the real files. New edition by SCOUT for the clean release.
A planted bug for every changed code line of these editions (a line that only says a message or a help text excepted when no reader
parses it); the copies are byte copies (shutil.copyfile: a read-only install gives writable copies).
  python3 -B mutants_rel1.py [FIRST:LAST]     (the planted bugs FIRST..LAST, 1-based; exit 0: every one of them killed)"""
import json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.realpath(__file__))
FO = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))
R = 'team/RESEARCH/tools/'; I = R + 'idea_to_grade/'; B2 = 'team/OUTSIDE/COORD/development/DEV1/b2_performance_v1/'
EXTRA = [I + f for f in ('I2G_PINS_V3_2_S6_REL1.json', 'I2G_PINS_V3_2_REL1.json', 'test_rel1_paths.py', 'test_patch_s6_rel1.py', 'release_pins_v3_2_rel1.py',
                         'i2g_rules_v1.py', 'i2g_universe_v1.py', 'alarm_contract_v1.py')] + [
    R + 'markout/markout_v1_2.py', R + 'markout/test_markout_v1_2.py', R + 'markout/test_markout_v1_2_base.py', R + 'markout/settings/SETTINGS_V1.json',
    R + 'alarm_stamp/test_alarm_stamp_ed1_1.py', R + 'alarm_stamp/STAMP_CATALOG_V1_1.tsv', R + 'alarm_context/CTX_CATALOG_V1.tsv', R + 'alarm_context/COIN_TYPES_V1.tsv',
    R + 'freeze_judge/WINDOWS_V1.tsv', 'team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V1.tsv']
T_PATHS = (I, 'test_rel1_paths.py'); T_PATCH = (I, 'test_patch_s6_rel1.py', '2000'); T_MO = (R + 'markout/', 'test_markout_v1_2.py', '@W')
T_ST = (R + 'alarm_stamp/', 'test_alarm_stamp_ed1_1.py')
M = [   # (file, the text, the bug, extra test)
    (I + 'idea_to_grade_rel1.py', "F = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))", "F = os.path.realpath(os.path.join(HERE, '..', '..', '..'))", None),
    (I + 'idea_to_grade_rel1.py', "GATE = None ", "GATE = F + '/team/FEED/stops/BACKFILL_GATE.txt' ", None),
    (I + 'idea_to_grade_rel1.py', "    if not GATE:\n        return True\n    with open(GATE) as f:", "    with open(GATE) as f:", None),
    (I + 'idea_to_grade_rel1.py', "    GATE = path or None\n", "    GATE = None\n", None),
    (I + 'idea_to_grade_rel1.py', "        if os.path.isabs(q) or '/../' in '/%s/' % q:", "        if False:", None),
    (I + 'idea_to_grade_rel1.py', "        out[os.path.realpath(os.path.join(F, q))] = h", "        out[q] = h", None),
    (I + 'idea_to_grade_rel1.py', "import i2g_engine_rel1 as E, detect_v2 as detect\n", "import i2g_engine_rel1 as E, detect\n", None),
    (I + 'idea_to_grade_rel1.py', "PINS_FILE = None ", "PINS_FILE = os.path.join(HERE, 'I2G_PINS_V2.json') ", None),
    (I + 'idea_to_grade_rel1.py', "    p.add_argument('--pins', required=True,", "    p.add_argument('--pins', default=PINS_FILE,", None),
    (I + 'idea_to_grade_rel1.py', "    p.add_argument('--lab-root', required=True, help='the lab days (the settings key LAB_DAYS)'); p.add_argument('--seed'",
     "    p.add_argument('--lab-root', default='/l'); p.add_argument('--seed'", None),
    (I + 'idea_to_grade_rel1.py', "research_window=window, gate=GATE)", "research_window=window)", None),
    (I + 'i2g_engine_rel1.py', "'..', '..', '..', '..'))   # the tree root", "'..', '..', '..'))   # the tree root", None),
    (I + 'i2g_engine_rel1.py', "    TOOLS + '/alarm_stamp/alarm_stamp_ed1_1.py':", "    TOOLS + '/alarm_stamp/alarm_stamp.py':", None),
    (I + 'i2g_engine_rel1.py', "load_path(B2 + '/alarm_stamp_projection_v2.py'", "load_path(B2 + '/alarm_stamp_projection_v1.py'", None),
    (I + 'i2g_engine_rel1.py', "load_path(B2 + '/draw_prepared_v2.py'", "load_path(B2 + '/draw_prepared_v1.py'", None),
    (I + 'i2g_engine_rel1.py', "    B2 + '/draw_prepared_v2.py': 'ef46ca7be926f96a',", "    B2 + '/draw_prepared_v2.py': '5ab85ba9e777f38f',", None),
    (I + 'i2g_grade_rel1.py', "'..', '..', '..', 'OUTSIDE', 'COORD', 'development'))", "'..', '..', 'OUTSIDE', 'COORD', 'development'))", None),
    (I + 'i2g_grade_rel1.py', "REF = DEV + '/DEV1/opportunity_compare_v1/compare_v2.py'", "REF = DEV + '/DEV1/opportunity_compare_v1/compare.py'", None),
    (I + 'i2g_grade_rel1.py', "            import i2g_engine_rel1 as E\n", "            import i2g_engine as E\n", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "PINS_FILE = os.path.join(HERE, 'I2G_PINS_V3_2_REL1.json')", "PINS_FILE = os.path.join(HERE, 'I2G_PINS_V3_2.json')", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "REGISTRY_REL = 'LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv'", "REGISTRY_REL = 'LIBRARY/ALARM_REGISTRY_V1.tsv'", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    canon = bool(LEDGER and REGISTRY) and ", "    canon = ", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    p.add_argument('--lab-root', required=True,", "    p.add_argument('--lab-root', default='/l',", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    p.add_argument('--research-root', required=True,", "    p.add_argument('--research-root', default='/x',", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    set_research_root(a.research_root); I2.set_gate(a.gate)\n", "    set_research_root(a.research_root)\n", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    a.ledger = a.ledger or LEDGER; a.registry = a.registry or REGISTRY\n", "", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    import i2g_engine_v3_2_rel1 as E\n", "    import i2g_engine_v3_2 as E\n", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "research_window=window, gate=I2.GATE)", "research_window=window)", None),
    (I + 'idea_to_grade_v3_2_s6_rel1.py', "import idea_to_grade_v3_2_s3_rel1 as S3", "import idea_to_grade_v3_2_s3 as S3", None),
    (I + 'idea_to_grade_v3_2_s6_rel1.py', "i2g_patch_s4_v1, i2g_patch_s6_rel1   # noqa", "i2g_patch_s4_v1, i2g_patch_s6_v1   # noqa", None),
    (I + 'idea_to_grade_v3_2_s3_rel1.py', "import idea_to_grade_v3_2_s2_rel1 as S2", "import idea_to_grade_v3_2_s2 as S2", None),
    (I + 'idea_to_grade_v3_2_s2_rel1.py', "    import i2g_engine_v3_2_s2_rel1, i2g_rules_fast_v1", "    import i2g_engine_v3_2_s2, i2g_rules_fast_v1", None),
    (I + 'i2g_engine_v3_2_s6_rel1.py', "import i2g_engine_rel1 as E2\n", "import i2g_engine as E2\n", None),
    (I + 'i2g_engine_v3_2_s6_rel1.py', "import i2g_patch_s6_rel1 as P6\n", "import i2g_patch_s6_v1 as P6\n", None),
    (I + 'i2g_engine_v3_2_rel1.py', "import i2g_engine_rel1 as E2\n", "import i2g_engine as E2\n", None),
    (I + 'i2g_patch_s6_rel1.py', "    import i2g_engine_rel1 as E2\n", "    import i2g_engine as E2\n", T_PATCH),
    (I + 'release_pins_v3_2_rel1.py', "    pins = {os.path.relpath(q, I2.F): h for q, h in pins.items()}", "    pins = dict(pins)", None),
    (I + 'make_pins_s6_rel1.py', "import release_pins_v3_2_rel1 as RP", "import release_pins_v3_2 as RP", None),
    (R + 'alarm_stamp/alarm_stamp_ed1_1.py', "import alarm_context_ed1_1 as AC ", "import alarm_context as AC ", T_ST),
    (R + 'alarm_stamp/alarm_stamp_ed1_1.py', "    if not out_root:\n        raise ValueError('OUT_ROOT_REQUIRED", "    if False:\n        raise ValueError('OUT_ROOT_REQUIRED", T_ST),
    (R + 'alarm_stamp/alarm_stamp_ed1_1.py', "os.path.join(HERE, 'alarm_stamp_ed1_1.py'), CATALOG", "os.path.join(HERE, 'alarm_stamp.py'), CATALOG", T_ST),
    (B2 + 'alarm_stamp_projection_v2.py', "from alarm_stamp_ed1_1 import *\nimport alarm_stamp_ed1_1 as PROJECTION_BASE", "from alarm_stamp import *\nimport alarm_stamp as PROJECTION_BASE", None),
    (R + 'markout/markout_v1_2.py', "os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))   # <team>", "os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))   # <team>", T_MO),
    (R + 'markout/markout_v1_2.py', "    import i2g_engine_rel1 as E2\n    import i2g_rules_v1_2 as RU\n    import i2g_rules_fast_v3 as RF\n", "    import i2g_engine as E2\n    import i2g_rules_v1_2 as RU\n    import i2g_rules_fast_v3 as RF\n", T_MO),
    (R + 'markout/markout_v1_2.py', "    import i2g_engine_rel1 as E2\n    import i2g_rules_v1_2 as RU\n    names3", "    import i2g_engine as E2\n    import i2g_rules_v1_2 as RU\n    names3", T_MO),
    (R + 'markout/markout_v1_2.py', "V34 = TOOLS + '/i2g_v3_3'", "V34 = TOOLS + '/i2g_v3_4'", T_MO),
    (I + 'idea_to_grade_rel1.py', "LAB_ROOT = None ", "LAB_ROOT = '/opt/lab_days' ", None),
    (I + 'idea_to_grade_rel1.py', "    global GATE\n", "", None),
    (I + 'idea_to_grade_rel1.py', "import i2g_engine_rel1 as E, i2g_grade_rel1 as GR, detect_v2 as detect\n", "import i2g_engine_rel1 as E, i2g_grade as GR, detect_v2 as detect\n", None),
    (I + 'idea_to_grade_rel1.py', "    out = {}\n    for q, h in pins.items():", "    out = dict(pins)\n    for q, h in pins.items():", None),
    (I + 'idea_to_grade_rel1.py', "            raise Refused('PINS_FILE', '%s names %s: a pins file", "            raise Refused('PINS_OTHER', '%s names %s: a pins file", None),
    (I + 'idea_to_grade_rel1.py', "        out[os.path.realpath(os.path.join(F, q))] = h\n    return out\n", "        out[os.path.realpath(os.path.join(F, q))] = h\n    return pins\n", None),
    (I + 'idea_to_grade_rel1.py', "    import i2g_engine_rel1 as E, i2g_grade_rel1 as GR\n", "    import i2g_engine_rel1 as E, i2g_grade as GR\n", None),
    (I + 'idea_to_grade_rel1.py', "'EVENT_LIST'):\n        import detect_v2 as detect\n", "'EVENT_LIST'):\n        import detect\n", None),
    (I + 'idea_to_grade_rel1.py', "selected rows\"\"\"\n    import detect_v2 as detect\n", "selected rows\"\"\"\n    import detect\n", None),
    (I + 'idea_to_grade_rel1.py', "    E = warm(); import i2g_grade_rel1 as GR, detect_v2 as detect\n", "    E = warm(); import i2g_grade as GR, detect_v2 as detect\n", None),
    (I + 'idea_to_grade_rel1.py', "    import i2g_grade_rel1 as GR\n", "    import i2g_grade as GR\n", None),
    (I + 'idea_to_grade_rel1.py', "(detect_v2.py format, DETECT_V1)", "(detect.py format)", None),
    (I + 'idea_to_grade_rel1.py', "    p.add_argument('--gate', default=None, help=\"the feed's stop gate file (the settings key FEED_GATE); empty or not given: no gate\")\n", "", None),
    (I + 'idea_to_grade_rel1.py', "    import detect_v2 as detect\n    set_gate(a.gate)\n", "    import detect\n    set_gate(a.gate)\n", None),
    (I + 'idea_to_grade_rel1.py', "    set_gate(a.gate)\n", "", None),
    (I + 'i2g_engine_rel1.py', "    TOOLS + '/alarm_context/alarm_context_ed1_1.py': 'ab5d915138cb1f01',", "    TOOLS + '/alarm_context/alarm_context.py': '38bdf42a6bdae4cb',", None),
    (I + 'i2g_engine_rel1.py', "    B2 + '/alarm_stamp_projection_v2.py': '914ec6f23260940e',", "    B2 + '/alarm_stamp_projection_v2.py': '049ceb37cb3b6947',", None),
    (I + 'i2g_engine_rel1.py', "    B2 + '/prepared_activity_v2.py': '2878fb0d5ae9d4f5',", "    B2 + '/prepared_activity_v1.py': 'aba7ea04de649037',", None),
    (I + 'i2g_grade_rel1.py', "PINS = {FAST: 'eec15093614540d5', REF: 'e7f7f91ad15183d7'}", "PINS = {FAST: 'eec15093614540d5', REF: '594a7bc354a323b1'}", None),
    (I + 'i2g_grade_rel1.py', "    import i2g_engine_rel1 as E\n    return E.load_path(path, name)", "    import i2g_engine as E\n    return E.load_path(path, name)", None),
    (I + 'i2g_grade_rel1.py', "    import resource\n    import i2g_engine_rel1 as E\n", "    import resource\n    import i2g_engine as E\n", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "import idea_to_grade_rel1 as I2\n", "import idea_to_grade as I2\n", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "LEDGER = REGISTRY = None ", "LEDGER = REGISTRY = '/x' ", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "LEDGER_REL = 'TRIES_LEDGER_V1.tsv'", "LEDGER_REL = 'TRIES_LEDGER.tsv'", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    global LEDGER, REGISTRY\n", "", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "REGISTRY = os.path.join(root, REGISTRY_REL)\n", "REGISTRY = os.path.join(root, LEDGER_REL)\n", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    import i2g_engine_v3_2_rel1, i2g_grade3_v3_2 ", "    import i2g_engine_v3_2, i2g_grade3_v3_2 ", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    import i2g_engine_rel1 as E2\n    E2.process_modules(refresh=True)", "    import i2g_engine as E2\n    E2.process_modules(refresh=True)", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "rows\"\"\"\n    import detect_v2 as detect\n    src = os.path.abspath(a.events)", "rows\"\"\"\n    import detect\n    src = os.path.abspath(a.events)", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "def selected_coins(a):\n    import detect_v2 as detect\n", "def selected_coins(a):\n    import detect\n", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    E = warm(); import i2g_grade_rel1 as GR, i2g_grade3_v3_2 as G3, detect_v2 as detect\n", "    E = warm(); import i2g_grade as GR, i2g_grade3_v3_2 as G3, detect_v2 as detect\n", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    p.add_argument('--gate', default=None, help=\"the feed's stop gate file (the settings key FEED_GATE); empty or not given: no gate\")\n    p.add_argument('--research-root'", "    p.add_argument('--research-root'", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    p.add_argument('--ledger', default=None,", "    p.add_argument('--ledger', default='/x/L.tsv',", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "    p.add_argument('--registry', default=None,", "    p.add_argument('--registry', default='/x/R.tsv',", None),
    (I + 'idea_to_grade_v3_2_rel1.py', "        p.error('--roster is required')\n    import detect_v2 as detect\n", "        p.error('--roster is required')\n    import detect\n", None),
    (I + 'idea_to_grade_v3_2_s2_rel1.py', "import idea_to_grade_v3_2_rel1 as G\n", "import idea_to_grade_v3_2 as G\n", None),
    (I + 'idea_to_grade_v3_2_s2_rel1.py', "    return i2g_engine_v3_2_s2_rel1\n", "    return i2g_rules_fast_v1\n", None),
    (I + 'idea_to_grade_v3_2_s3_rel1.py', "import idea_to_grade_v3_2_rel1 as G\n", "import idea_to_grade_v3_2 as G\n", None),
    (I + 'idea_to_grade_v3_2_s6_rel1.py', "import idea_to_grade_v3_2_rel1 as G\n", "import idea_to_grade_v3_2 as G\n", None),
    (I + 'idea_to_grade_v3_2_s6_rel1.py', "    return i2g_engine_v3_2_s6_rel1\n", "    return i2g_patch_s6_rel1\n", None),
    (I + 'i2g_engine_v3_2_s2_rel1.py', "import i2g_engine_rel1 as E2\n", "import i2g_engine as E2\n", None),
    (I + 'release_pins_v3_2_rel1.py', "import idea_to_grade_v3_2_rel1 as I3\n", "import idea_to_grade_v3_2 as I3\n", None),
    (I + 'release_pins_v3_2_rel1.py', "import idea_to_grade_rel1 as I2\n", "import idea_to_grade as I2\n", None),
    (I + 'release_pins_v3_2_rel1.py', "    import i2g_engine_rel1 as E2\n", "    import i2g_engine as E2\n", None),
    (I + 'release_pins_v3_2_rel1.py', "    for f in ('idea_to_grade_v3_2_rel1.py', 'idea_to_grade_rel1.py',", "    for f in ('idea_to_grade_v3_2.py', 'idea_to_grade.py',", None),
    (I + 'release_pins_v3_2_rel1.py', "    out = [q for q in pins if not q.startswith(I2.F + os.sep)]\n", "    out = []\n", None),
    (I + 'release_pins_v3_2_rel1.py', "'by': os.path.basename(sys.argv[0]),", "'by': 'release_pins_v3_2.py',", None),
    (I + 'release_pins_v3_2_rel1.py', "'paths': 'relative to the tree root (the folder above team/)', ", "", None),
    (I + 'make_pins_s6_rel1.py', "import idea_to_grade_v3_2_s6_rel1 as S6 ", "import idea_to_grade_v3_2_s6 as S6 ", None),
    (I + 'make_pins_s6_rel1.py', "import idea_to_grade_rel1 as I2\n", "import idea_to_grade as I2\n", None),
    (I + 'make_pins_s6_rel1.py', "for f in ('i2g_engine_v3_2_s2_rel1.py', 'i2g_rules_fast_v1.py',", "for f in ('i2g_engine_v3_2_s2.py', 'i2g_rules_fast_v1.py',", None),
    (R + 'alarm_stamp/alarm_stamp_ed1_1.py', "OUT_ROOT = None ", "OUT_ROOT = '/x/research_days' ", None),
    (R + 'alarm_stamp/alarm_stamp_ed1_1.py', "CATALOG = os.path.join(HERE, 'STAMP_CATALOG_V1_1.tsv')", "CATALOG = os.path.join(HERE, 'STAMP_CATALOG_V1.tsv')", T_ST),
    (R + 'alarm_stamp/alarm_stamp_ed1_1.py', "'# STAMP_CATALOG_V1_1: the codes of STAMP_CATALOG_V1, generated by alarm_stamp_ed1_1.py catalog;", "'# STAMP_CATALOG_V1: generated by alarm_stamp.py catalog;", T_ST),
    (R + 'markout/markout_v1_2.py', "I2G = TOOLS + '/idea_to_grade'\n", "I2G = TOOLS + '/idea_to_grade_v3'\n", T_MO),
]


def files():
    out = set(EXTRA)
    for p in ('I2G_PINS_V3_2_S6_REL1.json', 'I2G_PINS_V3_2_REL1.json'):
        out |= set(json.load(open(os.path.join(HERE, p)))['pins'])
    return sorted(out)


def run(tree, t, work):
    d, name = os.path.join(tree, t[0]), t[1]
    args = [a.replace('@W', os.path.join(work, 'w')) for a in t[2:]]
    r = subprocess.run([sys.executable, '-B', os.path.join(d, name)] + args, cwd=d, capture_output=True, text=True,
                       env=dict(os.environ, LAB3_CODE=os.path.join(tree, 'team', 'LAB3', 'code')), timeout=600)
    return r.returncode, (r.stdout + r.stderr).strip().split('\n')[-1][:120]


def main(argv):
    lo, hi = (int(x) for x in argv[0].split(':')) if argv else (1, len(M))
    fs = files(); killed = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, 'base')
        for rel in fs:
            os.makedirs(os.path.dirname(os.path.join(base, rel)), exist_ok=True); shutil.copyfile(os.path.join(FO, rel), os.path.join(base, rel))
        c, last = run(base, T_PATHS, tmp)
        print('UNMUTATED copy (%d files): test_rel1_paths exit %d: %s' % (len(fs), c, last))
        if c:
            return 2
        for n, (rel, a, b, extra) in enumerate(M, 1):
            if not lo <= n <= hi:
                continue
            tree = os.path.join(tmp, 'm%d' % n); shutil.copytree(base, tree, copy_function=shutil.copyfile)
            src = open(os.path.join(tree, rel)).read()
            assert src.count(a) == 1, ('mutant target not found once', n, rel, a[:80])
            open(os.path.join(tree, rel), 'w').write(src.replace(a, b))
            results = [run(tree, T_PATHS, tree)] + ([run(tree, extra, tree)] if extra else [])
            caught = any(c != 0 for c, _ in results); killed += caught
            print('MUTANT %2d %-38s %-60s %s' % (n, os.path.basename(rel), b.strip().split('\n')[-1][:60], 'KILLED' if caught else 'SURVIVED %s' % results))
            shutil.rmtree(tree)
    want = len([n for n in range(1, len(M) + 1) if lo <= n <= hi])
    print('MUTANTS %d of %d killed (planted bugs %d to %d of %d)' % (killed, want, lo, min(hi, len(M)), len(M)))
    return 0 if killed == want else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
