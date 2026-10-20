# Week 11: Automating PDFs & Word Documents

This project demonstrates how to automate common tasks involving PDF and Word documents using Python. It uses `PyPDF2` for PDF manipulation and `python-docx` for Word document creation and modification.

## Key Concepts Demonstrated

* **PDF Text Extraction**: Reading text content from PDF files.
* **PDF Merging / Splitting / Rotating / Encryption**: `merge_pdfs`, `split_pdf`, `rotate_pdf`, `encrypt_pdf`, `decrypt_pdf`.
* **Word Document Creation**: Programmatically generating new `.docx` files.
* **Adding Content to Word**: Headings, paragraphs, formatted text (bold, italic, font size, alignment), and tables.
* **Reading Word Documents**: Iterating through `document.paragraphs` and `document.tables`.
* **Modular Design**: PDF and Word logic live in separate modules (`pdf_processor.py`, `word_processor.py`).
* **Robustness**: Error handling for file operations, with logging for workflow visibility.

## Setup & How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/document-automator.git
   cd document-automator
   ```
2. **Install dependencies** (virtual environment recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Prepare input documents:**
   ```bash
   python create_sample_pdfs.py
   ```
   This creates `input_article.pdf` (2 pages), `dummy_doc1.pdf`, and `dummy_doc2.pdf` in `documents/`. You can replace them with your own PDFs.
4. **Run the script:**
   ```bash
   python main.py
   ```
   The script will:
   * Extract text from `input_article.pdf`.
   * Create `output_report.docx` with a heading, formatted text, the extracted text (per page), and a summary table.
   * Create `summary_report.docx` with a page-by-page overview table.
   * Merge `dummy_doc1.pdf` + `dummy_doc2.pdf` into `merged_output.pdf`.
   * Split `input_article.pdf` into single pages in `documents/split/`.

## Project Structure

```
document-automator/
├── src/
│   ├── __init__.py          # Python package marker
│   ├── pdf_processor.py     # PyPDF2 operations (extract, merge, split, rotate, encrypt)
│   ├── word_processor.py    # python-docx operations (create, add content, format, read)
│   └── utils.py             # Logging and directory helpers
├── documents/
│   ├── input_article.pdf    # Sample PDF for text extraction
│   ├── dummy_doc1.pdf       # Sample PDF for merging
│   ├── dummy_doc2.pdf       # Sample PDF for merging
│   ├── output_report.docx   # Generated Word report
│   ├── summary_report.docx  # Generated summary document
│   └── merged_output.pdf    # Generated merged PDF
├── create_sample_pdfs.py    # Generates the sample input PDFs
├── main.py                  # Entry point
├── requirements.txt
├── .gitignore
└── README.md
```

## Debugging Document Automation

* **`FileNotFoundError`**: Make sure the input PDFs are in `documents/` and the names match `main.py`.
* **`PyPDF2.errors.PdfReadError`**: The PDF is corrupted, encrypted with an unknown password, or not a valid PDF.
* **Blank Word document / missing content**: Image-based (scanned) PDFs contain no selectable text, so `extract_text()` returns nothing. Use OCR for those.
* **Formatting issues**: Formatting is applied to runs (`paragraph.runs[0]`); font sizes use `Pt()`.

## Limitations of PyPDF2

PyPDF2 is for manipulation and extraction; it cannot edit text or images on an existing page. For layout-aware extraction use `pdfminer.six` or `PyMuPDF`.

## Extension Ideas

* Template-based generation (`{{name}}` placeholders replaced from CSV/Excel).
* Mail merge for certificates or letters.
* PDF ↔ image conversion, document comparison, and full-text search indexing.
