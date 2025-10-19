import csv
import json
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

def export_to_markdown(transcript="", summary="", flashcards=None, quiz=None):
    """Export all content to Markdown format"""
    md_content = "# Lecture Content\n\n"
    
    if transcript:
        md_content += "## Transcript\n\n"
        md_content += transcript + "\n\n---\n\n"
    
    if summary:
        md_content += "## Summary\n\n"
        md_content += summary + "\n\n---\n\n"
    
    if flashcards:
        md_content += "## Flashcards\n\n"
        for i, card in enumerate(flashcards, 1):
            md_content += f"### Card {i}\n\n"
            md_content += f"**Question:** {card.get('question', 'N/A')}\n\n"
            md_content += f"**Answer:** {card.get('answer', 'N/A')}\n\n"
            if card.get('category'):
                md_content += f"**Category:** {card.get('category')}\n\n"
            md_content += "---\n\n"
    
    if quiz:
        md_content += "## Quiz Questions\n\n"
        
        if quiz.get('multiple_choice'):
            md_content += "### Multiple Choice Questions\n\n"
            for i, q in enumerate(quiz['multiple_choice'], 1):
                md_content += f"**Question {i}:** {q.get('question', 'N/A')}\n\n"
                md_content += "Options:\n"
                for opt in q.get('options', []):
                    md_content += f"- {opt}\n"
                md_content += f"\n**Correct Answer:** {q.get('correct_answer', 'N/A')}\n\n"
                if q.get('explanation'):
                    md_content += f"**Explanation:** {q['explanation']}\n\n"
                md_content += "---\n\n"
        
        if quiz.get('open_ended'):
            md_content += "### Open-Ended Questions\n\n"
            for i, q in enumerate(quiz['open_ended'], 1):
                md_content += f"**Question {i}:** {q.get('question', 'N/A')}\n\n"
                md_content += f"**Sample Answer:** {q.get('sample_answer', 'N/A')}\n\n"
                md_content += "---\n\n"
    
    return md_content

def export_flashcards_to_csv(flashcards):
    """Export flashcards to CSV format"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Question', 'Answer', 'Category'])
    
    # Write flashcards
    for card in flashcards:
        writer.writerow([
            card.get('question', ''),
            card.get('answer', ''),
            card.get('category', '')
        ])
    
    return output.getvalue()

def export_quiz_to_csv(quiz):
    """Export quiz to CSV format"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Multiple choice questions
    if quiz.get('multiple_choice'):
        writer.writerow(['Multiple Choice Questions'])
        writer.writerow(['Question', 'Options', 'Correct Answer', 'Explanation'])
        
        for q in quiz['multiple_choice']:
            writer.writerow([
                q.get('question', ''),
                ' | '.join(q.get('options', [])),
                q.get('correct_answer', ''),
                q.get('explanation', '')
            ])
        
        writer.writerow([])  # Empty row
    
    # Open-ended questions
    if quiz.get('open_ended'):
        writer.writerow(['Open-Ended Questions'])
        writer.writerow(['Question', 'Sample Answer'])
        
        for q in quiz['open_ended']:
            writer.writerow([
                q.get('question', ''),
                q.get('sample_answer', '')
            ])
    
    return output.getvalue()

def export_to_pdf(title, transcript="", summary="", flashcards=None, quiz=None):
    """Export content to PDF format"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#4285F4',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#34A853',
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Transcript
    if transcript:
        story.append(Paragraph("Transcript", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Split transcript into paragraphs
        for para in transcript.split('\n'):
            if para.strip():
                story.append(Paragraph(para, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
    
    # Summary
    if summary:
        story.append(Paragraph("Summary", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        for para in summary.split('\n'):
            if para.strip():
                story.append(Paragraph(para, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
    
    # Flashcards
    if flashcards:
        story.append(Paragraph("Flashcards", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        for i, card in enumerate(flashcards, 1):
            story.append(Paragraph(f"<b>Card {i}</b>", styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(f"<b>Question:</b> {card.get('question', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
            story.append(Paragraph(f"<b>Answer:</b> {card.get('answer', 'N/A')}", styles['Normal']))
            if card.get('category'):
                story.append(Spacer(1, 0.05*inch))
                story.append(Paragraph(f"<b>Category:</b> {card.get('category')}", styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        story.append(PageBreak())
    
    # Quiz
    if quiz:
        story.append(Paragraph("Quiz Questions", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        if quiz.get('multiple_choice'):
            story.append(Paragraph("Multiple Choice Questions", styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))
            
            for i, q in enumerate(quiz['multiple_choice'], 1):
                story.append(Paragraph(f"<b>Question {i}:</b> {q.get('question', 'N/A')}", styles['Normal']))
                story.append(Spacer(1, 0.05*inch))
                
                for opt in q.get('options', []):
                    story.append(Paragraph(f"• {opt}", styles['Normal']))
                
                story.append(Spacer(1, 0.05*inch))
                story.append(Paragraph(f"<b>Correct Answer:</b> {q.get('correct_answer', 'N/A')}", styles['Normal']))
                
                if q.get('explanation'):
                    story.append(Spacer(1, 0.05*inch))
                    story.append(Paragraph(f"<b>Explanation:</b> {q['explanation']}", styles['Normal']))
                
                story.append(Spacer(1, 0.15*inch))
        
        if quiz.get('open_ended'):
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Open-Ended Questions", styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))
            
            for i, q in enumerate(quiz['open_ended'], 1):
                story.append(Paragraph(f"<b>Question {i}:</b> {q.get('question', 'N/A')}", styles['Normal']))
                story.append(Spacer(1, 0.05*inch))
                story.append(Paragraph(f"<b>Sample Answer:</b> {q.get('sample_answer', 'N/A')}", styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
