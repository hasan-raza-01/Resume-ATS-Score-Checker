import fitz 
import pytesseract
from PIL import Image
import io
from pathlib import Path
from docx import Document as DocxDocument
import tempfile
import subprocess
from .base import *

class DOCXParser(BaseParser):
    def can_handle(self, file_type: str) -> bool:
        return file_type == "docx"
    
    def parse(self, file_path: Path) -> str:
        """Parse DOCX with native-first, OCR fallback strategy"""
        try:
            # Try native extraction first
            has_readable_content = self._detect_readable_docx(file_path)
            
            if has_readable_content:
                return self._extract_native_docx(file_path)
            else:
                return self._extract_docx_with_ocr(file_path)
                
        except Exception as e:
            self.logger.error(f"DOCX parsing failed: {e}")
            raise
    
    def _detect_readable_docx(self, file_path: Path) -> bool:
        """Check if DOCX has readable text content"""
        try:
            doc = DocxDocument(file_path)
            total_chars = 0
            
            # Sample first few paragraphs
            for i, para in enumerate(doc.paragraphs):
                if i >= 5:  # Check first 5 paragraphs
                    break
                total_chars += len(para.text.strip())
            
            # If decent amount of text found, use native
            return total_chars > 50
            
        except Exception:
            return False
    
    def _extract_native_docx(self, file_path: Path) -> str:
        """Extract using python-docx library"""
        full_text = ""
        doc = DocxDocument(file_path)
        
        # Extract paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                full_text += para.text.strip() + "\n"
        
        # Extract tables
        for i, table in enumerate(doc.tables):
            full_text += f"\nTable {i}\n"
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells)
                if row_text.strip():
                    full_text += row_text + "\n"
        self.logger.info("parsed through native method")
        return full_text
    
    def _extract_docx_with_ocr(self, file_path: Path) -> str:
        """Fallback: Convert DOCX to images and OCR"""
        full_text = ""
        try:
            # Convert DOCX to PDF first
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = Path(temp_pdf.name)
            
            # Convert using libreoffice
            result = subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'pdf',
                '--outdir', str(temp_pdf_path.parent), str(file_path)
            ], capture_output=True, timeout=60)
            
            if result.returncode == 0:
                # Find the generated PDF
                pdf_name = file_path.stem + '.pdf'
                actual_pdf_path = temp_pdf_path.parent / pdf_name
                
                if actual_pdf_path.exists():
                    # OCR the PDF
                    pdf_doc = fitz.open(actual_pdf_path)
                    
                    for page in pdf_doc:
                        pix = page.get_pixmap()
                        img_data = pix.tobytes("png")
                        img = Image.open(io.BytesIO(img_data))
                        
                        ocr_result = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                        page_text = " ".join([t for t in ocr_result['text'] if t.strip()])
                        full_text += page_text + "\n"
                    
                    pdf_doc.close()
                    actual_pdf_path.unlink()  # Clean up
            
            self.logger.info("parsed through ocr")
        except Exception as e:
            self.logger.error(f"DOCX OCR extraction failed: {e}")
            # Last resort - try basic extraction
            try:
                doc = DocxDocument(file_path)
                full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
                self.logger.info("parsed through native method")
            except:
                raise
        return full_text
    
__all__ = ["DOCXParser", ]