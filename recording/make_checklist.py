"""Render shotlist.csv as a printable PDF checklist in run order.

Usage: python recording/make_checklist.py  (needs reportlab)
Writes recording/shotlist_checklist.pdf next to this script.
"""
import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

HERE = Path(__file__).parent
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

try:
    pdfmetrics.registerFont(TTFont("Sans", FONT_DIR / "DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("Sans-Bold", FONT_DIR / "DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold")
    SANS, BOLD = "Sans", "Sans-Bold"
except Exception:  # fall back to built-in fonts (no arrows/checkbox glyphs)
    SANS, BOLD = "Helvetica", "Helvetica-Bold"

INK = colors.HexColor("#1f2328")
MUTED = colors.HexColor("#656d76")
RULE = colors.HexColor("#d0d7de")
BAND = colors.HexColor("#f2f4f7")
WARN = colors.HexColor("#fde68a")
PASS_A_BAND = colors.HexColor("#dbeafe")
TIER_BG = {"A": colors.HexColor("#dbeafe"), "B": colors.HexColor("#ede9fe"),
           "C": colors.HexColor("#f1f5f9")}

S = {
    "title": ParagraphStyle("t", fontName=BOLD, fontSize=16, leading=19, textColor=INK),
    "sub": ParagraphStyle("s", fontName=SANS, fontSize=8.5, leading=11, textColor=MUTED),
    "h": ParagraphStyle("h", fontName=BOLD, fontSize=11, leading=14, textColor=INK,
                        spaceBefore=6, spaceAfter=3),
    "blk": ParagraphStyle("b", fontName=BOLD, fontSize=8.5, leading=11, textColor=INK),
    "cell": ParagraphStyle("c", fontName=SANS, fontSize=7.5, leading=9.2, textColor=INK),
    "note": ParagraphStyle("n", fontName=SANS, fontSize=7, leading=8.6, textColor=MUTED),
    "id": ParagraphStyle("i", fontName=BOLD, fontSize=7.5, leading=9.2, textColor=INK),
}

BOX = "☐"  # ballot box

rows = {r["take_id"]: r for r in csv.DictReader(open(HERE / "shotlist.csv", newline=""))}
ss = lambda kind, rpms: [f"SS-{kind}-{r}" for r in rpms]

# Run order from RECORDING_PLAN.md section 6 (private road, no dyno).
# Entries are take ids, or (take_id, reps_override, label_suffix).
TIER_A = [1000, 1300, 1700, 2150, 2700, 3400, 4250, 5300, 6500]
TIER_B = [900, 1150, 1500, 1900, 2400, 3000, 3800, 4750, 5900]
SHIFTS = [("UP-WOT", 5, " 1>2"), ("UP-WOT", 5, " 2>3"), ("UP-WOT", 5, " 3>4")]
DOWNS = [("DOWN", 5, " 4>3"), ("DOWN", 5, " 3>2")]


def n(entries):
    """Pass B version of a take list: same takes with the -N suffix."""
    return [(t[0] + "-N",) + t[1:] if isinstance(t, tuple) else t + "-N" for t in entries]


GEARS = "Gears from the test run: PULL-LO in ____  PULL-HI in ____ (same in both passes). "
PRE = [
    ("0  Noise", "Engine off parked; then steady ~80 km/h in top gear, barely on throttle.",
     ["NOISE-PARK", "NOISE-CRUISE"]),
    ("1  Gain check: N mode + ESG ON", "Loudest case. Set gain to about -6 dBFS peaks, "
     "then LOCK it for the whole day.", ["GAIN-CHECK"]),
]


def pass_blocks(p, idle_label, extra):
    sfx = (lambda x: n(x)) if p == "B" else (lambda x: x)
    return [
        (f"{p}1 Idle", f"Stationary, gearbox in Neutral/P. Settled idle rpm: ______ ({idle_label})",
         sfx(["IDLE"])),
        (f"{p}2 Limiter", "Brief hold in 2nd.", sfx(["LIMIT"])),
        (f"{p}3 Full-load pulls", GEARS + "Full pedal, no changes mid-pull.",
         sfx(["PULL-LO", "PULL-HI"])),
        (f"{p}4 Coast-downs", "Lift fully, stay in gear, no brakes until the take ends.",
         sfx(["COAST-HI", "COAST-LO"])),
        (f"{p}5a Part-load holds, tier A", "8 s steady. Use 1st/2nd for the high-rpm points.",
         sfx(ss("PART", TIER_A))),
        (f"{p}5b Part-load holds, tier B", "", sfx(ss("PART", TIER_B))),
        (f"{p}6 Reference", "", sfx(["PULL-REF"])),
    ] + extra


PASS_A = pass_blocks("A", "Normal", [
    ("A7 Shifts, lift-offs, whine", "Shift reps are per shift.",
     SHIFTS + ["UP-PART"] + DOWNS + ["LIFT", "CRUISE-WHINE"]),
])
PASS_B = pass_blocks("B", "N mode", [
    ("B7 Shifts and lift-offs", "Shift reps are per shift. LIFT-N: stay off the throttle "
     "3 s after lifting, for pops.", n(SHIFTS) + n(DOWNS) + ["LIFT-N"]),
])

WIDTHS = [37 * mm, 29 * mm, 10 * mm, 24 * mm, 30 * mm, 16 * mm, 12 * mm,
          22 * mm, 12 * mm, 75 * mm]
HEAD = ["Done", "Take", "Tier", "Target rpm", "Load", "Gear", "Hold", "Start/end rpm", "Keep",
        "Notes"]


def arrows(v):
    return v.replace("->", "→").replace(">", "→")


def take_row(entry, show_note=True):
    tid, reps, suffix = (entry if isinstance(entry, tuple) else (entry, None, ""))
    r = rows[tid]
    reps = int(reps if reps is not None else r["reps"])
    gear = r["gear"] if not suffix else suffix.strip()
    hold = f'{r["hold_s"]} s' if r["hold_s"] else ""
    return [
        Paragraph(" ".join([BOX] * reps), ParagraphStyle("x", parent=S["cell"], fontSize=10,
                                                          leading=11)),
        Paragraph(tid, S["id"]),
        Paragraph(r["tier"], S["cell"]),
        Paragraph(arrows(r["target_rpm"]), S["cell"]),
        Paragraph(arrows(r["load"].replace(" pedal", "")), S["cell"]),
        Paragraph(arrows(gear), S["cell"]),
        Paragraph(hold, S["cell"]),
        "", "",
        Paragraph(arrows(r["notes"]), S["note"]) if show_note else "",
    ], r["tier"]


BASE_STYLE = [
    ("FONT", (0, 0), (-1, -1), SANS),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 2.2),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
    ("LEFTPADDING", (0, 0), (-1, -1), 3),
    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
]


def column_header():
    t = Table([[Paragraph(h, S["blk"]) for h in HEAD]], colWidths=WIDTHS)
    t.setStyle(TableStyle(BASE_STYLE + [("LINEBELOW", (0, 0), (-1, 0), 0.8, INK)]))
    return t


def block_table(name, note, takes, band=None):
    """One run-order block. The block band repeats if the block breaks across pages."""
    ids = [t[0] if isinstance(t, tuple) else t for t in takes]
    notes = {rows[i]["notes"] for i in ids}
    shared = len(ids) > 1 and len(notes) == 1
    if shared:
        note = " ".join(x for x in [note, notes.pop()] if x)
    label = f"<b>{arrows(name)}</b>" + (f"   <font color='#656d76'>{arrows(note)}</font>"
                                         if note else "")
    data = [[Paragraph(label, S["cell"])] + [""] * (len(HEAD) - 1)]
    band = band or (WARN if "ESG ON" in name else BAND)  # ESG-on blocks stand out
    style = BASE_STYLE + [("SPAN", (0, 0), (-1, 0)), ("BACKGROUND", (0, 0), (-1, 0), band),
                          ("LINEABOVE", (0, 0), (-1, 0), 0.6, RULE)]
    seen = set()
    for t in takes:
        n = rows[t[0] if isinstance(t, tuple) else t]["notes"]
        row, tier = take_row(t, show_note=not shared and n not in seen)  # note once per block
        seen.add(n)
        j = len(data)
        data.append(row)
        style += [("LINEBELOW", (0, j), (-1, j), 0.3, RULE),
                  ("BACKGROUND", (2, j), (2, j), TIER_BG.get(tier, colors.white)),
                  ("ALIGN", (2, j), (2, j), "CENTER"),
                  # write-in boxes
                  ("BOX", (7, j), (7, j), 0.4, RULE),
                  ("BOX", (8, j), (8, j), 0.4, RULE)]
    table = Table(data, colWidths=WIDTHS, repeatRows=1)
    table.setStyle(TableStyle(style))
    # Keep short blocks whole; long ones may split but keep the band with >= 3 rows.
    return table


def banner(title, note, colour):
    t = Table([[Paragraph(f"<b>{title}</b>   {note}", S["blk"])]], colWidths=[sum(WIDTHS)])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colour),
                           ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                           ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    return t


def session(title, blocks, note="", band=None):
    """Session banner + column header stay with the first block; short blocks stay whole."""
    head = banner(title, note, band) if band else Paragraph(title, S["h"])
    out = [KeepTogether([Spacer(1, 6), head, Spacer(1, 3), column_header(),
                         block_table(*blocks[0], band=band)])]
    for b in blocks[1:]:
        t = block_table(*b, band=band)
        out.append(KeepTogether([t]) if len(b[2]) <= 10 else t)
    return out


def header():
    settings = ["Mode + ESG for the pass, checked in menu", "Pass name said into recorder",
                "Manual / paddle mode",
                "A/C, fan, radio off", "Windows + sunroof closed, no rattles", "Warm engine",
                "Dash video on (optional)", "Gain locked since gain check", "Say take ID + gear, clap, go"]
    cells = [Paragraph(f"{BOX}  {s}", S["cell"]) for s in settings]
    grid = Table([cells[0:3], cells[3:6], cells[6:9]], colWidths=[89 * mm] * 3)
    grid.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, RULE),
                              ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    fields = Table([[Paragraph(x, S["sub"]) for x in
                     ["Date: ________________", "Location: ______________________",
                      "Recorder(s): ____________________", "Wind / direction: ______________"]]],
                   colWidths=[50 * mm, 70 * mm, 75 * mm, 72 * mm])
    return [
        Paragraph("Kona N sound capture: shot list", S["title"]),
        Paragraph("One phone in the cabin (RecForge II) · 48 kHz WAV · "
                  "Pass A: Normal + ESG off · Pass B: N + ESG ON · "
                  "file name: &lt;take&gt;_r&lt;rep&gt;.wav · "
                  "say the take ID out loud, clap, then record · "
                  "Private road, same direction every run", S["sub"]),
        Spacer(1, 4), fields, Spacer(1, 4),
        Paragraph("Before every block", S["blk"]), Spacer(1, 2), grid,
    ]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(SANS, 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(12 * mm, 7 * mm, "Generated from recording/shotlist.csv · "
                      "details in recording/RECORDING_PLAN.md")
    canvas.drawRightString(landscape(A4)[0] - 12 * mm, 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    out = HERE / "shotlist_checklist.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=landscape(A4), leftMargin=12 * mm,
                            rightMargin=12 * mm, topMargin=10 * mm, bottomMargin=12 * mm,
                            title="Kona N sound capture: shot list", author="")
    story = header()
    story += session("Before the passes", PRE)
    story += session("PASS A", PASS_A, "Normal mode, ESG OFF. Say \"pass A\" into the recorder.",
                     PASS_A_BAND)
    story += [PageBreak()]
    story += session("PASS B", PASS_B, "Switch to N mode, ESG ON. Same gears as pass A. "
                     "Say \"pass B\" into the recorder.", WARN)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(out)


if __name__ == "__main__":
    main()
