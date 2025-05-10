import fitz  # PyMuPDF
from io import BytesIO
from typing import Tuple, Optional, Any, Dict

from sqlalchemy.orm import Session

from app.schemas.document import DocumentVersionInDB
from app.services.translation import  TranslationService
from app.services.pdf_editor import  PDFEditor as  PDFEditService
from app.services.ocr import   OCRService
# from app.services.document_sign import    SigningService
import logging
from tenacity import retry, stop_after_attempt

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(
            self,
            ocr_service: "OCRService",  # Forward reference
            translation_service: "TranslationService",
            pdf_edit_service: "PDFEditService"
    ):
        self.ocr = ocr_service
        self.translator = translation_service
        self.pdf_editor = pdf_edit_service

    def process_document(self, file_bytes: bytes, file_type: str, target_lang: str) -> Dict[str, Any]:
        
        text, source_lang = self._extract_content(file_bytes, file_type)
      
        translated = self.translator.translate(text, target_lang)
        
        
        return {
            "content": translated["translated_text"],
            "file": self._rebuild_file(file_bytes, translated["translated_text"], file_type),
            "metadata": {
                "source_lang": source_lang,
                "file_type": file_type,
                "original_size": len(file_bytes)
            }
        }

    def _extract_content(self, file_bytes: bytes, file_type: str) -> Tuple[str, str]:
        """Unified content extraction with language detection"""
        try:
            if file_type == "pdf":
                with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                    text = "\n".join(page.get_text() for page in doc)
            else:
                text = self.ocr.extract_from_image(file_bytes)

            # Detect language from the text
            detected_language = "auto" #self.translator.detect_language(text[:500])
           # print( detected_language )
            # Validate the output (assuming it's a string for success, dict for error)
            if isinstance(detected_language, dict) and "Error code:" in detected_language:
                raise ValueError(f"Language detection failed: {detected_language}")

            return text, detected_language

        except Exception as e:
            logger.exception("Failed to extract content or detect language")
            raise RuntimeError(f"Failed to extract content or detect language: {e}") from e

    def _rebuild_file(self, original: bytes, text: str, file_type: str ="pdf") -> bytes:
        """Preserve original format while inserting translations"""
        # print(f"REBUILDING PDF USING DocumentService._rebuild_file{text}")
        if file_type == "pdf":
            # return self.pdf_editor.edit_pdf(original, {
            #     "replacements": [{
            #         "text": "PLACEHOLDER_TEXT",  # Use actual content replacement logic
            #         "new_text": text,
            #         "page": 0,
            #     }]
            # })
            return self.translator.rebuild_pdf(original,text)
        else:
            # Handle image/text file regeneration
            return self._rebuild_image(original, text)

    @retry(stop=stop_after_attempt(2))
    def edit_document(self, file_bytes: bytes, edits: dict) -> bytes:
        """Unified document editing interface"""
        return (self.pdf_editor.edit_pdf(file_bytes, edits))

    def sign_document(
        self,
        file_bytes: bytes,
        signers: list,
        document_type: str = 'internal'
    ) -> dict:
        """Document signing workflow"""
        return self.signer.sign_document(file_bytes, signers, document_type)

    def _rebuild_image(self, original: bytes, text: str) -> bytes:
        """Regenerate image with translated text (simplified example)"""
        # Implementation would use image editing libraries
        try:
            return self.ocr.rebuild_image(original, text)
        except Exception as e:

            return original  # Placeholder

    def clear_cache(self):
        """Manual cache management"""
        self._document_cache.clear()

    def get_version_by_id(self, version_id: int, db: Session) -> DocumentVersionInDB | None:
        return db.query(DocumentVersionInDB).filter(DocumentVersionInDB.id == version_id).first()