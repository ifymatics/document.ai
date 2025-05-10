# services/storage.py
from sqlalchemy import LargeBinary, Column, Integer,JSON
from pydantic import BaseModel, Field


class PDFFile(BaseModel):
    __tablename__ = "pdf_files"
    id = Column(Integer, primary_key=True)
    content = Column(LargeBinary)  # Stores PDF bytes directly
    annotations = Column(JSON)     # Stores PDF.js annotation data