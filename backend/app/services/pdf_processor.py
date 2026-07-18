import os
import fitz
from PIL import Image
from typing import List

class PDFProcessor:
    @staticmethod
    def pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 200) -> List[str]:
        """Convert PDF pages to images"""
        os.makedirs(output_dir, exist_ok=True)
        doc = fitz.open(pdf_path)
        img_paths = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat)
            img_path = os.path.join(output_dir, f"page_{page_num+1}.png")
            pix.save(img_path)
            img_paths.append(img_path)
        doc.close()
        return img_paths

    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count