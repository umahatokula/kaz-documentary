# Kaz Documentary

Turns a voiceover and a folder of images into a narrated documentary video in the Kaz evidence-board style. It uses one continuous camera over a map or board, pinned archival photos, red circles and strings, typed name tags, stamps, year and thesis cards, and a glitch end title. For key moments it can cut in vintage silent-film 2D animation.

**To use it,** ask: "Make a Kaz documentary from this voiceover and these images", optionally adding "make the [moment] part a vintage 2D animation".

**What you provide:** a voiceover (MP3 or WAV) or a script, plus photos of the people and events. You supply photos of real people yourself.

**Looks:** seven background themes (teal slate, cork board, chalkboard, blueprint navy, manila case file, olive army canvas, concrete grey). It suggests a different one for each video and you confirm it.

**What it makes:** maps, notes, labels, stamps, 2D scenes, intertitles, music and sound effects, delivered as a 1080p preview MP4 with subscribe prompts at calm moments and a 10-second YouTube end screen (empty spaces for a video element and your channel logo).

**Upload master:** once you approve the preview, Claude sets up `render_master.command` in your project folder. Double-click it on your Mac and it renders the same video natively at 2560x1440 (sharper YouTube encodes) into `out/`, rebuilding the soundtrack from your chapter WAVs. First run installs ffmpeg and a few Python packages via Homebrew; re-running resumes an interrupted render.

**Requirements** (all standard in Claude's workspace): Python 3 with numpy, opencv-python and Pillow; ffmpeg. Fonts (FreeMono Bold, GPL with font exception; Caladea, Apache 2.0) are bundled in `scripts/fonts/`. The Mac master needs Homebrew.
