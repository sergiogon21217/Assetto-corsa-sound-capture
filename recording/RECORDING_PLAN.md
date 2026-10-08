# Kona N recording plan (cabin-only, private road, two passes)

The exact list of what to record, where, and with what, for the Assetto Corsa
sound bank described in [`../PLAN.md`](../PLAN.md).

**Capture setup decided:**
- **One phone, inside the car** (RecForge II, §3). No footwell or exterior microphones.
- **Two full passes with the same rpm samples:**
  - **Pass A: Normal mode, ESG off.** The real mechanical sound. Source for the
    **interior** sound (`*_int` events).
  - **Pass B: N mode, ESG on.** Exhaust valve open plus Hyundai's sound enhancer. Source
    for the **exterior** sound (`*_ext` events), after the processing in §10.
- On a **straight private road**. No dyno, so no dyno roller/fan whine, but also no way
  to hold full throttle at a fixed rpm (§1).

The machine-readable shot list is [`shotlist.csv`](shotlist.csv) (61 takes). The printable
version is [`shotlist_checklist.pdf`](shotlist_checklist.pdf).

---

## 1. Method: what a road can and can't give

AC's engine sound is built from **loops at fixed rpm**, in on-throttle and off-throttle
sets. On a flat road:

| Layer | How it's captured | Why |
|---|---|---|
| **Full load (ON)** | **Slow WOT pulls** in a high gear, sliced at each grid rpm afterwards | The engine can't be held at a fixed rpm at WOT without a dyno. A high gear makes the rpm rise slowly |
| **Off-throttle (OFF)** | **Coast-downs** in gear | Engine braking in a high gear slows the decay |
| **Part load** | **Truly steady**: drive at constant speed so rpm is fixed | The one layer a road gives cleanly; it also helps the ON/OFF crossfade |
| Idle, limiter, shifts, lift-offs, whine | Directly | |

**How the sweeps become loops:** the processing tools track the rpm through each pull
from the engine tone in the audio (the main tone is rpm / 30 Hz, §4), resample a short
slice around each grid rpm so its pitch is flat, and then cut it to a whole number of
engine cycles. This works well if the sweep is slow. **Aim for 500 rpm per second or
less.** Time it on the tachometer: **1000→4000 should take at least 6 s**, and
**3000→limiter at least 7–8 s**.

**Gear choice is a trade-off:**
- Higher gear: slower sweep (better loops), but more speed, so more wind and tyre noise in
  the cabin, and more road needed.
- Lower gear: less road and less wind noise, but faster sweeps.

Pick gears using the test run in §5, and **use the same gears in both passes** so the A and B
loops line up. Splitting the range into a **low pull (1000→4000)** and a **high pull
(3000→limiter)** means each pull can use the best gear for its part of the range.

**Don't hold rpm under load with the brake** (throttle against the left foot). It overheats
the brakes and the DCT clutch quickly, and the brake noise gets into the recording.

---

## 2. Car settings

| | Pass A | Pass B |
|---|---|---|
| Drive mode | **Normal** | **N** |
| ESG | **Off** | **On** |
| Gearbox | Manual/paddle mode | Manual/paddle mode |

For both passes:
- Check the mode and ESG in the menu at the start of the pass, and again after any restart.
- A/C and fan off, radio off, **windows and sunroof closed**, nothing loose in the cabin
  (rattles end up in every loop).
- Warm engine (oil at temperature) before any take. Tyre pressures normal.
- **Same direction for every run** if there's any wind or slope, so takes match. Note the
  direction on the checklist.

N mode idles higher than Normal; that's expected. Write both settled idle rpms on the
checklist.

---

## 3. Recording

| Channel | Device | Placement | Feeds |
|---|---|---|---|
| **CAB** | Phone with **RecForge II** | Clamped or mounted (not held) between the front seats or on the dash, at about driver's head height, mic openings uncovered | Everything |
| **DASH** (optional) | A second phone filming the instrument cluster, mounted | Windscreen or vent mount, tachometer and speedo in frame | A visual rpm/speed record if a take needs checking |

**RecForge II settings:**
- WAV (PCM), **48 kHz**, 24-bit if offered (16-bit is fine otherwise), stereo.
- Audio source **"Unprocessed"** if listed, otherwise "Camcorder" or "Mic". Avoid "Voice
  communication" and "Voice recognition": they apply automatic gain and noise suppression.
- Manual gain, set once in the gain check (§6, block 1), then **locked for both passes**.
- Phone in **airplane mode** and **Do Not Disturb**.

**Gain check first, in Pass B settings.** N mode with ESG on is the loudest the cabin gets,
so set the gain there (peaks around **−6 dBFS** on the limiter). That leaves headroom for
both passes, and keeps the real loudness difference between them.

No OBD logger is needed: the rpm through every sweep is tracked from the audio, with the
spoken slates and the paper checklist for context.

---

## 4. The rpm grid

The same 19 points for **both passes**. For the pulls and coasts they're **slice centres**
(where loops get cut from the sweeps); for the part-load layer they're **actual hold points**.

Points are spaced about **2 semitones** apart (ratio ≈ 1.12), so neighbouring loops never
need more than about ±1 semitone of pitch shift at a crossfade.

| rpm | Tier | Main tone (2nd order) Hz | 1 engine cycle (ms) |
|---:|:--:|---:|---:|
| idle | A | – | – |
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
  a sweep, and how you can check any clip on a spectrogram. In Pass B the ESG adds its own
  synthetic tones; they follow the rpm too, so tracking still works.
- **Cycle** = 120 / rpm seconds, one full firing sequence. Loops are cut as whole cycles.
- **6500** assumes a limiter around 6,700–6,800 rpm. Adjust it if the mod's `engine.ini` or
  the real car says otherwise.
- **Idle** is whatever each mode settles at (N mode is higher). AC has a single idle rpm (in
  the mod's `engine.ini`), so each pass's idle loop is pitched slightly to match it if needed.
- **Tier A** points are every other point and are enough for a first working bank; **tier B**
  fills the gaps. For the sweeps this doesn't matter (every pull crosses every point), but
  for the part-load holds, do tier A first in each pass.

---

## 5. Test run (before recording)

One run in Pass A settings, watching the tachometer (a passenger with a stopwatch helps),
to choose gears for your road:

1. From ~1000 rpm, WOT in **5th** (or the highest gear you'd consider). Note the rpm and
   speed when you reach the safe braking point, and how long the pull took.
2. From ~3000 rpm, WOT in **4th**, then **3rd**. Which one reaches the limiter before the
   braking point?
3. Pick:
   - `PULL-LO` gear: the highest gear where 1000→4000 fits the road.
   - `PULL-HI` gear: the highest gear where 3000→limiter fits the road.
   - If neither 3rd nor 4th reaches the limiter, do the high pull in two halves
     (3000→5000, then 4500→limiter) and note it.
4. Check the cabin for wind whistle at the top speed. If it's loud, drop a gear.

Write the chosen gears on the checklist; Pass B uses the same ones.

---

## 6. Run order

Say the take ID out loud before each run **and the gear** (e.g. "pull low N, fifth gear,
run two"), clap, then go. The spoken slate replaces a data log, so say anything unusual too
("gust", "car passed", "lifted early").

| # | Block | Takes | Notes |
|---|---|---|---|
| 0 | Noise | `NOISE-PARK`, `NOISE-CRUISE` ×2 | Engine off parked; then a steady ~80 km/h in top gear, barely on throttle (no coasting in neutral: it's bad for the DCT). Used to clean up wind/tyre noise |
| 1 | Gain check | `GAIN-CHECK` | **N mode, ESG on.** Brief limiter hold in 2nd; set the gain so peaks are about −6 dBFS, then lock it for the whole day |
| **A** | **Pass A** | | **Switch to Normal mode, ESG off.** Say "pass A" into the recorder |
| A1 | Idle | `IDLE` ×2 | Stationary, gearbox in Neutral/P, 30 s each |
| A2 | Limiter | `LIMIT` ×3 | Brief hold in 2nd; skip if the gearbox upshifts at the limiter |
| A3 | Full-load pulls | `PULL-LO` ×4, `PULL-HI` ×4 | Smooth, full pedal, no pedal changes mid-pull. Let the engine cool on the drive back |
| A4 | Coast-downs | `COAST-HI` ×4, `COAST-LO` ×3 | Lift fully, stay in gear, no brakes until the take ends |
| A5 | Part-load holds | `SS-PART-*` ×2 each (tier A first) | Constant speed, steady rpm for 8 s. Use 1st/2nd for the high-rpm points |
| A6 | Reference | `PULL-REF` ×2 | Ordinary 2nd-gear pull, for A/B comparison later |
| A7 | One-shots | `UP-WOT`, `UP-PART`, `DOWN`, `LIFT` | Reps per shift as in the shot list |
| A8 | Whine | `CRUISE-WHINE` ×2 | Steady cruise in 6th–8th, then coast |
| **B** | **Pass B** | | **Switch to N mode, ESG on.** Say "pass B" into the recorder |
| B1–B6 | Same as A1–A6 | `IDLE-N`, `LIMIT-N`, `PULL-LO-N`, `PULL-HI-N`, `COAST-HI-N`, `COAST-LO-N`, `SS-PART-*-N`, `PULL-REF-N` | Same gears, same reps, same rpm points |
| B7 | One-shots | `UP-WOT-N`, `DOWN-N`, `LIFT-N` | N mode gives the spark-cut upshift and the pops, so `LIFT-N` has more reps |

Four pulls of each kind is deliberate: road takes vary (wind, gusts, a passing car), and
the best slice at each rpm can come from a different run.

The whole day is roughly twice the WOT time of a single pass. Let the car cool between the
passes, and watch the temperatures.

---

## 7. What each take becomes

| FMOD event | Built from | Minimum usable set |
|---|---|---|
| `engine_int` | **Pass A**: `IDLE`, slices of `PULL-LO`/`PULL-HI` (ON), `COAST-HI`/`COAST-LO` (OFF), `SS-PART-*`, `LIMIT` | 10 tier-A ON slices + 10 OFF slices |
| `engine_ext` | **Pass B**: the same takes with `-N`, processed as in §10 | same |
| `turbo` | `LIFT` / `LIFT-N` (whoosh); whistle from the pulls if it's audible | 2–3 lift-off variations |
| `gear_int` | Pass A: `UP-WOT`, `UP-PART`, `DOWN` | 3 variations each |
| `gear_ext` | Pass B: `UP-WOT-N`, `DOWN-N` | 3 variations each |
| `backfire_int` / `_ext` | `LIFT-N` pops (int: lightly processed; ext: §10 chain) | 4+ variations, or leave silent |
| `limiter` | `LIMIT` (int) / `LIMIT-N` (ext) | 1 clean bounce loop each |
| `transmission` | `CRUISE-WHINE` | 1 loop |
| `horn` | not recorded; keep the existing one | – |
| — (reference) | `PULL-REF`, `PULL-REF-N` | For comparing the finished bank with reality |

Recording both passes at the same rpm points also keeps the option open to swap roles after
listening: for example an ESG-on interior as an alternative version of the mod.

---

## 8. Naming and the checklist

Files: `<take_id>_r<rep>.wav`, e.g. `PULL-LO_r2.wav`, `SS-PART-3400-N_r1.wav`. If renaming
on the day is a hassle, keep RecForge's own file names: the spoken slates are enough to sort
them out later.

Fill in the PDF checklist as you go (gear, start/end rpm, keep Y/N). A photo of the
filled-in sheet is fine.

---

## 9. Handing the files over

After the day, provide:
1. **All WAV files**, unedited (no normalising, no noise reduction, no trimming beyond
   deleting obviously failed takes).
2. **The filled-in checklist** (a phone photo is fine).
3. Optional: the dash videos.
4. The mod's `engine.ini` (or just its idle and limiter rpm).

The rpm tracking, slicing, looping and FMOD build happen from those.

---

## 10. Building the exterior sound from Pass B

Pass B is still a cabin recording, so it needs processing to sound like it's outside. A
cabin recording differs from an exterior one mainly in **frequency balance**: the cabin adds
a low "boom" and the bodywork filters out the high exhaust rasp. Reverb comes last. Order:

1. **Clean the wind/tyre noise** using the `NOISE-CRUISE` profile. Use gentle settings;
   heavy noise reduction leaves watery artefacts that loop audibly.
2. **EQ, remove the cabin:** high-pass around 40 Hz, then find the 1–3 cabin boom peaks in
   roughly 60–200 Hz (they stay at the same frequency whatever the rpm) and cut them 3–6 dB.
3. **EQ, add the outside:** a gentle lift around 1–4 kHz for exhaust rasp and presence, and a
   little high shelf. Use light saturation if it still sounds too muffled.
4. **Space last, and done in FMOD** rather than baked into the files: a short, mostly
   early-reflection reverb (outdoor / small-space type, low wet mix of about 10–20%) as an
   effect on the `engine_ext` event or the exterior bus. That keeps the loops clean (reverb
   tails baked into a loop click at the loop point) and lets you tune it in game.
5. Use the same chain on `gear_ext`, `backfire_ext` and the exterior limiter so they match.
6. Check outside the car in game (replay chase cam and a trackside camera) against a Kunos
   turbo FWD car at the same rpm.

---

## 11. Checklists

**Before the day**
- [ ] Mod's `engine.ini`: confirm idle and limiter rpm, and adjust the top grid point
- [ ] Permission for the private road; someone to keep the road clear
- [ ] RecForge II set up (§3); phone storage free; phone charged
- [ ] Phone mount or clamp for the cabin
- [ ] Printed checklist

**At the road**
- [ ] Walk or drive the road: braking point marked, nothing on the surface
- [ ] Test run done (§5); gears chosen and written on the checklist
- [ ] Gain check done in N mode + ESG on; gain locked
- [ ] A/C, fan and radio off, windows and sunroof closed, cabin emptied of rattles
- [ ] Phone mounted, not hand-held, and not touching trim that buzzes

**At the start of each pass**
- [ ] Mode and ESG set for the pass (A: Normal + ESG off; B: N + ESG on), checked in the menu
- [ ] "Pass A" / "Pass B" said into the recorder

**After each block**
- [ ] Listen back to one take on headphones: no clipping, no rattles, phone still in place
- [ ] Checklist filled in: gear, start/end rpm, keep Y/N
