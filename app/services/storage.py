from app.core.config import settings
from app.models.document import Document, DocumentVersion
from app.schemas.document import DocumentVersionResponse, DocumentVersionInDB
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet

# api/services/storage.py
class StorageService:
    def __init__(self):
        
        self.crypto = Fernet(settings.ENCRYPTION_KEY.encode())

    def save_document(self, user_id: int, filename: str, content: bytes, file_type: str, db:Session) -> Document:
        """Create parent document record"""
        encrypted = self.crypto.encrypt(content)
        doc = Document(
            user_id=user_id,
            original_filename=filename,
            file_type=file_type,
            content=encrypted
        )
        db.add(doc)
        db.commit()
        print(f"FROM STORAGE===>{doc}")
        return doc

    def save_version(self,
                    document_id: int,
                    content: bytes,
                    target_language: str,
                     # source_language: str,
                     # file_type: str,
                     db:Session
                     ) -> DocumentVersionResponse:
        """Create versioned translation"""
        encrypted = self.crypto.encrypt(content)
        version = DocumentVersion(
            document_id=document_id,
            content=encrypted,
            target_language=target_language,
            # source_language=source_language,
            # file_type=file_type
        )
        print(f"VERSION IDENTIFIER====>:{version}")
        db.add(version)
        db.commit()
        return DocumentVersionResponse(
            id=version.id,
            document_id=document_id,
            version_id=version.id,
            download_url=f"/documents/download/{version.id}",

        )

    def get_latest_version(self, document_id: int, db:Session) -> DocumentVersion:
        return db.query(DocumentVersion)\
            .filter(DocumentVersion.document_id == document_id)\
            .order_by(DocumentVersion.created_at.desc())\
            .first()

    def get_version_by_id(self, version_id: int, db: Session) -> DocumentVersion | None:
        return db.query(DocumentVersion).filter(DocumentVersion.id == version_id).first()