import sys
import os
import subprocess

def install_and_import(package):
    """
    Tries to import a package, and if it's missing, installs it using pip.
    This ensures the script runs without requiring manual steps from the user.
    """
    try:
        __import__(package)
    except ImportError:
        print(f"Installing missing package: {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# We need reportlab to generate actual PDF files in Python.
install_and_import("reportlab")

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Make sure documents directory exists
os.makedirs("documents", exist_ok=True)

def create_policy_pdf():
    pdf_path = "documents/company_expense_policy.pdf"
    print(f"Generating: {pdf_path}")
    
    # Create the PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    story = []
    
    # Load default stylesheets
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A365D"), # Deep blue
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2C5282"),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=10
    )

    # Document Elements
    story.append(Paragraph("Enterprise Expense & Travel Policy", title_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("1. General Policy Guidelines", heading_style))
    story.append(Paragraph(
        "This document outlines the policy governing employee business expenses at BizWhisperer Inc. "
        "All employee business expenses must serve a direct business purpose and comply with these guidelines. "
        "Failure to adhere to these guidelines may result in rejection of reimbursement requests.",
        body_style
    ))
    
    story.append(Paragraph("2. Software & Tool Subscriptions", heading_style))
    story.append(Paragraph(
        "Software subscriptions and cloud resources (SaaS, cloud instances, database licenses) "
        "must be pre-approved. Any software subscription exceeding <b>$100/month</b> requires "
        "direct approval from the CEO (Alice Johnson). Subscriptions under $100/month can "
        "be approved by the respective Department Heads. Security tools must be vetted by IT before purchase.",
        body_style
    ))
    
    story.append(Paragraph("3. Travel & Business Lodging", heading_style))
    story.append(Paragraph(
        "All business travel must be pre-approved in writing by either the Sales Director (Diana Prince) "
        "or the CEO (Alice Johnson). "
        "Employees must book flights in economy class. Business class is prohibited unless "
        "specifically authorized by the CEO for flights exceeding 8 hours. "
        "The daily meal allowance for business trips is capped at a maximum of <b>$50 per day</b>. "
        "Original receipts must be scanned and submitted within 14 days of travel completion.",
        body_style
    ))
    
    story.append(Paragraph("4. Office Supplies & Pantry Pantry Snacks", heading_style))
    story.append(Paragraph(
        "Office supplies, minor hardware accessories (cables, keyboards), and pantry snacks "
        "with a total value of <b>under $200</b> can be approved directly by the HR Assistant (George Costanza). "
        "Any purchase exceeding $200 requires CEO (Alice Johnson) approval. Bulk orders must "
        "use approved vendors listed in the internal procurement portal.",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    print("Expense Policy PDF created successfully.")

def create_strategy_pdf():
    pdf_path = "documents/q2_financial_strategy.pdf"
    print(f"Generating: {pdf_path}")
    
    # Create the PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#2C3E50"), # Dark Slate
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#34495E"),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=10
    )

    story.append(Paragraph("Q2 Strategic Financial Plan", title_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("1. Executive Summary", heading_style))
    story.append(Paragraph(
        "In Q2, BizWhisperer Inc. aims to optimize operational costs across all departments. "
        "While sales growth remains strong, rising infrastructure and marketing overheads require "
        "immediate cost-mitigation strategies. The targets outlined here are designed to extend runway "
        "without impacting head count or core development velocity.",
        body_style
    ))
    
    story.append(Paragraph("2. Cloud & Hosting Cost Reduction", heading_style))
    story.append(Paragraph(
        "Cloud hosting (AWS) is currently our largest non-salary expense. "
        "To reduce software and hosting expenses, we plan to migrate from on-demand AWS EC2 instances "
        "to 3-year Reserved Instances (RIs) by the end of Q3. Engineering predicts this migration "
        "will reduce monthly AWS database and computing expenses by <b>30%</b>. Additionally, "
        "all unused QA/testing environments must be shut down during non-business hours (6 PM to 8 AM).",
        body_style
    ))
    
    story.append(Paragraph("3. Marketing & Advertising Realignment", heading_style))
    story.append(Paragraph(
        "Google Ads spend has shown diminishing returns over the last quarter. "
        "To improve marketing ROI, we will shift focus from Google Ads (reducing active spend "
        "by <b>$2,000 per month</b>) and reallocate resources to organic content marketing and SEO. "
        "Social media ads budget will be capped at $1,000 per month.",
        body_style
    ))
    
    story.append(Paragraph("4. Department-Specific Budget Targets", heading_style))
    story.append(Paragraph(
        "For the upcoming quarters, the following targets are set:<br/>"
        "• <b>Engineering:</b> Reduce general discretionary expense budget by <b>15%</b>.<br/>"
        "• <b>Sales:</b> Reallocate 10% of physical travel budgets to virtual demo tools.<br/>"
        "• <b>HR:</b> Maintain current headcount but pause open requisition roles until Q3 review.",
        body_style
    ))
    
    doc.build(story)
    print("Q2 Strategy PDF created successfully.")

if __name__ == "__main__":
    create_policy_pdf()
    create_strategy_pdf()
