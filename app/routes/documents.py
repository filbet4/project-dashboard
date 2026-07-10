"""
Document routes for Phase 5.

Handles:
- Upload document
- List project documents
- Download document
- Delete document
"""

import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status
)

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project, Document
from app.schemas import DocumentResponse

from app.dependencies import (
    get_current_user,
    get_project,
    require_owner,
    require_project_member,
)

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

UPLOAD_DIR = "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx"
}


@router.post(
    "/projects/{project_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED
)
def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Upload a document to a project.

    Both OWNER and PARTICIPANT
    are allowed to upload files.
    """

    user = get_current_user(token, db)

    project = get_project(project_id, db)

    require_project_member(
        project.id,
        user,
        db
    )

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOC and DOCX files are allowed."
        )

    project_folder = os.path.join(
        UPLOAD_DIR,
        f"project_{project.id}"
    )

    os.makedirs(
        project_folder,
        exist_ok=True
    )

    unique_filename = (
        f"{uuid.uuid4()}{extension}"
    )

    full_path = os.path.join(
        project_folder,
        unique_filename
    )

    with open(full_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    document = Document(
        filename=file.filename,
        filepath=full_path,
        content_type=file.content_type,
        project_id=project.id
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

@router.get(
    "/projects/{project_id}",
    response_model=list[DocumentResponse]
)
def list_documents(
    project_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    List all documents belonging to a project.

    Both OWNER and PARTICIPANT
    can view project documents.
    """

    user = get_current_user(token, db)

    project = get_project(project_id, db)

    require_project_member(
        project.id,
        user,
        db
    )

    documents = (
        db.query(Document)
        .filter(Document.project_id == project.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    return documents


@router.get("/{document_id}")
def download_document(
    document_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Download a document.

    Both OWNER and PARTICIPANT
    can download files.
    """

    user = get_current_user(token, db)

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    project = get_project(document.project_id, db)

    require_project_member(
        project.id,
        user,
        db
    )

    if not os.path.exists(document.filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File missing on disk"
        )

    return FileResponse(
        path=document.filepath,
        filename=document.filename,
        media_type=document.content_type
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Delete a document.

    Only the OWNER
    can delete project documents.
    """

    user = get_current_user(token, db)

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    project = get_project(document.project_id, db)

    require_owner(
        project,
        user
    )

    if os.path.exists(document.filepath):
        os.remove(document.filepath)

    db.delete(document)
    db.commit()

    return {
        "detail": "Document deleted successfully"
    }