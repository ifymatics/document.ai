from celery import shared_task

from app.schemas.document import FileType
from app.services.document import DocumentService
from app.services.translation import TranslationService
from app.auth.dependencies  import get_storage_service
from app.utils.logger import logger


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def process_translation_task(self, document_id: int, target_language: str):
    try:
        storage = get_storage_service()
        translator = TranslationService()
        doc_service = DocumentService()

        # Retrieve document
        document = storage.get_document(document_id)
        file_bytes = storage.get_file_content(document.original_file_id)

        # Process document
        text = doc_service.extract_text(file_bytes, document.file_type)
        translated_text = translator.translate_text(text, target_language)

        # Rebuild document
        if document.file_type == FileType.PDF:
            translated_bytes = doc_service.rebuild_pdf(file_bytes, translated_text)
        else:
            translated_bytes = file_bytes  # Simplified for non-PDF

        # Store new version
        version = storage.save_version(
            document_id=document_id,
            content=translated_bytes,
            target_language=target_language
        )

        return version.id
    except Exception as e:
        logger.error(f"Translation task failed: {str(e)}")
        raise self.retry(exc=e)