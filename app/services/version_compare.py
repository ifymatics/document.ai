# services/version_compare.py
import difflib
from pypdfium2 import PdfDocument

class VersionComparator:
    @staticmethod
    def compare_pdfs(pdf1_bytes, pdf2_bytes):
        pdf1_text = []
        pdf2_text = []
        
        for pdf_bytes, text_list in [(pdf1_bytes, pdf1_text), (pdf2_bytes, pdf2_text)]:
            pdf = PdfDocument(pdf_bytes)
            for i in range(len(pdf)):
                text_list.append(pdf[i].get_textpage().get_text_range())
        
        diff = difflib.unified_diff(
            pdf1_text,
            pdf2_text,
            fromfile="version1",
            tofile="version2"
        )
        return list(diff)