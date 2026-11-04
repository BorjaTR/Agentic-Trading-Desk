# tried_search_v1: tool card

Released in ALARM_V1_21_13 (step 1 copy search, chosen after desk trial 2; ALARM_V1_21_10 to V1_21_12 held, never current: GPT V12110, V12111 and V12112-TOOL HOLDs fixed here); TEST, NOT REVIEWED. The code: [tried_search_v1.py](../08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/tried_search_v1.py).
Answers AGENTS.md loop step 1, "was it tried?": which registry rows, claims and TRIED rows are closest to your idea's words, and, with your
definition, whether it is a COPY or NEAR of a registry alarm's or a claimed idea's definition, before any COUNT. It reads files only, runs no job,
reads no market data and writes nothing. It does not replace novelty (step 9), which compares fire lists after the GRADE.

## Run it
```
$PY -B <INSTALL>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/tried_search_v1.py --settings <S> <words of your idea>
$PY -B <INSTALL>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/tried_search_v1.py --settings <S> --def <RUN folder>/ideas/<IDEA>/defs/V1.json --self <RUN>_<IDEA> [<words>]
```
- `--def`: your definition; a relative path reads under RESEARCH_ROOT/ALARM_DESIGN. Its metric codes become words too (they count twice).
- `--self <RUN>_<IDEA>`: leave out your own claim, definitions and registry rows (the --def file itself is always left out).
- `--n`: hits printed per source, 1 to 50 (default 8).

## What you get
- `TRIED_SEARCH` line: the words, the def's sha16 and codes, each source with its sha16 and rows, defs read and defs unreadable.
- `REGISTRY`, `CLAIMS`, `TRIED` blocks: rows holding at least one word, most words first; each hit says which word was found in which field
  (`funding in one_line; e1.s01 in codes`). A word matches a whole token (E2.S04 is one token); a word of 4 or more letters also matches a
  longer token it starts.
- With --def, `DEF COPY|NEAR|SHARES <name> (<registry or claim> ...; def <path> sha16 <x>): <n> of <m> condition lines equal; codes; fire side`.
  The comparison is on structure: every input name is replaced by what it computes, `<` is turned to `>`, `a - b > 0` reads `a > b`.
  Numbers are compared at full precision; an event list a condition or the fire side reads counts by its file and days (not its name);
  the comparison base block (matched moments, its seed) and lists read only by the truth label or the base choose no fire, so a difference
  there is printed (`comparison base or unused event lists differ (fires unchanged)`), never a verdict; that note names only the base and
  the lists no condition or fire side reads, so a changed list the rule reads is a rule difference, never "fires unchanged" (ALARM_V1_21_15).
  COPY = the same condition lines, fire side and timing (grid_s, onset, refractory_s; the detector's defaults onset true, refractory 0).
  NEAR = the same lines and side with other timing; the same lines with the other side; or the same codes and lines with other
  numbers; or one rule is the other plus condition lines; or the same codes and half the lines. SHARES is information only.
- The last line: `VERDICT DEF COPY of ...` (not a new idea: change it, or run it as a named copy), `VERDICT DEF NEAR ...` (say on the card
  what differs), `VERDICT DEF INCOMPLETE` (no COPY or NEAR found, but some definition could not be read, or none was read: the paths are
  printed; not proven new), `VERDICT DEF NEW` (novelty on the fire list still decides), or `VERDICT WORDS ONLY` without --def. A COPY or
  NEAR is kept when other definitions are unreadable (a `DEF UNREADABLE` line names them).

## Refusals and exits
Exit 0 on any verdict; 2 refused (`REFUSED: ...` on stderr): no --settings, no word and no --def, a --def that is not JSON or has no inputs
or conditions (`BAD_DEF`), no def file, a registry without its columns, a bad --n or --self, an unknown option.

## How to read it right
- A COPY is about the rule, not the fires: the registry stops at its build stamp, so claims (IDEAS_CLAIMED) are searched too.
- NEW here is not novelty: two different rules can fire on the same moments. Step 9 (novelty_v5 on the GRADE fire list) still decides.
- Tests: tests/test_tried_search_v1.py (37, on frozen real fixtures; timing, precision, base and unreadable cases since ALARM_V1_21_11: DELEVHOUR, CLOSEOUT and WINDFALL disguised read COPY of SCOUTR12's try,
  AD2_OIFLUSH_OF1 and AD7_PAYERWIN_PW1; a planted new idea reads NEW), tests/mutants_tried_search_v1.py (26 planted bugs, all killed).
