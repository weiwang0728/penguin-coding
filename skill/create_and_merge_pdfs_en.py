#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create two PDF files and merge them - English version
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER
import fitz  # PyMuPDF

def create_pdf1():
    """Create the first PDF file"""
    doc = SimpleDocTemplate("pdf1_en.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Set title style
    title_style = styles['Title']
    title_style.alignment = TA_CENTER
    
    # Add content
    story.append(Paragraph("PDF Document 1", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    content_lines = [
        "Welcome to the PDF Processing Skill!",
        "",
        "This is the content of the first PDF file.",
        "",
        "Key Features:",
        "• Created using ReportLab library",
        "• Formatted text with paragraphs",
        "• Easy to merge with other PDFs",
        "",
        "Next, we will create a second PDF file,",
        "then merge them together.",
        "",
        "PDF (Portable Document Format) is a",
        "cross-platform file format that maintains",
        "consistent display across various devices.",
        "",
        "The ReportLab library is a powerful Python",
        "tool for creating PDFs programmatically."
    ]
    
    for line in content_lines:
        story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
    
    doc.build(story)
    print("✓ Created pdf1_en.pdf")

def create_pdf2():
    """Create the second PDF file"""
    doc = SimpleDocTemplate("pdf2_en.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Set title style
    title_style = styles['Title']
    title_style.alignment = TA_CENTER
    
    # Add content
    story.append(Paragraph("PDF Document 2", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    content_lines = [
        "This is the second PDF file!",
        "",
        "PDF merging technology allows us to",
        "combine multiple PDF files into one.",
        "",
        "Use cases for PDF merging:",
        "• Assembling multi-page reports",
        "• Combining chapter documents",
        "• Creating complete manuals",
        "• Archiving related documents",
        "",
        "We use PyMuPDF (fitz) library",
        "to perform the PDF merging operation.",
        "",
        "PyMuPDF is a high-performance Python library",
        "providing PDF reading, creation, editing,",
        "and merging capabilities.",
        "",
        "The merged PDF will contain all pages",
        "from both source files in order.",
        "",
        "Thank you for using this demo!"
    ]
    
    for line in content_lines:
        story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
    
    doc.build(story)
    print("✓ Created pdf2_en.pdf")

def merge_pdfs():
    """Merge two PDF files"""
    result = fitz.open()
    
    # Open and insert first PDF
    doc1 = fitz.open("pdf1_en.pdf")
    result.insert_pdf(doc1)
    doc1.close()
    
    # Open and insert second PDF
    doc2 = fitz.open("pdf2_en.pdf")
    result.insert_pdf(doc2)
    doc2.close()
    
    # Save merged PDF
    result.save("merged_en.pdf")
    result.close()
    
    print("✓ Merged into merged_en.pdf")
    
    # Display merge result info
    merged = fitz.open("merged_en.pdf")
    print(f"  Merged PDF contains {len(merged)} pages")
    merged.close()

def display_merged_content():
    """Display the content of merged PDF"""
    merged = fitz.open("merged_en.pdf")
    print("\n" + "=" * 70)
    print("MERGED PDF CONTENT:")
    print("=" * 70)
    
    for i, page in enumerate(merged, 1):
        text = page.get_text().strip()
        print(f"\n--- Page {i} ---")
        print(text)
    
    merged.close()
    print("\n" + "=" * 70)

def main():
    print("=" * 50)
    print("PDF Creation and Merging Demo")
    print("=" * 50)
    print()
    
    print("Step 1: Creating the first PDF...")
    create_pdf1()
    print()
    
    print("Step 2: Creating the second PDF...")
    create_pdf2()
    print()
    
    print("Step 3: Merging PDF files...")
    merge_pdfs()
    print()
    
    display_merged_content()
    
    print("\n" + "=" * 50)
    print("Complete! Generated three files:")
    print("  - pdf1_en.pdf (first PDF)")
    print("  - pdf2_en.pdf (second PDF)")
    print("  - merged_en.pdf (merged PDF)")
    print("=" * 50)

if __name__ == "__main__":
    main()
