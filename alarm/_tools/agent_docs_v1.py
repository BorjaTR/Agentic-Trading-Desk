#!/usr/bin/env python3
"""agent_docs_v1.py (SCOUT's K9, 30 Oct 2026; TEST, NOT REVIEWED): the agent docs of the Alarm package's tools, generated from their code.
the owner, 30 Oct 2026 23:07 Berlin: "build the system we said with the agents.md and the full system for agents to know instantly how to use
each tool and where everything is and all metrics and the process clear". This is layers 2 and 3 of that system, for every tool in TOOLS:
  cards/<tool>.md                  the tool card, written by hand (a skeleton is written only when none exists)
  cards/<tool>.TOOL.json           every command, argument, rule and example, and every output column; the parts read from the code are
                                   refreshed (GENERATED below), the parts written by hand are kept
  dictionaries/<tool>_COLUMNS.tsv  every output column: file, column, meaning, unit, known_at, empty_means, source_line; the column list and
                                   source_line come from the code; the other cells are kept; a new column gets NOT DOCUMENTED IN CODE
Code is read only inside the Alarm folder that holds this file (settings_v1.alarm_root); no data is read and no tool is run.

  python3 -B <Alarm>/_tools/agent_docs_v1.py (--check | --write) [--docs <folder>] [--tool <tool>]...
    --docs   the folder that holds cards/ and dictionaries/ (default: this Alarm folder; the dev home when SCOUT refreshes them there)
    --check  prints every difference between the docs and the code (STALE lines); exit 0 when there is none, 3 when there is one
    --write  refreshes every TOOL.json and dictionary (and writes a card skeleton where none exists); prints what changed; twins a
             file before it rewrites it (<file>.pre_agent_docs_<UTC stamp>); never deletes a file; a column the code no longer writes
             leaves its dictionary (printed as DROPPED; its old row stays in the twin)
Exit 0 ok, 3 stale (--check), 2 refused. A new tool: add its entry to TOOLS (its file, its outputs and where each output's columns are
written in the code), run --write, then write its card and the cells marked TO WRITE BY HAND or NOT DOCUMENTED IN CODE by hand.

How the columns are read from the code (one reader per kind of writer; each gives the column, its file and its line):
  seq NAME            a Python list or tuple of strings assigned to NAME (e.g. COLS)
  register NAME       the header of the KIT_V5 run register NAME (runs/TEMPLATE_V3/registers/NAME.tsv; reg_append_v1.py fills its first
                      column, the stamp, from the clock)
  literal PREFIX      a tab-separated header written as one string in the code (Python, printf or awk), from PREFIX to its closing quote
  md PREFIX           a markdown table header written as one string ('| a | b |')
  keys PATTERNS NAMES the row keys of a key-value file: each PATTERN must be in the code; the names are the keys
  fmt PREFIX NAMES    the fields of a printed line: one name per % field of the format string that starts with PREFIX
A register writer is also checked: every key the tool writes into the row (writer: dict keys or a seq) is a column of the register.
"""
import ast
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import settings_v1  # noqa: E402  (this package's own settings reader: it finds the Alarm folder)

NOT_DOC = 'NOT DOCUMENTED IN CODE'
BY_HAND = 'TO WRITE BY HAND'
DICT_HEAD = ['file', 'column', 'meaning', 'unit', 'known_at', 'empty_means', 'source_line']
CARD_SECTIONS = ['What it does', 'When to use it', 'Run it', 'What it gives', 'Limits and refusals', 'Where its data comes from']
GENERATED = ('file', 'file_sha16', 'reads', 'settings_keys', 'code_options', 'code_exits', 'usage_from_code', 'dictionary', 'archive')
INSTALL = '<INSTALL>'          # the Alarm release folder (the install); each card says where it is on the owner's Mac
ARCHIVE_LINE = 'archive/ holds past editions: read only, never run; to rerun one, use the old release install.'   # SCOUT 30 Oct 23:54 Berlin

K5 = 'Agentic/tree/ALARM_DESIGN/KIT_V5'
K6 = 'Agentic/tree/ALARM_DESIGN/KIT_V6'
RT = 'Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools'
RG = '08_Registry/tree/ALARM_DESIGN/REGISTRY'
REGISTERS = K5 + '/runs/TEMPLATE_V3/registers'
COUNT_JOB = K5 + '/jobs/JOB_COUNT_V6.job.sh.txt'
# the CLEAN template and its scratch tool are in archive/ since ALARM_V1_8 (CLEAN removed, the owner 31 Oct 2026 10:51 Berlin; UI review 0a123faee4315eaf)
GRADE8_JOB = K5 + '/jobs/JOB_GRADE_V8.job.sh.txt'      # queue_job_v6's GRADE and MONTH templates (SCOUT K12, 31 Oct; ALARM_V1_6)
MONTH8_JOB = K5 + '/jobs/JOB_MONTH_V8.job.sh.txt'
GRADE9_JOB = K5 + '/jobs/JOB_GRADE_V9.job.sh.txt'      # queue_job_v7's GRADE and MONTH templates (SCOUT K16, 31 Oct; ALARM_V1_7)
MONTH9_JOB = K5 + '/jobs/JOB_MONTH_V9.job.sh.txt'
GRADE10_JOB = K5 + '/jobs/JOB_GRADE_V10.job.sh.txt'    # queue_job_v8's GRADE and MONTH templates (SCOUT, 31 Oct; ALARM_V1_8: speed stage 1)
MONTH10_JOB = K5 + '/jobs/JOB_MONTH_V10.job.sh.txt'
GRADE11_JOB = K5 + '/jobs/JOB_GRADE_V11.job.sh.txt'    # queue_job_v9's GRADE and MONTH templates (SCOUT, 31 Oct; ALARM_V1_9: speed stage 2 D1)
MONTH11_JOB = K5 + '/jobs/JOB_MONTH_V11.job.sh.txt'
GRADE12_JOB = K5 + '/jobs/JOB_GRADE_V12.job.sh.txt'    # queue_job_v10's GRADE and MONTH templates (SCOUT, 31 Oct; ALARM_V1_10: D4 gm editions, D2 evt1)
MONTH12_JOB = K5 + '/jobs/JOB_MONTH_V12.job.sh.txt'
COUNT7_JOB = K5 + '/jobs/JOB_COUNT_V7.job.sh.txt'      # queue_job_v11's templates (SCOUT, 31 Oct; ALARM_V1_12: the fixes F1-F4)
GRADE13_JOB = K5 + '/jobs/JOB_GRADE_V13.job.sh.txt'
MONTH13_JOB = K5 + '/jobs/JOB_MONTH_V13.job.sh.txt'
RUN_README = K5 + '/runs/TEMPLATE_V3/README_RUN.md'      # a KIT_V5 run's layout: its registers and receipts
DT3 = '01_Detection/tree/team'                                   # the detection tree's team/ folder (SCOUT K13, 31 Oct)
WV3 = DT3 + '/LAB3/LAB1/tools/where_v2/where_v3.py'
MB2 = DT3 + '/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief_v2.py'

TOOLS = [
    {'tool': 'queue_job_v5', 'file': K5 + '/tools/queue_job_v5.py',
     'reads': [COUNT_JOB, RT + '/reg_append_v1.py', RUN_README],
     'outputs': [
         {'file': 'RUNS.tsv', 'columns': ['register', 'RUNS'], 'writer': ['dict_keys', K5 + '/tools/queue_job_v5.py', ['row', 'fields']]},
         {'file': 'STAGES.tsv', 'columns': ['literal', [COUNT_JOB], r'stage\trc\t']},
         {'file': 'COUNT_<V>.tsv', 'columns': ['literal', [COUNT_JOB], r'month\tfires\t']},
         {'file': 'FIRST20_<V>.tsv', 'columns': ['keys', COUNT_JOB, ['$1!="coin"', '$2!="t"'], ['coin', 't']]},
         {'file': 'DISK.tsv', 'columns': ['keys', COUNT_JOB, [r'"du_mb_W\t"', r"'free_mb_end\t"], ['du_mb_W', 'free_mb_end']]},
     ]},
    {'tool': 'queue_job_v6', 'file': K5 + '/tools/queue_job_v6.py',   # steps 6 GRADE and 10 MONTH (SCOUT K12, 31 Oct; ALARM_V1_6): GRADE and
     # MONTH on JOB_GRADE_V8 and JOB_MONTH_V8 (Outcomes with FEED_GATE and RESEARCH_STORE); queue_job_v5's GRADE and MONTH (V7) are the past edition
     'reads': [COUNT_JOB, GRADE8_JOB, MONTH8_JOB, RT + '/reg_append_v1.py', RUN_README],
     'outputs': [
         {'file': 'RUNS.tsv', 'columns': ['register', 'RUNS'], 'writer': ['dict_keys', K5 + '/tools/queue_job_v6.py', ['row', 'fields']]},
         {'file': 'STAGES.tsv', 'columns': ['literal', [COUNT_JOB], r'stage\trc\t']},
         {'file': 'COUNT_<V>.tsv', 'columns': ['literal', [COUNT_JOB], r'month\tfires\t']},
         {'file': 'FIRST20_<V>.tsv', 'columns': ['keys', COUNT_JOB, ['$1!="coin"', '$2!="t"'], ['coin', 't']]},
         {'file': 'DISK.tsv', 'columns': ['keys', COUNT_JOB, [r'"du_mb_W\t"', r"'free_mb_end\t"], ['du_mb_W', 'free_mb_end']]},
     ]},
    {'tool': 'queue_job_v7', 'file': K5 + '/tools/queue_job_v7.py',   # every job, steps 5, 6, 8 and 10 (SCOUT, 31 Oct; ALARM_V1_7): COUNT
     # (JOB_COUNT_V6), GRADE (JOB_GRADE_V9), ENTRY (JOB_ENTRY_V6), MONTH (JOB_MONTH_V9); KIND CLEAN refused (the owner 31 Oct 2026 10:51 Berlin)
     'reads': [COUNT_JOB, GRADE9_JOB, MONTH9_JOB, RT + '/reg_append_v1.py', RUN_README],
     'outputs': [
         {'file': 'RUNS.tsv', 'columns': ['register', 'RUNS'], 'writer': ['dict_keys', K5 + '/tools/queue_job_v7.py', ['row', 'fields']]},
         {'file': 'STAGES.tsv', 'columns': ['literal', [COUNT_JOB], r'stage\trc\t']},
         {'file': 'COUNT_<V>.tsv', 'columns': ['literal', [COUNT_JOB], r'month\tfires\t']},
         {'file': 'FIRST20_<V>.tsv', 'columns': ['keys', COUNT_JOB, ['$1!="coin"', '$2!="t"'], ['coin', 't']]},
         {'file': 'DISK.tsv', 'columns': ['keys', COUNT_JOB, [r'"du_mb_W\t"', r"'free_mb_end\t"], ['du_mb_W', 'free_mb_end']]},
     ]},
    {'tool': 'queue_job_v8', 'file': K5 + '/tools/queue_job_v8.py',   # every job, steps 5, 6, 8 and 10 (SCOUT, 31 Oct; ALARM_V1_8): COUNT
     # (JOB_COUNT_V6), GRADE (JOB_GRADE_V10), ENTRY (JOB_ENTRY_V6), MONTH (JOB_MONTH_V10): speed stage 1; KIND CLEAN refused as in v7
     'reads': [COUNT_JOB, GRADE10_JOB, MONTH10_JOB, RT + '/reg_append_v1.py', RUN_README],
     'outputs': [
         {'file': 'RUNS.tsv', 'columns': ['register', 'RUNS'], 'writer': ['dict_keys', K5 + '/tools/queue_job_v8.py', ['row', 'fields']]},
         {'file': 'STAGES.tsv', 'columns': ['literal', [COUNT_JOB], r'stage\trc\t']},
         {'file': 'COUNT_<V>.tsv', 'columns': ['literal', [COUNT_JOB], r'month\tfires\t']},
         {'file': 'FIRST20_<V>.tsv', 'columns': ['keys', COUNT_JOB, ['$1!="coin"', '$2!="t"'], ['coin', 't']]},
         {'file': 'DISK.tsv', 'columns': ['keys', COUNT_JOB, [r'"du_mb_W\t"', r"'free_mb_end\t"], ['du_mb_W', 'free_mb_end']]},
     ]},
    {'tool': 'queue_job_v9', 'file': K5 + '/tools/queue_job_v9.py',   # every job, steps 5, 6, 8 and 10 (SCOUT, 31 Oct; ALARM_V1_9): COUNT
     # (JOB_COUNT_V6), GRADE (JOB_GRADE_V11), ENTRY (JOB_ENTRY_V6), MONTH (JOB_MONTH_V11): speed stage 2 D1; KIND CLEAN refused as in v7
     'reads': [COUNT_JOB, GRADE11_JOB, MONTH11_JOB, RT + '/reg_append_v1.py', RUN_README],
     'outputs': [
         {'file': 'RUNS.tsv', 'columns': ['register', 'RUNS'], 'writer': ['dict_keys', K5 + '/tools/queue_job_v9.py', ['row', 'fields']]},
         {'file': 'STAGES.tsv', 'columns': ['literal', [COUNT_JOB], r'stage\trc\t']},
         {'file': 'COUNT_<V>.tsv', 'columns': ['literal', [COUNT_JOB], r'month\tfires\t']},
         {'file': 'FIRST20_<V>.tsv', 'columns': ['keys', COUNT_JOB, ['$1!="coin"', '$2!="t"'], ['coin', 't']]},
         {'file': 'DISK.tsv', 'columns': ['keys', COUNT_JOB, [r'"du_mb_W\t"', r"'free_mb_end\t"], ['du_mb_W', 'free_mb_end']]},
     ]},
    {'tool': 'queue_job_v10', 'file': K5 + '/tools/queue_job_v10.py',   # every job, steps 5, 6, 8 and 10 (SCOUT, 31 Oct; ALARM_V1_10): COUNT
     # (JOB_COUNT_V6), GRADE (JOB_GRADE_V12), ENTRY (JOB_ENTRY_V6), MONTH (JOB_MONTH_V12): D4 gm editions, D2 evt1; KIND CLEAN refused as in v7
     'reads': [COUNT_JOB, GRADE12_JOB, MONTH12_JOB, RT + '/reg_append_v1.py', RUN_README],
     'outputs': [
         {'file': 'RUNS.tsv', 'columns': ['register', 'RUNS'], 'writer': ['dict_keys', K5 + '/tools/queue_job_v10.py', ['row', 'fields']]},
         {'file': 'STAGES.tsv', 'columns': ['literal', [COUNT_JOB], r'stage\trc\t']},
         {'file': 'COUNT_<V>.tsv', 'columns': ['literal', [COUNT_JOB], r'month\tfires\t']},
         {'file': 'FIRST20_<V>.tsv', 'columns': ['keys', COUNT_JOB, ['$1!="coin"', '$2!="t"'], ['coin', 't']]},
         {'file': 'DISK.tsv', 'columns': ['keys', COUNT_JOB, [r'"du_mb_W\t"', r"'free_mb_end\t"], ['du_mb_W', 'free_mb_end']]},
     ]},
    {'tool': 'decide_v2', 'file': K5 + '/tools/decide_v2.py', 'reads': [RT + '/reg_append_v1.py', RT + '/read_stratentry_v1.py', RUN_README],
     'outputs': [
         {'file': 'DECISIONS.tsv', 'columns': ['register', 'DECISIONS'], 'writer': ['seq', K5 + '/tools/decide_v2.py', 'COLS']},
     ]},
    {'tool': 'decide_forward_v2', 'file': K5 + '/tools/decide_forward_v2.py', 'reads': [RT + '/reg_append_v1.py', RUN_README],
     'outputs': [
         {'file': 'DECISIONS.tsv', 'columns': ['register', 'DECISIONS'], 'writer': ['seq', K5 + '/tools/decide_forward_v2.py', 'COLS']},
     ]},
    {'tool': 'queue_job_v11', 'file': K5 + '/tools/queue_job_v11.py',   # every job, steps 5, 6, 8 and 10 (SCOUT, 31 Oct; ALARM_V1_12): COUNT
     # (JOB_COUNT_V7), GRADE (JOB_GRADE_V13), ENTRY (JOB_ENTRY_V7), MONTH (JOB_MONTH_V13): the fixes F1-F4; KIND CLEAN refused as in v7
     'reads': [COUNT7_JOB, GRADE13_JOB, MONTH13_JOB, RT + '/reg_append_v1.py', RUN_README],
     'outputs': [
         {'file': 'RUNS.tsv', 'columns': ['register', 'RUNS'], 'writer': ['dict_keys', K5 + '/tools/queue_job_v11.py', ['row', 'fields']]},
         {'file': 'STAGES.tsv', 'columns': ['literal', [COUNT7_JOB], r'stage\trc\t']},
         {'file': 'COUNT_<V>.tsv', 'columns': ['literal', [COUNT7_JOB], r'month\tfires\t']},
         {'file': 'FIRST20_<V>.tsv', 'columns': ['keys', COUNT7_JOB, ['$1!="coin"', '$2!="t"'], ['coin', 't']]},
         {'file': 'DISK.tsv', 'columns': ['keys', COUNT7_JOB, [r'"du_mb_W\t"', r"'free_mb_end\t"], ['du_mb_W', 'free_mb_end']]},
     ]},
    {'tool': 'decide_v3', 'file': K5 + '/tools/decide_v3.py', 'reads': [RT + '/reg_append_v1.py', RT + '/read_stratentry_v1.py', RUN_README],
     'outputs': [
         {'file': 'DECISIONS.tsv', 'columns': ['register', 'DECISIONS'], 'writer': ['seq', K5 + '/tools/decide_v3.py', 'COLS']},
     ]},
    {'tool': 'decide_forward_v3', 'file': K5 + '/tools/decide_forward_v3.py', 'reads': [RT + '/reg_append_v1.py', RUN_README],
     'outputs': [
         {'file': 'DECISIONS.tsv', 'columns': ['register', 'DECISIONS'], 'writer': ['seq', K5 + '/tools/decide_forward_v3.py', 'COLS']},
     ]},
    {'tool': 'audit_run_v3', 'file': K5 + '/tools/audit_run_v3.py', 'reads': [K5 + '/tools/decide_v2.py', K5 + '/tools/decide_forward_v2.py', RUN_README],
     'outputs': [
         {'file': 'AUDIT_<stamp>.txt (check lines)', 'columns': ['fmt', K5 + '/tools/audit_run_v3.py', '%-4s %-11s %s%s',
                                                                ['check', 'name', 'status', 'count']]},
         {'file': 'AUDIT_<stamp>.txt (SCORE line)', 'columns': ['fmt', K5 + '/tools/audit_run_v3.py', 'SCORE %d PASS', ['pass', 'warn', 'fail']]},
     ]},
    {'tool': 'board_line_v2', 'file': K5 + '/tools/board_line_v2.py', 'reads': [],
     'outputs': [
         {'file': '<BOARD>/<SEAT>.txt (the line)', 'columns': ['fmt', K5 + '/tools/board_line_v2.py', '%s %s %s %s',
                                                              ['stamp', 'seat', 'kind', 'text']]},
     ]},
    {'tool': 'idea_time_v2', 'file': K6 + '/tools/idea_time_v2.py', 'reads': [],
     'outputs': [
         {'file': 'printed: run line', 'columns': ['fmt', K6 + '/tools/idea_time_v2.py', '== %s', ['run', 'launch', 'START', 'DONE']]},
         {'file': 'printed: idea table', 'columns': ['literal', [K6 + '/tools/idea_time_v2.py'], r'idea\tclaimed\t']},
         {'file': 'printed: seat line', 'columns': ['fmt', K6 + '/tools/idea_time_v2.py', 'seat %s: launch',
                                                    ['seat', 'launch_to_first_claim', 'no_job_running', 'one_job_running',
                                                     'two_or_more_running', 'minutes_observed', 'first_own_pass']]},
     ]},
    {'tool': 'novelty_v2', 'file': RG + '/tools/novelty_v2.py', 'reads': [],
     'outputs': [
         {'file': 'printed: NOVELTY line', 'columns': ['fmt', RG + '/tools/novelty_v2.py', 'NOVELTY %s',
                                                       ['fire_list', 'fire_list_sha16', 'lean', 'fires', 'waves', 'registry_alarms',
                                                        'registry', 'registry_sha16']]},
         {'file': 'printed: nearest lines', 'columns': ['fmt', RG + '/tools/novelty_v2.py', 'nearest %d:',
                                                        ['rank', 'alarm', 'kind', 'state', 'lean', 'same_fires', 'same_side',
                                                         'other_side', 'waves_near', 'baseline']]},
         {'file': 'printed: VERDICT line', 'columns': ['fmt', RG + '/tools/novelty_v2.py', 'VERDICT %s', ['verdict']]},
     ]},
    {'tool': 'registry_build_v2', 'file': RG + '/tools/registry_build_v2.py', 'reads': [RG + '/tools/novelty_v2.py'],
     'outputs': [
         {'file': 'ALARM_REGISTRY_V1.tsv', 'columns': ['seq', RG + '/tools/registry_build_v2.py', 'COLS']},
     ]},
    {'tool': 'scoreboard_v2', 'file': RG + '/tools/scoreboard_v2.py', 'reads': [RG + '/tools/novelty_v2.py'],
     'outputs': [
         {'file': 'SCOREBOARD.md (family table)', 'columns': ['md', RG + '/tools/scoreboard_v2.py', '| family |']},
     ]},
    {'tool': 'index_v2', 'file': RG + '/index_v2.py', 'reads': [RG + '/tools/scoreboard_v2.py', RG + '/tools/novelty_v2.py'],
     'outputs': [
         {'file': 'ALARM_REGISTRY_V1_INDEX.md (new alarms tables)', 'columns': ['md', RG + '/index_v2.py', '| ID | round |']},
         {'file': 'ALARM_REGISTRY_V1_INDEX.md (every alarm table)', 'columns': ['md', RG + '/index_v2.py', '| ID | kind |']},
     ]},
    {'tool': 'inputs_read_v1', 'file': RG + '/tools/inputs_read_v1.py',
     'reads': [RG + '/tools/novelty_v2.py', RG + '/tools/scoreboard_v2.py',
               '01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief_v2.py', '01_Detection/tree/team/LAB3/METRICS_V1.tsv',
               '01_Detection/tree/team/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv',
               '01_Detection/tree/team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv',
               '01_Detection/tree/team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv'],
     'outputs': [
         {'file': 'INPUTS_READ_V1.tsv (--out)', 'columns': ['seq', RG + '/tools/inputs_read_v1.py', 'COLS']},
         {'file': 'printed: WROTE line', 'columns': ['fmt', RG + '/tools/inputs_read_v1.py', 'WROTE %s %s codes',
                                                    ['out', 'out_sha16', 'codes', 'read', 'page', 'page_sha16']]},
     ]},
    {'tool': 'machine_paths_v2', 'file': '_tools/machine_paths_v2.py', 'reads': [],
     'outputs': [
         {'file': 'OUT (--tsv)', 'columns': ['literal', ['_tools/machine_paths_v2.py'], r'file\tline\tpath\tkind']},
         {'file': 'printed: row lines', 'columns': ['fmt', '_tools/machine_paths_v2.py', r'%s\t%s:%d\t%s', ['kind', 'file', 'line', 'path']]},
         {'file': 'printed: KNOWN lines', 'columns': ['fmt', '_tools/machine_paths_v2.py', r'KNOWN\t%s:%d', ['file', 'line', 'path', 'reason']]},
         {'file': 'printed: STALE lines', 'columns': ['fmt', '_tools/machine_paths_v2.py', r'STALE\t%s:%d', ['file', 'line', 'path', 'known_file']]},
         {'file': 'printed: summary line', 'columns': ['fmt', '_tools/machine_paths_v2.py', '%s: %d files, CODE %d',
                                                       ['part', 'files', 'CODE', 'CALLS_ARCHIVE', 'KNOWN', 'MARKED', 'NAMES_ARCHIVE', 'ARCHIVE',
                                                        'TEXT', 'verdict']]},
     ]},
    {'tool': 'machine_paths_v3', 'file': '_tools/machine_paths_v3.py', 'reads': [],
     'outputs': [
         {'file': 'OUT (--tsv)', 'columns': ['literal', ['_tools/machine_paths_v3.py'], r'file\tline\tpath\tkind']},
         {'file': 'printed: row lines', 'columns': ['fmt', '_tools/machine_paths_v3.py', r'%s\t%s:%d\t%s', ['kind', 'file', 'line', 'path']]},
         {'file': 'printed: KNOWN lines', 'columns': ['fmt', '_tools/machine_paths_v3.py', r'KNOWN\t%s:%d', ['file', 'line', 'path', 'reason']]},
         {'file': 'printed: STALE lines', 'columns': ['fmt', '_tools/machine_paths_v3.py', r'STALE\t%s:%d', ['file', 'line', 'path', 'known_file']]},
         {'file': 'printed: summary line', 'columns': ['fmt', '_tools/machine_paths_v3.py', '%s: %d files, CODE %d',
                                                       ['part', 'files', 'CODE', 'CALLS_ARCHIVE', 'KNOWN', 'MARKED', 'NAMES_ARCHIVE', 'ARCHIVE',
                                                        'TEXT', 'verdict']]},
     ]},
    {'tool': 'run_isolated_v2', 'file': '_tools/run_isolated_v2.py', 'reads': ['_tools/settings_v1.py'],
     'outputs': [
         {'file': 'printed: OK line', 'columns': ['fmt', '_tools/run_isolated_v2.py', 'RUN ISOLATION OK:',
                                                 ['alarm', 'data_files', 'forbidden', 'script_exit']]},
         {'file': 'printed: FAILED line', 'columns': ['fmt', '_tools/run_isolated_v2.py', 'RUN ISOLATION FAILED:',
                                                     ['outside_modules', 'forbidden', 'bad_files', 'archive_files']]},
     ]},
    {'tool': 'run_isolated_v1', 'file': '_tools/run_isolated_v1.py', 'reads': ['_tools/run_all_tests_v1.py'],
     'outputs': [
         {'file': 'printed: OK line', 'columns': ['fmt', '_tools/run_isolated_v1.py', 'ISOLATION OK:',
                                                 ['modules', 'alarm', 'forbidden', 'script_exit']]},
         {'file': 'printed: FAILED line', 'columns': ['fmt', '_tools/run_isolated_v1.py', 'ISOLATION FAILED:',
                                                     ['outside_modules', 'forbidden', 'opened_files']]},
     ]},
    {'tool': 'where_v3', 'file': WV3,                     # step 2 METRICS (SCOUT K13, 31 Oct; R7 F32): find a code by words
     'reads': [DT3 + '/LAB3/METRICS_V1.tsv', DT3 + '/LAB3/METRICS_HL_CANDIDATE_V2.tsv', DT3 + '/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv',
               DT3 + '/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv', DT3 + '/RESEARCH/tools/alarm_stamp/STAMP_CATALOG_V1.tsv',
               DT3 + '/FEED/CATALOG_V1.tsv', DT3 + '/LIVELAYER/CATALOG_V1.tsv', DT3 + '/LAB3/METRICS_V2.tsv'],
     'outputs': [
         {'file': 'printed: one hit (three lines)', 'columns': ['fmt', WV3, '[%s] %s  | owner',
                                                               ['kind', 'code', 'owner', 'table', 'card', 'what', 'read_as']]},
         {'file': 'printed: NOT FOUND line', 'columns': ['fmt', WV3, 'NOT FOUND: "%s"', ['query', 'tables']]},
     ]},
    {'tool': 'metric_brief_v2', 'file': MB2,              # step 2 METRICS (SCOUT K13, 31 Oct; R7 F32): read a code before it goes in a rule
     'reads': [DT3 + '/LAB3/METRICS_V1.tsv', DT3 + '/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv',
               DT3 + '/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv', DT3 + '/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv'],
     'outputs': [
         {'file': 'printed: a brief (a header line, then LABEL: value lines)', 'columns': ['keys', MB2,
             ["out = [f'== {code}  {", "f = flag(trap.get('status'))", "f'   STATUS: {trap", "('meaning', 'MEANS')", "('unit_text', 'UNIT')",
              "('scope_text', 'SCOPE')", "('step', 'STEP')", "('window', 'WINDOW')", "('use_may', 'MAY USE')", "('first', 'FIRST DAY')",
              "('last', 'LAST DAY')", "('card', 'CARD')", "('empty_means', 'EMPTY MEANS')", "('never_read_as', 'NEVER READ AS')",
              "('read_it_as', 'READ IT AS')", ": NOT FOUND in METRICS_V1, METRIC_TRAPS_V3"],
             ['card_name', 'flag', 'STATUS', 'MEANS', 'UNIT', 'SCOPE', 'STEP', 'WINDOW', 'MAY USE', 'FIRST DAY', 'LAST DAY', 'CARD',
              'EMPTY MEANS', 'NEVER READ AS', 'READ IT AS', 'NOT FOUND']]},
     ]},
]


class Refused(Exception):
    pass


class Stale(Exception):
    pass


# ---------------------------------------------------------------- reading the code
def alarm_root():
    try:
        return settings_v1.alarm_root(__file__)
    except settings_v1.Refused as e:
        raise Refused(str(e))


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def text(alarm, rel):
    p = os.path.join(alarm, rel)
    if not os.path.isfile(p):
        raise Refused('NO FILE %s in the Alarm folder %s' % (rel, alarm))
    with open(p, encoding='utf-8') as f:
        return f.read()


def line_of(src, pos):
    return src.count('\n', 0, pos) + 1


def find_once(src, needle, rel):
    i = src.find(needle)
    if i < 0:
        raise Stale('%s: %r is not in the code' % (rel, needle))
    return i


def literal_at(src, i):
    """the string literal's content from position i to its closing quote (the quote not escaped)"""
    j = i
    while j < len(src) and not (src[j] in '\'"' and src[j - 1] != '\\'):
        j += 1
    return src[i:j]


def ex_seq(alarm, rel, name):
    tree = ast.parse(text(alarm, rel))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)) and all(isinstance(e, ast.Constant) and isinstance(e.value, str)
                                                                      for e in node.value.elts):
                return [(e.value, rel, e.lineno) for e in node.value.elts]
    raise Stale('%s: no list or tuple of strings named %s' % (rel, name))


def ex_register(alarm, name):
    rel = '%s/%s.tsv' % (REGISTERS, name)
    head = text(alarm, rel).split('\n', 1)[0]
    return [(c, rel, 1) for c in head.split('\t')]


def py_strings(src):
    """[(value, line)] of every string constant of a Python source that is no docstring (joined literals are one constant)"""
    tree = ast.parse(src)
    doc = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            b = node.body[0]
            if isinstance(b, ast.Expr) and isinstance(getattr(b, 'value', None), ast.Constant):
                doc.add(id(b.value))
    return [(n.value, n.lineno) for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc]


def decoded(prefix):
    return prefix.encode('utf-8').decode('unicode_escape')


def one_string(alarm, rel, prefix):
    """(value, line) of the one string of the code that starts with prefix: from the syntax tree for Python (prefix with \t written
    as backslash t), else the text from prefix to its closing quote"""
    src = text(alarm, rel)
    if rel.endswith('.py'):
        hit = sorted((n, v) for v, n in py_strings(src) if v.startswith(decoded(prefix)))
        if len(hit) != 1:
            raise Stale('%s: %d strings start with %r (want 1)' % (rel, len(hit), prefix))
        return hit[0][1], hit[0][0]
    i = find_once(src, prefix, rel)
    return decoded(literal_at(src, i)), line_of(src, i)


def ex_literal(alarm, rels, prefix):
    out = None
    for rel in rels:
        v, n = one_string(alarm, rel, prefix)
        cols = v[:-1].split('\t') if v.endswith('\n') else v.split('\t')
        got = [(c, rel, n) for c in cols]
        if out is None:
            out = got
        elif [c for c, _, _ in got] != [c for c, _, _ in out]:
            raise Stale('%s: the header %s differs from %s' % (rel, [c for c, _, _ in got], out[0][1]))
    return out


def ex_md(alarm, rel, prefix):
    v, n = one_string(alarm, rel, prefix)
    return [(c.strip(), rel, n) for c in v.split('|') if c.strip()]


FIELD = re.compile(r'%[-+ 0#]*[0-9]*(?:\.[0-9]+)?[sdifgeExr]')


def ex_fmt(alarm, rel, prefix, names):
    v, n = one_string(alarm, rel, prefix)
    fields = FIELD.findall(v.replace('%%', ''))
    if len(fields) != len(names):
        raise Stale('%s: the line %r has %d fields, the docs name %d' % (rel, prefix, len(fields), len(names)))
    return [(x, rel, n) for x in names]


def ex_keys(alarm, rel, patterns, names):
    src = text(alarm, rel)
    return [(n, rel, line_of(src, find_once(src, p, rel))) for p, n in zip(patterns, names)]


def ex_dict_keys(alarm, rel, names):
    """every string key of a dict literal assigned to one of names, or passed to <name>.update(...)"""
    keys = []
    for node in ast.walk(ast.parse(text(alarm, rel))):
        d = None
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            d = node.value
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'update'
              and isinstance(node.func.value, ast.Name) and node.func.value.id in names and node.args):
            d = node.args[0]
        if isinstance(d, ast.Dict):
            keys += [k.value for k in d.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)]
    return sorted(set(keys))


def columns(alarm, spec):
    """[(column, file, line)] of one output, read from the code"""
    kind, a = spec[0], spec[1:]
    if kind == 'seq':
        return ex_seq(alarm, a[0], a[1])
    if kind == 'register':
        return ex_register(alarm, a[0])
    if kind == 'literal':
        return ex_literal(alarm, a[0], a[1])
    if kind == 'md':
        return ex_md(alarm, a[0], a[1])
    if kind == 'fmt':
        return ex_fmt(alarm, a[0], a[1], a[2])
    if kind == 'keys':
        return ex_keys(alarm, a[0], a[1], a[2])
    raise Refused('UNKNOWN COLUMN READER %r' % kind)


def writer_keys(alarm, spec):
    if spec[0] == 'seq':
        return sorted({c for c, _, _ in ex_seq(alarm, spec[1], spec[2])})
    if spec[0] == 'dict_keys':
        return ex_dict_keys(alarm, spec[1], spec[2])
    raise Refused('UNKNOWN WRITER READER %r' % spec[0])


OPTION = re.compile(r'^--[a-z][a-z0-9-]*$')


def code_options(src):
    """the options the tool's code reads: string constants such as '--write' (docstrings never match: they hold spaces)"""
    out = {n.value for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Constant) and isinstance(n.value, str) and OPTION.match(n.value)}
    if 'take_settings(' in src:                  # the registry tools take --settings through novelty_v2.take_settings
        out.add('--settings')
    return sorted(out)


def code_exits(src):
    """the exit codes the code names: sys.exit(N), return N in main(), SystemExit(N), SystemExit('text') = 1; 0 = success"""
    out = {0}
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, 'attr', None) == 'exit' and node.args:
            if isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, int):
                out.add(node.args[0].value)
        if isinstance(node, ast.Raise) and node.exc is not None and isinstance(node.exc, ast.Call) \
                and getattr(node.exc.func, 'id', None) == 'SystemExit':
            arg = node.exc.args[0] if node.exc.args else None
            out.add(arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, int) else 1)
        if isinstance(node, ast.FunctionDef) and node.name == 'main':
            for r in ast.walk(node):
                vals = [r.value.body, r.value.orelse] if isinstance(r, ast.Return) and isinstance(r.value, ast.IfExp) else \
                    [r.value] if isinstance(r, ast.Return) else []
                out.update(v.value for v in vals if isinstance(v, ast.Constant) and isinstance(v.value, int) and not isinstance(v.value, bool))
    return sorted(out)


def settings_keys(src, read_srcs, keys):
    quoted = [k for k in keys if ("'%s'" % k) in src or ('"%s"' % k) in src]
    placed = [k for k in keys if any('@@%s@@' % k in s for s in read_srcs)]
    return [k for k in keys if k in quoted or k in placed]


def usage_from_code(src, name):
    """the command synopsis in the module docstring: the line that starts 'python3 -B ' and names the tool's file, and its indented
    continuation lines"""
    doc = ast.get_docstring(ast.parse(src), clean=False) or ''
    lines = doc.split('\n')
    for i, l in enumerate(lines):
        if l.strip().startswith('python3 -B ') and name in l:
            out = [l.strip()]
            for m in lines[i + 1:]:
                s = m.strip()
                if m.startswith('      ') and s[:1] in ('[', '-', '"', '<', '(') and not s.startswith('--settings '):
                    out.append(s)
                else:
                    break
            return ' '.join(out)
    raise Stale('no usage line (python3 -B ... %s) in the docstring' % name)


def generated(alarm, t):
    """the parts of a tool's TOOL.json read from its code, and its dictionary rows' columns and source lines"""
    src = text(alarm, t['file'])
    reads = [text(alarm, r) for r in t['reads']]
    outs = []
    for o in t['outputs']:
        cols = columns(alarm, o['columns'])
        names = [c for c, _, _ in cols]
        if len(set(names)) != len(names):
            raise Stale('%s %s: a column named twice %s' % (t['tool'], o['file'], names))
        if 'writer' in o:
            wk = writer_keys(alarm, o['writer'])
            miss = [k for k in wk if k not in names]
            unwritten = [c for c in names[1:] if c not in wk] if o['columns'][0] == 'register' else []
            if miss or unwritten:
                raise Stale('%s %s: the code writes %s that the register lacks, and leaves %s of it unwritten' % (
                    t['tool'], o['file'], miss, unwritten))
        outs.append({'file': o['file'], 'columns': cols})
    gen = {'file': t['file'], 'file_sha16': sha16(os.path.join(alarm, t['file'])),
           'reads': [{'path': r, 'sha16': sha16(os.path.join(alarm, r))} for r in t['reads']],
           'settings_keys': settings_keys(src, reads, settings_v1.keys()), 'code_options': code_options(src),
           'code_exits': code_exits(src), 'usage_from_code': usage_from_code(src, os.path.basename(t['file'])),
           'dictionary': 'dictionaries/%s_COLUMNS.tsv' % t['tool'], 'archive': ARCHIVE_LINE}
    return gen, outs


# ---------------------------------------------------------------- the docs
def read_dict(path):
    """{(file, column): row} of a dictionary, in file order"""
    rows = {}
    if not os.path.isfile(path):
        return rows
    with open(path, encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f if l.strip() and not l.startswith('#')]
    if not lines or lines[0].split('\t') != DICT_HEAD:
        raise Refused('DICTIONARY HEADER %s: want %s' % (path, '\t'.join(DICT_HEAD)))
    for n, l in enumerate(lines[1:], 2):
        c = l.split('\t')
        if len(c) != len(DICT_HEAD):
            raise Refused('DICTIONARY ROW %s row %d has %d cells, want %d' % (path, n, len(c), len(DICT_HEAD)))
        rows[(c[0], c[1])] = dict(zip(DICT_HEAD, c))
    return rows


def dict_text(tool, t, outs, old):
    """the dictionary: the generated column list and source lines, the hand-written cells kept"""
    lines = ['# %s_COLUMNS.tsv: every output column of %s (%s). Generated by _tools/agent_docs_v1.py: file, column and source_line come from '
             'the code; meaning, unit, known_at and empty_means are written by hand from the code (a quote in backticks is a quote of the '
             'code) and kept when the generator runs again. TEST, NOT REVIEWED.' % (tool, tool, t['file']), '# ' + ARCHIVE_LINE, '\t'.join(DICT_HEAD)]
    for o in outs:
        for c, rel, n in o['columns']:
            r = old.get((o['file'], c)) or {k: NOT_DOC for k in ('meaning', 'unit', 'known_at', 'empty_means')}
            lines.append('\t'.join([o['file'], c, r['meaning'], r['unit'], r['known_at'], r['empty_means'], '%s:%d' % (rel, n)]))
    return '\n'.join(lines) + '\n'


def skeleton_json(t, gen, outs):
    return {'tool': t['tool'], 'step': BY_HAND, 'question': BY_HAND,
            'commands': [{'name': BY_HAND, 'args': [{'name': o, 'required': False, 'meaning': BY_HAND, 'example': BY_HAND}
                                                      for o in gen['code_options']],
                          'example': BY_HAND, 'writes': BY_HAND, 'refuses': [{'exit': e, 'when': BY_HAND} for e in gen['code_exits'] if e],
                          'dry_runs': []}],
            'rules': [BY_HAND], 'refusal_probes': [{'args': [], 'exit': max(gen['code_exits']), 'prints': BY_HAND}],
            'outputs': [{'file': o['file'], 'where': BY_HAND} for o in outs]}


def merge_json(t, old, gen, outs):
    """the TOOL.json: hand-written keys kept; the generated keys and every output's column list refreshed; an option the code reads and
    no command names is added to the first command as NOT DOCUMENTED IN CODE"""
    new = dict(old) if old else skeleton_json(t, gen, outs)
    new.update(gen)
    known = {o.get('file'): o for o in (old or {}).get('outputs', [])}
    new['outputs'] = []
    for o in outs:
        k = dict(known.get(o['file']) or {'file': o['file'], 'where': BY_HAND})
        k['columns'] = [c for c, _, _ in o['columns']]
        new['outputs'].append(k)
    named = {a.get('name') for c in new.get('commands', []) for a in c.get('args', [])}
    for opt in gen['code_options']:
        if opt not in named and new.get('commands'):
            new['commands'][0].setdefault('args', []).append({'name': opt, 'required': False, 'meaning': NOT_DOC, 'example': BY_HAND})
    order = ['tool', 'file', 'file_sha16', 'archive', 'step', 'question', 'usage_from_code', 'settings_keys', 'code_options', 'code_exits', 'commands',
             'refusal_probes', 'rules', 'outputs', 'dictionary', 'reads']
    return dict([(k, new[k]) for k in order if k in new] + [(k, v) for k, v in new.items() if k not in order])


def card_skeleton(t, gen, outs):
    """a card to write by hand: the six sections, the facts the code gives (its command, outputs, exits, settings keys), the rest marked"""
    run = 'python3 -B %s/%s %s' % (INSTALL, t['file'], gen['usage_from_code'].split(' ', 3)[3] if gen['usage_from_code'].count(' ') >= 3 else '')
    body = {'What it does': ['- %s' % BY_HAND],
            'When to use it': ['- %s' % BY_HAND],
            'Run it': ['```', run, '```', '- %s' % BY_HAND],
            'What it gives': ['- %s (columns: [dictionary](../%s))' % (o['file'], gen['dictionary']) for o in outs] + ['- %s' % BY_HAND],
            'Limits and refusals': ['- exit %d: %s' % (e, BY_HAND) for e in gen['code_exits']],
            'Where its data comes from': ['- %s: %s' % (k, BY_HAND) for k in gen['settings_keys']] or ['- %s' % BY_HAND]}
    L = ['# %s: tool card' % t['tool'], '', '%s. The code: [%s](../%s). Exact commands: [TOOL.json](%s.TOOL.json). Every output column: '
         '[dictionary](../%s).' % (BY_HAND, os.path.basename(t['file']), t['file'], t['tool'], gen['dictionary']), ARCHIVE_LINE, '']
    for k in CARD_SECTIONS:
        L += ['## %s' % k] + body[k] + ['']
    return '\n'.join(L)


def plan_tool(alarm, docs, t):
    """[(path, new text, why)] for one tool: the files that differ from what the code gives (cards only when missing)"""
    gen, outs = generated(alarm, t)
    jp = os.path.join(docs, 'cards', '%s.TOOL.json' % t['tool'])
    dp = os.path.join(docs, gen['dictionary'])
    cp = os.path.join(docs, 'cards', '%s.md' % t['tool'])
    old = None
    if os.path.isfile(jp):
        with open(jp, encoding='utf-8') as f:
            try:
                old = json.load(f)
            except ValueError as e:
                raise Refused('TOOL.json NOT JSON %s: %s' % (jp, e))
    nj = json.dumps(merge_json(t, old, gen, outs), indent=1, ensure_ascii=False) + '\n'
    oldd = read_dict(dp)
    nd = dict_text(t['tool'], t, outs, oldd)
    todo = []
    for p, new, what in ((jp, nj, 'TOOL.json'), (dp, nd, 'dictionary')):
        cur = None
        if os.path.isfile(p):
            with open(p, encoding='utf-8') as f:
                cur = f.read()
        if cur != new:
            todo.append((p, new, why(cur, new, what, old, gen, oldd, outs)))
    if not os.path.isfile(cp):
        todo.append((cp, card_skeleton(t, gen, outs), 'card missing (a skeleton: write it by hand)'))
    return todo


def why(cur, new, what, old, gen, oldd, outs):
    if cur is None:
        return '%s missing' % what
    if what == 'TOOL.json':
        d = [k for k in GENERATED if (old or {}).get(k) != gen.get(k)]
        oc = {o.get('file'): o.get('columns') for o in (old or {}).get('outputs', [])}
        d += ['columns of %s' % o['file'] for o in outs if oc.get(o['file']) != [c for c, _, _ in o['columns']]]
        return 'TOOL.json differs: %s' % (', '.join(d) or 'layout or a new option')
    have = set(oldd)
    want = {(o['file'], c) for o in outs for c, _, _ in o['columns']}
    parts = []
    if want - have:
        parts.append('new columns %s' % sorted('%s %s' % k for k in want - have))
    if have - want:
        parts.append('DROPPED (no longer in the code) %s' % sorted('%s %s' % k for k in have - want))
    return 'dictionary differs: %s' % ('; '.join(parts) or 'source lines, order or header')


def twin(p):
    """the twin of an existing file before it is rewritten (<file>.pre_agent_docs_<UTC stamp>, opened new; _2, _3 in one second)"""
    if not os.path.exists(p):
        return None
    base = '%s.pre_agent_docs_%s' % (p, datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    tw, k = base, 1
    while True:
        try:
            with open(p, 'rb') as f, open(tw, 'xb') as g:
                g.write(f.read())
            return tw
        except FileExistsError:
            k += 1
            tw = '%s_%d' % (base, k)


def main(argv):
    a = list(argv)
    mode = [m for m in ('--check', '--write') if m in a]
    a = [x for x in a if x not in ('--check', '--write')]
    docs, only = None, []
    while a:
        k = a.pop(0)
        if k in ('--docs', '--tool') and a:
            v = a.pop(0)
            if k == '--docs':
                docs = v
            else:
                only.append(v)
        else:
            raise Refused('USAGE agent_docs_v1.py (--check | --write) [--docs <folder>] [--tool <tool>]... (unknown %r)' % k)
    if len(mode) != 1:
        raise Refused('USAGE agent_docs_v1.py (--check | --write) [--docs <folder>] [--tool <tool>]...')
    alarm = alarm_root()
    docs = os.path.abspath(docs or alarm)
    names = [t['tool'] for t in TOOLS]
    bad = [x for x in only if x not in names]
    if bad:
        raise Refused('UNKNOWN TOOL %s (tools: %s)' % (bad, ', '.join(names)))
    tools = [t for t in TOOLS if not only or t['tool'] in only]
    stale = 0
    for t in tools:
        try:
            todo = plan_tool(alarm, docs, t)
        except Stale as e:
            print('STALE %s: the code no longer matches its reader: %s' % (t['tool'], e))
            stale += 1
            continue
        for p, new, w in todo:
            if mode[0] == '--check':
                print('STALE %s: %s (%s)' % (t['tool'], w, os.path.relpath(p, docs)))
                stale += 1
            else:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                tw = twin(p)
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(new)
                print('WROTE %s: %s (%s)%s' % (t['tool'], w, os.path.relpath(p, docs), ' twin %s' % os.path.basename(tw) if tw else ''))
    print('agent docs %s: %d tools, %d %s (code from %s, docs in %s)' % (
        mode[0][2:], len(tools), stale, 'stale' if mode[0] == '--check' else 'unreadable', alarm, docs))
    return 3 if stale else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
