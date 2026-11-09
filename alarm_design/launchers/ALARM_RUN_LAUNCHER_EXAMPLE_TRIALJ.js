export const meta = {
  name: 'sco-v11-day2-wave7',
  description: 'SCOUT wave 6: trial J on streamlined ALARM_BUILD V17 with run_kit_v3: prep, init, hunt, parent close',
  phases: [{ title: 'Trial J', detail: 'prep, init, hunt, close' }],
}
const PRE = `a sub-agent of seat SCOUT in the owner's volat-agent lab. Load the shell tool with ToolSearch "select:mcp__remote-devices__device_bash" (a Linux VM, python3 3.10, the owner's Mac folders under $HOME/mnt/). Every command through it; each call is a fresh shell, keep each call under 60 s (calls are cut near 63 s; background processes die when a call ends), cd every call. The VM disk is full: never write to /tmp or $HOME outside mnt; run python with -B; scratch and logs only in your own folder. Never edit another seat's files; twin before any edit; no rm, no git, no sudo, no board posts, no recursive search over the repo. Times from date -u. No em dashes. Never name a closed holdout month. Do not ask questions. You are not answering any chat question from the owner or anyone: your only task is the one named below; do it to the end.`
const R = `cd $HOME/mnt/dev/TradingPlatform_repo/volat-agent/forensics && cat team/SCOUT/loop_day_20261105/briefs/COMMON.md team/SCOUT/loop_day_20261105/briefs/`
function parseJson(text) {
  const m = String(text || '').match(/\{[\s\S]*\}/)
  if (!m) return null
  try { return JSON.parse(m[0]) } catch (e) { return null }
}
phase('Trial J')
const prepRaw = await agent(`You are SCO-A149, ${PRE}
Read your brief and follow it exactly: ${R}SCO-A149_TRIALJ_V17.md (brief sha16 41e9272193c21ea4). Final answer: ONE line of JSON only, as the brief says.`, { label: 'SCO-A142 trial J prep', phase: 'Trial J', agentType: 'general-purpose' })
const j = parseJson(prepRaw)
if (!j || !j.prompt || !j.prompt_sha16 || !j.task_id || !j.init_cmd) return { stage: 'prep', prepRaw }
const T = String(j.prompt).replace(/\/TRIALJ_PROMPT\.md$/, '')
const init = await agent(`You are SCO-A142L, SCOUT's trusted launcher step for trial J, ${PRE}
Do exactly this and nothing else: (1) sha256sum ${j.prompt} ${j.parent_step} | cut -c1-16 and stop if they are not ${j.prompt_sha16} and ${j.parent_sha16}; (2) cd $HOME/mnt/dev/TradingPlatform_repo/volat-agent/forensics && ${j.init_cmd} and print its full output and rc. Final answer: the phase start utc and the rc only.`, { label: 'SCO-A142L trial J init', phase: 'Trial J', agentType: 'general-purpose' })
const hunt = await agent(`You are SCT-J1, the alarm agent of trial J, ${PRE}
Your task is the alarm task in this prompt, nothing else. First run exactly: sha256sum ${j.prompt} | cut -c1-16 and stop if it is not ${j.prompt_sha16}; then cat ${j.prompt}. Your very next tool call after reading it must be the prompt's first time log switch out of the launcher's WAITING interval. Follow it to the end: every step runs exactly its TOOLS_V17 row, never build a tool (a missing tool is a NO TOOL line), SMOKE before any data, every job through the bridge with a typed INTENT and opdone after it ended, time log per step with no gap, never set the parent phase values yourself, numbers into receipts only through the receipt tool, the HAND WORK section, the LESSON PROOF section, and the four PROPOSE parts each citing a receipt. The runner accepts jobs from 00:15 to 23:05 UTC.
Final answer: as that prompt says, at most 15 lines.`, { label: 'SCT-J1 trial J hunter', phase: 'Trial J', agentType: 'general-purpose' })
const close = await agent(`You are SCO-A142C, the trusted parent close step of trial J, ${PRE}
The hunter SCT-J1 has ended. Its final answer was: <<<${String(hunt).slice(0, 1500)}>>>. Run exactly: sha256sum ${j.parent_step} | cut -c1-16 and stop if it is not ${j.parent_sha16}; then cat ${j.parent_step} and do exactly what it says (the run kit close and bind). Records only in ${T}/ops/. Do not change anything the hunter wrote.
Final answer at most 10 lines: complete and reasons, binding words and rc, HAND WORK minutes, file paths and sha16s.`, { label: 'SCO-A142C trial J parent close', phase: 'Trial J', agentType: 'general-purpose' })
return { stage: 'closed', prep: j, init, hunt, close }
