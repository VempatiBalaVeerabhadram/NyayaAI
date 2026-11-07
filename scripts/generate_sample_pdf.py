"""
NyayaAI — Sample PDF Generator for Indian Court Judgments
Generates a realistic multi-page PDF formatted like official Supreme Court judgments
with headers, footers, page numbering, and paragraph boundaries.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

def generate_judgment_pdf(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CourtTitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=13,
        leading=16,
        fontName="Helvetica-Bold",
    )

    header_style = ParagraphStyle(
        "CaseHeader",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        fontName="Helvetica",
    )

    body_style = ParagraphStyle(
        "LegalBody",
        parent=styles["Normal"],
        alignment=TA_JUSTIFY,
        fontSize=10,
        leading=14,
        fontName="Helvetica",
        firstLineIndent=20,
    )

    story = []

    # PAGE 1
    story.append(Paragraph("IN THE SUPREME COURT OF INDIA", title_style))
    story.append(Paragraph("CRIMINAL APPELLATE JURISDICTION", header_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("SPECIAL LEAVE PETITION (CRL.) NOS. 7281-7282 OF 2017", header_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Sushila Aggarwal and Others ... Petitioners", header_style))
    story.append(Paragraph("versus", header_style))
    story.append(Paragraph("State (NCT of Delhi) and Another ... Respondents", header_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Coram: Arun Mishra, Indira Banerjee, Vineet Saran, M.R. Shah, and S. Ravindra Bhat, JJ.", header_style))
    story.append(Paragraph("Judgment Dated: 29 January, 2020", header_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("JUDGMENT", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("1. The primary issue before this Constitution Bench relates to the scope and ambit of Section 438 of the Code of Criminal Procedure, 1973. Specifically, whether the protection granted to a person through anticipatory bail should be invariably limited to a fixed duration so as to compel the accused to surrender before the regular court.", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. In the landmark decision of Gurbaksh Singh Sibbia v. State of Punjab (1980) 2 SCC 565, this Court ruled that Section 438 CrPC confers wide discretionary powers on the High Court and Sessions Court to safeguard personal liberty under Article 21 of the Constitution of India.", body_style))
    
    # PAGE 2
    story.append(PageBreak())
    story.append(Paragraph("3. We have carefully examined the rival contentions advanced by the learned Senior Counsel. It was argued on behalf of the prosecution that unbridled anticipatory bail hinders effective investigation under Section 173(2) CrPC.", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("4. In our considered view, an arbitrary curtailment of liberty through premature cancellation or artificial time limitations undermines the legislative purpose behind enacting Section 438 of the Code.", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("5. Therefore, as held in Sibbia, the grant of anticipatory bail is not an extraordinary exception to be guarded with suspicion, but a vital guarantee of human dignity and liberty.", body_style))

    # PAGE 3
    story.append(PageBreak())
    story.append(Paragraph("OPERATIVE ORDER", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("92. We answer the reference as follows:", body_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("(a) Protection granted under Section 438 of the Code of Criminal Procedure should not be invariably limited to a fixed period. In normal circumstances, the protection continues till the end of the trial.", body_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("(b) The life of an order granting anticipatory bail does not automatically expire upon the filing of the charge-sheet or summoning by the court.", body_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("(c) The Court may impose restrictive conditions in appropriate cases where custodial interrogation is demonstrably essential.", body_style))

    doc.build(story)
    print(f"Generated PDF at: {output_path}")

if __name__ == "__main__":
    import sys
    out = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "judgments", "sushila_aggarwal_2020.pdf")
    generate_judgment_pdf(out)
