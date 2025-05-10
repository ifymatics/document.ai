# services/pdf_editor.py
import pypdfium2 as pdfium
from PIL import Image
import io
import numpy as np
import cv2

class PDFEditor:
    def __init__(self):
        self._pdf = None
        self.changes = []

    def load(self, pdf_bytes: bytes):
        self._pdf = pdfium.PdfDocument(pdf_bytes)

    @property
    def pdf(self):
        if self._pdf is None:
            raise ValueError("PDF not loaded. Call `load(pdf_bytes)` before using the editor.")
        return self._pdf

    def edit_text(self, page_index, old_text, new_text):
        page = self.pdf[page_index]
        textpage = page.get_textpage()
        for text in textpage.get_text_range():
            if text.get_text() == old_text:
                page.remove_text(text.get_bbox())
                page.insert_text(
                    text.get_text_position(),
                    new_text,
                    font_size=text.get_fontsize(),
                    color=text.get_color()
                )
                self.changes.append(f"Text edited: {old_text} → {new_text}")

    def add_image(self, page_index, image_bytes, position, size):
        img = Image.open(io.BytesIO(image_bytes))
        page = self.pdf[page_index]
        page.insert_image(position, img, size=size)
        self.changes.append("Image added")

    def add_signature(self, page_index, signature_data, position):
        signature_img = self._data_uri_to_image(signature_data)
        self.add_image(page_index, signature_img, position, (150, 50))

    def recognize_form_fields(self):
        form_fields = []
        for i in range(len(self.pdf)):
            page = self.pdf[i]
            bitmap = page.render_to(pdfium.BitmapConv.pil_image, scale=2)
            img = np.array(bitmap)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if 50 < w < 500 and 10 < h < 50:
                    form_fields.append({
                        "page": i,
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h,
                        "type": "text_field"
                    })
        return form_fields

    def save(self):
        output = io.BytesIO()
        self.pdf.save(output)
        output.seek(0)
        return output.getvalue()

    def _data_uri_to_image(self, data_uri):
        # Placeholder: implement your data URI conversion here
        pass
