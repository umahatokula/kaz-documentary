#!/bin/bash
# kaz-documentary (copy into the episode folder, chmod +x): renders the full-quality YouTube upload master (2560x1440) of the episode in this
# folder, on this Mac. Double-click in Finder (if macOS blocks it: right-click > Open).
# Output: out/<name>_1440p.mp4 (+ .srt). Re-running after a stop resumes where it left off.
cd "$(dirname "$0")" || exit 1
EP="$PWD"
pause() { echo; read -r -p "Press Enter to close."; }
echo "== kaz-documentary master render: $(basename "$EP")"
[ -f "$EP/kaz/run_master.py" ] || { echo "Missing kaz/run_master.py in this folder. Ask Claude to set up the master render."; pause; exit 1; }

export PATH="$HOME/.homebrew/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
BREW="$(command -v brew)"

if ! command -v ffmpeg >/dev/null; then
  [ -n "$BREW" ] || { echo "ffmpeg is missing and Homebrew was not found. Paste this window to Claude."; pause; exit 1; }
  echo "Installing ffmpeg (one time, a few minutes)..."
  for i in 1 2 3; do "$BREW" install ffmpeg && break; echo "Retrying in 10 s..."; sleep 10; done
  command -v ffmpeg >/dev/null || { echo "Could not install ffmpeg. Paste this window to Claude."; pause; exit 1; }
fi
echo "Using $(command -v ffmpeg)"

PY3="$(command -v python3)"
if [ -z "$PY3" ] || ! "$PY3" -c "import venv" 2>/dev/null; then
  [ -n "$BREW" ] && { echo "Installing Python (one time)..."; "$BREW" install python; PY3="$(command -v python3)"; }
fi
[ -n "$PY3" ] || { echo "Python 3 not found. Paste this window to Claude."; pause; exit 1; }

VENV="$HOME/.kaz-documentary/venv"
if [ ! -x "$VENV/bin/python" ]; then echo "Setting up Python packages (one time)..."; mkdir -p "$HOME/.kaz-documentary"; "$PY3" -m venv "$VENV" || { pause; exit 1; }; fi
"$VENV/bin/python" -c "import numpy, cv2, PIL" 2>/dev/null || {
  "$VENV/bin/python" -m pip install -q --upgrade pip
  "$VENV/bin/python" -m pip install -q numpy opencv-python-headless pillow || { echo "Could not install Python packages. Paste this window to Claude."; pause; exit 1; }
}

echo "Keep the Mac plugged in. It will stay awake until the render finishes."
START=$(date +%s)
caffeinate -dimsu "$VENV/bin/python" "$EP/kaz/run_master.py" || { echo; echo "Render failed (see above). Paste this window to Claude. Running this file again resumes."; pause; exit 1; }

OUT="$(ls -t "$EP"/out/*_1440p.mp4 2>/dev/null | head -1)"
echo
echo "Finished in about $(( ($(date +%s) - START) / 60 )) min: $OUT ($(du -h "$OUT" | cut -f1))"
echo "Upload this file to YouTube. The _master folder is scratch; you can delete it."
open -R "$OUT"
pause
