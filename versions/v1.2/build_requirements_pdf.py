"""Builds 'Hospital Directory API v1.2 - Requirements.pdf' (short technical edition).

Source of truth: requirements/*/requirement.md and Hospital_Directory_API_OpenAPI_v1.2.yaml.
Styling matches the original v1.2 bundle (21 Sep 2026): same palette, fonts and cover layout.
Scope: the 3 items kept after the 4 Nov 2026 meeting (first-names and encounter_type dropped).

Run:  python build_requirements_pdf.py
Needs: reportlab, arabic-reshaper, python-bidi, Windows Segoe UI + Consolas fonts.
"""
import re
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle, XPreformatted)

HERE = Path(__file__).parent
OUT = HERE / "Hospital Directory API v1.2 - Requirements.pdf"
FONTS = Path("C:/Windows/Fonts")
REPO_URL = "https://github.com/aidepartmentrah-pixel/RESTful-API-Integration"
GENERATED = "4 November 2026"

pdfmetrics.registerFont(TTFont("UI", str(FONTS / "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("UI-B", str(FONTS / "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Mono", str(FONTS / "consola.ttf")))
pdfmetrics.registerFontFamily("UI", normal="UI", bold="UI-B", italic="UI", boldItalic="UI-B")

# Palette sampled from the original bundle.
BAND = colors.HexColor("#b5573b")       # cover band, table headers, bullets
RUST = colors.HexColor("#8c4028")       # titles, headings, inline accents
INK = colors.HexColor("#2b2b2e")
MUTED = colors.HexColor("#6b6f76")
BAND_SUB = colors.HexColor("#ebd9d1")   # URL text on the cover band
RULE = colors.HexColor("#e2e4e9")
CODE_BG = colors.HexColor("#f4f5f7")
ZEBRA = colors.HexColor("#fafafb")

PAGE_W, PAGE_H = LETTER
MARGIN_X = 0.95 * 72                    # matches the original's ~67pt left edge
W = PAGE_W - 2 * MARGIN_X

cover_t = ParagraphStyle("cover_t", fontName="UI-B", fontSize=25, leading=30, textColor=RUST)
cover_sub = ParagraphStyle("cover_sub", fontName="UI", fontSize=12.5, leading=17, textColor=MUTED)
meta_k = ParagraphStyle("meta_k", fontName="UI-B", fontSize=9.5, leading=13, textColor=MUTED)
meta_v = ParagraphStyle("meta_v", fontName="UI", fontSize=9.5, leading=13, textColor=MUTED)
toc_h = ParagraphStyle("toc_h", fontName="UI-B", fontSize=12.5, leading=16, textColor=INK, spaceAfter=4)
toc = ParagraphStyle("toc", fontName="UI", fontSize=10.5, leading=16, textColor=INK)
h1 = ParagraphStyle("h1", fontName="UI-B", fontSize=17, leading=21, textColor=RUST,
                    spaceBefore=16, spaceAfter=2)
h1_sub = ParagraphStyle("h1_sub", fontName="UI-B", fontSize=11, leading=14, textColor=INK, spaceAfter=4)
h2 = ParagraphStyle("h2", fontName="UI-B", fontSize=10.5, leading=13, textColor=RUST,
                    spaceBefore=7, spaceAfter=3)
body = ParagraphStyle("body", fontName="UI", fontSize=9.3, leading=13.2, textColor=INK)
why = ParagraphStyle("why", parent=body, textColor=MUTED, leftIndent=8, borderPadding=0)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=12, bulletIndent=2, spaceAfter=1.5,
                        bulletColor=BAND, bulletFontSize=7)
cell = ParagraphStyle("cell", parent=body, fontSize=8.5, leading=11.5)
cell_h = ParagraphStyle("cell_h", parent=cell, fontName="UI-B", textColor=colors.white)
code = ParagraphStyle("code", fontName="Mono", fontSize=8.3, leading=11, textColor=INK)

ARABIC = re.compile(r"[\u0600-\u06FF][\u0600-\u06FF ]*[\u0600-\u06FF]|[\u0600-\u06FF]")


def ar(text):
    """Shape + reorder Arabic for a left-to-right PDF line."""
    return get_display(arabic_reshaper.reshape(text))


def c(text):
    """Inline code, rust like the original."""
    return f'<font face="Mono" size="8.6" color="#8c4028">{text}</font>'


def P(text, style=body):
    return Paragraph(text, style)


def bullets(items):
    return [Paragraph(t, bullet, bulletText="\u25cf") for t in items]


def why_line(text):
    return P(f'<font name="UI-B" color="#6b6f76">Why:</font> {text}', why)


def table(rows, widths):
    data = [[Paragraph(str(x), cell_h if i == 0 else cell) for x in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BAND),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, RULE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for r in range(2, len(rows), 2):
        style.append(("BACKGROUND", (0, r), (-1, r), ZEBRA))
    t.setStyle(TableStyle(style))
    return t


def block(src):
    """Code block. Arabic runs are shaped and switched to Segoe UI (Consolas has no Arabic)."""
    src = src.strip("\n").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    src = ARABIC.sub(lambda m: f'<font face="UI">{ar(m.group(0))}</font>', src)
    pre = XPreformatted(src, code)
    t = Table([[pre]], colWidths=[W], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def params(rows, widths):
    return KeepTogether([P("Parameters", h2), table(rows, widths)])


def resp(src, label="Response &mdash; " + c("200 OK")):
    return KeepTogether([P(label, h2), block(src)])


def section(num, title, endpoint):
    return [CondPageBreak(60 * mm), P(f"Requirement {num}", h1), P(f"{title} &mdash; {endpoint}", h1_sub)]


story = []

# ------------------------------------------------------------------- cover
meta = Table(
    [[P(k, meta_k), P(v, meta_v)] for k, v in [
        ("Document", "Technical requirements, v1.2"),
        ("Source repository", REPO_URL),
        ("Spec file", "Hospital_Directory_API_OpenAPI_v1.2.yaml (attached separately)"),
        ("Generated", GENERATED),
        ("Status", "Internal proposal -- not yet submitted to / accepted by the vendor"),
    ]],
    colWidths=[47 * mm, W - 47 * mm - 20], hAlign="CENTER")
meta.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))
rule = Table([[""]], colWidths=[W], rowHeights=[1])
rule.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.6, RULE)]))

contents = [
    ("", "Conventions that apply to every requirement"),
    ("1.", "Proposed addendum to OpenAPI v1.1 &mdash; father-name candidate lookup"),
    ("2.", "Proposed addendum to OpenAPI v1.1 &mdash; worker section/administration names"),
    ("3.", "Proposed new endpoint &mdash; live ER visit roster (for HCopilot)"),
]

story += [
    Spacer(1, 132),   # clears the band; the title sits on its lower edge like the original
    P("Hospital Directory API<br/>Version 1.2 -- Proposed Additions", cover_t),
    Spacer(1, 14),
    P("Three requests to extend the OpenAPI v1.1 contract currently in production. Each has been "
      "built and verified against our reference mock; none has been tested against the real server yet.",
      cover_sub),
    Spacer(1, 20),
    rule,
    Spacer(1, 6),
    meta,
    Spacer(1, 36),
    P("Contents", toc_h),
    *[P(f"{n} {t}" if n else t, toc) for n, t in contents],
    PageBreak(),
]

# ------------------------------------------------------------- conventions
story += [
    P("Conventions", h1),
    P("Apply to every requirement below", h1_sub),
    *bullets([
        "Auth: " + c("X-API-Key") + " header. Missing or invalid key returns " + c("401 UNAUTHORIZED") + ".",
        "Error body: " + c('{"error": "&lt;CODE&gt;", "message": "&lt;text&gt;"}') + ". Codes used: "
        + c("UNAUTHORIZED") + " (401), " + c("VALIDATION_ERROR") + " (422), " + c("SERVER_ERROR") + " (500).",
        "A search with no matches returns " + c("200") + " with an empty list, never " + c("404") + ".",
        "All IDs are strings, even when stored as numbers.",
        "Display names use the English value when stored, otherwise the Arabic value.",
        c("Content-Type: application/json; charset=utf-8") + ". Arabic text must arrive as valid UTF-8; "
        "we have seen Arabic arrive garbled from the current API, so please verify this on each new endpoint.",
        "Read-only. No write endpoints are requested.",
        "Everything not listed in this document is unchanged from v1.1.",
    ]),
]

# ------------------------------------------------------------ requirement 1
story += section(1, "Father-name candidate lookup", c("GET /patients/father-names"))
story += [
    why_line("To find a patient, HCAT currently tries up to 32 common father names one by one against "
             + c("GET /patients") + ". This endpoint replaces the guessing with a single lookup."),
    Spacer(1, 2),
    P("Returns the distinct father names on file for a first + last name pair. It does not return patient "
      "records: once the user picks a father name, the caller uses the existing " + c("GET /patients")
      + " with all three names."),
    params([
        ["Name", "Required", "Rule"],
        [c("first_name"), "Yes", "Non-blank (whitespace-only is rejected). Case-insensitive substring match "
                                  "on the Arabic or English column, same as " + c("/patients") + "."],
        [c("last_name"), "Yes", "Same rule as " + c("first_name") + "."],
        [c("limit"), "No", "Integer 1..200, default 50."],
    ], [28 * mm, 20 * mm, W - 48 * mm]),
    resp("""
{
  "success": true,
  "first_name": "عباس",
  "last_name": "زهرالدين",
  "candidates": [
    {"father_name": "محمد", "patient_count": 20},
    {"father_name": "حسن", "patient_count": 20},
    {"father_name": "أحمد", "patient_count": 1}
  ],
  "total_candidates": 3
}"""),
    P("Rules", h2),
    *bullets([
        "One entry per distinct, non-blank father name. " + c("patient_count") + " = number of records with "
        "that exact first + father + last combination.",
        "Order: " + c("patient_count") + " descending, then " + c("father_name") + " alphabetically, so the "
        "list is identical between calls.",
        c("total_candidates") + " = number of distinct candidates <b>before</b> " + c("limit")
        + " is applied (lets the UI show \u201cshowing 50 of 120\u201d).",
        "No " + c("patient_id") + " or other patient fields in the response.",
    ]),
    P("Errors", h2),
    P(c("401") + " bad key &nbsp;&nbsp;|&nbsp;&nbsp; " + c("422") + " missing/blank " + c("first_name")
      + " or " + c("last_name") + ", or " + c("limit") + " out of range &nbsp;&nbsp;|&nbsp;&nbsp; "
      + c("500") + " server error"),
]

# ------------------------------------------------------------ requirement 2
story += section(2, "Worker section and administration names",
                 c("Worker") + " in " + c("GET /workers") + " and " + c("GET /workers/{employee_id}"))
story += [
    why_line(c("section_id") + " and " + c("administration_id") + " are always " + c("null")
             + " today, and an ID alone means nothing outside your system. HCAT users cannot tell which "
             "section or administration a worker belongs to."),
    Spacer(1, 2),
    P("Two parts, both on the existing " + c("Worker") + " object:"),
    *bullets([
        "<b>Populate</b> the existing " + c("section_id") + " and " + c("administration_id")
        + " fields from the HR application.",
        "<b>Add</b> the resolved display names, the same way " + c("department_name")
        + " is already resolved from " + c("department_id") + ".",
    ]),
    Spacer(1, 4),
    table([
        ["Field", "Type", "Value"],
        [c("section_name"), "string, nullable",
         "Name resolved from " + c("section_id") + ". " + c("null") + " if the ID is null or cannot be resolved."],
        [c("administration_name"), "string, nullable",
         "Name resolved from " + c("administration_id") + ". " + c("null")
         + " if the ID is null or cannot be resolved."],
    ], [40 * mm, 28 * mm, W - 68 * mm]),
    Spacer(1, 5),
    P("No change to parameters, pagination or errors."),
]

# ------------------------------------------------------------ requirement 3
story += section(3, "Live ER visit roster (for HCopilot)", c("GET /er/current-visits"))
story += [
    why_line("HCopilot nurses currently search for each ER patient by hand before starting a handover. "
             "A live roster lets them pick from a list. Today the roster only exists on the ER web page ("
             + c("meraj:8080") + "), which has no JSON API."),
    Spacer(1, 2),
    P("Returns every patient currently in the ER. Please expose it with the same host, auth and "
      "conventions as the Directory API; the exact path is your choice."),
    P("Request", h2),
    P("No parameters. " + c("X-API-Key") + " auth. <b>No pagination:</b> every call returns the complete "
      "list. HCopilot detects departures by comparing " + c("er_visit_id") + " sets between polls, so a "
      "partial page would make patients look departed. ER headcount is dozens, not thousands."),
    resp("""
{
  "success": true,
  "items": [
    {
      "er_visit_id": "48213",
      "first_name": "عباس",
      "father_name": "محمد",
      "last_name": "زهرالدين",
      "arrival_time": "2026-09-18T14:32:00+03:00",
      "gender": null,
      "age": null,
      "chief_complaint": null
    }
  ],
  "total": 1
}"""),
    KeepTogether([
        P("Fields", h2),
        table([
            ["Field", "Format", "Notes"],
            [c("er_visit_id"), "string, required", "Stable for the whole visit. Used as the comparison key."],
            [c("first_name") + ", " + c("father_name") + ", " + c("last_name"), "string",
             "Plain values. No Arabic/English split needed."],
            [c("arrival_time"), "ISO-8601 with offset",
             "<b>One</b> combined field (the ER page currently splits it into date and time)."],
            [c("gender"), "string or null", "Open item: which values?"],
            [c("age"), "integer or null", "Open item: " + c("birth_date") + " preferred (age goes stale)."],
            [c("chief_complaint"), "string or null", "Open item: a coded value is preferred over free text."],
        ], [50 * mm, 34 * mm, W - 84 * mm]),
    ]),
    P("Rules", h2),
    *bullets([
        "Order: " + c("arrival_time") + " ascending (earliest first), stable between polls.",
        c("total") + " = number of items.",
        "Not requested: " + c("doctor_name") + " (always empty in practice); bed, triage time and departure "
        "time (HCopilot manages these itself).",
    ]),
    KeepTogether([
        P("Please confirm", h2),
        *bullets([
            "Is \u201ccreation time\u201d the arrival time, and which timezone is it written in (we assume UTC+3)?",
            "Which values " + c("gender") + " will contain.",
            "Whether " + c("birth_date") + " can be returned instead of " + c("age") + ".",
            "Whether " + c("chief_complaint") + " is coded or free text.",
            "That the ordering can be guaranteed, and that UTF-8 is correct on this endpoint.",
        ]),
    ]),
]


# ----------------------------------------------------------------- chrome
def on_cover(canv, doc):
    canv.saveState()
    band_h = 165.6
    canv.setFillColor(BAND)
    canv.rect(0, PAGE_H - band_h, PAGE_W, band_h, stroke=0, fill=1)
    canv.setFillColor(colors.white)
    canv.setFont("UI-B", 12)
    canv.drawString(MARGIN_X - 5, PAGE_H - 62, "RAH -- AI Department")
    canv.setFillColor(BAND_SUB)
    canv.setFont("UI", 9.5)
    canv.drawRightString(PAGE_W - MARGIN_X + 5, PAGE_H - 62, REPO_URL)
    canv.restoreState()


def on_page(canv, doc):
    canv.saveState()
    top = PAGE_H - 36
    canv.setFillColor(RUST)
    canv.setFont("UI-B", 8.3)
    canv.drawString(MARGIN_X - 5, top, "Hospital Directory API - v1.2 Requirements")
    canv.setFillColor(MUTED)
    canv.setFont("UI", 8.3)
    canv.drawRightString(PAGE_W - MARGIN_X + 5, top, REPO_URL)
    canv.setStrokeColor(RULE)
    canv.setLineWidth(0.6)
    canv.line(MARGIN_X - 5, top - 9, PAGE_W - MARGIN_X + 5, top - 9)
    canv.line(MARGIN_X - 5, 46, PAGE_W - MARGIN_X + 5, 46)
    canv.setFont("UI", 8)
    canv.drawString(MARGIN_X - 5, 33, "Proposed additions -- not yet accepted by the vendor")
    canv.drawRightString(PAGE_W - MARGIN_X + 5, 33, f"Page {doc.page}")
    canv.restoreState()


doc = SimpleDocTemplate(str(OUT), pagesize=LETTER, leftMargin=MARGIN_X, rightMargin=MARGIN_X,
                        topMargin=62, bottomMargin=60,
                        title="Hospital Directory API v1.2 - Requirements",
                        author="RAH AI Department")
doc.build(story, onFirstPage=on_cover, onLaterPages=on_page)
print(OUT)
