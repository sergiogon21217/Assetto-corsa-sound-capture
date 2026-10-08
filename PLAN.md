# Plan: real recorded sound for the Hyundai Kona N in Assetto Corsa

Goal: replace the sound on a Kona N car mod with an FMOD bank built from
recordings of a real Kona N, so it sounds right inside the car, outside it, on
throttle, off throttle, on upshifts and with the N-mode pops.

The Kona N is not a Kunos car, so this assumes a Kona N **car mod** already
exists (its folder is referred to below as `content/cars/<kona_n>/`). If you
don't have one, you'll need to build or find a car first. Sound is a separate
layer on top.

---

## 0. Reference facts about the car

| Item | Value | Why it matters |
|---|---|---|
| Engine | 2.0 L Smartstream G2.0 T-GDi inline-4, turbocharged | 4-cylinder firing order: the main engine tone is the **2nd engine order** (f = rpm / 60 × 2) |
| Output | ~280 PS, ~392 Nm (N Grin Shift gives a short overboost) | Load and turbo layers |
| Idle / limiter | about 800 rpm idle, limiter around 6,700–6,800 rpm (**read the exact values from the mod's `engine.ini`**) | Sets the range of the `rpms` parameter |
| Gearbox | 8-speed wet dual-clutch (N DCT) | Fast upshifts with a spark cut, so you need "fart"/shift one-shots |
| Exhaust | Variable exhaust valve; pops and crackles in N mode | Separate backfire layer, plus closed-valve vs open-valve character |
| Cabin | Electronic Sound Generator (ESG) plays synthetic engine sound through the speakers | Interior recordings will include it unless you turn it off in the N settings. Decide which you want |
| Sister cars | i30 N, Veloster N and Elantra N use closely related 2.0 T-GDi engines | Fallback source material if you can't get the right Kona N recordings |

EU-market cars may have a gasoline particulate filter, which softens the crackles.
Write down which market your recording car is from.

---

## 1. How AC sound works (what we're building)

- AC uses **FMOD Studio 1.08.xx**. You must use that exact major/minor version.
  Banks built with newer FMOD versions won't load.
- Each car ships:
  - `content/cars/<kona_n>/sfx/<kona_n>.bank`
  - `content/cars/<kona_n>/sfx/GUIDs.txt` (from *File → Export GUIDs* in FMOD)
- Start from the **Kunos AC sound SDK FMOD project** (it ships with the AC SDK /
  "Assetto Corsa - Car SFX" template). It already has the right event paths,
  buses and parameters. Rename the `cars/<name>` folder to the car's folder name.
- Main events (check the exact list in the SDK template):
  - `event:/cars/<kona_n>/engine_ext` and `engine_int`: looped, driven by the
    `rpms` and `throttle` parameters
  - `gear_ext` / `gear_int`: one-shots on each shift
  - `backfire_ext` / `backfire_int`: pops on lift-off
  - `turbo`: blow-off, spool and whistle
  - `transmission`: gear whine, driven by speed or rpm
  - `limiter`: optional, if the template has it
  - `bodywork`, `horn`
- Tyres, wind, skids and collisions come from the common AC banks, so leave them alone.

---

## 2. Capture: what to record

> The detailed version (exact rpm grid, channels, run order, shot list) is in
> [`recording/RECORDING_PLAN.md`](recording/RECORDING_PLAN.md) and
> [`recording/shotlist.csv`](recording/shotlist.csv).

### 2.1 Gear
- 3–4 recorders or channels, time-synced with a clap or slate at the start of every take:
  1. **Exhaust**: dynamic mic (e.g. SM57-type) 30–50 cm behind the tip, off-axis
     to the exhaust flow, wind protection. Use a pad or low gain because it will clip.
  2. **Engine bay**: lavalier or small-capsule mic taped away from heat and the belt.
     This gives the turbo and induction sounds.
  3. **Cabin**: stereo pair or a Zoom-style recorder at driver's head height.
  4. (Optional) **External drive-by / chase**: for replays and the external camera.
- Record at 48 kHz / 24-bit WAV (32-bit float if the recorder supports it).
- **No OBD logger (decided).** Each sample's rpm is tracked from the engine tone in
  the audio (§3, step 2), with spoken slates and a paper take log for context.
- Action camera: optional, but it helps with syncing and with checking what was happening.

### 2.2 Takes (best to worst)
1. **Dyno, steady-state** (ideal): hold rpm in about 250–500 rpm steps from idle to
   the limiter, each for 5–10 s, at **full load** and at **zero load / coast**.
   Do this in one gear, usually 4th.
2. **Dyno or road ramps**: slow full-throttle pulls idle→limiter, and slow
   off-throttle coast-downs limiter→idle (12–20 s each).
3. **Road, legal location / track day**: WOT pulls in 2nd–3rd, lift-offs,
   upshifts in N mode (you need the DCT spark-cut "brap"), downshift blips,
   launch control, idle, cold start, and closed-valve vs open-valve exhaust.
4. **Extras**: 5+ clean pops/crackles, turbo blow-off/flutter on lift,
   gear whine at steady cruise, horn, door (optional).

**Decided:** record with **one phone in the cabin** (RecForge II), in **two passes with
the same rpm samples**: **Pass A** in Normal mode with the ESG off (source for the interior
sound) and **Pass B** in N mode with the ESG on (source for the exterior sound, after EQ
plus a light reverb in FMOD; see `recording/RECORDING_PLAN.md` §10). Recording is on a **straight private road**
(no dyno): full-load loops come from slow WOT pulls and off-throttle loops from
coast-downs, both sliced and pitch-flattened at each grid rpm; part-load loops are
recorded as true constant-speed holds.

**Decided after the 2026-10-08 session:** the bank is built from the **N-mode (ESG on)
recordings only**, for both the interior and exterior sounds. The interior uses the cabin
recordings as they are; the exterior uses the same loops through the processing in
`recording/RECORDING_PLAN.md` §10. Normal-mode files are kept but not used. Which file
feeds what is in `recording/sessions/2026-10-08_inventory.csv`.

### 2.3 If you can't get a car
Using other people's recordings (YouTube, sound libraries) is only OK with
permission. Credit the source and don't redistribute ripped audio.
The i30 N and Veloster N are fair fallbacks (§0).

---

## 3. Processing: turn recordings into loops

Suggested tools: Reaper or Audacity for editing, plus the Python scripts planned
for this repo (§6).

1. **Sync** all channels (and any dash video) to the slate clap.
2. **Tag rpm** for every region:
   - from audio: a spectrogram/FFT peak of the 2nd engine order,
     `rpm = f_peak × 30`. At 3,000 rpm that's a 100 Hz fundamental.
3. **Cut loops**: from steady-state takes, or from short windows of the road
   sweeps after resampling each window to a constant pitch using the tracked rpm, take 0.5–2 s. Cut at zero crossings, and cut a
   whole number of combustion cycles (1 cycle = 120 / rpm seconds for all 4 cylinders) so
   the loop doesn't "tick".
   - Target set: about 10–16 loops per layer, for example 800 (idle), 1000, 1500, 2000,
     2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, limiter.
   - Layers: `ext_on` (exhaust, load), `ext_off` (exhaust, coast),
     `int_on`, `int_off`, plus engine-bay turbo/induction for both.
4. **Clean**: high-pass under ~30 Hz, remove wind thumps, gentle
   de-noise only. Don't compress the dynamics much, because AC mixes them.
5. **Level-match** loops within each layer so crossfades don't pump.
   Keep ext and int at their real relative loudness and adjust later in FMOD.
6. **One-shots**: cut the upshift spark-cut, downshift blip, pops (several
   variations), blow-off (2–3 variations) and limiter bounce.
7. Name files predictably, e.g. `ext_on_3500.wav`, `int_off_2000.wav`.

---

## 4. FMOD build

1. Install **FMOD Studio 1.08.xx** and open the AC SDK car template.
2. Rename the car event folder to `<kona_n>`. It must match the car folder name exactly.
3. `engine_ext` / `engine_int`:
   - Parameter `rpms` (0 → a bit above the limiter) and `throttle` (0–1).
   - Place each loop at its recorded rpm on the `rpms` parameter sheet as a
     looping single sound. Neighbouring loops overlap and crossfade (volume automation).
   - Pitch automation on each instrument: 0 semitones at its own rpm and
     `12 × log2(rpm / rpm_rec)` at the edges of its region.
     The processing script (§6) can output this table.
   - Layer on-load vs off-load: `throttle` crossfades the `_on` and `_off` sets.
4. `backfire_*`: multi-instrument with the pop variations, random pitch ±1–2 st.
5. `turbo`: spool/whistle loop pitched by rpm/boost, plus blow-off
   one-shot, if the template drives it.
6. `gear_*`: DCT upshift crack/fart, a slight random pick.
7. `transmission`: low-level whine, mostly for the interior.
8. Mixing: compare with a well-regarded Kunos FWD turbo car at the same rpm
   (e.g. a Kunos hot hatch). Match loudness on the ext bus and int bus so the
   Kona isn't much louder or quieter than the rest of the grid.
9. Build → Desktop, then **File → Export GUIDs**. Copy `<kona_n>.bank` and
   `GUIDs.txt` into `content/cars/<kona_n>/sfx/`.

---

## 5. Test in game

- Content Manager → the car → drive a practice session. Also check **showroom-free
  testing** with the in-game replay camera outside the car.
- Checklist:
  - [ ] Idle is steady, no loop click
  - [ ] Slow WOT pull 1,000 → limiter: no audible seams or pitch jumps
  - [ ] Slow coast-down: the off-throttle layer engages cleanly
  - [ ] Throttle tapping at a fixed rpm: on/off crossfade isn't choppy
  - [ ] Upshifts and downshifts trigger, and pops happen on lift
  - [ ] Interior vs exterior: relative level feels right against a Kunos car
  - [ ] Limiter matches the real car (bounce rate/tone)
  - [ ] No bank errors in `Documents/Assetto Corsa/logs/log.txt`
- Iterate between §3 and §4 on any seams you find.

---

## 6. What this repo contains

```
recording/         # recording plan, shot list, checklist, session inventories
recordings/        # raw takes (git-ignored)
processing/        # per-session config: which file is which loop source
tools/             # processing pipeline (see tools/README.md)
  rpm.py           # rpm vs time from audio
  loops.py         # pitch-flattening + whole-cycle loop cutting
  build_loops.py   # session config -> loops + manifest (with level smoothing)
  pitch_table.py   # crossfade/pitch automation values for FMOD
  preview.py       # listen to the loop set without FMOD
loops/<session>/   # processed loops (output) + manifest + FMOD table
fmod/              # FMOD 1.08 project (from the AC SDK template) - next
build/             # <kona_n>.bank + GUIDs.txt ready to drop into the car - next
```

Milestones:
1. **M1: prototype**: pipeline built and first loop set made from the 2026-10-08
   N-mode recordings (done); next, a working bank in game.
2. **M2: capture day**: 2026-10-08, partial (see `recording/sessions/`).
3. **M3: full bank**: all layers, one-shots and a mixing pass.
4. **M4: release**: README credits (mod author, recording sources), install
   instructions, and permission from the car-mod author to ship the sound with
   or for their car.

---

## 7. Risks / open questions

- **Which Kona N mod?** Folder name, `engine.ini` rpm limits and whether the
  author allows sound replacements. This needs to be answered first.
- **Road-only capture (decided).** Sweeps instead of steady holds, plus wind/tyre
  noise at speed. Workable with slow sweeps, rpm tracked from the audio and a rolling noise
  profile, but processing has to pitch-flatten each slice before looping.
- ~~**ESG in the cabin.**~~ Decided: both. ESG off (Normal mode) for the interior, ESG on (N mode) as the exterior source.
- **FMOD 1.08 availability.** Old versions are downloadable from the FMOD site
  archive with a free account.
- **Legal/safety**: record WOT pulls only on the closed private road, with it kept clear.
