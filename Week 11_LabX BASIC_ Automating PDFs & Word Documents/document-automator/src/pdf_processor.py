# document-automator/src/pdf_processor.py
from PyPDF2 import PdfReader, PdfWriter
import os
from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

PAGE_SEPARATOR = "--- Page End ---"


class PDFProcessor:
    """
    Handles operations related to PDF files using PyPDF2.
    """

    def __init__(self):
        logger.info("PDFProcessor initialized.")

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts all text from a given PDF file.
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None

        text_content = ""
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            logger.info(f"Extracting text from '{pdf_path}' ({num_pages} pages)...")
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text() or ""  # Image-only pages return no text
                text_content += page_text + f"\n{PAGE_SEPARATOR}\n"  # Separator for readability
            logger.info(f"Successfully extracted text from '{pdf_path}'.")
            return text_content
        except Exception as e:
            logger.error(f"Error extracting text from '{pdf_path}': {e}")
            return None

    def merge_pdfs(self, pdf_paths, output_path):
        """
        Merges multiple PDF files into a single output PDF.
        """
        if not pdf_paths:
            logger.warning("No PDF paths provided for merging.")
            return False

        writer = PdfWriter()

        logger.info(f"Merging PDFs into '{output_path}'...")
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                logger.warning(f"Skipping non-existent PDF for merging: {pdf_path}")
                continue
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"Added '{pdf_path}' to merge queue.")
            except Exception as e:
                logger.error(f"Error reading PDF '{pdf_path}' for merging: {e}")
                continue

        if len(writer.pages) == 0:
            logger.warning("No pages were added to the merged PDF. Output file will be empty or not created.")
            return False

        try:
            with open(output_path, 'wb') as f:
                writer.write(f)
            logger.info(f"PDFs successfully merged to '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error writing merged PDF to '{output_path}': {e}")
            return False

    def split_pdf(self, pdf_path, output_dir=".", pages_per_split=1):
        """
        Splits a PDF into multiple smaller PDFs, each containing a specified number of pages.
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False

        ensure_directory_exists(output_dir)

        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            logger.info(f"Splitting '{pdf_path}' ({total_pages} pages) into chunks of {pages_per_split} pages.")

            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            for i in range(0, total_pages, pages_per_split):
                writer = PdfWriter()
                output_filename = os.path.join(output_dir, f"{base_name}_part_{(i // pages_per_split) + 1}.pdf")

                for j in range(i, min(i + pages_per_split, total_pages)):
                    writer.add_page(reader.pages[j])

                with open(output_filename, 'wb') as f:
                    writer.write(f)
                logger.info(f"Created split PDF: {output_filename}")

            logger.info(f"Successfully split '{pdf_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error splitting PDF '{pdf_path}': {e}")
            return False

    def rotate_pdf(self, pdf_path, output_path, degrees=90):
        """
        Rotates every page of a PDF clockwise by the given degrees (multiple of 90).
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False

        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            for page in reader.pages:
                page.rotate(degrees)
                writer.add_page(page)
            with open(output_path, 'wb') as f:
                writer.write(f)
            logger.info(f"Rotated '{pdf_path}' by {degrees} degrees -> '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error rotating PDF '{pdf_path}': {e}")
            return False

    def encrypt_pdf(self, pdf_path, output_path, password):
        """
        Encrypts a PDF with a user password.
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False

        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            with open(output_path, 'wb') as f:
                writer.write(f)
            logger.info(f"Encrypted '{pdf_path}' -> '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error encrypting PDF '{pdf_path}': {e}")
            return False

    def decrypt_pdf(self, pdf_path, password):
        """
        Opens an encrypted PDF and returns a PdfReader if the password is correct, else None.
        """
        try:
            reader = PdfReader(pdf_path)
            if reader.is_encrypted and not reader.decrypt(password):
                logger.error(f"Wrong password for '{pdf_path}'.")
                return None
            logger.info(f"Decrypted '{pdf_path}' ({len(reader.pages)} pages).")
            return reader
        except Exception as e:
            logger.error(f"Error decrypting PDF '{pdf_path}': {e}")
            return None
