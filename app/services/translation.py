
import logging
import requests
from openai import OpenAI
import pypdfium2 as pdfium
from threading import Lock
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional, Tuple, List

from reportlab.pdfbase import pdfmetrics

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from reportlab.pdfbase import ttfonts
import io
from matplotlib import font_manager




logger = logging.getLogger(__name__)

class TranslationError(Exception):
    pass

class TranslationService:
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1"
    LIBRE_API_URL = "https://6j2q5nl3-5001.uks1.devtunnels.ms"#"https://nw12kt5q-5001.use2.devtunnels.ms"
    DEEPSEEK_API_KEY="sk-7c272739285e40fd8792537a19da9af9"
    FREE_TIER_LIMIT = 500_000  # 500k characters/month
    BASE_RATE = 0.15  # $0.15 per million characters beyond limit

    def __init__(self):
        self.monthly_char_usage = 0
        self.last_reset_date = datetime.now()
        self.usage_lock = Lock()
        self.logger = logging.getLogger(__name__)

        # Paid tier stub
        self.paid_tier = {}  # Replace with actual Google client if used

    def _get_deepseek_headers(self) -> dict:
        api_key = self.DEEPSEEK_API_KEY#os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise EnvironmentError("Missing DEEPSEEK_API_KEY environment variable.")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    def _get_libre_headers(self) -> dict:
        #api_key = self.DEEPSEEK_API_KEY#os.getenv("DEEPSEEK_API_KEY")
        # if not api_key:
        #     raise EnvironmentError("Missing DEEPSEEK_API_KEY environment variable.")
        return {
            "Content-Type": "application/json"
        }

    def _get_deepseek_client(self) -> OpenAI:
        api_key = self.DEEPSEEK_API_KEY
        if not api_key:
            raise EnvironmentError("Missing DEEPSEEK_API_KEY environment variable.")
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    def _check_monthly_reset(self):
        now = datetime.now()
        with self.usage_lock:
            if now.month != self.last_reset_date.month or now.year != self.last_reset_date.year:
                self.monthly_char_usage = 0
                self.last_reset_date = now

    def _update_usage(self, char_count: int):
        with self.usage_lock:
            self._check_monthly_reset()
            self.monthly_char_usage += char_count

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=10))
    def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> dict:
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text"
        }

        try:
            response = requests.post(f"{self.base_url}/translate", json=payload, timeout=10)
            response.raise_for_status()
            translated_text = response.json()["translatedText"]

            return {
                "translated_text": translated_text,
                "source_lang": response.json().get("detectedSourceLanguage", source_lang)
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Translation failed: {e}")
            self.logger.error(f"Payload sent: {payload}")

            # Optional: fallback to return original if needed
            return {
                "translated_text": text,  # fallback: return original
                "source_lang": source_lang
            }
    def translate1(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        is_premium: bool = False
    ) -> dict:
        try:
            if is_premium:
                return self._google_translate(text, target_lang, source_lang)
            print("Before self._libre_translate is called")
            result =  self._libre_translate(text, target_lang, source_lang)
            # print(result)
            return result #self._libre_translate(text, target_lang, source_lang)
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise TranslationError(f"Translation failed: {str(e)}")

    def _google_translate(self, text: str, target_lang: str, source_lang: Optional[str]) -> dict:
        result = self.paid_tier.translate(
            text,
            target_language=target_lang,
            source_language=source_lang,
            format_='text'
        )
        return {
            'translated_text': result['translatedText'],
            'detected_lang': result['detectedSourceLanguage'],
            'engine': 'google',
            'cost': len(text) * 20e-6
        }

    def _deepseek_translate(self, text: str, target_lang: str, source_lang: Optional[str]) -> dict:
        self._update_usage(len(text))
        try:
            response = requests.post(
                self.DEEPSEEK_API_URL,
                headers=self._get_deepseek_headers(),
                json={
                    "text": text,
                    "target_lang": target_lang,
                    "source_lang": source_lang or "auto"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            translated = data['data']['translations'][0]['text']
            detected = data['data']['detected_source_lang']
            excess = max(0, self.monthly_char_usage - self.FREE_TIER_LIMIT)
            cost = (excess * self.BASE_RATE) / 1_000_000

            return {
                'translated_text': translated,
                'detected_lang': detected,
                'engine': 'deepseek',
                'cost': cost,
                'monthly_usage': self.monthly_char_usage,
                'free_remaining': max(0, self.FREE_TIER_LIMIT - self.monthly_char_usage)
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise TranslationError("Monthly free tier limit exceeded")
            raise TranslationError(f"HTTP error during DeepSeek translation: {str(e)}")

        except KeyError as e:
            raise TranslationError(f"Unexpected API response format: {str(e)}")

    def _libre_translate(self, text: str, target_lang: str, source_lang: Optional[str], url_part:str="translate") -> dict:
        # self._update_usage(len(text))
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text"
        }
        try:
            response = requests.post(
            f"{self.LIBRE_API_URL}/{url_part}",
            headers=self._get_libre_headers(),
            json=payload,
            timeout=10,
            verify=False  # Only for dev tunnels; remove in production
            )
            response.raise_for_status()
            data = response.json()
           # print("RAW RESPONSE:", data)

            translated_text = data['translatedText']
            detected = data['detectedLanguage'] or "auto"

            return {
                'translated_text': translated_text,
                'detected_lang': detected["language"]
            }

        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Translation failed: {e}")
            self.logger.error(f"Payload sent: {payload}")
            if e.response.status_code == 429:
                raise TranslationError("Monthly free tier limit exceeded")
            raise TranslationError(f"HTTP error during LibreTranslate: {str(e)}")

        except KeyError as e:
            raise TranslationError(f"Unexpected API response format: {str(e)}")

    def detect_language(self, text: str) -> str:
        try:
            client = self._get_deepseek_client()
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a language detection assistant. Identify the language of the user's text and respond ONLY with the language name in English."
                    },
                    {
                        "role": "user",
                        "content": f"Detect the language of this text: {text}"
                    }
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.exception(f"Language detection failed {str(e)}")
            raise TranslationError(f"Language detection failed: {str(e)}")
        


    def is_rtl(text: str) -> bool:
        """Basic heuristic to check if text is RTL."""
        rtl_chars = [c for c in text if '\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F']
        return len(rtl_chars) > 0






    def get_system_font_path(self) -> str:
        """Dynamically get a system .ttf font file path"""
        fonts = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
        if not fonts:
            raise RuntimeError("No system TTF fonts found.")
        return fonts[0]  # Return the first available TTF font

    def rebuild_pdf(self, original_pdf_bytes: bytes, translated_text:str) -> bytes:
        # print(f"Inside new rebuild function: {translated_lines}")

        # Get system font and register it
        font_path = self.get_system_font_path()
        font_name = "DynamicFont"
        pdfmetrics.registerFont(ttfonts.TTFont(font_name, font_path))

        # Load original PDF to get page size (assumes first page's size is representative)
        original_pdf = pdfium.PdfDocument(original_pdf_bytes)
        original_page = original_pdf[0]
        width, height = original_page.get_size()

        # Prepare a canvas
        temp_output = io.BytesIO()
        c = canvas.Canvas(temp_output, pagesize=(width, height))
        c.setFont(font_name, 12)

        # Render the translated text top-down (rough layout, can be improved later)
        x, y = 40, height - 40
        line_spacing = 14

        for line in translated_text.splitlines():
            if y < 40:  # Create a new page if we're at the bottom margin
                c.showPage()
                c.setFont(font_name, 12)
                y = height - 40

            c.drawString(x, y, line)
            y -= line_spacing

        c.showPage()
        c.save()
        temp_output.seek(0)
        return temp_output.getvalue()

    def rebuild_pdf1(self, original_pdf_bytes: bytes, translated_text: str) -> bytes:
        # print(f" REBUILDING_TEXT: {translated_text}")
        pdf = pdfium.PdfDocument(original_pdf_bytes)
        page = pdf[0]
        n_pages = len(pdf)
        textpage = page.get_textpage()

        for text in textpage.get_text_range():
            if text.get_text().strip():
                page.insert_text(
                    text.get_text_position(),
                    translated_text,
                    font_size=text.get_fontsize()
                )

        return pdf.save()
