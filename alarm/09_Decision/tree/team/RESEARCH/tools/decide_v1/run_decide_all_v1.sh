#!/bin/bash
# run_decide_all_v1.sh (DECIDE seat, 26 Oct 2026): decision tool V1 on the six frozen alarms, Sep 10 - Dec 31 2025, research mode.
# Every alarm with the default rulebook (the take-all baseline); M and S3W also with their own rulebooks. One process at a time.
# usage: run_decide_all_v1.sh <forensics root> <profile cards root> <new out folder> [where /Volumes is mounted, empty on the Mac]
# A run that refuses prints "REFUSED <CODE>: why" in its log and exits 2.
set -euo pipefail
F="$1"; P="$2"; O="$3"; V="${4:-}"
D="$F/team/RESEARCH/tools/decide_v1"; L="$F/team/RESEARCH/LIBRARY"
C="$L/context_split/runs_v41/commit_974f4eeb79487e91"; K="$L/cause_lib/run_v1_2"
[ -e "$O" ] && { echo "out $O exists" >&2; exit 2; }
mkdir -p "$O"
one() {  # alarm id, short name, rulebook file, label
  python3 -B "$D/decide_v1.py" --universe "$L/UNIVERSE_ALARMS_V1.tsv" --alarm-id "$1" --first 20250910 --last 20251231 \
    --research-window 20250910:20251231 --rulebook "$D/rulebooks/$3" --safety "$D/SAFETY_V1.json" --lab-tools "$D/LAB_TOOLS_V1.json" \
    --admitted "$D/ADMITTED_INPUTS_V1.json" --volumes-root "$V" --root "$F" --mode research --ctx-cards "$C/STATE_CARDS_$1_V41.tsv" \
    --prof-cards "$P/a/CARDS_$1.tsv,$P/b/CARDS_$1.tsv,$P/c/CARDS_$1.tsv" --pmm-cards "$K/PMM_$2.tsv" --out "$O/$1_$4" > "$O/$1_$4.log" 2>&1 || true
  echo "$1 $4 $(tail -c 400 "$O/$1_$4.log")"
}
for a in C:C M:M H0:H0 S2B0:S2B0 S2R1:S2R1 S3W:S3W; do one "ALM_${a%%:*}_V1" "${a##*:}" RULES_DEFAULT_V1.json DEFAULT; done
one ALM_M_V1 M RULES_ALM_M_V1.json OWN
one ALM_S3W_V1 S3W RULES_ALM_S3W_V1.json OWN
