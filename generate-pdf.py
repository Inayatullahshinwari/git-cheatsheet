#!/usr/bin/env python3
"""Generate a professional PDF from git-cheatsheet commands."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import re
import sys
import os

# Colors
BG = HexColor("#0a0a0a")
FG = HexColor("#e4e4e7")
MUTED = HexColor("#71717a")
ACCENT = HexColor("#22c55e")
ORANGE = HexColor("#f97316")
BLUE = HexColor("#60a5fa")
CODE_BG = HexColor("#1a1a1a")
BORDER = HexColor("#2a2a2a")
CARD_BG = HexColor("#111113")

# Category colors
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

# Extract commands from HTML
def extract_commands(html_path):
    with open(html_path, "r") as f:
        content = f.read()
    
    # Find the commands array
    match = re.search(r'commands:\s*\[(.*?)\n\s*\],', content, re.DOTALL)
    if not match:
        print("ERROR: Could not find commands array", file=sys.stderr)
        sys.exit(1)
    
    commands_text = match.group(1)
    commands = []
    
    # Parse each command entry
    for m in re.finditer(r"\{\s*cat:\s*'(\w+)'.*?title:\s*'([^']+)'.*?code:\s*'([^']*)'.*?desc:\s*'([^']*)'", commands_text, re.DOTALL):
        cat, title, code, desc = m.groups()
        code = code.replace("\\n", "\n").replace("\\'", "'")
        commands.append({
            "cat": cat,
            "title": title,
            "code": code,
            "desc": desc,
        })
    
    return commands

def build_pdf(commands, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=15*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm,
        title="Git Cheatsheet",
        author="Inayatullah Shinwari",
    )
    
    width = doc.width
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        "PdfTitle", fontName="Helvetica-Bold", fontSize=28, textColor=FG,
        leading=34, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "PdfSubtitle", fontName="Helvetica", fontSize=11, textColor=MUTED,
        leading=16, spaceAfter=20,
    ))
    styles.add(ParagraphStyle(
        "PdfCatTitle", fontName="Helvetica-Bold", fontSize=14, textColor=FG,
        leading=20, spaceBefore=16, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "PdfCmdTitle", fontName="Helvetica-Bold", fontSize=9, textColor=FG,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        "PdfCode", fontName="Courier", fontSize=8.5, textColor=ACCENT,
        leading=13, spaceBefore=2, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        "PdfDesc", fontName="Helvetica", fontSize=7.5, textColor=MUTED,
        leading=11, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "PdfFooter", fontName="Helvetica", fontSize=7, textColor=MUTED,
        alignment=TA_CENTER,
    ))
    
    # Cover page - dark background
    from reportlab.platypus import Frame, PageTemplate, BaseDocTemplate
    from reportlab.lib.colors import Color
    
    # Create cover page with dark background
    cover_style = ParagraphStyle(
        "CoverTitle", fontName="Helvetica-Bold", fontSize=32, textColor=FG,
        leading=38, spaceAfter=6,
    )
    cover_sub = ParagraphStyle(
        "CoverSub", fontName="Helvetica", fontSize=12, textColor=MUTED,
        leading=18, spaceAfter=6,
    )
    cover_ver = ParagraphStyle(
        "CoverVer", fontName="Courier", fontSize=10, textColor=ACCENT,
        leading=14, spaceAfter=20,
    )
    
    # Build cover as a table with dark background
    cover_data = [[Paragraph("Git Cheatsheet", cover_style)]]
    cover_table = Table(cover_data, colWidths=[width])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 80*mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 80*mm),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 10*mm))
    
    sub_data = [[Paragraph("The Ultimate Reference — 80+ Essential Commands", cover_sub)]]
    sub_table = Table(sub_data, colWidths=[width])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 6*mm))
    
    ver_data = [[Paragraph("Commands for Git v2.54.0", cover_ver)]]
    ver_table = Table(ver_data, colWidths=[width])
    ver_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(ver_table)
    story.append(Spacer(1, 30*mm))
    
    author_data = [[Paragraph("By Inayatullah Shinwari", cover_sub)]]
    author_table = Table(author_data, colWidths=[width])
    author_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(author_table)
    story.append(Spacer(1, 4*mm))
    
    link_data = [[Paragraph("https://inayatullahshinwari.github.io/git-cheatsheet", cover_sub)]]
    link_table = Table(link_data, colWidths=[width])
    link_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(link_table)
    story.append(PageBreak())
    
    # Group commands by category
    categories = {}
    for cmd in commands:
        categories.setdefault(cmd["cat"], []).append(cmd)
    
    for cat_key in ["basics", "staging", "branching", "remote", "undo", "advanced", "config", "workflow"]:
        if cat_key not in categories:
            continue
        
        cat_cmds = categories[cat_key]
        color = CAT_COLORS[cat_key]
        
        # Category header
        story.append(Paragraph(CAT_LABELS[cat_key], styles["PdfCatTitle"]))
        
        # Build table: 2 columns
        col_width = (width - 6*mm) / 2
        data = []
        row_styles = []
        
        for i in range(0, len(cat_cmds), 2):
            row_data = []
            for j in range(2):
                if i + j < len(cat_cmds):
                    cmd = cat_cmds[i + j]
                    cell_parts = []
                    cell_parts.append(Paragraph(cmd["title"], styles["PdfCmdTitle"]))
                    
                    # Code block
                    code_lines = cmd["code"].split("\n")
                    for line in code_lines:
                        cell_parts.append(Paragraph(f"  $ {line}", styles["PdfCode"]))
                    
                    cell_parts.append(Paragraph(cmd["desc"], styles["PdfDesc"]))
                    
                    cell_content = cell_parts
                    row_data.append(cell_content)
                else:
                    row_data.append([])
            
            data.append(row_data)
        
        # Create table
        table = Table(data, colWidths=[col_width, col_width], repeatRows=0)
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 6*mm))
    
    # Footer
    story.append(PageBreak())
    story.append(Spacer(1, 80*mm))
    story.append(Paragraph("Built with ❤️ by Inayatullah Shinwari", styles["PdfFooter"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("https://inayatullahshinwari.github.io/git-cheatsheet", styles["PdfFooter"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Support: Liberapay • Ko-fi • Crypto (USDT TRC20)", styles["PdfFooter"]))
    
    doc.build(story)
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    output_path = os.path.join(os.path.dirname(__file__), "git-cheatsheet.pdf")
    
    commands = extract_commands(html_path)
    print(f"Extracted {len(commands)} commands")
    build_pdf(commands, output_path)
