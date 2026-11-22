#!/bin/bash
# kaz-documentary episode launcher: renders this episode's 2560x1440 upload master with the series toolkit
# (../_toolkit, installed once for every episode). Double-click in Finder (if macOS blocks it: right-click > Open).
cd "$(dirname "$0")" || exit 1
TK="$(cd .. && pwd)/_toolkit"
[ -f "$TK/render_episode.sh" ] || TK="$HOME/Documents/Kaz Documentary/_toolkit"
if [ ! -f "$TK/render_episode.sh" ]; then
  echo "Kaz Documentary toolkit not found (expected ../_toolkit). Ask Claude to set it up."; read -r -p "Press Enter to close."; exit 1
fi
exec bash "$TK/render_episode.sh" "$PWD"
