
# app/schemas/document.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from pydantic import ConfigDict
from app.schemas.user import UserInDBBase


class FileType(str, Enum):
    PDF = "pdf"
    JPG = "jpg"
    PNG = "png"
    JPEG = "jpeg"


class DocumentBase(BaseModel):
    original_filename: str = Field(..., example="contract.pdf")
    file_type: FileType
    original_language: str = Field(..., example="de")


class DocumentCreate(DocumentBase):
    pass


class DocumentVersionBase(BaseModel):
    target_language: str = Field(..., example="en")
    created_at: datetime


class DocumentVersionCreate(DocumentVersionBase):
    content: bytes  # Will be handled as base64 in API
    annotations: Optional[dict] = None


class DocumentVersionInDB(DocumentVersionBase):
    id: int
    document_id: int

    class Config:
        from_attributes = True

class DocumentEditResponse(BaseModel):
    version_id: int
    download_url: str

class DocumentInDB(DocumentBase):
    id: int
    user_id: int
    created_at: datetime
    user: UserInDBBase
    versions: List[DocumentVersionInDB] = []

    class Config:
        from_attributes = True


class DocumentWithContent(DocumentInDB):
    versions: List[DocumentVersionInDB] = []


class DocumentVersionWithContent(DocumentVersionInDB):
    content: bytes

    class Config:
        json_encoders = {
            bytes: lambda v: v.decode('latin-1')  # For base64 representation
        }


class DocumentEditRequest(BaseModel):
    annotations: List[dict] = Field(..., example=[
        {
            "page": 0,
            "x": 100,
            "y": 100,
            "text": "Approved",
            "color": "#FF0000"
        }
    ])
    text_replacements: Optional[dict] = Field(None, example={
        "old_text": "new_text"
    })


class TranslationRequest(BaseModel):
    target_language: str = Field(..., example="en")
    preserve_formatting: bool = True


class DocumentDownloadResponse(BaseModel):
    content: bytes
    filename: str
    media_type: str

    class Config:
        json_encoders = {
            bytes: lambda v: v.decode('latin-1')
        }

class DocumentEditResponse(BaseModel):
    version_id: int
    download_url: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: str


class DocumentEditResponse(BaseModel):
    version_id: int
    download_url: str

# Update existing DocumentVersionInDB to match ORM model
class DocumentVersionInDB(BaseModel):
    id: int
    document_id: int
    target_language: str
    created_at: datetime
    annotations: Optional[dict] = None

    class Config:
        # from_attributes = True  # For Pydantic v1 compatibility
        # For Pydantic v2 use:
        model_config = ConfigDict(from_attributes=True)



class DocumentVersionInDB(BaseModel):
    id: int
    document_id: int
    target_language: str
    created_at: datetime
    annotations: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


from pydantic import BaseModel, ConfigDict

class DocumentVersionResponse(BaseModel):
    id: int
    document_id: int
    version_id: int
    download_url: str


    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)

class DocumentInDB(BaseModel):
    id: int
    user_id: int
    original_filename: str
    file_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)