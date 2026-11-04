---
name: desk-setup
description: Use when a desk installs the Crypto Alarm Desk or points it at new data - checks the install, asks the trading style, finds the data and its metric register, compares the data with the style and the engine's minimums, and ends in GO, GO WITH GAPS or STOP with what is missing. Basic V1 edition: one supported profile, no converter yet.
---

# Desk setup (basic, V1)

Goal: from an empty folder to a desk that can run its first sealed try, asking only what you cannot find out yourself. Every branch ends
in a working setup or a clear STOP that says what is missing. Never write inside the data folder; never download anything without the
desk's yes. Write the result to `OUTPUT_ROOT/setup/SETUP_REPORT_<YYYYMMDDTHHMMSSZ>.md` (stamp from the clock) and show it.

## 1. Install
- Python 3.10 or 3.11 with `alarm/settings/PYTHON_PACKAGES.txt`. Settings: `cp settings/desk.env.example settings/desk.env` and set
  DATA_ROOT, OUTPUT_ROOT, PYTHON (paths with letters, digits and `_ . / -` only). A settings file may live outside the repo: pass it with
  `--settings <file>` to every desk command.
- `python3 -B desk/desk.py setup`, then `python3 -B desk/desk.py check`. Any fault other than the expected empty keys (HL_FILLS,
  RUNNER_RELEASE, FEED_GATE) is a STOP: report it word for word.
- `python3 -B desk/desk.py tests` proves the engine on this machine (a long run; private-data rows report KNOWN with their reason).

## 2. Trading style (ask, one question at a time)
What do you trade (venues, coins), at which horizon, and what decision should an alarm serve? Map the answer:
| style | needs at least | V1 says |
|---|---|---|
| HFT, under 1 s | tick trades and book updates with exchange stamps, known latency | out of scope: STOP, say what it would need |
| intraday fast, seconds to 15 min | trades or 1 to 5 s bars, flow or liquidations, OI at 1 min | partly: minute decisions only; claims that need order inside a minute are refused |
| intraday 15 min to hours (native) | 1 min bars plus one non-price metric at 1 min or finer | supported: the engine's pinned profile |
| swing, hours to days | hourly bars, daily OI or funding | not in V1: STOP, needs a separately reviewed edition |
| position, days to weeks | daily bars, a year or more | not in V1: too few events |

## 3. Data and register
- The engine reads one-format day folders: `DATA_ROOT/lab_days/FORMAT.json` and `DATA_ROOT/lab_days/day=YYYYMMDD/<PART>/index.json`.
  Look, read only: `python3 -B -c "import os,sys; r=sys.argv[1]; d=sorted(x for x in os.listdir(r) if x.startswith('day=')); print(len(d), d[:1], d[-1:]); print(sorted(os.listdir(os.path.join(r,d[-1]))) if d else 'no days')" <DATA_ROOT>/lab_days`
- No `lab_days` there, or the data is not yet in the format: the desk ships no converter, it ships instructions. List what the desk has
  (folders, file kinds, columns, time stamps), then, with the desk's yes, follow `docs/CONVERT_YOUR_DATA_V2.md` (fit, parts, column
  mapping, writing, the small proofs first) to write a new data folder: the only write into a data folder, never into the user's raw
  files. The format, with the code line of every rule: `docs/DATA_FORMAT_V2.md`. Never invent a value: a missing field leaves its code
  out. Download nothing without the desk's yes. Data without the engine's days (20250910 to 20251231) or without trades: STOP and say so.
- The register: the engine's metric menu `alarm/Agentic/tree/ALARM_DESIGN/KIT_V5/METRIC_MENU_V2.tsv` names every code the rule tool
  accepts, with unit, window and when each value is known. A desk's own metric list is mapped name by name to these codes; anything not
  on the menu is UNPROVEN and may not be read by a rule until its own proof passes.
- The fixed test sample: `python3 -B desk/data/sample_check.py <DATA_ROOT>/lab_days` says SAMPLE OK when the data holds it unchanged.
  It pins the lab's own index bytes: converted data says CHANGED or MISSING there (expected); pin your own sample as
  `docs/CONVERT_YOUR_DATA_V2.md` step 5c says.

## 4. Fit and minimums
| need | hard minimum | why |
|---|---|---|
| price | trades or 1 minute bars, one exchange | every moment and outcome is measured from price |
| coins | 10 | events are counted across coins |
| history | 4 build months, plus later months kept closed | build on some months, confirm on others |
| independent reading | one non-price metric (OI, funding or liquidations) | the TRUE check needs a label the rule does not read |
| time stamps | when each value was known | nothing may use later data |
Setup ready is not idea ready: the 30-waves-in-3-of-4-build-months bar is each idea's COUNT, and falling short there is a valid result.

## 5. End
- GO: install checks pass, native profile, data in the format, every minimum met.
- GO WITH GAPS: runs, but each gap is named (a metric family missing, coins under 50, history under 12 months); every later result
  names the gap it ran with.
- STOP: what is missing and what would fix it, in one list.
Then hand over to the alarm-desk skill (`/new-alarm`).
