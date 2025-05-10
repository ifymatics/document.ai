from datetime import datetime
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    original_filename = Column(String)
    original_language = Column(String)
    file_type = Column(String)
    content = Column(LargeBinary)  # Encrypted original
    created_at = Column(DateTime, default=datetime.utcnow)
    
    versions = relationship("DocumentVersion", back_populates="document")
    user = relationship("User", back_populates="documents")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(LargeBinary)
    target_language = Column(String)

    annotations = Column(JSON)  # Stores PDF annotations
    created_at = Column(DateTime, default=datetime.utcnow)
    # user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    document = relationship("Document", back_populates="versions")
    # user = relationship("User", back_populates="documents")