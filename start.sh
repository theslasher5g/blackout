#!/bin/sh
# BLACKOUT Start (Linux/macOS):  sh start.sh        Optional: MODEL=datei.gguf  CTX=8192  UI_LAN=1
ROOT="$(cd "$(dirname "$0")" && pwd)"; export BLACKOUT_ROOT="$ROOT"
case "$(uname -s)" in Linux) os=linux;; Darwin) os=mac;; *) echo "Windows: start.bat nutzen"; exit 1;; esac
case "$(uname -m)" in x86_64|amd64) ar=x64;; arm64|aarch64) ar=arm64;; *) ar=x64;; esac
BIN="$ROOT/bin/$os-$ar"; [ -d "$BIN" ] || BIN="$ROOT/bin/$os-x64"
[ -d "$BIN" ] || { echo "Keine Programme fuer $os-$ar in $ROOT/bin (prepare.py --platforms ...)"; exit 1; }
# exFAT-SSDs sind oft nicht ausfuehrbar -> Kopie in tmp
if [ ! -x "$BIN/llama-server" ]; then
  T="${TMPDIR:-/tmp}/blackout-bin"; mkdir -p "$T"; cp -R "$BIN/." "$T/"; chmod -R u+x "$T"; BIN="$T"
fi
if [ "$os" = linux ]; then ram=$(awk '/MemTotal/{printf "%d",$2/1048576}' /proc/meminfo)
else ram=$(( $(sysctl -n hw.memsize) / 1073741824 )); fi
if [ -z "$MODEL" ]; then
  while read -r need f; do
    [ -f "$ROOT/models/$f" ] && [ "$ram" -ge "$need" ] && MODEL="$f" && break
  done < "$ROOT/models/tiers.txt"
  [ -z "$MODEL" ] && MODEL="$(ls "$ROOT/models" | grep -m1 '\.gguf$')"
fi
[ -f "$ROOT/models/$MODEL" ] || { echo "Kein Modell gefunden in $ROOT/models"; exit 1; }
echo "RAM: ${ram} GB  ->  Modell: $MODEL"
export LD_LIBRARY_PATH="$BIN:$LD_LIBRARY_PATH" DYLD_LIBRARY_PATH="$BIN:$DYLD_LIBRARY_PATH"
PIDS=""; trap 'kill $PIDS 2>/dev/null' EXIT INT TERM
if ls "$ROOT"/zim/*.zim >/dev/null 2>&1 && [ -x "$BIN/kiwix-serve" ]; then
  "$BIN/kiwix-serve" --port 8080 "$ROOT"/zim/*.zim >/dev/null 2>&1 & PIDS="$PIDS $!"
fi
"$BIN/llama-server" -m "$ROOT/models/$MODEL" -c "${CTX:-8192}" --host 127.0.0.1 --port 8081 >"${TMPDIR:-/tmp}/blackout-llm.log" 2>&1 & PIDS="$PIDS $!"
PY="$(command -v python3 || command -v python)"
if [ -z "$PY" ]; then
  echo "Kein Python gefunden. Ohne Chat-Oberflaeche nutzbar:"
  echo "  KI:      http://localhost:8081   Bibliothek: http://localhost:8080"; wait; exit
fi
echo "Gleich bereit: http://localhost:8000  (KI braucht beim Laden 10-60 s)"
( sleep 3; xdg-open http://localhost:8000 2>/dev/null || open http://localhost:8000 2>/dev/null ) &
"$PY" "$ROOT/app/rag_server.py"
