# Reconstruction kits

Three kits live in the toolkit (`scripts/`, shipped to `_toolkit/`). An episode's insert script imports one, draws its scenes in 1920x1080 design coordinates, finishes every frame with the kit's treatment and renders its own frame range in `full` mode to `$KAZ_VOUT` (copy the `__main__` block from `example_silent_vint_hm.py`). Run each kit file directly to render a demo still.

| Kit | Look | Treatment | Scene change | Helpers |
|---|---|---|---|---|
| `recon_silent.py` | Sepia silent film, boiling lines on twos | `film(img, fi)` | `iris(out, r)`, `intertitle(...)` | `wline`, `wpoly`, `wrect`, `dashed`, `figure`, `car`, `sky` |
| `recon_newspaper.py` | Newsprint: invented masthead, headlines, columns, halftone photos, red pen | `press(img, fi)` | `wipe(prev, cur, u)` (page turn) | `page`, `masthead`, `headline`, `columns`, `photo`, `ring`, `underline`, `note`, `clipping`, `stamp` |
| `recon_sketch.py` | Courtroom-artist pastels on toned paper | `sketch_look(img, fi)` | `draw_on(prev, cur, u)` (artist's sweep) | `sheet`, `stroke`, `hatch`, `blob`, `person`, `bench`, `witness_box`, `table`, `window`, `caption`, `label`, `stamp` |

Rules for all kits:
- Label every reconstruction on screen as illustrative (each kit's `stamp()` does this). A recreated document is always marked "SCHEMATIC · NOT THE ORIGINAL DOCUMENT".
- Never recreate a real outlet's masthead, logo or a real document's exact layout; use invented names and the user's own screenshots.
- Sketched people are generic figures, never likenesses of real people; photos inside `recon_newspaper.photo()` are the user's own files.
- Red only for meaning. Keep violence non-graphic; cut away before impact.
- Newspaper: drawing to the cut needs both frames; render the outgoing and incoming scene, finish both with `press`, then `wipe`. Sketch: the same with `sketch_look` and `draw_on`.
- Animate on twos (`math.floor(t*12)/12`) for silent film and sketch; newspaper can run at 30 fps (type setting reads better smooth).
