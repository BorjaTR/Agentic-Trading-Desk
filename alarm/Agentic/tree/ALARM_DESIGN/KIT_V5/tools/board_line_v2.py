#!/usr/bin/env python3
"""board_line_v2.py (SCOUT for ALARM_DESIGN KIT_V5, 30 Oct 2026; edition 2 of board_line_v1.py ea7b62eb1437170d; TEST, NOT REVIEWED). Appends
ONE line to your board <BOARD>/<SEAT>.txt (BOARD: the team board folder hb, a key of the settings file). Runs from the Alarm package on
any machine. Never deletes; twins the board before the append (cp of the whole file to <board>.pre_<RUN>_<stamp>, opened 'x'; _2, _3
within one second).

  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/board_line_v2.py --settings <settings file> <RUN> <KIND>
             "<text: what, with files and sha16>"

Edition 2 changes only where things are (the owner 30 Oct 2026 22:21 Berlin: "Let's make sure everything can run from the release folder";
CLEAN_RELEASE_V1 section 6): the board folder is the settings key BOARD, read by the package's own _tools/settings_v1.py
(board_line_v1.py found the dev tree itself, _roots()); the line, its checks, the twin, the printed line and the exit codes are
board_line_v1.py's.

The line is '<UTC stamp from the clock> <SEAT> <KIND> <text>'. Refused: a line of 578 characters or more, a tab, a newline, an em dash,
a KIND not in the list, a text under 10 characters. KINDs: START CLAIM COUNT PREREG JOB DECISION STUCK ASK ANSWER CHECKPOINT DONE NOTE.
"""
import sys, os, re, datetime, importlib.util

CFG = {'HB': None,   # the board folder: configure() takes it from the settings key BOARD
       'now': lambda: datetime.datetime.now(datetime.timezone.utc)}
KINDS = ('START', 'CLAIM', 'COUNT', 'PREREG', 'JOB', 'DECISION', 'STUCK', 'ASK', 'ANSWER', 'CHECKPOINT', 'DONE', 'NOTE')
RUNTAG = re.compile(r'^([A-Z][A-Z0-9]{0,11})_([0-9]{8})$')
LIMIT = 578


class Refused(Exception):
    pass


def settings_reader():
    """the settings reader of the Alarm package this file is in (<Alarm>/_tools/settings_v1.py), loaded from that file"""
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise Refused('NOT INSIDE AN ALARM PACKAGE: %s (run the copy in the Alarm folder)' % os.path.abspath(__file__))
        d = os.path.dirname(d)
    spec = importlib.util.spec_from_file_location('settings_v1', os.path.join(d, '_tools', 'settings_v1.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def configure(settings):
    """CFG['HB'] from the settings key BOARD (inside an Alarm package: settings_v1.alarm_root of this file)"""
    S = settings_reader()
    try:
        S.alarm_root(__file__)
        CFG['HB'] = S.get(settings, 'BOARD')
    except S.Refused as e:
        raise Refused('SETTINGS: %s' % e)


def main(argv):
    argv = list(argv)
    settings = None
    if '--settings' in argv:
        i = argv.index('--settings')
        if i + 1 >= len(argv):
            raise Refused('--settings NEEDS A VALUE')
        settings = argv[i + 1]; del argv[i:i + 2]
    if len(argv) != 3:
        raise Refused('USAGE board_line_v2.py --settings <settings file> RUN KIND "text"')
    if not settings:
        raise Refused('--settings <file> IS REQUIRED: the settings file of this machine (<Alarm>/settings/SETTINGS_<MACHINE>.env)')
    runtag, kind, text = argv
    m = RUNTAG.match(runtag)
    if not m:
        raise Refused('BAD RUN TAG %r' % runtag)
    if kind not in KINDS:
        raise Refused('KIND %r: one of %s' % (kind, ' '.join(KINDS)))
    if '\t' in text or '\n' in text or '\r' in text:
        raise Refused('TAB OR NEWLINE IN THE TEXT')
    if '\u2014' in text:
        raise Refused('EM DASH IN THE TEXT')
    if len(text.strip()) < 10:
        raise Refused('TEXT TOO SHORT: say what, with its file')
    seat = m.group(1)
    now = CFG['now']()
    stamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    line = '%s %s %s %s' % (stamp, seat, kind, text.strip())
    if len(line) >= LIMIT:
        raise Refused('LINE IS %d CHARACTERS (the limit is under %d): shorten it' % (len(line), LIMIT))
    configure(settings)
    p = os.path.join(CFG['HB'], seat + '.txt')
    if os.path.exists(p):
        base = '%s.pre_%s_%s' % (p, runtag, now.strftime('%Y%m%dT%H%M%SZ'))
        twin, k = base, 1
        while True:                                   # two lines in the same second get _2, _3 (GPT1 PROBLEMS 29 Oct 14:47:51Z)
            try:
                g = open(twin, 'xb')
                break
            except FileExistsError:
                k += 1
                twin = '%s_%d' % (base, k)
        with open(p, 'rb') as f, g:
            g.write(f.read())
        with open(p, 'rb') as f:
            f.seek(0, 2)
            n = f.tell()
            last = b'\n'
            if n:
                f.seek(n - 1); last = f.read(1)
        with open(p, 'a') as f:
            if last != b'\n':
                f.write('\n')
            f.write(line + '\n')
    else:
        with open(p, 'x') as f:
            f.write(line + '\n')
    print('POSTED', p, len(line), 'chars')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
