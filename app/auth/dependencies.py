from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from functools import lru_cache
from app.core.auth import get_current_user
from app.models.user import User
from app.services.document import DocumentService
from app.services.storage import StorageService
from app.services.ocr import OCRService
from app.services.translation import TranslationService
from app.services.pdf_editor import PDFEditor as PDFEditService
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def verify_admin_access(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges"
        )
    return current_user



@lru_cache()
def get_storage_service() -> StorageService:
    return StorageService()



def get_ocr_service() -> OCRService:
    return OCRService()

def get_translation_service() -> TranslationService:
    return TranslationService()

def get_pdf_edit_service() -> PDFEditService:
    return PDFEditService()



def get_document_service(
    ocr_service: OCRService = Depends(get_ocr_service),
    translation_service: TranslationService = Depends(get_translation_service),
    pdf_edit_service: PDFEditService = Depends(get_pdf_edit_service),
) -> DocumentService:
    return DocumentService(
        ocr_service=ocr_service,
        translation_service=translation_service,
        pdf_edit_service=pdf_edit_service
    )