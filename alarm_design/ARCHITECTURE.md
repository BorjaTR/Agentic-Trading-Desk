# ARCHITECTURE: alarm_design ALARM_BUILD_V26 (SCOUT, 2026-11-07; status: RELEASED)
From Templates/ARCHITECTURE_TEMPLATE_V1.md, short form.
## 1. Identity
alarm_design, edition ALARM_BUILD_V26, area Alarm, owner SCOUT. Edition before: ALARM_BUILD_V25 (SCO-A171, current from job 20270490). Made by team/SCOUT/sco_a183/pack/make_v26.py (with fix_pages_v26.py) from the library V25 files and team/DOCS/ONE_PROCESS_V1.
## 2. Purpose and scope
The members of MANIFEST_V26.tsv (START, PROCESS, QUESTIONS, GATES, PROMPT, CHANGES, route_check_v26, rules_check_v26, TOOLS, CURATED_V7, DOC_CONFLICTS_V7, and the pages LEARNING_LOOP.md and FLOWCHART.html) and PIPE_SETTINGS_V3_TEMPLATE.json (not a manifest member). Steps unchanged from V25.
## 6. Design
make_v26.py resolves each TOOLS_V25 row (RELEASE/<tool>/current under the edition current with V26, INSTALL/ under ALARM_V1_22_1) and moves its sha16 and edition word where the file differs; adds row T03-05; lands the SCO-A177 texts with dates written YYYYMMDD (rule CLOSED_MONTHS) and the run-part slots written @SLOT@ (launch_v1 refuses an unfilled {SLOT}). Moved: T01-03 sha16 09d4586046f18aca edition ALARM_V1_21_16 -> T01-03 sha16 263c856cb9aa871f edition ALARM_V1_22_1; T02-06 sha16 3d044667d3ae405b edition MAC_DESK_V49 -> T02-06 sha16 bc65d94396ef376f edition MAC_DESK_V49_3; T02-11 sha16 3d044667d3ae405b edition MAC_DESK_V49 -> T02-11 sha16 bc65d94396ef376f edition MAC_DESK_V49_3; T02-12 sha16 3d044667d3ae405b edition MAC_DESK_V49 -> T02-12 sha16 bc65d94396ef376f edition MAC_DESK_V49_3; T02-13 sha16 c44cc5beff982bef edition ALARM_V1_21_16 -> T02-13 sha16 920f14e472851b4d edition ALARM_V1_22_1; T02-18 sha16 c44cc5beff982bef edition ALARM_V1_21_16 -> T02-18 sha16 920f14e472851b4d edition ALARM_V1_22_1; T02-20 sha16 c44cc5beff982bef edition ALARM_V1_21_16 -> T02-20 sha16 920f14e472851b4d edition ALARM_V1_22_1; T02-22 sha16 c44cc5beff982bef edition ALARM_V1_21_16 -> T02-22 sha16 920f14e472851b4d edition ALARM_V1_22_1; T02-24 sha16 8120216aae88986a edition ALARM_UNDERSTAND_V1 -> T02-24 sha16 8d937d6c2a69e3e9 edition ALARM_UNDERSTAND_V1_3; T02-25 sha16 d4a6f56135d841b5 edition ALARM_UNDERSTAND_V1_1 -> T02-25 sha16 85298c981705ad22 edition ALARM_UNDERSTAND_V1_3; T02-31 sha16 f856dc3c6667d6ce edition ALARM_UNDERSTAND_V1_1 -> T02-31 sha16 92d11903dd4f5c0d edition ALARM_UNDERSTAND_V1_3.
## 9. Placement
<RELEASE_ROOT>/Alarm/alarm_design/ALARM_BUILD_V26, read only. Pairs with Alarm/alarm_pipeline current = ALARM_PIPELINE_V1_4_1 and Alarm/alarm current = ALARM_V1_22_1.
## 12. Tests
pack_check_v4_1 (PACK_TEMPLATE_V3) from /tmp; route_check_v26; rules_check_v26 --root --release; start_paths_check.py on START_V26 HOW TO LAUNCH (every named path exists).
## 15. Safety
No git, no deletion. Nothing runs from this folder by itself.
