#!/usr/bin/env python3
"""Generate a professional PDF from git-cheatsheet commands."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, NextPageTemplate
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re
import sys
import os

BG = HexColor("#000000")
FG = HexColor("#ffffff")
FG_SOFT = HexColor("#e4e4e7")
MUTED = HexColor("#71717a")
DIM = HexColor("#52525b")
ACCENT = HexColor("#22c55e")
ORANGE = HexColor("#f97316")

CAT_COLORS = {
    "basics": HexColor("#22c55e"),
    "staging": HexColor("#eab308"),
    "branching": HexColor("#3b82f6"),
    "remote": HexColor("#a855f7"),
    "undo": HexColor("#ef4444"),
    "advanced": HexColor("#06b6d4"),
    "config": HexColor("#ec4899"),
    "workflow": HexColor("#6366f1"),
}

CAT_LABELS = {
    "basics": "Basics — Initialize, clone, and inspect",
    "staging": "Staging & Commit — Add, commit, and manage changes",
    "branching": "Branching — Create, switch, merge, rebase",
    "remote": "Remote — Push, pull, fetch, manage remotes",
    "undo": "Undo & Stash — Reset, revert, and stash",
    "advanced": "Advanced — Cherry-pick, bisect, reflog",
    "config": "Config — User, editor, credentials",
    "workflow": "Workflow — Submodules, archives, cleanup",
}

def extract_commands(html_path):
    with open(html_path, "r") as f:
        content = f.read()
    match = re.search(r'commands:\s*\[(.*?)\n\s*\],', content, re.DOTALL)
    if not match:
        print("ERROR: Could not find commands array", file=sys.stderr)
        sys.exit(1)
    commands_text = match.group(1)
    commands = []
    for m in re.finditer(r"\{\s*cat:\s*'(\w+)'.*?title:\s*'([^']+)'.*?code:\s*'([^']*)'.*?desc:\s*'([^']*)'", commands_text, re.DOTALL):
        cat, title, code, desc = m.groups()
        code = code.replace("\\n", "\n").replace("\\'", "'")
        commands.append({"cat": cat, "title": title, "code": code, "desc": desc})
    return commands

def bg_callback(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
    canvas.setFont("Courier", 6.5)
    canvas.setFillColor(DIM)
    canvas.drawRightString(doc.pagesize[0] - 15*mm, 8*mm, "github.com/Inayatullahshinwari")
    canvas.restoreState()

def make_center_table(paragraph, bg=BG, padding=0, w=None):
    data = [[paragraph]]
    t = Table(data, colWidths=[w] if w else None)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t

def build_pdf(commands, output_path):
    page_w, page_h = A4
    lm = rm = 15*mm
    tm = bm = 15*mm
    content_w = page_w - lm - rm
    content_h = page_h - tm - bm

    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=lm, rightMargin=rm,
        topMargin=tm, bottomMargin=bm,
        title="Git Cheatsheet",
        author="Inayatullah Shinwari",
    )

    frame = Frame(lm, bm, content_w, content_h)
    doc.addPageTemplates([PageTemplate(id="bg", frames=frame, onPage=bg_callback)])

    story = []
    styles = getSampleStyleSheet()

    cover_title = ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=36, textColor=FG, leading=42, spaceAfter=8)
    cover_sub = ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=13, textColor=MUTED, leading=18, spaceAfter=4)
    cover_ver = ParagraphStyle("CoverVer", fontName="Courier", fontSize=11, textColor=ACCENT, leading=15, spaceAfter=30)
    cover_author = ParagraphStyle("CoverAuthor", fontName="Helvetica", fontSize=10, textColor=DIM, leading=14, spaceAfter=4)
    cover_link = ParagraphStyle("CoverLink", fontName="Courier", fontSize=9, textColor=ORANGE, leading=13)

    styles.add(ParagraphStyle("PdfCatTitle", fontName="Helvetica-Bold", fontSize=13, textColor=FG_SOFT, leading=18, spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle("PdfCmdTitle", fontName="Helvetica-Bold", fontSize=9, textColor=FG_SOFT, leading=12))
    styles.add(ParagraphStyle("PdfCode", fontName="Courier", fontSize=8.5, textColor=ACCENT, leading=13, spaceBefore=2, spaceAfter=2))
    styles.add(ParagraphStyle("PdfDesc", fontName="Helvetica", fontSize=7.5, textColor=MUTED, leading=11, spaceAfter=6))

    support_title = ParagraphStyle("SupportTitle", fontName="Helvetica-Bold", fontSize=24, textColor=FG, leading=30, spaceAfter=8)
    support_sub = ParagraphStyle("SupportSub", fontName="Helvetica", fontSize=11, textColor=MUTED, leading=16, spaceAfter=4)
    support_foot = ParagraphStyle("SupportFoot", fontName="Helvetica", fontSize=8, textColor=DIM, leading=12, alignment=TA_CENTER)
    support_foot2 = ParagraphStyle("SupportFoot2", fontName="Courier", fontSize=8, textColor=DIM, leading=12, alignment=TA_CENTER)

    div_data = [[Paragraph("", ParagraphStyle("div", fontSize=1, leading=1))]]
    div_table = Table(div_data, colWidths=[content_w * 0.5])
    div_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#2a2a2a")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("HEIGHT", (0, 0), (-1, -1), 0.5*mm),
    ]))

    # COVER
    story.append(Spacer(1, 55*mm))
    story.append(make_center_table(Paragraph("Git Cheatsheet", cover_title), padding=8*mm, w=content_w))
    story.append(Spacer(1, 6*mm))
    story.append(make_center_table(Paragraph("The Ultimate Reference", cover_sub), w=content_w))
    story.append(Spacer(1, 2*mm))
    story.append(make_center_table(Paragraph("80+ Essential Commands", cover_sub), w=content_w))
    story.append(Spacer(1, 8*mm))
    story.append(make_center_table(Paragraph("Commands for Git v2.54.0", cover_ver), w=content_w))
    story.append(Spacer(1, 35*mm))
    story.append(make_center_table(Paragraph("By Inayatullah Shinwari", cover_author), w=content_w))
    story.append(Spacer(1, 3*mm))
    story.append(make_center_table(Paragraph("https://inayatullahshinwari.github.io/git-cheatsheet", cover_link), w=content_w))
    story.append(PageBreak())

    # COMMANDS
    categories = {}
    for cmd in commands:
        categories.setdefault(cmd["cat"], []).append(cmd)

    for cat_key in ["basics", "staging", "branching", "remote", "undo", "advanced", "config", "workflow"]:
        if cat_key not in categories:
            continue
        cat_cmds = categories[cat_key]
        story.append(Paragraph(CAT_LABELS[cat_key], styles["PdfCatTitle"]))

        col_width = (content_w - 6*mm) / 2
        data = []
        for i in range(0, len(cat_cmds), 2):
            row_data = []
            for j in range(2):
                if i + j < len(cat_cmds):
                    cmd = cat_cmds[i + j]
                    cell_parts = []
                    cell_parts.append(Paragraph(cmd["title"], styles["PdfCmdTitle"]))
                    for line in cmd["code"].split("\n"):
                        cell_parts.append(Paragraph(f"  $ {line}", styles["PdfCode"]))
                    cell_parts.append(Paragraph(cmd["desc"], styles["PdfDesc"]))
                    row_data.append(cell_parts)
                else:
                    row_data.append([])
            data.append(row_data)

        table = Table(data, colWidths=[col_width, col_width])
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 6*mm))

    # SUPPORT PAGE
    story.append(PageBreak())
    story.append(Spacer(1, 50*mm))
    story.append(make_center_table(Paragraph("Support This Project", support_title), padding=8*mm, w=content_w))
    story.append(Spacer(1, 6*mm))
    story.append(make_center_table(Paragraph("This cheatsheet is free and always will be.", support_sub), w=content_w))
    story.append(Spacer(1, 20*mm))

    support_item_label = ParagraphStyle("siLbl", fontName="Helvetica-Bold", fontSize=10, textColor=FG_SOFT, leading=14, alignment=TA_CENTER)
    support_item_value = ParagraphStyle("siVal", fontName="Courier", fontSize=9, textColor=ORANGE, leading=13, alignment=TA_CENTER)
    support_item_desc = ParagraphStyle("siDesc", fontName="Helvetica", fontSize=8, textColor=MUTED, leading=11, alignment=TA_CENTER)

    for label, value, desc in [
        ("Liberapay", "https://liberapay.com/inayatullahshinwari/donate", "Recurring donations, open-source friendly"),
        ("Ko-fi", "https://ko-fi.com/inayatullahshinwari", "One-time tips, quick and easy"),
        ("Crypto (USDT TRC20)", "TUFAAC9Zau3waUuHMnrPoaK92JbXp4YMag", "Direct wallet transfer, no fees"),
    ]:
        story.append(make_center_table(Paragraph(label, support_item_label), w=content_w))
        story.append(Spacer(1, 2*mm))
        story.append(make_center_table(Paragraph(value, support_item_value), w=content_w))
        story.append(Spacer(1, 1*mm))
        story.append(make_center_table(Paragraph(desc, support_item_desc), w=content_w))
        story.append(Spacer(1, 10*mm))

    story.append(Spacer(1, 10*mm))
    story.append(make_center_table(div_table, w=content_w))
    story.append(Spacer(1, 8*mm))
    story.append(make_center_table(Paragraph("Thank you for keeping this project alive.", ParagraphStyle("thanks", fontName="Helvetica-Oblique", fontSize=9, textColor=DIM, leading=13, alignment=TA_CENTER)), w=content_w))
    story.append(Spacer(1, 6*mm))
    story.append(make_center_table(Paragraph("Built with ❤ by Inayatullah Shinwari", support_foot), w=content_w))
    story.append(Spacer(1, 3*mm))
    story.append(make_center_table(Paragraph("https://inayatullahshinwari.github.io/git-cheatsheet", support_foot2), w=content_w))

    doc.build(story)
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    output_path = os.path.join(os.path.dirname(__file__), "git-cheatsheet.pdf")
    commands = extract_commands(html_path)
    print(f"Extracted {len(commands)} commands")
    build_pdf(commands, output_path)
