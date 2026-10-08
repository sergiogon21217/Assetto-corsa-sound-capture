# Handover: Kauai N sound mod

State as of 2026-10-08, for continuing in a local Claude Code session on the Windows PC
that has Assetto Corsa and FMOD.

- **Repo:** `sergiogon21217/Assetto-corsa-sound-capture`, branch `claude/kona-n-sound-mod-vi9tz6`
- **Target car:** `C:\Program Files (x86)\Steam\steamapps\common\assettocorsa\content\cars\hyundai_kauai_n`
  (the Hyundai Kona N, sold as "Kauai" in some markets)

## Decisions made (don't revisit without a reason)

- **Recording:** one phone (RecForge II, 48 kHz WAV) in the cabin, on a private road, with no
  dyno and no OBD logger. rpm is tracked from the audio.
- **N-mode recordings only (ESG on)** for both interior and exterior. Normal-mode files are
  kept but not used.
- **Interior** = cabin loops with gentle road-noise reduction. **Exterior** = the same loops
  plus exterior EQ, with reverb added in FMOD.
- **Engine events** use three tracks crossfaded by `throttle`: `off` (coast-down slices, with
  idle at the bottom), `part` (steady holds) and `on` (WOT pull slices).
- **FMOD Studio 1.08.12 exactly.** AC rejects banks built with 1.09 or newer. Start from the
  Kunos SDK project in `assettocorsa\sdk\audio\`.

## Done

| What | Where |
|---|---|
| Recording plan, shot list, PDF checklist | `recording/` |
| Session inventory (file → role, mode, measured rpm) | `recording/sessions/2026-10-08_inventory.csv` |
| Processing pipeline (rpm tracking, loop cutting, one-shots, int/ext processing, FMOD staging) | `tools/` (see `tools/README.md`) |
| 43 loops + manifest + crossfade/pitch table | `loops/2026-10-08/` (int/ and ext/ versions inside) |
| One-shots: 2 upshifts, 4 crackle bursts, 8 pops, 1 lift-off whoosh | `loops/2026-10-08/oneshots/` |
| Audio staged per FMOD event, plus the instrument placement list | `fmod/Assets/hyundai_kauai_n/`, `fmod/instruments.csv` |
| FMOD build guide for AC | `fmod/FMOD_BUILD.md` |
| FMOD 1.08 probe script (read-only) | `fmod/scripts/kona_probe.js` |

## Next steps

1. **Read the car's `data\engine.ini`:** idle rpm, limiter rpm, and turbo `MAX_BOOST`.
   - The loops cover ~900 to 6,750 rpm.
   - If the limiter is above ~7,000, raise `RPMS_MAX` and the top loop's range in
     `tools/stage_fmod.py`, then rerun it.
   - If `data` is packed into `data.acd`, Content Manager can unpack it if the car is yours.
2. **Check the car's existing `sfx\` folder,** if any (which bank and GUIDs it ships), and back
   it up before replacing anything.
3. **FMOD setup:** follow `fmod/FMOD_BUILD.md` §1. Copy the SDK project, duplicate the
   template car folder as `hyundai_kauai_n`, create the bank `hyundai_kauai_n`, and import
   `fmod/Assets/hyundai_kauai_n`.
4. **Run the probe** (`FMOD_BUILD.md` §2) on `engine_ext` and read the console output. It shows
   the real FMOD 1.08 object names (tracks, sounds, parameters, autopitch, automation).
5. **Write `fmod/scripts/kona_build_engine.js`** using those names. It should read
   `fmod/instruments.csv` (or a JS copy of it) and build `engine_int` and `engine_ext`:
   - three tracks;
   - 86 looping instruments placed on `rpms` with fades;
   - AutoPitch with the root rpm from the CSV;
   - throttle volume automation on each track (table in `FMOD_BUILD.md` §3);
   - a reverb on `engine_ext`.

   Use ES5 only (no `let`, `const` or arrow functions). Test on a copy of the project.
6. **Do the other events by hand** (`FMOD_BUILD.md` §4): gear, backfire, limiter, turbo blow-off.
7. **Build, export GUIDs and install** into `hyundai_kauai_n\sfx\` (§5). Test with Content
   Manager Quick Drive, restarting the session after each rebuild (§6).

## Known gaps

- **Missing sounds:** no downshift recording (upshifts are reused, quieter, for `state` 0), no
  turbo whistle/spool, and no transmission whine. The template's sounds are kept for those.
- **High frequencies:** the phone recorded almost nothing above ~4 kHz.
- **Weakest stretch:** full-throttle loops from 1,500 to 2,700 rpm come from one fast pull
  (`1k 4k.wav`). Listen for warble there.

## Rebuilding the audio

The raw recordings are **not** in git. They're in the 7z archive on Google Drive (RecForge
folder, 31 WAVs). Extract the archive to `recordings\2026-10-08\RecForge\`, then:

```
pip install -r requirements.txt
python tools/build_loops.py processing/2026-10-08.json
python tools/pitch_table.py loops/2026-10-08
python tools/oneshots.py processing/2026-10-08.json
python tools/process.py processing/2026-10-08.json
python tools/stage_fmod.py processing/2026-10-08.json
python tools/preview.py loops/2026-10-08/ext recordings/2026-10-08/RecForge
```
