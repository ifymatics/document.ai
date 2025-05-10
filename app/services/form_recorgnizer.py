# services/form_recognizer.py
import cv2
import numpy as np
from pypdfium2 import PdfDocument


class FormRecognizer:
    @staticmethod
    def detect_fields(pdf_bytes):
        pdf = PdfDocument(pdf_bytes)
        fields = []
        
        for i in range(len(pdf)):
            page = pdf[i]
            img = np.array(page.render_to(
                pdfium.BitmapConv.pil_image,
                scale=2
            ))
            
            # Advanced field detection using OpenCV
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2)
            
            # Detect text fields
            contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                aspect_ratio = w / float(h)
                
                if 2 < aspect_ratio < 10 and w > 50 and h > 10:
                    fields.append({
                        "page": i,
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h,
                        "type": "text_field"
                    })
        
        return fields