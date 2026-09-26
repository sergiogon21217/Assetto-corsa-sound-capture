# Kona N recording plan

The exact list of what to record, where, and with what, for the Assetto Corsa
sound bank described in [`../PLAN.md`](../PLAN.md).

The machine-readable shot list is [`shotlist.csv`](shotlist.csv) (70 takes). Print it
or load it on a tablet on the day, and tick takes off as you go.

---

## 1. Sessions

| Session | Where | What it gives | Time needed |
|---|---|---|---|
| **Dyno** (primary) | Chassis dyno with load control (eddy-current or similar), 2WD/FWD | Steady-rpm engine loops: the core of the bank | 1.5–2 h booking (about 30–40 min of actual running) |
| **Track** | Track day, private road or closed course | Shifts, pops, blow-off, whine, horn, drive-by | 1–2 h |

The dyno matters because AC's engine sound is built from **loops at fixed rpm**.
On the road, a WOT pull goes up about 1,000 rpm per second, which is too fast to
cut clean loops. Only a dyno can hold the car at exactly 3,400 rpm under full load
for 8 seconds.

Ask the dyno shop two questions when booking:
1. *Can you hold a steady rpm under load (steady-state / constant-speed mode)?* You need yes.
2. *Can the dyno motor the car (drive the wheels with the engine off-throttle)?* This is rare.
   If yes, record the `SS-OFF` takes. If no, the off-throttle layer comes from
   coast-downs (`CD-OFF`) instead.

---

## 2. Channels (sources)

| Channel | Mic | Placement | Gain target | Feeds |
|---|---|---|---|---|
| **EXH** | Dynamic (SM57-type) + foam/fur windscreen | 30–50 cm behind the tailpipe, ~45° off the exhaust flow, out of the dyno fan blast | Peaks ≤ −6 dBFS at the limiter | `engine_ext`, `backfire_ext`, `gear_ext` |
| **BAY** | Lavalier or small condenser, heat-rated tape | Engine bay near the turbo inlet / intake pipe, away from the belt, fans and exhaust manifold | Peaks ≤ −6 dBFS on WOT | `turbo`, mixed into `engine_ext` for induction |
| **CAB** | Stereo pair or handheld stereo recorder | Driver headrest height, clamped (not held), windows up | Peaks ≤ −6 dBFS on WOT | `engine_int`, `gear_int`, `backfire_int`, `transmission` |
| **EXT** | Stereo recorder on a stand | Track only: roadside 5–10 m (drive-by), 3 m in front (horn) | Varies | `horn`, exterior mix reference |
| **OBD** | OBD-II dongle + logging app | OBD port | ≥ 10 Hz | rpm, pedal %, boost/MAP, gear, speed for tagging every clip |

Recorder settings: **48 kHz, 24-bit** (or 32-bit float), WAV, all channels on one
multitrack recorder if possible. If you use several recorders, **clap in view of all
mics at the start and end of every block** so you can check sync drift.

Set gains once at the limiter on the first WOT block, then don't change them.
The loops need the real loudness differences between rpm points.

---

## 3. The rpm grid

Points are spaced about **2 semitones** apart (ratio ≈ 1.12), so neighbouring loops
never need to be pitch-shifted more than about ±1 semitone at a crossfade. That's
where pitch-shifting stops being audible. Low rpm needs tighter spacing in rpm
because pitch is logarithmic.

- **Tier A** points are every other point, about 4 semitones apart. They're enough for a
  first working bank. Record them first.
- **Tier B** points fill the gaps. Record them if time and heat allow.

| rpm | Tier | Main tone (2nd order) Hz | 1 engine cycle (ms) | Cycles in a ~1 s loop | Step from previous |
|---:|:--:|---:|---:|---:|---:|
| 800 (idle) | A | 26.7 | 150.0 | 7 | – |
| 900 | B | 30.0 | 133.3 | 7 | 2.0 st |
| 1000 | A | 33.3 | 120.0 | 8 | 1.8 st |
| 1150 | B | 38.3 | 104.3 | 10 | 2.4 st |
| 1300 | A | 43.3 | 92.3 | 11 | 2.1 st |
| 1500 | B | 50.0 | 80.0 | 12 | 2.5 st |
| 1700 | A | 56.7 | 70.6 | 14 | 2.2 st |
| 1900 | B | 63.3 | 63.2 | 16 | 1.9 st |
| 2150 | A | 71.7 | 55.8 | 18 | 2.1 st |
| 2400 | B | 80.0 | 50.0 | 20 | 1.9 st |
| 2700 | A | 90.0 | 44.4 | 22 | 2.0 st |
| 3000 | B | 100.0 | 40.0 | 25 | 1.8 st |
| 3400 | A | 113.3 | 35.3 | 28 | 2.2 st |
| 3800 | B | 126.7 | 31.6 | 32 | 1.9 st |
| 4250 | A | 141.7 | 28.2 | 35 | 1.9 st |
| 4750 | B | 158.3 | 25.3 | 40 | 1.9 st |
| 5300 | A | 176.7 | 22.6 | 44 | 1.9 st |
| 5900 | B | 196.7 | 20.3 | 49 | 1.9 st |
| 6500 | A | 216.7 | 18.5 | 54 | 1.7 st |
| limiter | A | – | – | – | – |

- **Main tone** = rpm / 30 Hz (4-cylinder, 4-stroke: 2 firings per revolution). Use it
  on a spectrogram to confirm the actual rpm of each clip.
- **Cycle** = 120 / rpm seconds, one full firing sequence of all 4 cylinders. Loops are
  cut as a whole number of cycles at the *measured* rpm. The column is only a guide.
- **6500** assumes a limiter around 6,700–6,800 rpm. If the mod's `engine.ini` or the
  real car says otherwise, move the top point to about 200–300 rpm below the limiter.
- **Idle**: use the car's real warm idle, whatever it settles at, for the 800 row.

---

## 4. Dyno session: run order

Car setup for all dyno takes: warm engine (oil at temperature), **N mode**, exhaust
valve open, manual/paddle mode, **4th gear**, ESG **off** (N custom settings)
unless the take says otherwise, A/C off, windows up, phone silent.

**Heat management:** WOT holds heat-soak the engine and intercooler. Run in blocks of
**at most 5 WOT points**, then idle or cool down for 2–3 minutes with the dyno fans on. Log
intake air temperature if the OBD app shows it, and pause if it keeps climbing.

| # | Block | Takes (see `shotlist.csv`) | Notes |
|---|---|---|---|
| 0 | Setup | `NOISE-DYNO` | 30 s engine off, fans on. Clap. |
| 1 | Idle | `IDLE-N` ×2, `IDLE-N-ESG` (B) | 30 s each |
| 2 | Level check | `LIMIT` ×1 | Set all gains here, then lock them |
| 3 | Reference ramps | `RAMP-ON` ×3, `RAMP-ON-ESG` (B) | Slow sweep; used later to A/B the finished bank |
| 4 | ON, tier A, low | `SS-ON-1000 1300 1700 2150 2700` | Stabilise, then **8 s hold**. 2 reps each. Cool down after |
| 5 | ON, tier A, high | `SS-ON-3400 4250 5300 6500`, `LIMIT` ×2 | Cool down after |
| 6 | OFF | `CD-OFF` ×4 **or** `SS-OFF-*` (motoring dyno only) | Coast-down in 5th: lift fully from 6500 and let the rollers spin down as slowly as possible |
| 7 | ON, tier B | `SS-ON-900 1150 1500 1900 2400` / `3000 3800 4750 5900` | Two blocks with a cool-down between |
| 8 | Optional | `SS-MID-*` (tier C) | Part-throttle layer, 6 s holds, one rep |
| 9 | Close | Clap, `NOISE-DYNO` again if conditions changed | |

Each `SS-*` take: **say the take ID out loud** into CAB at the start (e.g. "S S on
thirty-four hundred, take one"). Then clap, then stabilise rpm, then hold. The
spoken slate makes sorting files trivial.

Rough WOT budget: 18 ON points × 2 reps × ~18 s (settle + hold) ≈ **11 minutes of
full load**, spread over 4 blocks.

---

## 5. Track session: run order

Car in N mode, exhaust valve open, ESG off unless noted. Only on a closed course or
track.

| Takes | Reps | How |
|---|---|---|
| `NOISE-TRACK` | 1 | 30 s engine off, all channels |
| `UP-WOT` | 5 per shift | WOT to about 6,000 rpm, paddle upshift 1→2, 2→3, 3→4. You want the DCT spark-cut "brap" |
| `UP-PART` | 5 | Around 3,500 rpm, part throttle |
| `DOWN` | 5 per shift | Braking downshifts 4→3, 3→2 around 3,000 rpm to catch the rev-match blip |
| `POP` | 10+ | WOT to 5,000+ in 3rd, then lift sharply and hold off-throttle for 3 s. Aim for **20+ clean individual pops** after editing |
| `BOV` | 6 | Same as a pop run, focused on BAY: turbo whoosh/flutter on lift. It may be subtle (recirculating valve) |
| `CRUISE-WHINE` | 2 | 15 s steady cruise in 6th–8th, then 15 s coasting. CAB only |
| `HORN` | 3 | Parked, EXT 3 m in front |
| `DRIVEBY` | 4 | EXT roadside: 2 at WOT, 2 at cruise. Mix reference only |

---

## 6. What each take becomes

| FMOD event | Built from | Minimum usable set |
|---|---|---|
| `engine_ext` | EXH (+ some BAY): `IDLE-N`, `SS-ON-*`, `SS-OFF-*` or `CD-OFF` windows, `LIMIT` | 10 tier-A ON loops + 10 OFF loops |
| `engine_int` | CAB: same takes | same |
| `turbo` | BAY: `SS-ON-*` (whistle per rpm), `BOV` | 4–5 whistle loops + 3 blow-off variations |
| `backfire_ext` / `_int` | EXH / CAB: `POP` | 8+ variations |
| `gear_ext` / `_int` | EXH / CAB: `UP-WOT`, `UP-PART`, `DOWN` | 3 variations each |
| `limiter` | `LIMIT` | 1 clean 2–3 s bounce loop |
| `transmission` | CAB: `CRUISE-WHINE` | 1 loop |
| `horn` | EXT: `HORN` | 1 |
| — (reference) | `RAMP-ON`, `DRIVEBY`, `*-ESG` | For comparing the finished bank with reality |

---

## 7. Naming and the take log

Files: `<take_id>_r<rep>_<channel>.wav`, e.g. `SS-ON-3400_r1_EXH.wav`,
`POP_r7_CAB.wav`. OBD log: one CSV per session, e.g. `dyno_obd.csv`.

Take log columns (fill on paper or in the CSV while recording):
`take_id, rep, clock_time, actual_rpm, gear, drive_mode, esg, IAT, keep(Y/N), notes`.

Put raw files in `recordings/<session>/` (git-ignored or Git LFS, because they're large)
and the OBD CSVs in `logs/`.

---

## 8. Checklists

**Before the day**
- [ ] Mod's `engine.ini`: confirm idle and limiter rpm, and adjust the top grid point
- [ ] Dyno booked; steady-state mode confirmed; motoring yes/no noted
- [ ] Batteries/SD cards ×2, spare cable, heat-rated tape, cable ties, windscreens
- [ ] OBD logger tested (rpm, pedal, MAP/boost, gear, IAT at ≥10 Hz)
- [ ] Ear protection for everyone near the car
- [ ] Printed shot list

**At the car**
- [ ] Mic cables routed away from the exhaust, belt, fans and dyno rollers
- [ ] EXH mic out of the direct exhaust gas stream and fan airflow
- [ ] Tyre pressures and car strapping done by dyno staff
- [ ] N mode, valve open, ESG off, 4th gear manual mode, A/C off
- [ ] Recorder armed, OBD logging, clap

**After each block**
- [ ] Listen back to one take on headphones: no clipping, no wind thumps, EXH mic still in place
- [ ] Log kept/rejected takes

---

## 9. If you can't record a real Kona N

In order of preference:

1. **Borrow a car**: Kona N / Hyundai N owners' clubs, forums, Discord servers,
   local N meets, or a Hyundai dealer with a demo car. Offer credit in the mod,
   and a dyno sheet makes a good trade for the owner's time.
2. **Sister cars**: the i30 N, Veloster N and Elantra N use closely related 2.0 T-GDi engines.
   Follow this same plan, but note the exhaust differs, so tune EXH by ear against Kona N videos.
3. **Commercial sound libraries**: search for Kona N / i30 N / Veloster N. Check that the
   licence explicitly allows use in a *freely distributed game mod*.
4. **Other people's videos/recordings**: only with written permission. YouTube audio is
   lossy-compressed and usually shows only ramps, so treat it as a **mixing reference**,
   not source material.
