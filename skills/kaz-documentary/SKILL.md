---
name: kaz-documentary
description: This skill should be used when the user asks to "make a Kaz documentary", "make a documentary video", "make an evidence-board video", "animate this history script", "turn my voiceover into a documentary", "add a vintage 2D animation part", "make a silent-film style section", or wants a narrated explainer with archival photos, maps, red annotations, typed labels and one continuous camera rendered to MP4.
---

# Kaz Documentary

Build narrated documentary videos in code, in the Kaz evidence-board style. Optionally cut in vintage 2D silent-film sections for key moments. Render to MP4 with the voiceover, music bed and SFX.

Bundled scripts are in `${CLAUDE_PLUGIN_ROOT}/skills/kaz-documentary/scripts/`:

| Script | Role |
|---|---|
| `board_engine.py` | Evidence-board renderer: one world surface, a camera with keyframes, pinned cards, tags, strings, circles, stamps, year card, thesis card, end title, grain and vignette. |
| `vintage_engine.py` | Vintage 2D silent-film renderer: sepia street map, side-view street scene with a car and figures, an intertitle card, boiling lines on twos, grain, scratches, flicker, gate weave and iris wipes. |
| `align_timing.py` | Estimates sentence start times from the script and silence detection, for when Whisper is unavailable. |
| `sound_bed.py` | Synthesizes a drone, pulse and SFX from a cue JSON. No downloads. |
| `splice.sh` | Replaces a frame range of the board video with a vintage insert. |
| `mix_and_mux.sh` | Ducks the bed under the voice, normalizes to -14 LUFS and outputs a shareable MP4. |
| `themes.py` | Seven background looks (teal_slate, cork, chalkboard, blueprint, manila, olive_canvas, concrete): board texture, map land, border and label colours. Chosen with the `KAZ_THEME` environment variable. Also draws country maps from Natural Earth GeoJSON. |
| `promo.py` | Promo pass: picks calm moments (`pick`), then adds 4 s subscribe prompts there and appends a 10 s YouTube end screen with empty space for one video element and the channel logo (`build`). `preview` renders sample prompt frames. |
| `hd.py` | Resolution layer. Screen-space drawing is written in 1920x1080 design coordinates; `KAZ_SCALE=4/3` renders it natively at 2560x1440 (`SD` wraps an ImageDraw, `SFont` a font, `PXW`/`PXH` are the pixel size). Also resolves the bundled fonts in `fonts/`. |
| `run_master.py`, `make_audio.py`, `render_master.command` | 1440p upload master on the user's Mac: the double-click launcher sets up ffmpeg and Python, rebuilds the soundtrack from the chapter WAVs, renders board chunks and inserts in parallel at 2560x1440, then runs the promo pass into `out/`. Driven by `episode.json` (fields listed in `run_master.py`). |

Both engines are worked examples from a real project (Sarajevo 1914). For each new video, copy them into a project folder and edit the data blocks: asset paths, card layout, camera keys, tags, lines, ellipses, overlay times and scene drawings. Keep the rendering machinery as it is, including the `hd.py` resolution layer.

Read `references/style-guide.md` before planning shots. Read `references/engine-guide.md` before editing an engine.

## Workflow

1. **Intake.** Collect the voiceover (or script), the images, aspect ratio (16:9 by default), resolution (1080p by default), the channel name (for the subscribe prompts, end title and end screen), the background theme, and which moments should become vintage 2D sections. Use the defaults when unstated and say so.
2. **Background theme.** Every video gets its own look so the channel's uploads don't all match. Look for `kaz_theme.txt` in the user's previous project folders (or ask which theme the last video used). Suggest one theme that fits the story and differs from the last video, for example blueprint navy for an aviation or engineering mystery, olive canvas for a coup or military story, manila for a court or case-file story, chalkboard for an ideas-driven story, cork for an investigation with many people, concrete for a modern or urban story, and teal slate as the neutral default. Wait for the user to confirm it. If they want to compare, render one or two stills of the first beats once per theme (`KAZ_THEME=name python3 board_engine.py stills ...`) and tile them into a labelled sheet. Write the chosen name into `kaz_theme.txt` in the project folder.
3. **Assets rule.** Photos of real people and real archival photos must come from the user. Never download photos of real people from the web. Suggest public-domain sources (Wikimedia Commons, the Library of Congress). Generate maps, notes, stamps, labels, intertitles and 2D drawings yourself. Never recreate a real outlet's logo or masthead; use the user's screenshot or a generic masthead.
4. **Timing.** Try faster-whisper for word timestamps. If the model can't download, ask for the script text and run `align_timing.py` (edit its sentence list), then sanity-check the starts against the pause list it prints.
5. **Shot list.** One beat per sentence. For each beat give the time range, beat recipe (style-guide §2), assets, trigger word and camera move. Mark vintage-2D beats. Share it briefly along with any missing images.
6. **Build the board.** Copy `board_engine.py` and `themes.py` into the project folder together, set `KAZ_THEME` for every render, and edit the data blocks. Render stills at one timestamp per beat (`python3 board_engine.py stills 2,9,22,...`), tile them into a contact sheet, and look at it. Fix layout, colour (frames are BGR), font glyphs and camera targets before the full render. Locate map coordinates by drawing a grid over the map image.
7. **Build vintage inserts.** Copy `vintage_engine.py`, set `T0`/`T1` to the insert's frame range, redraw the scenes for the story, and keep the film treatment, twos, iris wipes and the red-only accent. Check stills, especially the order of action relative to the voiceover.
8. **Render.** Split the full render into chunks, one process per CPU core (`python3 board_engine.py full START END part.mp4`), then concat. Render each insert, then run `splice.sh`.
9. **Sound.** Write a cue JSON (whooshes on camera moves, typing on tags, thuds on stamps, shots, scratches on circles, `film` and `engine` ranges over inserts), run `sound_bed.py`, then `mix_and_mux.sh`. When the voiceover comes as chapter WAVs, build the mix with `make_audio.py` instead (same chain as the Mac master, so both soundtracks match sample for sample).
10. **Promo pass.** Every video gets subscribe prompts and an end screen.
   - Write `busy.json`: the `[start, end]` ranges of every year, count and thesis card, each vintage insert, each stamp and flash, and the end title. Run `python3 promo.py pick DURATION busy.json` to get three calm 4 s windows near 10%, 45% and 75% of the runtime (at least 60 s apart, none in the first 20 s or the last 25 s). Use `--targets` for more or fewer prompts on very short or long videos.
   - Check the narration at each picked time; move a prompt off any reveal, verdict or emotional beat.
   - Run `python3 promo.py build master.mp4 final.mp4 --channel NAME --times T1,T2,T3 --bg-time T`, where `master.mp4` is the mixed video and `T` is a wide board shot near the end (the end-screen background, blurred and darkened).
   - The prompt is a pinned paper note in the bottom-right corner: a typed line, a red SUBSCRIBE button with a bell, a cursor that clicks it to SUBSCRIBED, a bell ring, then it slides away. It comes with a soft pop, click and ding.
   - The end screen runs 10 s: the channel name at the top, "WATCH NEXT" above an empty 16:9 space on the left (x 150-1050, y 290-796) and "SUBSCRIBE" below an empty circle space on the right (centre 1460,543, radius 200), for the YouTube video element and channel logo. Never draw outlines or boxes round these spaces, since the user places YouTube's elements by hand and they may not line up. Tell the user where the spaces are.
11. **QC and deliver.** Pull five or so frames around each insert boundary and key mark. Check that marks land on their words, no text is cut off, and there are no glyph boxes. Send the MP4 with a short description of what happens, and note that timing was estimated if Whisper wasn't used. This 1080p file is the preview for approval, not the upload.
12. **1440p upload master on the user's Mac (every video, once the preview is approved).** 1440p uploads get YouTube's higher-bitrate encodes, so they look sharper even for 1080p viewers, and the full-quality file never has to pass through the chat's send limit.
   - In the project folder on the Mac (the folder with the chapter WAVs and photos), create `kaz/` holding: the episode's board script and insert scripts, `hd.py`, `themes.py`, `promo.py`, `sound_bed.py`, `make_audio.py`, `run_master.py`, `fonts/`, any data files the scripts read (word timings, GeoJSON, `photos.json`, `cues.json`), the captions `.srt`, and `episode.json`. Put `render_master.command` in the project folder itself and `chmod +x` it. Point every path in the scripts at their own folder (`ROOT`) or `KAZ_ASSETS` (the project folder); no workspace paths. Insert scripts must render their own frame range in `full` mode and write to `$KAZ_VOUT`.
   - Before shipping, prove the layer: stills at `KAZ_SCALE=1` must be byte-identical to the approved preview, and stills at `KAZ_SCALE=1.3333333333` must show the same layout at 2560x1440. Run `run_master.py` once on a few seconds (shrink the ranges) to test the whole chain.
   - Ship small files only: the user's link may time out above a few MB. Send the code as one `.tgz` with `device_commit_files` (stagedPath under /mnt/user-data/outputs, 25 MB max) and unpack it with `device_bash`. Never ship the mixed audio; `make_audio.py` rebuilds it from the WAVs already on the Mac.
   - Tell the user to double-click `render_master.command` (if macOS blocks it: right-click > Open). It finds Homebrew in `~/.homebrew`, `/opt/homebrew` or `/usr/local`, installs ffmpeg and the Python packages once, keeps the Mac awake, sizes the worker count to memory (about 3 GB per worker), and resumes if re-run. Output: `out/<name>_1440p.mp4` at 20 Mbps (about 9 GB per hour) plus the `.srt`. `_master/` is scratch.

## Rules

- Keep one continuous camera with no hard cuts, except planned world changes (iris wipes into and out of vintage inserts, a glitch into the end title).
- Keep the theme to the background, map and label colours. Cards, tags, stamps, red marks and the vintage inserts' sepia look stay the same in every theme. On light themes (manila) the dark tag boxes still work; check that map labels stay readable.
- Use red only for meaning: circles, strings, stamps, key labels and the end title.
- Keep violence non-graphic: flash, smoke and an intertitle, never blood or wounds.
- Keep the preview small: shareable encodes at CRF 24. Grain inflates the bitrate, so for long videos encode the preview with `promo.py build --bitrate` sized to fit the send limit (about 3300k for 14 minutes stays under 400 MB). The upload is the Mac master (step 12).
- Draw everything that lives on screen (tags, overlays, year/count/thesis/list cards, end titles, vintage scenes, promo) through `SD(...)` and `SFont(...)` in 1920x1080 design coordinates, and size screen arrays (grain, vignette, warps) with `PXW`/`PXH`. Leave world-space card drawing alone; cards get their resolution from `R`.
- Every video ends with the promo pass: subscribe prompts at calm moments and the 10 s end screen with empty, unoutlined spaces for the video element and logo.
