# Kaz Documentary

Turns a voiceover and a folder of images into a narrated documentary video in the Kaz evidence-board style. It uses one continuous camera over a map or board, pinned archival photos, red circles and strings, typed name tags, stamps, year and thesis cards, and a glitch end title. For key moments it can cut in vintage silent-film 2D animation.

**To use it,** ask: "Make a Kaz documentary from this voiceover and these images", optionally adding "make the [moment] part a vintage 2D animation".

**What you provide:** a voiceover (MP3 or WAV) or a script, plus photos of the people and events. You supply photos of real people yourself.

**Every episode looks different (v0.6):** before each video Claude asks you a set of style questions: story structure, opening, length, a signature sequence, background theme (seven), reconstruction style (silent film, newspaper print or courtroom sketch), map style, music bed (drone, piano, pulse or ambient), who narrates (your ElevenLabs clone, your own recording or Kokoro), host intro/outro in your real voice, a closing "What the evidence shows" segment (drafted by Claude, approved and voiced by you) and thumbnail layout (pinned, split, full-bleed or case file). It recommends one option per question and leaves out anything used too recently, so uploads don't look template-made (YouTube's "inauthentic content" rule). Your choices are logged in `~/Documents/Kaz Documentary/style_log.json`.

**What it makes:** maps, notes, labels, stamps, 2D scenes, intertitles, music and sound effects, delivered as a 1080p preview MP4 with subscribe prompts at calm moments and a 10-second YouTube end screen (empty spaces for a video element and your channel logo).

**Upload master:** episodes live in `~/Documents/Kaz Documentary/<episode>/`, with one shared `_toolkit/` for the whole series. Once you approve the preview, Claude sets up `render_master.command` in the episode folder. Double-click it on your Mac and it renders the same video natively at 2560x1440 (sharper YouTube encodes) into `out/`, rebuilding the soundtrack from your chapter WAVs. ffmpeg and the Python packages are installed once, on the series' first render; re-running resumes an interrupted render.

**Requirements** (all standard in Claude's workspace): Python 3 with numpy, opencv-python and Pillow; ffmpeg. Fonts (FreeMono Bold, GPL with font exception; Caladea, Apache 2.0) are bundled in `scripts/fonts/`. The Mac master needs Homebrew.
