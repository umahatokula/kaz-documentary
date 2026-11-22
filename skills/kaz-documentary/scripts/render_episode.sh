#!/bin/bash
# kaz-documentary series toolkit: renders the 2560x1440 upload master of one episode.
# Usage: render_episode.sh EPISODE_DIR (called by the episode's render_master.command).
# Everything installed here (ffmpeg via Homebrew, the Python venv) is shared by every episode in the series.
TK="$(cd "$(dirname "$0")" && pwd)"; EP="$1"
pause() { echo; read -r -p "Press Enter to close."; }
echo "== Kaz Documentary master render: $(basename "$EP")   (toolkit $(cat "$TK/VERSION" 2>/dev/null))"
[ -f "$EP/kaz/episode.json" ] || { echo "No kaz/episode.json in $EP. Ask Claude to set up this episode's master render."; pause; exit 1; }

export PATH="$HOME/.homebrew/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
BREW="$(command -v brew)"
if ! command -v ffmpeg >/dev/null; then
  [ -n "$BREW" ] || { echo "ffmpeg is missing and Homebrew was not found. Paste this window to Claude."; pause; exit 1; }
  echo "Installing ffmpeg (one time for the whole series, a few minutes)..."
  for i in 1 2 3; do "$BREW" install ffmpeg && break; echo "Retrying in 10 s..."; sleep 10; done
  command -v ffmpeg >/dev/null || { echo "Could not install ffmpeg. Paste this window to Claude."; pause; exit 1; }
fi
echo "Using $(command -v ffmpeg)"

VENV="$TK/venv"
if [ ! -x "$VENV/bin/python" ]; then
  PY3="$(command -v python3)"
  if [ -z "$PY3" ] || ! "$PY3" -c "import venv" 2>/dev/null; then
    [ -n "$BREW" ] && { echo "Installing Python (one time)..."; "$BREW" install python; PY3="$(command -v python3)"; }
  fi
  [ -n "$PY3" ] || { echo "Python 3 not found. Paste this window to Claude."; pause; exit 1; }
  echo "Setting up the series' Python packages (one time)..."; "$PY3" -m venv "$VENV" || { pause; exit 1; }
fi
"$VENV/bin/python" -c "import numpy, cv2, PIL" 2>/dev/null || {
  "$VENV/bin/python" -m pip install -q --upgrade pip
  "$VENV/bin/python" -m pip install -q numpy opencv-python-headless pillow || { echo "Could not install Python packages. Paste this window to Claude."; pause; exit 1; }
}

echo "Keep the Mac plugged in. It will stay awake until the render finishes."
START=$(date +%s)
caffeinate -dimsu "$VENV/bin/python" "$TK/run_master.py" "$EP" || { echo; echo "Render failed (see above). Paste this window to Claude. Running it again resumes."; pause; exit 1; }
OUT="$(ls -t "$EP"/out/*_1440p.mp4 2>/dev/null | head -1)"
echo
echo "Finished in about $(( ($(date +%s) - START) / 60 )) min: $OUT ($(du -h "$OUT" | cut -f1))"
echo "Upload this file to YouTube. The _master folder is scratch; you can delete it."
open -R "$OUT"
pause
