# Engine guide

## board_engine.py
- **Coordinates:** world space is `WW×WH` (5000×4100). The camera maps world to screen through `world_M` (centre, zoom, rotation). Cards store pixels at `R=2` per world unit.
- **Data blocks to edit per video:**
  - `IMG`: asset paths.
  - `build_bg()`: background colour and the optional map placement (`MAP(x,y)` converts map-image coordinates in the 684×528 reference space into world coordinates; adjust the resize and offset for a new map).
  - `K`: camera keys `(t, cx, cy, zoom, rot)`. Use pairs: a short move key, then a long slow drift key. Interpolation is eased, with zoom in log space.
  - `TAGS`: `(world anchor, text, t0, screen offset)`. They type on at 22 chars/s, fade at t0+7, and all return for the finale (`t > 85.3`; change this per video).
  - `LINES`: red strings `(A, B, t0, dur, "string")`.
  - `ELLS`: hand-drawn circles `(centre, rx, ry, t0, dur)`.
  - `ROUTE`: a dashed path. The headline underline is in `draw_overlays`.
  - `screen_overlays()`: the year card window, the thesis window and the end title (all hard-coded times; edit them).
  - `build()`: `add(make_card(path, width_world), cx, cy, rot, appear_t)`, `make_paper(lines, w, h)` for typed notes, and `make_stamp(text)`.
  - Shakes and flashes: the `for st in (...)` lists inside `render`.
- **Modes:** `stills t1,t2,...` writes `stills.mp4` (one frame per timestamp); `full START END out.mp4` renders a frame range.
- Frames are **BGR**. Specify background colours in BGR.

## vintage_engine.py
- `T0, T1`: the insert range in seconds (frame-aligned). `S2`: when the street scene starts.
- `map_scene(t)`: schematic map. Edit the roads, labels, `PATH` (the car route), the reveal labels and the red circle.
- `street(t)`: side view. Uses `car()` and `figure(d, x, y, t, k, col, arm, scale)`, where `arm` goes from 0 (down) to 1 (pointing forward). Time the subject's step and arm raise to land before the impact time.
- `intertitle(t)`: text card.
- `frame(fi)`: chooses the scene, applies twos, `film()`, the impact flash (the hard-coded `69.25`; change it) and the iris wipes.
- Run `python3 vintage_engine.py stills 64.0,66.0,...` to check, then `python3 vintage_engine.py full` (renders frames `round(T0*30)` to `round(T1*30)` into `vintage.mp4`, or into `$KAZ_VOUT` when set).

## Resolution layer (hd.py)
- Both engines draw on-screen elements in 1920x1080 design coordinates. `KAZ_SCALE` sets the real pixel size: unset or `1` gives 1920x1080 (byte-identical to the pre-layer engines), `1.3333333333` gives 2560x1440.
- Screen drawing: `d = SD(ImageDraw.Draw(img))` and `SFont(path, size)`. `getbbox`/`getlength` answer in design units, so centring maths is unchanged. New screen images use `Image.new(mode, (PXW, PXH))`; a small screen sprite is `int(w*KS) x int(h*KS)` and is pasted at `int(x*KS), int(y*KS)`.
- Screen arrays: grain, vignette and glow grids are `PXH x PXW`; build coordinate grids as `xx = np.arange(PXW)/KS` so formulas stay in design units. Pixel shifts (`np.roll`, gate weave, scratches, blur radii) are multiplied by `KS`.
- World space is untouched: `world_M` is multiplied by `KS`, so cards, maps and the background are warped straight to the output size. Never wrap card drawing in `SD`.
- `KAZ_CRF` and `KAZ_PRESET` set the chunk encode; `KAZ_ASSETS` is the project folder on the Mac.

## Performance
1080p board frames take about 0.15–0.3 s each on one core; 1440p about 1.8x that, with about 2.7 GB of memory per board process. Split across cores. At 1440p the grain makes constant-quality encodes huge (about 160 Mbps at CRF 18), so the master uses a 20 Mbps cap. Encode the master at CRF 18, then deliver at CRF 24 (about 90 MB per 90 s).
