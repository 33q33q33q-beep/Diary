#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""USER-MANUAL.md から USER-MANUAL.pdf を生成（ReportLab + 日本語CIDフォント）"""
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# 日本語（縦書き用CIDだが横組みでも利用可）
FONT = "HeiseiMin-W3"
pdfmetrics.registerFont(UnicodeCIDFont(FONT))


def styles():
    return {
        "h1": ParagraphStyle(
            name="H1",
            fontName=FONT,
            fontSize=15,
            leading=20,
            spaceAfter=8,
            spaceBefore=4,
        ),
        "h2": ParagraphStyle(
            name="H2",
            fontName=FONT,
            fontSize=11.5,
            leading=15,
            spaceAfter=5,
            spaceBefore=10,
        ),
        "body": ParagraphStyle(
            name="Body",
            fontName=FONT,
            fontSize=9.2,
            leading=13,
            spaceAfter=3,
        ),
        "small": ParagraphStyle(
            name="Small",
            fontName=FONT,
            fontSize=8,
            leading=11,
            spaceAfter=2,
        ),
    }


def fmt_inline(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r'<font face="Courier" size="8">\1</font>', s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"<b>\1</b>", s)
    return s


def parse_md_to_story(text, st):
    story = []
    lines = text.split("\n")
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        raw = line.rstrip()
        s = raw.strip()

        if not s:
            i += 1
            continue
        if s == "---":
            story.append(Spacer(1, 5))
            i += 1
            continue

        if s.startswith("# ") and not s.startswith("## "):
            story.append(Paragraph(fmt_inline(s[2:]), st["h1"]))
            i += 1
            continue
        if s.startswith("## "):
            story.append(Paragraph(fmt_inline(s[3:]), st["h2"]))
            i += 1
            continue

        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                row_line = lines[i].strip()
                if re.match(r"^\|[\s\-:|]+\|$", row_line):
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.split("|")[1:-1]]
                if cells:
                    rows.append([fmt_inline(c) for c in cells])
                i += 1
            if rows:
                data = [[Paragraph(c, st["small"]) for c in r] for r in rows]
                cw = len(rows[0])
                if cw == 3:
                    w = [48 * mm, 42 * mm, 88 * mm]
                elif cw == 2:
                    w = [75 * mm, 103 * mm]
                else:
                    w = [178 * mm / cw] * cw
                t = Table(data, colWidths=w, repeatRows=1)
                t.setStyle(
                    TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
                            ("TOPPADDING", (0, 0), (-1, -1), 3),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 6))
            continue

        if s.startswith("- "):
            story.append(Paragraph("・" + fmt_inline(s[2:]), st["body"]))
            i += 1
            continue
        if re.match(r"^\d+\.\s", s):
            story.append(Paragraph(fmt_inline(s), st["body"]))
            i += 1
            continue
        if s.startswith("*") and s.endswith("*") and len(s) > 2:
            inner = s[1:-1]
            story.append(Paragraph(fmt_inline(inner), st["small"]))
            i += 1
            continue

        story.append(Paragraph(fmt_inline(s), st["body"]))
        i += 1

    return story


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_path = os.path.join(root, "USER-MANUAL.md")
    pdf_path = os.path.join(root, "USER-MANUAL.pdf")
    if not os.path.isfile(md_path):
        print("Missing USER-MANUAL.md", file=sys.stderr)
        sys.exit(1)

    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="私の日記 Webアプリ マニュアル",
    )
    st = styles()
    story = parse_md_to_story(text, st)
    doc.build(story)
    print("Wrote", pdf_path)


if __name__ == "__main__":
    main()
