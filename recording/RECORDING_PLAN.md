# Kona N recording plan (cabin-only)

The exact list of what to record, where, and with what, for the Assetto Corsa
sound bank described in [`../PLAN.md`](../PLAN.md).

**Capture setup decided:** everything is recorded **inside the car**, in
**Normal drive mode**, with the **ESG (sound enhancer) off**. There are no exterior
microphones. The exterior sound (`*_ext` events) is derived from the cabin
recordings afterwards (§8).

The machine-readable shot list is [`shotlist.csv`](shotlist.csv) (66 takes). Print it
or load it on a tablet on the day, and tick takes off as you go.

---

## 1. Sessions

| Session | Where | What it gives | Time needed |
|---|---|---|---|
| **Dyno** (primary) | Chassis dyno with load control (eddy-current or similar), 2WD/FWD | Steady-rpm engine loops: the core of the bank | 1.5–2 h booking (about 30–40 min of actual running) |
| **Road** | Quiet road, private road or track | Shifts, lift-offs, gearbox whine | 30–60 min |

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

## 2. Car settings (every take)

- **Drive mode: Normal.** Use the same mode for every take, because the exhaust valve,
  throttle mapping and shift behaviour change between modes.
- **ESG off.** Check this in the N/vehicle settings menu before starting, and check it
  again after any restart, because some settings reset.
- **Manual/paddle shifting**, so the gearbox holds 4th on the dyno and shifts when you choose.
- A/C and fan off, radio off, windows up, phone on silent, no loose items in the cabin
  (rattles end up in every loop).
- Warm engine (oil at temperature) before any take.

---

## 3. Microphones (sources)

| Channel | Mic | Placement | Feeds |
|---|---|---|---|
| **CAB** (required) | Stereo handheld recorder (Zoom/Tascam type) or a phone with a decent app, WAV | Clamped (not held) between the front seats at driver's head height, pointing forward | `engine_int`, `gear_int`, `transmission`, and the base of all `*_ext` |
| **FWL** (optional, recommended) | Second recorder or phone | Passenger footwell, close to the firewall, on a foam pad (not touching metal) | Darker, more engine and less cabin; a better base for the exterior version (§8), and some turbo sound |
| **OBD** | OBD-II dongle + logging app (OBDLink + Torque/RealDash or similar) | OBD port | rpm, pedal %, boost/MAP, gear, speed, intake temp at ≥ 10 Hz, for tagging every clip |

Recorder settings: **48 kHz, 24-bit** (or 32-bit float), WAV. Not MP3, and not a phone's
default voice-memo format.

Set gains once on the first `LIMIT` take so peaks land around **−6 dBFS**, then
**don't change them** for the rest of the day. The loops need the real loudness
differences between rpm points. If you use two recorders, **clap at the start and end of
every block** so they can be synced.

---

## 4. The rpm grid

Points are spaced about **2 semitones** apart (ratio ≈ 1.12), so neighbouring loops
never need to be pitch-shifted more than about ±1 semitone at a crossfade. That's
where pitch-shifting stops being audible.

- **Tier A** points are every other point, about 4 semitones apart. They're enough for a
  first working bank. Record them first.
- **Tier B** points fill the gaps. Record them if time and heat allow.

| rpm | Tier | Main tone (2nd order) Hz | 1 engine cycle (ms) | Cycles in a ~1 s loop |
|---:|:--:|---:|---:|---:|
| 800 (idle) | A | 26.7 | 150.0 | 7 |
| 900 | B | 30.0 | 133.3 | 7 |
| 1000 | A | 33.3 | 120.0 | 8 |
| 1150 | B | 38.3 | 104.3 | 10 |
| 1300 | A | 43.3 | 92.3 | 11 |
| 1500 | B | 50.0 | 80.0 | 12 |
| 1700 | A | 56.7 | 70.6 | 14 |
| 1900 | B | 63.3 | 63.2 | 16 |
| 2150 | A | 71.7 | 55.8 | 18 |
| 2400 | B | 80.0 | 50.0 | 20 |
| 2700 | A | 90.0 | 44.4 | 22 |
| 3000 | B | 100.0 | 40.0 | 25 |
| 3400 | A | 113.3 | 35.3 | 28 |
| 3800 | B | 126.7 | 31.6 | 32 |
| 4250 | A | 141.7 | 28.2 | 35 |
| 4750 | B | 158.3 | 25.3 | 40 |
| 5300 | A | 176.7 | 22.6 | 44 |
| 5900 | B | 196.7 | 20.3 | 49 |
| 6500 | A | 216.7 | 18.5 | 54 |
| limiter | A | – | – | – |

- **Main tone** = rpm / 30 Hz (4-cylinder, 4-stroke). Use it on a spectrogram to
  confirm the actual rpm of each clip.
- **Cycle** = 120 / rpm seconds, one full firing sequence of all 4 cylinders. Loops are
  cut as a whole number of cycles at the *measured* rpm. The column is only a guide.
- **6500** assumes a limiter around 6,700–6,800 rpm. If the mod's `engine.ini` or the
  real car says otherwise, move the top point to about 200–300 rpm below the limiter.
- **Idle**: use the car's real warm idle for the 800 row.

---

## 5. Dyno session: run order

All in Normal mode, ESG off, 4th gear in manual mode.

**Heat management:** run in blocks of **at most 5 WOT points**, then idle or cool down
for 2–3 minutes with the dyno fans on. Watch the intake air temperature on the OBD app,
and pause if it keeps climbing.

| # | Block | Takes (see `shotlist.csv`) | Notes |
|---|---|---|---|
| 0 | Setup | `NOISE-DYNO` | 30 s engine off, fans on (gives a noise profile for cleanup). Clap. |
| 1 | Idle | `IDLE` ×2 | 30 s each |
| 2 | Level check | `LIMIT` ×1 | Set gains here, then lock them |
| 3 | Reference ramps | `RAMP-ON` ×3 | Slow sweep; used later to A/B the finished bank |
| 4 | ON, tier A, low | `SS-ON-1000 1300 1700 2150 2700` | Stabilise, then **8 s hold**. 2 reps each. Cool down after |
| 5 | ON, tier A, high | `SS-ON-3400 4250 5300 6500`, `LIMIT` ×2 | Cool down after |
| 6 | OFF | `CD-OFF` ×4 **or** `SS-OFF-*` (motoring dyno only) | Coast-down in 5th: lift fully from 6500 and let the rollers spin down as slowly as possible |
| 7 | ON, tier B | `SS-ON-900 1150 1500 1900 2400` / `3000 3800 4750 5900` | Two blocks with a cool-down between |
| 8 | Optional | `SS-MID-*` (tier C) | Part-throttle layer, 6 s holds, one rep |
| 9 | Close | Clap | |

Each `SS-*` take: **say the take ID out loud** before it starts (e.g. "S S on thirty-four
hundred, take one"), then clap, stabilise the rpm, and hold. The spoken slate makes
sorting files trivial.

Rough WOT budget: 18 ON points × 2 reps × ~18 s ≈ **11 minutes of full load**, spread
over 4 blocks.

---

## 6. Road session: run order

Normal mode, ESG off. Do WOT runs only where it's legal and safe.

| Takes | Reps | How |
|---|---|---|
| `NOISE-ROAD` | 1 | 30 s parked, engine off |
| `UP-WOT` | 5 per shift | WOT to about 6,000 rpm, paddle upshift 1→2, 2→3, 3→4 |
| `UP-PART` | 5 | Around 3,500 rpm, part throttle |
| `DOWN` | 5 per shift | Braking downshifts 4→3, 3→2 around 3,000 rpm |
| `LIFT` | 6 | WOT to 4,000+ in 3rd, then lift sharply and stay off for 3 s. Captures the turbo whoosh and any pops |
| `POP-N` (optional) | 8 | **Only if you want pops in the mod.** Normal mode gives few or none, so this is the one exception: N mode with ESG still off. Leave it out for a fully "Normal" car |
| `CRUISE-WHINE` | 2 | 15 s steady cruise in 6th–8th, then 15 s coasting |

Not recorded: horn and drive-by (they need an exterior mic). Keep the horn from the
car mod's current bank or from the AC default.

---

## 7. What each take becomes

| FMOD event | Built from | Minimum usable set |
|---|---|---|
| `engine_int` | CAB: `IDLE`, `SS-ON-*`, `SS-OFF-*` or `CD-OFF` windows, `LIMIT` | 10 tier-A ON loops + 10 OFF loops |
| `engine_ext` | FWL (or CAB) loops, processed as in §8 | same loops |
| `turbo` | FWL/CAB: `LIFT` (whoosh); whistle from `SS-ON-*` if it's audible | 2–3 lift-off variations |
| `gear_int` / `gear_ext` | `UP-WOT`, `UP-PART`, `DOWN` (ext version processed as in §8) | 3 variations each |
| `backfire_int` / `_ext` | `LIFT` or `POP-N`, if any pops are captured | 4+ variations, or leave the event silent |
| `limiter` | `LIMIT` | 1 clean 2–3 s bounce loop |
| `transmission` | `CRUISE-WHINE` | 1 loop |
| `horn` | not recorded; keep the existing one | – |
| — (reference) | `RAMP-ON` | For comparing the finished bank with reality |

---

## 8. Building the exterior sound from cabin recordings

Reverb on its own won't make a cabin recording sound like it's outside. A cabin
recording differs from an exterior one mainly in **frequency balance**: the
cabin adds a low "boom" and the bodywork filters out the high exhaust rasp.
So the processing order is:

1. **Start from the FWL loops** if you have them (closer to the engine, less cabin
   resonance). Otherwise use the CAB loops.
2. **EQ, remove the cabin:** high-pass around 40 Hz, then find the 1–3 cabin boom
   peaks in roughly 60–200 Hz (they stay at the same frequency whatever the rpm)
   and cut them 3–6 dB.
3. **EQ, add the outside:** a gentle lift around 1–4 kHz for exhaust rasp and
   presence, and a little high shelf. Use light saturation if it still sounds too
   muffled.
4. **Space last, and done in FMOD** rather than baked into the files: a short,
   mostly early-reflection reverb (outdoor / small-space type, low wet mix of about
   10–20%) as an effect on the `engine_ext` event or the exterior bus. That keeps the loops
   clean (reverb tails baked into a loop click at the loop point) and lets you tune it
   in game.
5. Use the same EQ chain on `gear_ext` and `backfire_ext` so they match the engine.
6. Check outside the car in game: replay chase cam and a trackside camera,
   against a Kunos turbo FWD car at the same rpm.

The same EQ settings work for every loop, so it's a single preset you apply to all
of them.

---

## 9. Naming and the take log

Files: `<take_id>_r<rep>_<channel>.wav`, e.g. `SS-ON-3400_r1_CAB.wav`,
`LIFT_r3_FWL.wav`. OBD log: one CSV per session, e.g. `dyno_obd.csv`.

Take log columns (fill on paper or in the CSV while recording):
`take_id, rep, clock_time, actual_rpm, gear, IAT, keep(Y/N), notes`.

Put raw files in `recordings/<session>/` (git-ignored or Git LFS, because they're large)
and the OBD CSVs in `logs/`.

---

## 10. Checklists

**Before the day**
- [ ] Mod's `engine.ini`: confirm idle and limiter rpm, and adjust the top grid point
- [ ] Dyno booked; steady-state mode confirmed; motoring yes/no noted
- [ ] Recorder(s) set to 48 kHz / 24-bit WAV; batteries and spare SD card
- [ ] Clamp/mount for CAB; foam pad for FWL
- [ ] OBD logger tested (rpm, pedal, MAP/boost, gear, IAT at ≥10 Hz)
- [ ] Printed shot list

**In the car**
- [ ] Normal mode, ESG off (check in the menu), manual/paddle mode, 4th gear
- [ ] A/C, fan and radio off, windows up, cabin emptied of rattles
- [ ] Recorders mounted, not hand-held, and not touching trim that buzzes
- [ ] Recorder armed, OBD logging, clap

**After each block**
- [ ] Listen back to one take on headphones: no clipping, no rattles, recorder still in place
- [ ] Log kept/rejected takes
- [ ] ESG still off and mode still Normal
