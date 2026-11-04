#!/bin/bash
# setup_python_v1.sh (SCOUT helper K14, 31 Oct 2026; TEST, NOT REVIEWED): the Python setup step of the Alarm release (R7_FIXES F37).
# the owner's portability law (30 Oct 2026, 23:49-23:57 Berlin): every tool is portable to another machine; the release folder holds
# everything with relative paths and the data is the only thing outside it; "Python itself is a machine install, not bundled: a setup
# step checks it is installed on the path and downloads it if it isn't". This is that step. Bash 3.2 (macOS's bash): no associative
# arrays, no ${x,,}, no readlink -f. It never deletes anything.
#
#   bash <Alarm>/_tools/setup_python_v1.sh --check [--python <path>]
#     The python3 on PATH (or the one named): its version (at least 3.10; the team runs 3.11), and every package line of
#     <Alarm>/settings/PYTHON_PACKAGES.txt ('#' comments and blank lines skipped; name==version exact, name>=version a minimum)
#     importable at a version that holds. One line per item (OK, MISSING, WRONG, or UNCHECKED when there is no good python3 to ask),
#     then one CHECK line. The probes run from /, so no module of the current folder stands in for a package. Exit 0 all OK;
#     1 something missing or wrong (each named); 2 usage, or REFUSED: a packages line that is not name==version or name>=version.
#   bash <Alarm>/_tools/setup_python_v1.sh --install <folder> [--dry]
#     <folder>: a new or empty folder outside the Alarm folder. A python3 3.10 or 3.11 on PATH (the versions the release is tested
#     on) is used as it is; otherwise the pinned CPython 3.11.18 build for this machine (the table below, by uname) is downloaded to
#     <folder>/download/, its sha256 checked against the table, and unpacked into <folder>/python. Then <folder>/venv is made with
#     that python, pip install -r <Alarm>/settings/PYTHON_PACKAGES.txt runs in it, --check runs with <folder>/venv/bin/python3, and
#     the line PYTHON=<folder>/venv/bin/python3 is printed for this machine's settings file (settings/SETTINGS_<MACHINE>.env). A venv
#     cannot be moved: make a new one instead.
#     --dry: print the URL and sha256 it would use and the steps, and change nothing.
#     Exit 0 done (with --dry: the plan can run); 1 a step failed (named; what was made is left in <folder>); 2 usage, or REFUSED:
#     a <folder> inside the Alarm folder, one that exists and is not an empty folder, a packages line it cannot read.
#
# The pinned table: python-build-standalone release 20261026 (CPython 3.11.18), its "install_only" tarballs (they unpack to python/:
# bin/python3, lib/, ...). Read on 31 Oct 2026 by SCOUT's K14 from the release page
#   https://github.com/astral-sh/python-build-standalone/releases/tag/20261026   (published 2026-10-26T15:54:13Z)
# and the release's own SHA256SUMS file
#   https://github.com/astral-sh/python-build-standalone/releases/download/20261026/SHA256SUMS
#   (that file's sha256: 39af6e3d3c712476893409f714a3b9ab795a861a89ec1628cbc99b45d1271a73)
# Each sha256 below is that file's line for its asset, and equals the digest GitHub's API lists for the asset. A new pin is a new
# edition of this script, with its test's table changed to match.
set -u

PIN_RELEASE=20261026
PIN_PYTHON=3.11.18

pinned() {   # $1 a platform: PIN_URL, PIN_SHA256 and PIN_FILE (the asset) of its pinned build; all empty when none is pinned for it
  PIN_URL=''; PIN_SHA256=''; PIN_FILE=''
  case "$1" in
    aarch64-apple-darwin)
      PIN_URL=https://github.com/astral-sh/python-build-standalone/releases/download/20261026/cpython-3.11.18%2B20261026-aarch64-apple-darwin-install_only.tar.gz
      PIN_SHA256=cba3455e18516fbe8668cff2820c9b6a53447c552d612443c2b2fb60d390a908 ;;
    x86_64-apple-darwin)
      PIN_URL=https://github.com/astral-sh/python-build-standalone/releases/download/20261026/cpython-3.11.18%2B20261026-x86_64-apple-darwin-install_only.tar.gz
      PIN_SHA256=a85474bcc78a98ca6b0070d8d615b0494b912b960239e6f18cc12d648f2dc270 ;;
    x86_64-unknown-linux-gnu)
      PIN_URL=https://github.com/astral-sh/python-build-standalone/releases/download/20261026/cpython-3.11.18%2B20261026-x86_64-unknown-linux-gnu-install_only.tar.gz
      PIN_SHA256=a87ee63646c8f8438b7af3954b2135ed2af91d033c631f12a8f20af903046d06 ;;
    aarch64-unknown-linux-gnu)
      PIN_URL=https://github.com/astral-sh/python-build-standalone/releases/download/20261026/cpython-3.11.18%2B20261026-aarch64-unknown-linux-gnu-install_only.tar.gz
      PIN_SHA256=a344c887b04a309f292cac1ef7c7a85e39e11932ec301d635258c569d830861b ;;
  esac
  [ -z "$PIN_URL" ] || PIN_FILE=cpython-$PIN_PYTHON+$PIN_RELEASE-$1-install_only.tar.gz
}

platform() {   # UNAME_S, UNAME_M and PLATFORM: the pinned build's name for this machine (empty when the table has none for it)
  UNAME_S=$(uname -s 2>/dev/null); UNAME_M=$(uname -m 2>/dev/null); PLATFORM=''
  case "$UNAME_S/$UNAME_M" in
    Darwin/arm64)              PLATFORM=aarch64-apple-darwin ;;
    Darwin/x86_64)             PLATFORM=x86_64-apple-darwin ;;
    Linux/x86_64)              PLATFORM=x86_64-unknown-linux-gnu ;;
    Linux/aarch64|Linux/arm64) PLATFORM=aarch64-unknown-linux-gnu ;;
  esac
}

NL='
'
PROBE_VERSION='import sys; print("PYTHON %d.%d.%d" % tuple(sys.version_info[:3]))  # setup_python_v1 probe: version'
PROBE_IMPORT='# setup_python_v1 probe: import. argv[1] a distribution; prints IMPORT <it> OK <module> <version>, or IMPORT <it> NO <module> <error>
import importlib, sys
d = sys.argv[1]
k = d.lower().replace("-", "_").replace(".", "_")
try:
    from importlib import metadata
except Exception:
    metadata = None
v = ""
if metadata is not None:
    try:
        v = metadata.version(d) or ""
    except Exception:
        v = ""
m, mod, err = None, k, "?"
try:
    m = importlib.import_module(k)
except BaseException as e:
    err = type(e).__name__
    if v:
        try:
            alts = sorted(x for x, ds in metadata.packages_distributions().items() if any(y.lower().replace("-", "_").replace(".", "_") == k for y in ds))
        except Exception:
            alts = []
        for x in alts:
            try:
                m, mod = importlib.import_module(x), x
                break
            except BaseException as e2:
                err = type(e2).__name__
if m is None:
    print("IMPORT %s NO %s %s" % (d, mod, err))
else:
    print("IMPORT %s OK %s %s" % (d, mod, (v or str(getattr(m, "__version__", "") or "?")).replace(" ", "_")))'

usage() {   # $1 why: the usage, exit 2
  echo "USAGE ${1:-}: bash setup_python_v1.sh --check [--python <path>]  |  bash setup_python_v1.sh --install <folder> [--dry]"
  exit 2
}
refuse() { echo "REFUSED $*"; exit 2; }

last_line() {   # $1 a prefix, $2 a text: the last line of the text that starts with the prefix
  local rest=$2 l r=''
  while [ -n "$rest" ]; do
    l=${rest%%"$NL"*}
    case "$rest" in *"$NL"*) rest=${rest#*"$NL"} ;; *) rest='' ;; esac
    case "$l" in "$1"*) r=$l ;; esac
  done
  printf '%s' "$r"
}
first_line() { local l=${1%%"$NL"*}; printf '%s' "${l:0:160}"; }

VRE='^([0-9]+(\.[0-9]+)*)(.*)$'
NRE='^[a-z]*[-._]?([0-9]+)'
vparse() {   # $1 a version: V_REL (its dotted numbers), V_PHASE (0 dev, 1 a, 2 b, 3 rc, 4 final, 5 post) and V_N; 1 when it cannot be read
  local v=$1 suf
  case "$v" in *[[:upper:]]*) v=$(printf '%s' "$v" | tr '[:upper:]' '[:lower:]') ;; esac
  v=${v%%+*}; v=${v#v}                         # a local label (+...) is ignored, as pip does; a leading v is dropped
  [[ $v =~ $VRE ]] || return 1
  V_REL=${BASH_REMATCH[1]}; suf=${BASH_REMATCH[3]}; V_PHASE=4; V_N=0
  suf=${suf#[-._]}
  case "$suf" in
    '')                             V_PHASE=4 ;;
    dev*)                           V_PHASE=0 ;;
    a|a[0-9]*|alpha*)               V_PHASE=1 ;;
    b|b[0-9]*|beta*)                V_PHASE=2 ;;
    rc*|c|c[0-9]*|pre*)             V_PHASE=3 ;;
    post*|rev*|r|r[0-9]*|[0-9]*)    V_PHASE=5 ;;
    *)                              return 1 ;;
  esac
  if [[ $suf =~ $NRE ]]; then V_N=${BASH_REMATCH[1]}; fi
  return 0
}

vcmp() {   # $1 $2 two versions: VCMP -1 ($1 is older), 0 (the same), 1 (newer), 2 (one cannot be read); numbers compare as numbers
  local r1 p1 n1 r2 p2 n2 a b
  VCMP=2
  vparse "$1" || return 0; r1=$V_REL; p1=$V_PHASE; n1=$V_N
  vparse "$2" || return 0; r2=$V_REL; p2=$V_PHASE; n2=$V_N
  while [ -n "$r1" ] || [ -n "$r2" ]; do
    a=${r1%%.*}; b=${r2%%.*}; a=${a:-0}; b=${b:-0}
    case "$r1" in *.*) r1=${r1#*.} ;; *) r1='' ;; esac
    case "$r2" in *.*) r2=${r2#*.} ;; *) r2='' ;; esac
    if [ $((10#$a)) -lt $((10#$b)) ]; then VCMP=-1; return 0; fi
    if [ $((10#$a)) -gt $((10#$b)) ]; then VCMP=1; return 0; fi
  done
  if [ "$p1" -lt "$p2" ]; then VCMP=-1; elif [ "$p1" -gt "$p2" ]; then VCMP=1
  elif [ $((10#$n1)) -lt $((10#$n2)) ]; then VCMP=-1; elif [ $((10#$n1)) -gt $((10#$n2)) ]; then VCMP=1; else VCMP=0; fi
  return 0
}

holds() {   # $1 the version found, $2 == or >=, $3 the version the line wants: 0 when it holds
  vcmp "$1" "$3"
  case "$2" in
    '==') [ "$VCMP" = 0 ] ;;
    '>=') [ "$VCMP" = 0 ] || [ "$VCMP" = 1 ] ;;
    *)    return 1 ;;
  esac
}

PRE='^([A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?)[[:space:]]*(==|>=)[[:space:]]*([^[:space:]]+)$'
NP=0
read_packages() {   # P_NAME, P_OP and P_VER (NP lines) from PKGS; REFUSED when the file is missing or a line is not name==version or name>=version
  local line n=0
  [ -f "$PKGS" ] || refuse "NO PACKAGES FILE $PKGS"
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n+1))
    line=${line%%#*}
    line=${line#"${line%%[![:space:]]*}"}; line=${line%"${line##*[![:space:]]}"}
    [ -n "$line" ] || continue
    [[ $line =~ $PRE ]] || refuse "PACKAGES LINE $n IS NOT name==version OR name>=version: $line ($PKGS)"
    P_NAME[$NP]=${BASH_REMATCH[1]}; P_OP[$NP]=${BASH_REMATCH[3]}; P_VER[$NP]=${BASH_REMATCH[4]}
    vparse "${P_VER[$NP]}" || refuse "PACKAGES LINE $n HAS A VERSION THIS CHECK CANNOT READ: $line ($PKGS)"
    NP=$((NP+1))
  done < "$PKGS"
}

find_python() {   # $1 a path, a command name, or empty (python3 on PATH): FOUND_PY (an absolute path; empty when there is none)
  case "$1" in
    '')  FOUND_PY=$(command -v python3 2>/dev/null) || FOUND_PY='' ;;
    */*) FOUND_PY=$1 ;;
    *)   FOUND_PY=$(command -v "$1" 2>/dev/null) || FOUND_PY='' ;;
  esac
  case "$FOUND_PY" in
    /*|'') ;;
    */*)   FOUND_PY=$(pwd -P)/$FOUND_PY ;;
    *)     FOUND_PY='' ;;                      # a shell builtin or function is no python3
  esac
}

item() { printf '%-9s %-20s %s\n' "$1" "$2" "$3"; }

check_python() {   # $1 a python (empty: none), $2 where it came from: one line per item; CHECK_BAD (how many not OK) and CHECK_PYVER
  local py=$1 from=$2 out line ver i spec bad=0 names='' detail
  CHECK_PYVER=''
  if [ -z "$py" ]; then
    item MISSING python3 "none on PATH"; bad=1; names=python3
  elif [ ! -f "$py" ] || [ ! -x "$py" ]; then
    item MISSING python3 "$py ($from): not an executable file"; bad=1; names=python3
  else
    out=$(cd / && "$py" -B -c "$PROBE_VERSION" < /dev/null 2>&1); line=$(last_line "PYTHON " "$out"); ver=${line#PYTHON }
    if [ -z "$line" ] || ! vparse "$ver"; then
      item WRONG python3 "$py ($from): the version probe failed: $(first_line "$out")"; bad=1; names=python3
    else
      vcmp "$ver" 3.10
      if [ "$VCMP" = 0 ] || [ "$VCMP" = 1 ]; then
        item OK python3 "$ver $py ($from; at least 3.10, the team runs 3.11)"; CHECK_PYVER=$ver
      else
        item WRONG python3 "$ver $py ($from): older than 3.10"; bad=1; names=python3
      fi
    fi
  fi
  i=0
  while [ $i -lt $NP ]; do
    spec=${P_NAME[$i]}${P_OP[$i]}${P_VER[$i]}
    if [ -z "$CHECK_PYVER" ]; then
      item UNCHECKED "$spec" "no good python3 to ask"; bad=$((bad+1)); names="$names $spec"
    else
      out=$(cd / && "$py" -B -c "$PROBE_IMPORT" "${P_NAME[$i]}" < /dev/null 2>&1); line=$(last_line "IMPORT ${P_NAME[$i]} " "$out")
      set -f; set -- $line; set +f
      if [ $# -lt 5 ]; then
        item WRONG "$spec" "the import probe failed: $(first_line "$out")"; bad=$((bad+1)); names="$names $spec"
      elif [ "$3" = NO ]; then
        item MISSING "$spec" "not importable: import $4 gives $5"; bad=$((bad+1)); names="$names $spec"
      elif [ "$5" = '?' ]; then
        item WRONG "$spec" "importable (import $4) but its version is not known"; bad=$((bad+1)); names="$names $spec"
      elif holds "$5" "${P_OP[$i]}" "${P_VER[$i]}"; then
        item OK "$spec" "$5"
      else
        detail="$5 installed"; [ "$VCMP" != 2 ] || detail="$5 installed: a version this check cannot read"
        item WRONG "$spec" "$detail"; bad=$((bad+1)); names="$names $spec"
      fi
    fi
    i=$((i+1))
  done
  CHECK_BAD=$bad
  if [ $bad -eq 0 ]; then
    echo "CHECK OK: python3 $CHECK_PYVER ($py) and the $NP packages of $PKGS"
  else
    echo "CHECK FAILED: $bad of $((NP+1)) items not OK: ${names# } ($PKGS)"
  fi
}

resolve() {   # $1 a path: RESOLVED, its absolute path, each part that exists taken with its links resolved (pwd -P), the rest as written
  local rest=$1 part cur
  case "$1" in /*) cur=/ ;; *) cur=$(pwd -P) ;; esac
  while [ -n "$rest" ]; do
    part=${rest%%/*}
    case "$rest" in */*) rest=${rest#*/} ;; *) rest='' ;; esac
    case "$part" in
      ''|.) ;;
      ..)   cur=${cur%/*}; [ -n "$cur" ] || cur=/ ;;
      *)    if [ "$cur" = / ]; then cur=/$part; else cur=$cur/$part; fi
            if [ -d "$cur" ]; then cur=$(CDPATH= cd -P "$cur" 2>/dev/null && pwd -P) || return 1; fi ;;
    esac
  done
  RESOLVED=$cur
}

is_empty_dir() {   # $1 a folder: 0 when it holds nothing (no file, folder or link; dot names too)
  local f
  [ -r "$1" ] && [ -x "$1" ] || return 1
  for f in "$1"/* "$1"/.[!.]* "$1"/..?*; do
    if [ -e "$f" ] || [ -L "$f" ]; then return 1; fi
  done
  return 0
}

sha256_of() {   # $1 a file: SHA, its sha256 in lower-case hex (shasum, sha256sum or openssl, the first one here); empty when none works
  local h=''
  if command -v shasum >/dev/null 2>&1; then h=$(shasum -a 256 "$1" 2>/dev/null)
  elif command -v sha256sum >/dev/null 2>&1; then h=$(sha256sum "$1" 2>/dev/null)
  elif command -v openssl >/dev/null 2>&1; then h=$(openssl dgst -sha256 -r "$1" 2>/dev/null)
  fi
  h=${h%% *}
  SHA=$(printf '%s' "$h" | tr '[:upper:]' '[:lower:]')
}

base_ok() { case "$1" in 3.10|3.10.*|3.11|3.11.*) return 0 ;; esac; return 1; }   # the versions the release is tested on

fail() { echo "FAILED $*"; echo "INSTALL FAILED: nothing is deleted; anything already made stays in $DEST (run again with a new folder)"; exit 1; }

do_install() {
  local base='' out line bver file venvpy dl=''
  resolve "$DEST_ARG" || refuse "CANNOT RESOLVE THE FOLDER $DEST_ARG"
  DEST=$RESOLVED
  case "$DEST/" in "$ALARM"/*) refuse "FOLDER INSIDE THE ALARM FOLDER $DEST (the Alarm folder holds the release only; Python is a machine install outside it)" ;; esac
  local state=new
  if [ -e "$DEST" ] || [ -L "$DEST" ]; then
    [ -d "$DEST" ] || refuse "NOT A FOLDER $DEST"
    is_empty_dir "$DEST" || refuse "FOLDER EXISTS AND IS NOT EMPTY $DEST (give a new folder or an empty one: nothing is ever overwritten)"
    state='an empty folder'
  fi
  read_packages
  [ $DRY -eq 0 ] || echo "DRY RUN: nothing is changed"
  echo "INSTALL  $DEST ($state); packages $PKGS ($NP lines)"
  find_python ''
  if [ -n "$FOUND_PY" ] && [ -f "$FOUND_PY" ] && [ -x "$FOUND_PY" ]; then
    out=$(cd / && "$FOUND_PY" -B -c "$PROBE_VERSION" < /dev/null 2>&1); line=$(last_line "PYTHON " "$out"); bver=${line#PYTHON }
    if [ -n "$line" ] && base_ok "$bver"; then
      base=$FOUND_PY; echo "PYTHON3  $FOUND_PY $bver on PATH: used as it is (3.10 or 3.11), no download"
    elif [ -n "$line" ]; then
      echo "PYTHON3  $FOUND_PY $bver on PATH: not 3.10 or 3.11 (the versions the release is tested on), so the pinned $PIN_PYTHON is used"
    else
      echo "PYTHON3  $FOUND_PY on PATH: its version probe failed ($(first_line "$out")), so the pinned $PIN_PYTHON is used"
    fi
  else
    echo "PYTHON3  none on PATH, so the pinned $PIN_PYTHON is used"
  fi
  platform; pinned "$PLATFORM"
  if [ -n "$PIN_URL" ]; then
    echo "PLATFORM $PLATFORM (uname: $UNAME_S $UNAME_M)"
    echo "URL      $PIN_URL"
    echo "SHA256   $PIN_SHA256"
  else
    echo "PLATFORM none pinned for uname '$UNAME_S $UNAME_M' (the table: aarch64-apple-darwin, x86_64-apple-darwin, x86_64-unknown-linux-gnu, aarch64-unknown-linux-gnu)"
  fi
  if [ -z "$base" ]; then
    [ -n "$PIN_URL" ] || fail "plan: no python3 3.10 or 3.11 on PATH and no pinned build for this machine: install Python 3.11 yourself, then run --install again"
    if command -v curl >/dev/null 2>&1; then dl=curl; elif command -v wget >/dev/null 2>&1; then dl=wget; fi
    [ -n "$dl" ] || fail "plan: neither curl nor wget is on PATH to download $PIN_URL"
    file=$DEST/download/$PIN_FILE
    echo "STEP     download $PIN_URL to $file ($dl)"
    echo "STEP     sha256 of $file must be $PIN_SHA256 (the table)"
    echo "STEP     unpack $file into $DEST/python (tar); $DEST/python/bin/python3 must say $PIN_PYTHON"
    base=$DEST/python/bin/python3
    if [ $DRY -eq 0 ]; then
      mkdir -p "$DEST/download" || fail "download: cannot make $DEST/download"
      if [ "$dl" = curl ]; then curl -fsSL --retry 2 --connect-timeout 30 -o "$file" "$PIN_URL"; else wget -q -O "$file" "$PIN_URL"; fi
      [ $? -eq 0 ] && [ -f "$file" ] || fail "download: $dl could not fetch $PIN_URL"
      sha256_of "$file"
      [ "$SHA" = "$PIN_SHA256" ] || fail "sha256: $file has ${SHA:-no sha256 (no shasum, sha256sum or openssl here)}, the table says $PIN_SHA256: not unpacked (the file is left there)"
      echo "DONE     download and sha256 ($SHA)"
      tar -xzf "$file" -C "$DEST" || fail "unpack: tar could not unpack $file"
      [ -f "$base" ] && [ -x "$base" ] || fail "unpack: no $base"
      out=$(cd / && "$base" -B -c "$PROBE_VERSION" < /dev/null 2>&1); line=$(last_line "PYTHON " "$out")
      [ "$line" = "PYTHON $PIN_PYTHON" ] || fail "unpack: $base says '${line:-$(first_line "$out")}', not PYTHON $PIN_PYTHON"
      echo "DONE     unpack: $base is Python $PIN_PYTHON"
    fi
  fi
  venvpy=$DEST/venv/bin/python3
  echo "STEP     venv: $base -m venv $DEST/venv"
  echo "STEP     pip: $venvpy -m pip install --disable-pip-version-check -r $PKGS"
  echo "STEP     check: --check --python $venvpy"
  echo "STEP     print the settings line PYTHON=$venvpy (for settings/SETTINGS_<MACHINE>.env)"
  if [ $DRY -eq 1 ]; then echo "DRY RUN: nothing was changed"; exit 0; fi
  mkdir -p "$DEST" || fail "venv: cannot make $DEST"
  "$base" -m venv "$DEST/venv" < /dev/null || fail "venv: $base -m venv $DEST/venv"
  [ -f "$venvpy" ] && [ -x "$venvpy" ] || fail "venv: no $venvpy"
  echo "DONE     venv $DEST/venv"
  "$venvpy" -m pip install --disable-pip-version-check -r "$PKGS" < /dev/null || fail "pip: $venvpy -m pip install -r $PKGS"
  echo "DONE     pip"
  check_python "$venvpy" "the new venv"
  [ "$CHECK_BAD" -eq 0 ] || fail "check: $CHECK_BAD items not OK with $venvpy (above)"
  echo "PYTHON=$venvpy"
  exit 0
}

MODE=''; PY_ARG=''; PY_GIVEN=0; DEST_ARG=''; DRY=0
[ $# -gt 0 ] || usage "no arguments"
while [ $# -gt 0 ]; do
  case "$1" in
    --check)   [ -z "$MODE" ] || usage "--check and --install do not go together"; MODE=check; shift ;;
    --install) [ -z "$MODE" ] || usage "--check and --install do not go together"
               [ $# -ge 2 ] || usage "--install needs a folder"
               case "$2" in ''|-*) usage "--install needs a folder" ;; esac
               MODE=install; DEST_ARG=$2; shift 2 ;;
    --python)  [ $PY_GIVEN -eq 0 ] || usage "--python twice"
               [ $# -ge 2 ] || usage "--python needs a path"
               case "$2" in ''|-*) usage "--python needs a path" ;; esac
               PY_GIVEN=1; PY_ARG=$2; shift 2 ;;
    --dry)     DRY=1; shift ;;
    *)         usage "unknown argument $1" ;;
  esac
done
[ -n "$MODE" ] || usage "--check or --install"
if [ "$MODE" = check ] && [ $DRY -eq 1 ]; then usage "--dry goes with --install"; fi
if [ "$MODE" = install ] && [ $PY_GIVEN -eq 1 ]; then usage "--python goes with --check"; fi

SELF=${BASH_SOURCE[0]}
case "$SELF" in */*) HERE=${SELF%/*} ;; *) HERE=. ;; esac
HERE=$(CDPATH= cd -P "$HERE" 2>/dev/null && pwd -P) || refuse "CANNOT FIND THE FOLDER OF $SELF"
ALARM=$(CDPATH= cd -P "$HERE/.." 2>/dev/null && pwd -P) || refuse "CANNOT FIND THE ALARM FOLDER ABOVE $HERE"
PKGS=$ALARM/settings/PYTHON_PACKAGES.txt

if [ "$MODE" = check ]; then
  read_packages
  if [ $PY_GIVEN -eq 1 ]; then find_python "$PY_ARG"; [ -n "$FOUND_PY" ] || FOUND_PY=$PY_ARG; FROM=--python; else find_python ''; FROM=PATH; fi
  check_python "$FOUND_PY" "$FROM"
  [ "$CHECK_BAD" -eq 0 ] && exit 0
  exit 1
fi
do_install
