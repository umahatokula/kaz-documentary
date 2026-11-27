# Per-episode style menu

YouTube does not monetise "inauthentic" content: videos that look made from a template with little variation, or mass-produced. A consistent brand is fine; identical episodes are not. So every episode is built from a fresh set of choices, and the user makes each one.

## How to run it

1. Run `python3 scripts/style_menu.py "SERIES_DIR"` (the series folder, e.g. `~/Documents/Kaz Documentary`; read `style_log.json` from the user's Mac with `device_bash` if the series lives there). It prints every decision, its allowed options and the options blocked by the rotation rules.
2. Ask the user every decision with AskUserQuestion, in three rounds of up to four questions. Put the option that fits the story best first, marked "(Recommended)", with one line on why it fits this story. Leave blocked options out (mention once that they were used recently). Each option's description says what the viewer will see.
   - **Round 1, story** (before the script prompt): `structure`, `opening`, `length`, `set_piece`. For `set_piece`, offer 2-3 sequences built only for this story; the user can type their own.
   - **Round 2, look**: `theme`, `reconstruction`, `map_style`, `sound_mood`.
   - **Round 3, voice and packaging**: `voice`, `host_bookends`, `perspective`, `thumb_layout` (the main thumbnail; the test thumbnail uses a different allowed layout).
3. If the user picks a blocked option anyway (by typing it), say once which recent episode used it, then accept it and record it with `--force`.
4. Record the choices: `python3 scripts/style_menu.py "SERIES_DIR" add EPISODE choices.json` (or a JSON string), and save the same JSON as `kaz/style.json` in the episode. Ship the updated `style_log.json` back to the series folder on the Mac.
5. Follow the choices through the build:
   - `structure`, `opening`, `length` and `perspective` go into the script prompt (`references/script-prompt.md`).
   - `theme` → `KAZ_THEME`; `map_style` → how `build_bg` draws the maps; `reconstruction` → which kit the insert script imports; `set_piece` → one sequence designed and built for this episode only (on the board or as an insert).
   - `sound_mood` → `"mood"` in `cues.json` (read by `sound_bed.py`).
   - `voice` and `host_bookends` → which WAVs the chapters list in `episode.json` holds (see SKILL.md, Narration).
   - `thumb_layout` → `thumbs.py` specs.

## Rotation rules (from styles.json)

| Decision | May not repeat |
|---|---|
| theme | any of the last 3 episodes |
| structure, opening, reconstruction, map_style, sound_mood, thumb_layout | the previous episode |
| length, voice, host_bookends, perspective, set_piece | no rule (set_piece is new every time by definition) |

## Matching choices to stories

- **Structure.** `latest_first` when the case moved recently (a report, a ruling, an arrest). `one_evidence` when one object carries the case (an envelope, a radio log, an autopsy). `two_accounts` when there is a clear official version to test. `chronological` when the order of events is the mystery.
- **Reconstruction.** `silent_film` for journeys, streets and arrivals. `newspaper` when the press is part of the story (a journalist, a cover-up in print, a famous headline). `courtroom_sketch` for trials, inquiries, panels and testimony. `none` when the board carries it.
- **Map.** `geographic` for stories across countries. `sketch` for one town, street or site. `transit` for a timed journey (flights, convoys, last movements).
- **Sound.** `piano` for grief and a life cut short. `pulse` for last hours and procedure. `ambient` for landscapes and long aftermaths. `drone` for menace and conspiracy.
