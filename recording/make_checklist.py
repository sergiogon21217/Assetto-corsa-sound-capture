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
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
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

# Run order from RECORDING_PLAN.md sections 5 and 6.
# Entries are take ids, or (take_id, reps_override, label_suffix).
DYNO = [
    ("0  Setup", "Engine off, fans on. Clap.", ["NOISE-DYNO"]),
    ("1  Idle", "30 s each.", ["IDLE"]),
    ("2  Level check", "Set gains to about -6 dBFS peaks, then LOCK them.", [("LIMIT", 1, "")]),
    ("3  Reference ramps", "Slow sweep 1000 -> limiter.", ["RAMP-ON"]),
    ("4  ON, tier A, low", "Stabilise, then 8 s hold. Cool down 2-3 min after.",
     ss("ON", [1000, 1300, 1700, 2150, 2700])),
    ("5  ON, tier A, high", "Cool down 2-3 min after.",
     ss("ON", [3400, 4250, 5300, 6500]) + [("LIMIT", 2, "")]),
    ("6  OFF layer", "CD-OFF if the dyno can't motor the car. SS-OFF-* only on a motoring dyno.",
     ["CD-OFF"] + ss("OFF", [1000, 1300, 1700, 2150, 2700, 3400, 4250, 5300, 6500,
                             900, 1150, 1500, 1900, 2400, 3000, 3800, 4750, 5900])),
    ("7a ON, tier B, low", "Cool down 2-3 min after.", ss("ON", [900, 1150, 1500, 1900, 2400])),
    ("7b ON, tier B, high", "", ss("ON", [3000, 3800, 4750, 5900])),
    ("8  Optional mid load", "Part throttle, 6 s holds, one rep.",
     ss("MID", [900, 1000, 1150, 1300, 1500, 1700, 1900, 2150, 2400, 2700,
                3000, 3400, 3800, 4250, 4750, 5300, 5900, 6500])),
]
ROAD = [
    ("Noise", "", ["NOISE-ROAD"]),
    ("Shifts", "Reps are per shift.",
     [("UP-WOT", 5, " 1>2"), ("UP-WOT", 5, " 2>3"), ("UP-WOT", 5, " 3>4"),
      "UP-PART", ("DOWN", 5, " 4>3"), ("DOWN", 5, " 3>2")]),
    ("Lift-offs", "POP-N only if you want pops (N mode, ESG still off).", ["LIFT", "POP-N"]),
    ("Whine", "", ["CRUISE-WHINE"]),
]

WIDTHS = [37 * mm, 29 * mm, 10 * mm, 24 * mm, 30 * mm, 16 * mm, 12 * mm,
          22 * mm, 12 * mm, 75 * mm]
HEAD = ["Done", "Take", "Tier", "Target rpm", "Load", "Gear", "Hold", "Actual rpm", "Keep",
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


def block_table(name, note, takes):
    """One run-order block. The block band repeats if the block breaks across pages."""
    ids = [t[0] if isinstance(t, tuple) else t for t in takes]
    notes = {rows[i]["notes"] for i in ids}
    shared = len(ids) > 1 and len(notes) == 1
    if shared:
        note = " ".join(x for x in [note, notes.pop()] if x)
    label = f"<b>{arrows(name)}</b>" + (f"   <font color='#656d76'>{arrows(note)}</font>"
                                         if note else "")
    data = [[Paragraph(label, S["cell"])] + [""] * (len(HEAD) - 1)]
    style = BASE_STYLE + [("SPAN", (0, 0), (-1, 0)), ("BACKGROUND", (0, 0), (-1, 0), BAND),
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


def session(title, blocks):
    """Session title + column header stay with the first block; short blocks stay whole."""
    out = [KeepTogether([Paragraph(title, S["h"]), column_header(), block_table(*blocks[0])])]
    for b in blocks[1:]:
        t = block_table(*b)
        out.append(KeepTogether([t]) if len(b[2]) <= 10 else t)
    return out


def header():
    settings = ["Normal drive mode", "ESG OFF (check menu)", "Manual / paddles, 4th on dyno",
                "A/C, fan, radio off", "Windows up, no rattles", "Warm engine",
                "OBD logging", "Gains locked after LIMIT", "Clap at start + end of block"]
    cells = [Paragraph(f"{BOX}  {s}", S["cell"]) for s in settings]
    grid = Table([cells[0:3], cells[3:6], cells[6:9]], colWidths=[89 * mm] * 3)
    grid.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, RULE),
                              ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    fields = Table([[Paragraph(x, S["sub"]) for x in
                     ["Date: ________________", "Location: ______________________",
                      "Recorder(s): ____________________", "Car / VIN: __________________"]]],
                   colWidths=[50 * mm, 70 * mm, 75 * mm, 72 * mm])
    return [
        Paragraph("Kona N sound capture: shot list", S["title"]),
        Paragraph("Cabin-only (CAB + optional FWL footwell) · 48 kHz / 24-bit WAV · "
                  "file name: &lt;take&gt;_r&lt;rep&gt;_&lt;channel&gt;.wav · "
                  "say the take ID out loud, clap, then record · "
                  "Tier A first, then B; C optional", S["sub"]),
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
    story += session("Dyno session", DYNO) + session("Road session", ROAD)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(out)


if __name__ == "__main__":
    main()
