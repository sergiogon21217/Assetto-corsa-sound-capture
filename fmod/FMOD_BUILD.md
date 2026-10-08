# Building the Kauai N sound bank in FMOD

Step-by-step, on Windows, for the car `hyundai_kauai_n`
(`C:\Program Files (x86)\Steam\steamapps\common\assettocorsa\content\cars\hyundai_kauai_n`).
The audio is ready in `fmod/Assets/hyundai_kauai_n/`, and `fmod/instruments.csv` says where
every file goes. Items marked ⚠ come from community
sources and haven't been confirmed against Kunos's own documentation.

## 0. What you need

- **FMOD Studio 1.08.12 exactly** (fmod.com/download, free account, pick 1.08.12 from the
  version list). AC checks for this version; banks built with 1.09 or newer don't load.
  If FMOD ever offers to *upgrade* the project, you're on the wrong version: cancel.
- **The Kunos sound SDK**, installed with the game: `steamapps/common/assettocorsa/sdk/audio/`
  (an example FMOD project plus *AC Audio Pipeline 1.9.pdf*).
- **The car folder name: `hyundai_kauai_n`.** Everything below writes it as `<car>`. The bank
  (`hyundai_kauai_n.bank`) and the event folder (`event:/cars/hyundai_kauai_n/...`) must use
  exactly this name.
- **The mod's idle and limiter rpm** from its `engine.ini` (the real car: idle ~900 in N
  mode, limiter ~6,750).

## 1. Set up the project

1. Copy the SDK's FMOD project folder somewhere else and work on the copy, never the original.
2. Open the copied `.fspro` in FMOD Studio 1.08.12.
3. In the **Events** browser, find the template car folder under `cars/` (⚠ probably `tatuusfa1`).
   Right-click it, **Duplicate**, and rename the copy to `<car>`.
4. In the **Banks** browser, create a bank named exactly `<car>`. Select all events in
   `cars/<car>/`, right-click, **Assign to Bank** `<car>`, and remove them from the template's
   bank.
5. Drag the folder `fmod/Assets/hyundai_kauai_n` from this repo into the **Assets** browser.

## 2. (Optional, recommended) Run the probe

FMOD 1.08's scripting names aren't documented online, so a build script can't be written
safely from here. The probe reads them from your copy of the template:

1. Copy `fmod/scripts/kona_probe.js` into a `Scripts` folder next to your `.fspro` file.
2. In FMOD: **Scripts → Reload**.
3. Select `cars/<car>/engine_ext` in the Events browser, then **Scripts → Kona N → Probe selected event**.
4. Open **Window → Console**, copy all of the output and send it back.

With that output, a script can place all 86 engine loops automatically, so steps 3–4 below
become one click. Until then, they're manual.

## 3. Engine events: `engine_int` and `engine_ext`

Do `engine_int` first using `Assets/hyundai_kauai_n/engine_int/...`, then repeat for `engine_ext`
using `engine_ext/...`. AC drives two parameters on both: `rpms` (the engine rpm) and
`throttle` (0–1).

1. Open the event. Note how the template uses `rpms` and `throttle` and keep both parameters,
   with their names unchanged. If the `rpms` range ends below 7,500, extend it (⚠ the SDK
   suggests about twice the redline).
2. Delete the template's engine instruments. Keep the parameters and any master-track effects.
3. Create three audio tracks named `off`, `part` and `on`.
4. For each row of `fmod/instruments.csv` with this event:
   - Drag the file onto its track on the **rpms** parameter sheet.
   - Set its start to `rpms_start` and its length to `rpms_end - rpms_start`. Turn on **Loop**.
   - Drag the fade-in handle to `rpms_full` and the fade-out handle back to `rpms_full`, so
     the instrument fades in from the previous loop's rpm and out to the next one's. Use an
     S-curve or equal-power fade shape if offered.
   - **Pitch:** add **Modulation → AutoPitch** with root pitch = `autopitch_root` and
     minimum pitch at its lowest. AutoPitch scales pitch in proportion to `rpms / root`, which
     is exactly what the loops need. If AutoPitch isn't available in 1.08, automate
     the instrument's pitch from `loops/2026-10-08/fmod_table.csv` instead (same rpm points,
     pitch in semitones).
5. Crossfade the tracks with **throttle**, as automation on each track's volume. Starting points:

   | Track | throttle 0 | 0.3 | 0.6 | 0.9 | 1.0 |
   |---|---|---|---|---|---|
   | off | 0 dB | −∞ | −∞ | −∞ | −∞ |
   | part | −∞ | 0 dB | 0 dB | −∞ | −∞ |
   | on | −∞ | −∞ | −∞ | 0 dB | 0 dB |

   `off` has the idle loop at its bottom, so idle at zero throttle is covered.
6. **`engine_ext` only:** add an **FMOD Reverb** effect on the event's master track. Start with
   a short decay (about 0.6 s), early delay about 10 ms and wet level about −12 dB. This
   supplies the "outside" space that the cabin recordings lack.

## 4. The other events

| Event | What to do | Files |
|---|---|---|
| `gear_int` / `gear_ext` | Replace the template sound with a **Multi Instrument** (random) holding both upshifts. AC sets `state` 1 for upshifts and 0 for downshifts; no downshifts were recorded, so use the same multi for both, about 4 dB quieter for `state` 0. | `gear_int/upshift_*.wav`, `gear_ext/upshift_*.wav` |
| `backfire_int` / `backfire_ext` | A **Multi Instrument** (random) of the crackle bursts, plus an optional second multi of single pops at lower volume. Keep the template's `throttle` logic. | `backfire_*/crackle_*.wav`, `backfire_*/pop_*.wav` |
| `limiter` | Replace the template's loop with ours (Loop on). Keep the template's `decay` automation. | `limiter/limiter_loop.wav` |
| `turbo` | Keep the template's spool/whistle (none was recorded). Optionally replace its blow-off sound, driven by the `bov` parameter, with the lift-off whoosh. | `turbo/bov_lift_1.wav` |
| everything else | `horn`, `wind`, `bodywork`, `wheel`, `skid_*`, `gear_grind`, `tractioncontrol_*`, `transmission`, `door`: keep the template's for now. Don't delete these events. | – |

## 5. Build and install

1. **File → Build** (Desktop platform). Then **File → Export GUIDs**.
2. From the project's build output, take `<car>.bank` and `GUIDs.txt`.
3. **Back up** the car's existing `content\cars\hyundai_kauai_n\sfx\` folder (if it has one),
   then copy both files in, creating `sfx\` if needed.
   Never copy or overwrite `common.bank` or the master bank.
4. Restart the AC session to hear changes. Banks load per session, so start a new Quick Drive
   in Content Manager after every rebuild.

## 6. Test

- Idle: steady, no loop click. Slow full-throttle pull to the limiter: no seams or pitch jumps.
- Lift-off: the coast-down layer takes over smoothly, and crackles play.
- Shifts: the upshift crack plays on each shift.
- Inside versus outside camera: interior and exterior levels feel right next to a Kunos car.
- Too loud or too quiet overall: with CSP, add per-event multipliers in the car's `ext_config`
  under `[AUDIO_VOLUME]` instead of rebuilding.
- No bank errors in `Documents/Assetto Corsa/logs/log.txt`.

Shipping the mod: only ship a modified bank with permission from the car mod's author.
Changing a car's sound files can also cause checksum mismatches on multiplayer servers.
