#!/usr/bin/env python3
"""Paper figures for the Safety Copilot agentic architecture, as standalone SVG.

Geometry mirrors the canvas artboards: figures are drawn at 2x and carry a
physical size, so they drop into a paper at 7 in (full width) or 3.5 in (one
column) with no scaling. Text stays as text; fonts fall back to Arial.
"""
from __future__ import annotations

import html
from pathlib import Path

OUT = Path(__file__).resolve().parent
INK, SEC, BODY = "#1B1D1F", "#4A4E52", "#33373B"
BLUE, BLUE_BG, BLUE_LINE, BLUE_DK = "#2C5A85", "#EEF3F8", "#9FB3C6", "#1E4263"
AMBER, AMBER_DK, AMBER_BG = "#9A5210", "#8A4A0E", "#FBF1E4"
GREY_BG, GREY_LINE, GREY = "#F0EFEA", "#9E9A90", "#767676"
SANS = "IBM Plex Sans, Helvetica Neue, Arial, sans-serif"
COND = "IBM Plex Sans Condensed, IBM Plex Sans, Helvetica Neue, Arial, sans-serif"
CW_SANS, CW_COND = 0.52, 0.47          # conservative average glyph width


class Svg:
    def __init__(self, w: float, h: float, inches: float):
        self.w, self.h, self.inches = w, h, inches
        self.p: list[str] = []

    # ---------------------------------------------------------------- shapes
    def rect(self, x, y, w, h, fill="none", stroke=None, sw=2.0, r=0, dash=None):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{sw}"'
            if dash:
                s += f' stroke-dasharray="{dash}"'
        self.p.append(s + "/>")

    def line(self, x1, y1, x2, y2, stroke=INK, sw=2.0, dash=None):
        s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"'
        self.p.append(s + (f' stroke-dasharray="{dash}"/>' if dash else "/>"))

    def poly(self, pts, stroke=INK, sw=2.0, fill="none", dash=None):
        s = f'<polyline points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'
        self.p.append(s + (f' stroke-dasharray="{dash}"/>' if dash else "/>"))

    def tri(self, pts, fill=INK):
        self.p.append(f'<polygon points="{pts}" fill="{fill}"/>')

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=2.0):
        s = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{sw}"'
        self.p.append(s + "/>")

    # ----------------------------------------------------------------- text
    def text(self, x, y, s, fs=20, fill=INK, weight=400, font=SANS, anchor="start"):
        self.p.append(
            f'<text x="{x}" y="{y}" font-family="{font}" font-size="{fs}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{html.escape(s)}</text>')

    def wrap(self, x, y, s, w, fs=20, fill=BODY, weight=400, font=SANS, lh=1.3, anchor="start"):
        """Greedy wrap at an estimated glyph width; returns the y after the block."""
        cw = (CW_COND if font is COND else CW_SANS) * fs
        limit = max(1, int(w / cw))
        words, line, lines = s.split(), "", []
        for word in words:
            trial = f"{line} {word}".strip()
            if len(trial) <= limit or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        for i, ln in enumerate(lines):
            self.text(x, y + i * fs * lh, ln, fs, fill, weight, font, anchor)
        return y + (len(lines) - 1) * fs * lh

    def height_of(self, s, w, fs=20, font=SANS, lh=1.3) -> float:
        cw = (CW_COND if font is COND else CW_SANS) * fs
        limit = max(1, int(w / cw))
        words, line, n = s.split(), "", 1
        for word in words:
            trial = f"{line} {word}".strip()
            if len(trial) <= limit or not line:
                line = trial
            else:
                n += 1
                line = word
        return (n - 1) * fs * lh

    def arrow_down(self, x, y1, y2, stroke=INK, sw=2.5):
        self.line(x, y1, x, y2 - 12, stroke, sw)
        self.tri(f"{x},{y2} {x-7},{y2-13} {x+7},{y2-13}", stroke)

    def arrow_right(self, x1, x2, y, stroke=INK, sw=2.5):
        self.line(x1, y, x2 - 12, y, stroke, sw)
        self.tri(f"{x2},{y} {x2-13},{y-7} {x2-13},{y+7}", stroke)

    def save(self, name: str):
        mm = self.inches * 25.4
        hmm = mm * self.h / self.w
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{mm:.2f}mm" height="{hmm:.2f}mm" '
                f'viewBox="0 0 {self.w} {self.h}" font-family="{SANS}">\n'
                f'<rect width="{self.w}" height="{self.h}" fill="#FFFFFF"/>\n')
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / name).write_text(head + "\n".join(self.p) + "\n</svg>\n")
        print(f"{name}: {self.w}x{self.h} px -> {mm:.1f}x{hmm:.1f} mm")


# ══════════════════════════════════════════════ Fig. 1 — architecture
def fig1():
    s = Svg(1344, 560, 7.0)
    s.rect(20, 20, 1304, 232, BLUE_BG, r=10)
    s.rect(20, 268, 1304, 132, AMBER_BG, AMBER, 2, 10, "10 6")
    s.rect(20, 416, 1304, 124, GREY_BG, r=10)

    for y, ttl, sub, col in ((62, "CODE", "deterministic, auditable", BLUE),
                             (310, "LLM", "isolated, text only", AMBER_DK),
                             (458, "PEOPLE", "final authority", INK)):
        s.text(36, y, ttl, 24, col, 700, COND)
        s.wrap(36, y + 26, sub, 144, 20, SEC)

    boxes = [(196, "1", "Plant data", "process, reliability, maintenance"),
             (412, "2", "Masked feed", "anonymised, nothing after t_now"),
             (628, "3", "Stream", "one dated analysis per trigger"),
             (844, "4", "Phase A", "evidence assembled and cross-checked"),
             (1148, "6", "Report", "decision view and audit log")]
    for x, n, ttl, sub in boxes:
        s.rect(x, 44, 172, 184, "#FFFFFF", BLUE, 2.5, 8)
        s.circle(x + 28, 72, 14, BLUE)
        s.text(x + 28, 79, n, 17, "#FFFFFF", 700, SANS, "middle")
        s.text(x + 14, 116, ttl, 24, INK, 600, COND)
        s.wrap(x + 14, 146, sub, 144, 20, BODY)

    for x1, x2 in ((369, 412), (585, 628), (801, 844), (1017, 1148)):
        s.arrow_right(x1, x2, 136)
    s.text(1082, 122, "numbers", 21, INK, 600, COND, "middle")

    s.arrow_down(930, 229, 280)
    s.text(944, 256, "closed evidence", 21, INK, 600, COND)

    s.rect(844, 280, 256, 108, "#FFFFFF", AMBER, 2.5, 8, "10 6")
    s.circle(872, 308, 14, AMBER_DK)
    s.text(872, 315, "5", 17, "#FFFFFF", 700, SANS, "middle")
    s.text(896, 315, "Phase B", 26, INK, 600, COND)
    s.wrap(858, 348, "LLM interprets and recommends", 228, 20, BODY)
    s.wrap(196, 318, "A fresh session for every analysis, with no tools, files, memory or "
                     "network access.", 620, 21, BODY)

    s.poly("1101,334 1200,334 1200,241", INK, 2.5)
    s.tri("1200,229 1193,242 1207,242")
    s.text(1112, 358, "judgement", 21, INK, 600, COND)

    s.arrow_down(1290, 229, 426)
    s.rect(1132, 426, 188, 108, "#FFFFFF", INK, 2.5, 8)
    s.rect(1136, 430, 180, 100, "none", INK, 1.2, 6)
    s.circle(1160, 454, 14, INK)
    s.text(1160, 461, "7", 17, "#FFFFFF", 700, SANS, "middle")
    s.text(1184, 461, "People", 24, INK, 600, COND)
    s.wrap(1146, 494, "act on the recommendation", 160, 20, BODY)
    s.wrap(196, 466, "The report only recommends. People accept, act or reject.", 900, 21, BODY)
    s.save("fig1_architecture.svg")


# ══════════════════════════════════════════════ Fig. 2 — RUN_A timeline
def fig2():
    s = Svg(1344, 640, 7.0)
    s.text(20, 30, "(a) What opened each analysis in 2025", 24, INK, 700, COND)
    s.rect(962, 14, 16, 16, INK)
    s.text(988, 30, "plant record", 20, BODY)
    s.circle(1136, 22, 7, "#FFFFFF", INK, 3)
    s.text(1154, 30, "process signal", 20, BODY)

    s.line(60, 150, 1300, 150, INK, 2.5)
    months = [(60, "Jan"), (175.1, "Feb"), (279.1, "Mar"), (394.2, "Apr"), (505.6, "May"),
              (620.7, "Jun"), (732.1, "Jul"), (847.2, "Aug"), (962.3, "Sep"), (1073.7, "Oct"),
              (1188.8, "Nov")]
    for i, (x, m) in enumerate(months + [(1300, "")]):
        s.line(x, 145, x, 155, INK, 2)
        if m:
            nxt = (months + [(1300, "")])[i + 1][0]
            s.text((x + nxt) / 2, 178, m, 20, SEC, 400, SANS, "middle")

    labels = [(396, 72, "middle", "1–2  channel A fails and is repaired", 340),
              (617, 110, "middle", "3  test overdue", 200),
              (839.7, 72, "middle", "4  training overdue", 220),
              (951.1, 110, "middle", "5  channel B fails", 200),
              (1324, 72, "end", "6  load +15 %, not revalidated", 340)]
    for x, y, anchor, txt, w in labels:
        lx = 1289 if anchor == "end" else x
        s.text(x, y, txt, 21, INK, 500, COND, anchor)
        s.line(lx, y + 10, lx, 140, INK, 1.5)
        s.rect(lx - 8, 142, 16, 16, INK)

    s.circle(1300, 190, 8, "#FFFFFF", INK, 3)
    s.poly("60,198 60,206 1280,206 1280,198", GREY, 2, "none", "6 5")
    s.text(60, 232, "No alarm until 28 Nov: plant records alone open analyses 1–5.", 20, BODY)
    s.text(1324, 232, "6–8  pressure LO  ·  9–14  see (b)", 21, INK, 500, COND, "end")
    s.line(20, 254, 1324, 254, "#D6D3CA", 2)

    s.text(20, 284, "(b) 1 December: reactor pressure (kPa) and analyses 9–14", 24, INK, 700, COND)
    for y, txt, col, dash, w in ((352, "SIS trip 2900", AMBER_DK, "12 6", 700),
                                 (404, "HIHI 2800", BLUE, "4 4", 700),
                                 (430, "HI 2750", SEC, "2 5", 400),
                                 (534, "LO 2550", SEC, "2 5", 400)):
        s.line(150, y, 1300, y, col, 2, dash)
        s.text(142, y + 7, txt, 20, col, w, COND, "end")

    pts = [(150.6, 484.3, "9"), (413.3, 534.2, "10"), (1046.3, 429.5, "11"),
           (1125.4, 403.8, "12"), (1262.4, 351.9, "13"), (1300, 339.9, "14")]
    s.poly("150.6,484.3 413.3,534.2 489.8,537.6 1046.3,429.5 1125.4,403.8 1262.4,351.9 "
           "1300,339.9", INK, 3.5)
    for cx, cy, n in pts:
        s.circle(cx, cy, 15, INK)
        s.text(cx, cy + 6, n, 17 if n == "9" else 16, "#FFFFFF", 700, SANS, "middle")

    s.text(172, 456, "feed flow lost", 21, INK, 600, COND)
    s.text(432, 506, "pressure LO", 21, INK, 600, COND)
    s.text(1062, 458, "HI", 21, INK, 600, COND)
    s.text(1110, 384, "HIHI: B1 does not act", 21, BLUE, 700, COND, "end")
    s.text(1240, 334, "SIS trip", 21, AMBER_DK, 700, COND, "end")
    s.text(1324, 306, "still rising", 21, INK, 600, COND, "end")

    s.line(150, 580, 1300, 580, INK, 2.5)
    for x, t in ((150, "00:00"), (379.5, "00:30"), (609, "01:00"), (838.5, "01:30"),
                 (1068, "02:00"), (1297.5, "02:30")):
        s.line(x, 574, x, 586, INK, 2)
        s.text(x, 608, t, 20, SEC, 400, SANS, "middle")
    s.save("fig2_run_a_timeline.svg")


# ══════════════════════════════════════════════ Fig. 3 — Phase A
def fig3():
    s = Svg(672, 840, 3.5)
    x, w, y = 20, 632, 20

    h = 14 + 26 + 8 + 3 * 26 + 14
    s.rect(x, y, w, h, GREY_BG, GREY_LINE, 2, 8)
    s.text(x + 18, y + 38, "Inputs known at t_now", 24, INK, 700, COND)
    for i, t in enumerate(("Masked process series and alarms",
                           "Work orders and channel states recorded so far",
                           "Declared design basis and bowtie diagram")):
        s.text(x + 18, y + 70 + i * 26, t, 20, BODY)
    y += h
    s.arrow_down(x + w / 2, y + 6, y + 40)
    y += 46

    rows = [("Design basis", "barriers, ladder, validity limits"),
            ("Current state", "values with rates, voted channels"),
            ("Demand outcome", "detect, decide, act, per barrier"),
            ("Top-event frequency", "design vs now, two engines")]
    checks = ["C1  Validity envelope", "C2  PFD decomposition", "C3  Window compression",
              "C4  Redundancy observability", "C5  Decidability gaps", "C6  Side effects",
              "C7  Distance and rate", "C8  Threat persistence"]
    h = 16 + 34 + 16 + len(rows) * 32 + 18 + 28 + 10 + 4 * 38 + 16
    s.rect(x, y, w, h, "#FFFFFF", BLUE, 2.5, 8)
    s.text(x + 18, y + 44, "Phase A", 28, BLUE, 700, COND)
    s.rect(x + w - 178, y + 20, 160, 30, BLUE_BG, BLUE, 1.5, 15)
    s.text(x + w - 98, y + 41, "Python, no LLM", 20, BLUE_DK, 600, SANS, "middle")
    ry = y + 82
    for lab, val in rows:
        s.text(x + 18, ry, lab, 21, INK, 700, COND)
        s.text(x + 248, ry, val, 20, BODY)
        ry += 32
    s.line(x + 18, ry - 4, x + w - 18, ry - 4, "#C9D5E1", 1.5)
    s.text(x + 18, ry + 26, "Eight cross-checks", 21, INK, 700, COND)
    cy = ry + 42
    for i, c in enumerate(checks):
        cx = x + 18 + (i % 2) * 300
        if i % 2 == 0 and i:
            cy += 38
        s.rect(cx, cy, 288, 30, BLUE_BG, BLUE_LINE, 1.5, 6)
        s.text(cx + 10, cy + 21, c, 20, INK, 500, COND)
    y += h
    s.arrow_down(x + w / 2, y + 6, y + 40)
    y += 46

    body = "Every value is tagged as reading, computed or assumption. No conclusion is drawn."
    hb = 14 + 26 + 10 + s.height_of(body, w - 36, 20) + 20 + 14
    s.rect(x, y, w, hb, "#FFFFFF", INK, 2.5, 8)
    s.text(x + 18, y + 38, "Closed evidence for Phase B", 24, INK, 700, COND)
    s.wrap(x + 18, y + 70, body, w - 36, 20, BODY)
    s.h = y + hb + 20
    s.save("fig3_phase_a.svg")


# ══════════════════════════════════════════════ Fig. 4 — Phase B
def fig4():
    s = Svg(672, 900, 3.5)
    x, w, y = 20, 632, 20
    half = (w - 16) / 2

    for i, (ttl, sub, col) in enumerate(
            (("Method", "skill, 4 references, bowtie diagram", INK),
             ("Evidence", "closed Phase A, as text and JSON", BLUE))):
        bx = x + i * (half + 16)
        s.rect(bx, y, half, 108, "#FFFFFF", col, 2.5 if col == BLUE else 2, 8)
        s.text(bx + 16, y + 38, ttl, 24, col, 700, COND)
        s.wrap(bx + 16, y + 70, sub, half - 32, 20, BODY)
    y += 108
    s.poly(f"{x + half / 2},{y + 4} {x + half / 2},{y + 22} "
           f"{x + w - half / 2},{y + 22} {x + w - half / 2},{y + 4}", INK, 2.5)
    s.arrow_down(x + w / 2, y + 22, y + 52)
    y += 58

    chips = ["tools", "files", "memory", "network", "earlier analyses"]
    h = 16 + 34 + 10 + 30 + 12 + 28 + 10 + 34 + 16
    s.rect(x, y, w, h, AMBER_BG, AMBER, 2.5, 10, "10 6")
    s.text(x + 18, y + 44, "Phase B: a fresh session per analysis", 26, AMBER_DK, 700, COND)
    s.text(x + 18, y + 78, "Claude Opus 5 or GPT-6 Astra, identical input bytes", 20, BODY)
    s.text(x + 18, y + 116, "Not available in the session", 21, INK, 700, COND)
    cx = x + 18
    for c in chips:
        cw = len(c) * 11 + 24
        s.rect(cx, y + 130, cw, 32, "#FFFFFF", INK, 1.5, 16)
        s.text(cx + cw / 2, y + 151, c, 20, INK, 400, SANS, "middle")
        s.line(cx + 10, y + 145, cx + cw - 10, y + 145, INK, 1.5)
        cx += cw + 8
    y += h
    s.arrow_down(x + w / 2, y + 6, y + 40)
    y += 46

    gates = ["no tool was available or used", "the requested model answered",
             "every report section is present", "no data-provenance term leaked"]
    h = 14 + 30 + 12 + len(gates) * 28 + 14
    s.rect(x, y, w, h, "#FFFFFF", INK, 2, 8)
    s.text(x + 18, y + 38, "Answer accepted only if", 24, INK, 700, COND)
    for i, g in enumerate(gates):
        s.text(x + 18, y + 72 + i * 28, str(i + 1), 20, INK, 700, SANS)
        s.text(x + 44, y + 72 + i * 28, g, 20, BODY)
    y += h

    s.line(x + w / 2, y + 4, x + w / 2, y + 22, INK, 2.5)
    s.poly(f"{x + half / 2},{y + 22} {x + w - half / 2},{y + 22}", INK, 2.5)
    s.arrow_down(x + half / 2, y + 22, y + 52)
    s.arrow_down(x + w - half / 2, y + 22, y + 52)
    y += 58

    outs = [("Yes: report", "decision, barrier states, evidence strength; human decision pending",
             INK, "#FFFFFF", 2.5, None),
            ("No: rejected", "archived, then redone in a new session", GREY, GREY_BG, 2, "8 5")]
    hb = 0
    for i, (ttl, sub, col, bg, sw, dash) in enumerate(outs):
        bx = x + i * (half + 16)
        hh = 14 + 30 + 10 + s.height_of(sub, half - 32, 20) + 20 + 14
        hb = max(hb, hh)
        s.rect(bx, y, half, hh, bg, col, sw, 8, dash)
        s.text(bx + 16, y + 38, ttl, 24, INK, 700, COND)
        s.wrap(bx + 16, y + 70, sub, half - 32, 20, BODY)
    s.h = y + hb + 20
    s.save("fig4_phase_b.svg")


for f in (fig1, fig2, fig3, fig4):
    f()
