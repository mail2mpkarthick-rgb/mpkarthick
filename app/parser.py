import os
import json
import docx2txt
from PIL import Image
import pytesseract


class DocumentParser:
    SUPPORTED_EXTENSIONS = {'.docx', '.pdf', '.txt', '.csv'}

    @staticmethod
    def extract_text_from_docx(docx_path: str) -> dict:
        """Extracts text and embedded images from Word documents."""
        if not os.path.exists(docx_path):
            return {"text": "", "embedded_images": [], "error": "File not found"}
        try:
            text = docx2txt.process(docx_path)
            # Note: docx2txt extracts text and writes images to a directory
            # We can capture those embedded images
            img_dir = os.path.splitext(docx_path)[0] + "_images"
            embedded_images = []
            if os.path.exists(img_dir):
                for img_file in sorted(os.listdir(img_dir)):
                    img_path = os.path.join(img_dir, img_file)
                    if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        embedded_images.append(img_path)
            return {"text": text, "embedded_images": embedded_images, "error": None}
        except Exception as e:
            return {"text": f"[Word file parsing failed: {str(e)}]", "embedded_images": [], "error": str(e)}

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> dict:
        """Extracts text from PDF files."""
        if not os.path.exists(pdf_path):
            return {"text": "", "embedded_images": [], "error": "File not found"}
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return {"text": text, "embedded_images": [], "error": None}
        except Exception as e:
            return {"text": f"[PDF parsing failed: {str(e)}]", "embedded_images": [], "error": str(e)}

    @staticmethod
    def extract_text_from_txt(txt_path: str) -> dict:
        """Extracts text from plain text files."""
        if not os.path.exists(txt_path):
            return {"text": "", "error": "File not found"}
        try:
            with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return {"text": text, "embedded_images": [], "error": None}
        except Exception as e:
            return {"text": f"[TXT parsing failed: {str(e)}]", "embedded_images": [], "error": str(e)}

    @staticmethod
    def extract_text_from_csv(csv_path: str) -> dict:
        """Extracts text from CSV files — reads as structured text."""
        if not os.path.exists(csv_path):
            return {"text": "", "error": "File not found"}
        try:
            import csv
            rows = []
            with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                for row in reader:
                    rows.append(", ".join(row))
            text = "\n".join(rows)
            return {"text": f"CSV Data ({len(rows)} rows):\n{text}", "embedded_images": [], "error": None}
        except Exception as e:
            return {"text": f"[CSV parsing failed: {str(e)}]", "embedded_images": [], "error": str(e)}

    @staticmethod
    def parse_document(filepath: str) -> dict:
        """Auto-detect file type and parse accordingly.
        Returns dict with 'text', 'embedded_images', and 'error' keys."""
        if not os.path.exists(filepath):
            return {"text": "", "embedded_images": [], "error": "File not found"}

        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.docx':
            return DocumentParser.extract_text_from_docx(filepath)
        elif ext == '.pdf':
            return DocumentParser.extract_text_from_pdf(filepath)
        elif ext == '.txt':
            return DocumentParser.extract_text_from_txt(filepath)
        elif ext == '.csv':
            return DocumentParser.extract_text_from_csv(filepath)
        else:
            # Fallback: try as plain text
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                return {"text": text, "embedded_images": [], "error": None}
            except OSError as e:
                return {"text": "", "embedded_images": [], "error": f"Unsupported file format {ext}: {e}"}

    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """Extracts readable text components from screenshots using Tesseract OCR."""
        if not os.path.exists(image_path):
            return ""
        try:
            with Image.open(image_path) as img:
                return pytesseract.image_to_string(img)
        except Exception as e:
            return f"OCR Extraction failed: {str(e)}"

