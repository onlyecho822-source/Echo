"""
Document processing API routes.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.config import settings
from app.services.document_processor import document_processor

router = APIRouter()


@router.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from a document.

    Supports: pdf, docx, doc, txt, md, png, jpg, jpeg

    Args:
        file: Document file

    Returns:
        Extracted text content
    """
    # Validate file extension
    filename = file.filename or "document"
    extension = Path(filename).suffix.lower().lstrip(".")
    valid_extensions = set(document_processor.get_supported_formats())

    if extension not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document format: {extension}. Supported: {', '.join(sorted(valid_extensions))}"
        )

    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = settings.upload_path / f"{file_id}.{extension}"

        content = await file.read()

        # Check file size
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.max_upload_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({size_mb:.1f}MB). Max: {settings.max_upload_size_mb}MB"
            )

        file_path.write_bytes(content)

        # Extract text
        text = await document_processor.extract_text(file_path)

        # Clean up
        file_path.unlink(missing_ok=True)

        return {
            "filename": filename,
            "file_type": extension,
            "text": text,
            "character_count": len(text),
            "word_count": len(text.split()) if text else 0,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text extraction failed: {str(e)}"
        )


@router.get("/formats")
async def get_supported_formats():
    """Get list of supported document formats."""
    return {
        "formats": document_processor.get_supported_formats(),
        "max_file_size_mb": settings.max_upload_size_mb,
    }
