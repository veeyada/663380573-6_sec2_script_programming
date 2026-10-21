# document-automator/create_sample_pdfs.py
# Generates the sample input PDFs (input_article.pdf, dummy_doc1.pdf, dummy_doc2.pdf)
# Requires: pip install reportlab
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

DOCUMENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documents')


def create_input_article(path):
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Introduction to Automation", styles['Heading1']),
        Paragraph(
            "Automation is the creation and application of technology to produce and deliver goods "
            "and services with minimal human intervention. The implementation of automation "
            "technologies, techniques, and processes improves the efficiency, reliability, and speed "
            "of many tasks that were previously performed manually.", styles['BodyText']),
        Spacer(1, 12),
        Paragraph("This leads to increased productivity, reduced costs, and improved quality.", styles['BodyText']),
        PageBreak(),
        Paragraph("Benefits of Automation", styles['Heading1']),
        Paragraph("1. Increased Efficiency: Tasks are completed faster and with higher throughput.", styles['BodyText']),
        Paragraph("2. Cost Reduction: Lower labor costs and reduced waste.", styles['BodyText']),
        Paragraph("3. Improved Accuracy: Minimizes human error.", styles['BodyText']),
        Paragraph("4. Enhanced Safety: Dangerous tasks can be automated.", styles['BodyText']),
        Paragraph("5. Greater Consistency: Uniform quality in output.", styles['BodyText']),
        Spacer(1, 12),
        Paragraph("Conclusion", styles['Heading2']),
        Paragraph(
            "Automation is transforming industries globally. Embracing these technologies is crucial "
            "for future competitiveness.", styles['BodyText']),
    ]
    SimpleDocTemplate(path, pagesize=A4).build(story)


def create_one_line_pdf(path, text):
    styles = getSampleStyleSheet()
    SimpleDocTemplate(path, pagesize=A4).build([Paragraph(text, styles['BodyText'])])


if __name__ == "__main__":
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    create_input_article(os.path.join(DOCUMENTS_DIR, 'input_article.pdf'))
    create_one_line_pdf(os.path.join(DOCUMENTS_DIR, 'dummy_doc1.pdf'), "This is Dummy Document 1 for merging test.")
    create_one_line_pdf(os.path.join(DOCUMENTS_DIR, 'dummy_doc2.pdf'), "This is Dummy Document 2 for merging test.")
    print(f"Sample PDFs created in: {DOCUMENTS_DIR}")
