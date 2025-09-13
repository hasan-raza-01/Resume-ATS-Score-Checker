import fitz
import pytesseract
from PIL import Image
import io
import asyncio
from pathlib import Path
from .base import *

class PDFParser(BaseParser):
    
    def __init__(self, ocr_threshold: float = 0.1):
        super().__init__()
        self.ocr_threshold = ocr_threshold
    
    def can_handle(self, file_type: str) -> bool:
        return file_type == "pdf"
    
    async def parse(self, path: Path) -> str:
        """Parse PDF with native-first, OCR fallback strategy"""
        data = ""
        try:
            # Run fitz operations in executor since they're CPU-bound
            loop = asyncio.get_event_loop()
            pdf_doc = await loop.run_in_executor(None, fitz.open, str(path))
            
            has_text_layer = await self._detect_text_layer(pdf_doc)
            
            if has_text_layer:
                data = await self._extract_native_text(pdf_doc)
                data += await self._extract_tables(pdf_doc)
            else:
                data = await self._extract_with_ocr(pdf_doc)
            
            pdf_doc.close()
            
        except Exception as e:
            self.logger.error(f"PDF parsing failed: {e}")
            raise e
        
        return data
    
    async def _detect_text_layer(self, pdf_doc) -> bool:
        loop = asyncio.get_event_loop()
        total_chars = 0
        sample_pages = min(3, len(pdf_doc))
        
        for page_num in range(sample_pages):
            page = pdf_doc[page_num]
            text = await loop.run_in_executor(None, page.get_text)
            total_chars += len(text.strip())
        
        return total_chars > 50
    
    async def _extract_native_text(self, pdf_doc) -> str:
        loop = asyncio.get_event_loop()
        full_text = ""
        
        for page in pdf_doc:
            blocks = await loop.run_in_executor(None, page.get_text, "dict")
            
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = "".join(span["text"] for span in line["spans"])
                        if line_text.strip():
                            full_text += line_text + "\n"
        
        self.logger.info("parsed through native method")
        return full_text
    
    async def _ocr_main(self, page, dpi: int = 400) -> str:
        loop = asyncio.get_event_loop()
        
        def _do_ocr():
            pix = page.get_pixmap(dpi=dpi)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            ocr_result = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            return " ".join([t for t in ocr_result['text'] if t.strip()])
        
        return await loop.run_in_executor(None, _do_ocr)
    
    async def _extract_with_ocr(self, pdf_doc) -> str:
        full_text = ""
        
        for page in pdf_doc:
            page_text = await self._ocr_main(page)
            if len(page_text) < 50:
                page_text = await self._ocr_main(page, dpi=600)
            full_text += page_text + "\n"
        
        self.logger.info("parsed through ocr")
        return full_text
    
    async def _extract_tables(self, pdf_doc) -> str:
        loop = asyncio.get_event_loop()
        tables = []
        
        def _extract_camelot():
            try:
                import camelot
                extracted_tables = camelot.read_pdf(str(pdf_doc.name), pages='all')
                return [f"\nTable {i}\n{table.df.to_string(index=False)}\n" 
                       for i, table in enumerate(extracted_tables)]
            except ImportError:
                self.logger.warning("Camelot not available for table extraction")
                return []
            except Exception as e:
                self.logger.error(f"Table extraction failed: {e}")
                return []
        
        try:
            tables = await loop.run_in_executor(None, _extract_camelot)
        except Exception as e:
            self.logger.error(f"Table extraction failed: {e}")
        
        return "\n".join(tables)

__all__ = ["PDFParser"]
