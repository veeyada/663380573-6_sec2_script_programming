# document-automator/main.py
import datetime
import os

from src.pdf_processor import PDFProcessor, PAGE_SEPARATOR
from src.word_processor import WordProcessor
from src.utils import ensure_directory_exists, setup_logging

logger = setup_logging(__name__)


def main():
    """
    Main entry point for the document automation application.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    documents_dir = os.path.join(base_dir, 'documents')
    ensure_directory_exists(documents_dir)

    # --- Configuration for Input/Output Files ---
    input_pdf_path = os.path.join(documents_dir, 'input_article.pdf')
    output_docx_path = os.path.join(documents_dir, 'output_report.docx')
    summary_docx_path = os.path.join(documents_dir, 'summary_report.docx')
    merged_pdf_output_path = os.path.join(documents_dir, 'merged_output.pdf')
    split_output_dir = os.path.join(documents_dir, 'split')
    dummy_pdf1 = os.path.join(documents_dir, 'dummy_doc1.pdf')
    dummy_pdf2 = os.path.join(documents_dir, 'dummy_doc2.pdf')

    # Check if essential input PDF exists
    if not os.path.exists(input_pdf_path):
        logger.critical(f"Required input PDF '{input_pdf_path}' not found.")
        logger.info("Run 'python create_sample_pdfs.py' or place a PDF with text in the 'documents' folder.")
        return

    # Check for dummy PDFs for merging example
    dummy_pdfs_exist = os.path.exists(dummy_pdf1) and os.path.exists(dummy_pdf2)
    if not dummy_pdfs_exist:
        logger.warning("Dummy PDFs for merging example (dummy_doc1.pdf, dummy_doc2.pdf) not found. Skipping PDF merge task.")

    pdf_proc = PDFProcessor()
    word_proc = WordProcessor()

    logger.info("--- Starting Document Automation Workflow ---")

    # --- Task 1: Extract Text from PDF and Create Word Report ---
    logger.info("Task 1: Extracting text from PDF and generating Word report.")
    extracted_text = pdf_proc.extract_text_from_pdf(input_pdf_path)

    if extracted_text:
        page_count = extracted_text.count(PAGE_SEPARATOR)
        word_count = len(extracted_text.replace(PAGE_SEPARATOR, "").split())

        doc = word_proc.create_document()
        word_proc.add_heading(doc, "Automated Document Report", level=1)
        word_proc.add_paragraph(doc, "This report was automatically generated from PDF content and structured data.", bold=True, font_size=12)
        word_proc.add_paragraph(doc, "--- Extracted Content from PDF ---", italic=True, font_size=10, align='center')
        word_proc.add_extracted_text(doc, extracted_text, PAGE_SEPARATOR)  # Add the extracted text

        word_proc.add_heading(doc, "Summary Data", level=2)

        # Example data for a table
        table_data = [
            ["Metric", "Value", "Notes"],
            ["Total Pages Processed", str(page_count), "From Input PDF"],
            ["Total Words", str(word_count), "Approximate"],
            ["Document Type", "PDF/Word Hybrid", ""],
            ["Generated Date", datetime.date.today().isoformat(), ""],
        ]
        word_proc.add_table(doc, table_data, col_widths=[1.5, 1.5, 3.0])  # Example column widths

        word_proc.save_document(doc, output_docx_path)

        # --- Task 2: Generate a Summary Word Document ---
        logger.info("Task 2: Generating summary Word document.")
        summary = word_proc.create_document()
        word_proc.add_heading(summary, "Summary Report", level=1)
        word_proc.add_paragraph(summary, f"Source file: {os.path.basename(input_pdf_path)}", italic=True)
        word_proc.add_paragraph(
            summary,
            f"The source PDF contains {page_count} page(s) and about {word_count} words. "
            "Below are the section headings detected on each page.",
            align='justify',
        )
        word_proc.add_heading(summary, "Page Overview", level=2)
        overview = [["Page", "First Line (Title)", "Words"]]
        for idx, page_text in enumerate([p for p in extracted_text.split(PAGE_SEPARATOR) if p.strip()], start=1):
            lines = [ln.strip() for ln in page_text.splitlines() if ln.strip()]
            overview.append([str(idx), lines[0] if lines else "(no text)", str(len(page_text.split()))])
        word_proc.add_table(summary, overview, col_widths=[0.7, 4.0, 1.0])
        word_proc.save_document(summary, summary_docx_path)

        # Read the report back to verify content (python-docx reading)
        paragraphs, tables = word_proc.read_document(output_docx_path)
        if paragraphs is not None:
            logger.info(f"Verification: report has {len(paragraphs)} paragraphs and {len(tables)} table(s).")
    else:
        logger.error("Could not extract text from PDF. Skipping Word document generation.")

    # --- Task 3: Merge Multiple PDFs (Optional Example) ---
    if dummy_pdfs_exist:
        logger.info("Task 3: Merging dummy PDFs.")
        pdfs_to_merge = [dummy_pdf1, dummy_pdf2]
        pdf_proc.merge_pdfs(pdfs_to_merge, merged_pdf_output_path)
    else:
        logger.warning("Skipping PDF merge task as dummy PDFs (dummy_doc1.pdf, dummy_doc2.pdf) were not found.")

    # --- Task 4: Split the input PDF into single pages ---
    logger.info("Task 4: Splitting input PDF into single pages.")
    pdf_proc.split_pdf(input_pdf_path, output_dir=split_output_dir, pages_per_split=1)

    logger.info("--- Document Automation Workflow Completed ---")


if __name__ == "__main__":
    main()
