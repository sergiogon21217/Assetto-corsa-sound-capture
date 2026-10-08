# Processing tools

Turn the cabin recordings into an engine loop set for FMOD. Needs Python 3 with
`numpy` and `scipy` (`pip install -r requirements.txt`).

```
# 1. put the session's WAVs in recordings/<date>/RecForge/ (git-ignored)
# 2. list the sources in processing/<date>.json (see processing/2026-10-08.json)
python tools/build_loops.py processing/2026-10-08.json   # loops + manifest.csv
python tools/pitch_table.py loops/2026-10-08             # fmod_table.csv + FMOD_TABLE.md
python tools/preview.py loops/2026-10-08 recordings/2026-10-08/RecForge   # listening previews
```

| File | What it does |
|---|---|
| `rpm.py` | Tracks rpm from the audio. The main engine tone is rpm / 30 Hz; each frame scores candidate rpms by their harmonics, and a Viterbi pass picks the smoothest path. `refine()` / `local_track()` give ~0.1 % precision on steady holds. `python tools/rpm.py file.wav` prints a time,rpm CSV. |
| `loops.py` | `flatten()` re-times a stretch of audio so the engine runs at exactly one rpm (works on sweeps and drifting holds). `make_loop()` picks a whole-number-of-cycles loop length by autocorrelation and crossfades the loop point. |
| `build_loops.py` | Runs the session config: `steady` holds give one loop each, `sweep` pulls/coast-downs give one loop per grid rpm, `free` (limiter) gives one unaligned loop. Keeps the best loop per rpm and smooths levels across rpm (gain in `manifest.csv`). |
| `pitch_table.py` | Equal-power volume and pitch (semitones) automation points per loop for the `rpms` parameter. |
| `preview.py` | Plays the loops along rpm paths with the same crossfade rules, and re-synthesises a real pull and coast-down to compare against the recording. |

Layers: `part` (steady holds, light load), `on` (full-throttle pull slices), `off`
(coast-down slices), `limiter`.
