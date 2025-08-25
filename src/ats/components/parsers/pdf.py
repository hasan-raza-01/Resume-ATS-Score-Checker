import fitz 
import pytesseract
from PIL import Image
import io
from .base import * 
from pathlib import Path

class PDFParser(BaseParser):
    def __init__(self, ocr_threshold: float = 0.1):
        super().__init__()
        self.ocr_threshold = ocr_threshold
    
    def can_handle(self, file_type: str) -> bool:
        return file_type == "pdf"
    
    def parse(self, file_path: Path) -> str:
        """Parse PDF with native-first, OCR fallback strategy"""
        data = ""
        try:
            pdf_doc = fitz.open(file_path)
            
            has_text_layer = self._detect_text_layer(pdf_doc)
            if has_text_layer:
                data = self._extract_native_text(pdf_doc)
            else:
                data = self._extract_with_ocr(pdf_doc)
            
            data += self._extract_tables(pdf_doc)
            pdf_doc.close()
        except Exception as e:
            self.logger.error(f"PDF parsing failed: {e}")
            raise
        return data
    
    def _detect_text_layer(self, pdf_doc) -> bool:
        total_chars = 0
        sample_pages = min(3, len(pdf_doc))
        for page_num in range(sample_pages):
            page = pdf_doc[page_num]
            text = page.get_text()
            total_chars += len(text.strip())
        return total_chars > 100
    
    def _extract_native_text(self, pdf_doc) -> str:
        full_text = ""
        for page in pdf_doc:
            blocks = page.get_text("dict")
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = "".join(span["text"] for span in line["spans"])
                        if line_text.strip():
                            full_text += line_text + "\n"
        self.logger.info("parsed through native method")
        return full_text
    
    def _extract_with_ocr(self, pdf_doc) -> str:
        full_text = ""
        for page in pdf_doc:
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            ocr_result = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            page_text = " ".join([t for t in ocr_result['text'] if t.strip()])
            full_text += page_text + "\n"
            self.logger.info("parsed through ocr")
        return full_text
    
    def _extract_tables(self, pdf_doc) -> str:
        tables = []
        try:
            import camelot
            extracted_tables = camelot.read_pdf(str(pdf_doc.name), pages='all')
            for i, table in enumerate(extracted_tables):
                tables.append(f"\nTable {i}\n{table.df.to_string(index=False)}\n")
        except ImportError:
            self.logger.warning("Camelot not available for table extraction")
        except Exception as e:
            self.logger.error(f"Table extraction failed: {e}")
        return "\n".join(tables)

__all__ = ["PDFParser", ]