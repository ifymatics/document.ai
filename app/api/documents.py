# app/api/document.py
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.core.auth import get_current_user_optional
from app.db.database import get_db
from app.services.document import DocumentService
from app.services.storage import StorageService
from app.auth.dependencies import get_current_active_user, get_document_service, get_storage_service
from app.models.user import User
from app.schemas.document import (
    DocumentVersionResponse,
    DocumentEditResponse,
    ErrorResponse, DocumentVersionInDB
)

router = APIRouter()

@router.post(
    "/translate",
    response_model=DocumentVersionResponse,
    responses={500: {"model": ErrorResponse}}
)
async def translate_document(
    file: UploadFile = File(...),
    target_language: str = Form("en"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    doc_service: DocumentService = Depends(get_document_service),
    storage: StorageService = Depends(get_storage_service)
):
    try:
        file_bytes = await file.read()
        file_type = file.filename.split(".")[-1].lower()

        # Step 1: Translate and recreate the PDF (returns bytes and metadata)
        result = doc_service.process_document(file_bytes, file_type, target_language)


        # Step 2: Save the original document
        document = storage.save_document(
            user_id=user.id if user else 1,
            filename=file.filename,
            content=file_bytes,
            file_type=file_type,
            db=db
        )

        # Step 3: Save the translated version
        version = storage.save_version(
            document_id=document.id,
            content=result['file'],  # translated PDF bytes
            target_language=target_language,
            db=db
        )

        # Step 4: Return response with download URL
        return DocumentVersionResponse(
            id=version.id,
            document_id=document.id,
            version_id=version.id,
            download_url=f"/documents/download/{version.id}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail=str(e),
                error_code="TRANSLATION_ERROR"
            ).dict()
        )

@router.post(
    "/edit/{document_id}",
    response_model=DocumentEditResponse,
    responses={500: {"model": ErrorResponse}}
)
async def edit_document(
    document_id: int,
    edits: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
    doc_service: DocumentService = Depends(get_document_service),
    storage: StorageService = Depends(get_storage_service)
):
    try:
        document = storage.get_document(document_id, user.id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    detail="Document not found",
                    error_code="DOCUMENT_NOT_FOUND"
                ).dict()
            )

        edited_bytes = doc_service.edit_pdf(document.latest_version.content, edits)

        version = storage.save_version(
            document_id=document_id,
            content=edited_bytes,
            annotations=edits.get("annotations"),
            db=db
        )

        return DocumentEditResponse(
            version_id=version.id,
            download_url=f"/documents/download/{version.id}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail=str(e),
                error_code="EDITING_ERROR"
            ).dict()
        )
@router.get("/download/{version_id}")
async def download_translated_document(
    version_id: int,
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
):
    print(version_id)
    # Step 1: Retrieve version from storage
    version: DocumentVersionInDB = storage.get_version_by_id(version_id, db=db)


    if not version:
        raise HTTPException(status_code=404, detail="Document version not found.")


    # ✅ Step 2: Decrypt the content
    decrypted_bytes = storage.crypto.decrypt(version.content)

    # Step 3: Convert to file-like object
    file_stream = BytesIO(decrypted_bytes)

    # Step 3: Return as downloadable PDF file
    return StreamingResponse(
        file_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="translated_{version_id}.pdf"'
        }
    )