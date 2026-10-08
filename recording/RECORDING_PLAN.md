# Kona N recording plan (cabin-only, private road)

The exact list of what to record, where, and with what, for the Assetto Corsa
sound bank described in [`../PLAN.md`](../PLAN.md).

**Capture setup decided:**
- Everything recorded **inside the car**. No exterior microphones; the exterior sound
  (`*_ext` events) is derived from the cabin recordings afterwards (§9).
- **Normal drive mode**, **ESG (sound enhancer) off**.
- On a **straight private road**. No dyno, so no dyno roller/fan whine, but also no way
  to hold full throttle at a fixed rpm (§1).

The machine-readable shot list is [`shotlist.csv`](shotlist.csv) (33 takes). The printable
version is [`shotlist_checklist.pdf`](shotlist_checklist.pdf).

---

## 1. Method: what a road can and can't give

AC's engine sound is built from **loops at fixed rpm**, in on-throttle and off-throttle
sets. On a flat road:

| Layer | How it's captured | Why |
|---|---|---|
| **Full load (ON)** | **Slow WOT pulls** in a high gear, sliced at each grid rpm afterwards | The engine can't be held at a fixed rpm at WOT without a dyno. A high gear makes the rpm rise slowly |
| **Off-throttle (OFF)** | **Coast-downs** in gear | Engine braking in a high gear slows the decay, the same as on a dyno |
| **Part load** | **Truly steady**: drive at constant speed so rpm is fixed | The one layer a road gives cleanly; it also helps the ON/OFF crossfade |
| Idle, shifts, lift-offs, whine | As before | |

**How the sweeps become loops:** the processing tools track the rpm through each pull
(from OBD plus the engine tone), resample a short slice around each grid rpm so its pitch
is flat, and then cut it to a whole number of engine cycles. This works well if the sweep
is slow. **Aim for 500 rpm per second or less**: at that rate a 0.25 s slice only moves
about 125 rpm, which is easy to flatten.

**Gear choice is a trade-off:**
- Higher gear: slower sweep (better loops), but more speed, so more wind and tyre noise in
  the cabin, and more road needed.
- Lower gear: less road and less wind noise, but faster sweeps.

Pick gears using the test run in §5. Splitting the range into a **low pull (1000→4000)** and
a **high pull (3000→limiter)** means each pull can use the best gear for its part of the range.

**Don't hold rpm under load with the brake** (throttle against the left foot). It overheats
the brakes and the DCT clutch quickly, and the brake noise gets into the recording.

---

## 2. Car settings (every take)

- **Drive mode: Normal.** Use the same mode for every take, because the exhaust valve,
  throttle mapping and shift behaviour change between modes.
- **ESG off.** Check it in the settings menu before starting, and after any restart.
- **Manual/paddle shifting**, so the gearbox holds the gear through each pull.
- A/C and fan off, radio off, **windows and sunroof closed**, phone on silent, nothing loose
  in the cabin (rattles end up in every loop).
- Warm engine (oil at temperature) before any take. Tyre pressures normal.
- **Same direction for every run** if there's any wind or slope, so takes match. Note the
  direction in the log.

---

## 3. Microphones (sources)

| Channel | Mic | Placement | Feeds |
|---|---|---|---|
| **CAB** (required) | Stereo handheld recorder (Zoom/Tascam type) or a phone with a decent app, WAV | Clamped (not held) between the front seats at driver's head height, pointing forward | `engine_int`, `gear_int`, `transmission`, and the base of all `*_ext` |
| **FWL** (optional, recommended) | Second recorder or phone | Passenger footwell, close to the firewall, on a foam pad (not touching metal) | Darker, more engine and less wind; a better base for the exterior version (§9) |
| **OBD** | OBD-II dongle + logging app (OBDLink + Torque/RealDash or similar) | OBD port | rpm, pedal %, boost/MAP, gear, speed, intake temp at ≥ 10 Hz. **Essential for road sweeps**: it gives the rpm curve the slicing uses |

Recorder settings: **48 kHz, 24-bit** (or 32-bit float), WAV. Not MP3, and not a phone's
default voice-memo format.

Set gains on the first `LIMIT` take so peaks land around **−6 dBFS**, then **don't change
them**. If you use two recorders plus the OBD logger, **clap at the start of every run**
and blip the throttle once at idle: the clap syncs the recorders and the blip lines the
audio up with the OBD rpm trace.

---

## 4. The rpm grid

The same 19 points as before. For the pulls and coasts they're **slice centres** (where
loops get cut from the sweeps); for the part-load layer they're **actual hold points**.

Points are spaced about **2 semitones** apart (ratio ≈ 1.12), so neighbouring loops never
need more than about ±1 semitone of pitch shift at a crossfade.

| rpm | Tier | Main tone (2nd order) Hz | 1 engine cycle (ms) |
|---:|:--:|---:|---:|
| 800 (idle) | A | 26.7 | 150.0 |
| 900 | B | 30.0 | 133.3 |
| 1000 | A | 33.3 | 120.0 |
| 1150 | B | 38.3 | 104.3 |
| 1300 | A | 43.3 | 92.3 |
| 1500 | B | 50.0 | 80.0 |
| 1700 | A | 56.7 | 70.6 |
| 1900 | B | 63.3 | 63.2 |
| 2150 | A | 71.7 | 55.8 |
| 2400 | B | 80.0 | 50.0 |
| 2700 | A | 90.0 | 44.4 |
| 3000 | B | 100.0 | 40.0 |
| 3400 | A | 113.3 | 35.3 |
| 3800 | B | 126.7 | 31.6 |
| 4250 | A | 141.7 | 28.2 |
| 4750 | B | 158.3 | 25.3 |
| 5300 | A | 176.7 | 22.6 |
| 5900 | B | 196.7 | 20.3 |
| 6500 | A | 216.7 | 18.5 |
| limiter | A | – | – |

- **Main tone** = rpm / 30 Hz (4-cylinder, 4-stroke). It's how the tools track rpm through
  a sweep, and how you can check any clip on a spectrogram.
- **Cycle** = 120 / rpm seconds, one full firing sequence. Loops are cut as whole cycles.
- **6500** assumes a limiter around 6,700–6,800 rpm. Adjust it if the mod's `engine.ini` or
  the real car says otherwise.
- **Tier A** points are every other point and are enough for a first working bank; **tier B**
  fills the gaps. For the sweeps this doesn't matter (every pull crosses every point), but
  for the part-load holds, do tier A first.

---

## 5. Test run (before recording)

One run with OBD logging only, to choose gears for your road:

1. From ~1000 rpm, WOT in **5th** (or the highest gear you'd consider). Note the rpm and
   speed when you reach the safe braking point. Note the sweep rate (rpm/s) in the log.
2. From ~3000 rpm, WOT in **4th**, then **3rd**. Which one reaches the limiter before the
   braking point?
3. Pick:
   - `PULL-LO` gear: the highest gear where 1000→4000 fits the road.
   - `PULL-HI` gear: the highest gear where 3000→limiter fits the road.
   - If neither 3rd nor 4th reaches the limiter, do the high pull in two halves
     (3000→5000, then 4500→limiter) and log it.
4. Check the cabin for wind whistle at the top speed. If it's loud, drop a gear.

---

## 6. Run order

All in Normal mode, ESG off, manual mode. Say the take ID out loud before each run
(e.g. "pull low, run two"), clap, blip, then go.

| # | Block | Takes | Notes |
|---|---|---|---|
| 0 | Noise | `NOISE-PARK`, `NOISE-ROLL` | Engine off parked; then rolling in neutral at speed (only if safe). Used to clean up wind/tyre noise |
| 1 | Idle | `IDLE` ×2 | 30 s each, stationary |
| 2 | Level check | `LIMIT` ×3 | First one sets the gains: lock them after. Skip if the gearbox upshifts at the limiter |
| 3 | Full-load pulls | `PULL-LO` ×4, `PULL-HI` ×4 | Smooth, full pedal, no pedal changes mid-pull. Let the engine and intake cool on the drive back |
| 4 | Coast-downs | `COAST-HI` ×4, `COAST-LO` ×3 | Lift fully, stay in gear, no brakes until the take ends |
| 5 | Part-load holds | `SS-PART-*` ×2 each (tier A first) | Constant speed, steady rpm for 8 s. Use 1st/2nd for the high-rpm points to keep the speed sensible |
| 6 | Reference | `PULL-REF` ×2 | Ordinary 2nd-gear pull, for A/B comparison later |
| 7 | One-shots | `UP-WOT`, `UP-PART`, `DOWN`, `LIFT`, `POP-N` (optional) | Reps per shift as in the shot list |
| 8 | Whine | `CRUISE-WHINE` ×2 | Steady cruise in 6th–8th, then coast |

Four pulls of each kind is deliberate: road takes vary (wind, gusts, a passing car), and
the best slice at each rpm can come from a different run.

---

## 7. What each take becomes

| FMOD event | Built from | Minimum usable set |
|---|---|---|
| `engine_int` | CAB: `IDLE`, slices of `PULL-LO`/`PULL-HI` (ON), `COAST-HI`/`COAST-LO` (OFF), `SS-PART-*`, `LIMIT` | 10 tier-A ON slices + 10 OFF slices |
| `engine_ext` | FWL (or CAB), the same takes, processed as in §9 | same |
| `turbo` | FWL/CAB: `LIFT` (whoosh); whistle from the pulls if it's audible | 2–3 lift-off variations |
| `gear_int` / `gear_ext` | `UP-WOT`, `UP-PART`, `DOWN` | 3 variations each |
| `backfire_int` / `_ext` | `LIFT` or `POP-N`, if any pops are captured | 4+ variations, or leave silent |
| `limiter` | `LIMIT` | 1 clean bounce loop |
| `transmission` | `CRUISE-WHINE` | 1 loop |
| `horn` | not recorded; keep the existing one | – |
| — (reference) | `PULL-REF` | For comparing the finished bank with reality |

---

## 8. Naming and the take log

Files: `<take_id>_r<rep>_<channel>.wav`, e.g. `PULL-LO_r2_CAB.wav`,
`SS-PART-3400_r1_FWL.wav`. OBD log: one CSV for the session (or one per run if the app
allows), e.g. `road_obd.csv`.

Take log columns (fill on paper or in the CSV while recording):
`take_id, rep, clock_time, gear, start_rpm, end_rpm, direction, IAT, keep(Y/N), notes`.

Put raw files in `recordings/road/` (git-ignored or Git LFS, because they're large) and
the OBD CSVs in `logs/`.

---

## 9. Building the exterior sound from cabin recordings

Reverb on its own won't make a cabin recording sound like it's outside. A cabin
recording differs from an exterior one mainly in **frequency balance**: the cabin adds
a low "boom" and the bodywork filters out the high exhaust rasp. So the processing order is:

1. **Start from the FWL loops** if you have them. Otherwise use the CAB loops.
2. **Clean the wind/tyre noise** using the `NOISE-ROLL` profile. Use gentle settings; heavy
   noise reduction leaves watery artefacts that loop audibly.
3. **EQ, remove the cabin:** high-pass around 40 Hz, then find the 1–3 cabin boom peaks in
   roughly 60–200 Hz (they stay at the same frequency whatever the rpm) and cut them 3–6 dB.
4. **EQ, add the outside:** a gentle lift around 1–4 kHz for exhaust rasp and presence, and a
   little high shelf. Use light saturation if it still sounds too muffled.
5. **Space last, and done in FMOD** rather than baked into the files: a short, mostly
   early-reflection reverb (outdoor / small-space type, low wet mix of about 10–20%) as an
   effect on the `engine_ext` event or the exterior bus. That keeps the loops clean (reverb
   tails baked into a loop click at the loop point) and lets you tune it in game.
6. Use the same EQ chain on `gear_ext` and `backfire_ext` so they match the engine.
7. Check outside the car in game (replay chase cam and a trackside camera) against a Kunos
   turbo FWD car at the same rpm.

---

## 10. Checklists

**Before the day**
- [ ] Mod's `engine.ini`: confirm idle and limiter rpm, and adjust the top grid point
- [ ] Permission for the private road; someone to keep the road clear
- [ ] Recorder(s) set to 48 kHz / 24-bit WAV; batteries and spare SD card
- [ ] Clamp/mount for CAB; foam pad for FWL
- [ ] OBD logger tested (rpm, pedal, MAP/boost, gear, speed, IAT at ≥10 Hz)
- [ ] Printed checklist

**At the road**
- [ ] Walk or drive the road: braking point marked, nothing on the surface
- [ ] Test run done (§5); gears chosen and written on the checklist
- [ ] Normal mode, ESG off (check the menu), manual/paddle mode
- [ ] A/C, fan and radio off, windows and sunroof closed, cabin emptied of rattles
- [ ] Recorders mounted, not hand-held, and not touching trim that buzzes

**After each block**
- [ ] Listen back to one take on headphones: no clipping, no rattles, recorder still in place
- [ ] Log kept/rejected takes, gear and start/end rpm
- [ ] ESG still off and mode still Normal
