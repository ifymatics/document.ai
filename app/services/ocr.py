

from app.utils.logger import logger

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO



class OCRService:
    def __init__(self):
        # Configure Tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        self._image_cache = {}

    def extract_from_image(self, image_bytes: bytes) -> str:
        """Efficient OCR extraction with image preprocessing"""
        cache_key = hash(image_bytes)
        if cached := self._image_cache.get(cache_key):
            return cached

        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Preprocess image for better OCR
            processed = self._preprocess_image(img)

            # Perform OCR with optimized config
            text = pytesseract.image_to_string(
                processed,
                config='--oem 3 --psm 6 -c preserve_interword_spaces=1'
            )

            self._image_cache[cache_key] = text
            return text

        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            raise OCRProcessingError("Image processing failed")

    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Optimized image preprocessing pipeline"""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(thresh, h=7)

        return denoised

    def rebuild_image(self, original: bytes, text: str) -> bytes:
        """Efficient image regeneration with translated text overlay"""

            # Create new image with text overlay
        with Image.open(BytesIO(original)) as img:
            img = img.convert("RGB")
            draw = ImageDraw.Draw(img)

            # Use optimal font size (5% of image height)
            font_size = max(12, int(img.height * 0.05))
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

            # Calculate text position (centered at bottom 20%)
            text_width, text_height = draw.textsize(text, font=font)
            x = (img.width - text_width) // 2
            y = img.height - int(img.height * 0.2) - text_height

            # Add semi-transparent background
            draw.rectangle(
                [(x - 10, y - 10), (x + text_width + 10, y + text_height + 10)],
                fill=(255, 255, 255, 128)
            )

             # Add translated text
            draw.text((x, y), text, font=font, fill=(0, 0, 0))

            # Save to bytes
            output = BytesIO()
            img.save(output, format=img.format, quality=95)
            return output.getvalue()


class OCRProcessingError(Exception):
    pass




