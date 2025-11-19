"""
Main fact-checking API routes.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.schemas import (
    FactCheckRequest,
    FactCheckResponse,
    FactCheckResult,
    MediaType,
    ProcessingStatus,
)
from app.services.fact_checker import fact_checker
from app.services.audio_processor import audio_processor
from app.services.video_processor import video_processor
from app.services.document_processor import document_processor

router = APIRouter()


@router.post("/text", response_model=FactCheckResponse)
async def check_text(request: FactCheckRequest):
    """
    Fact-check text content directly.

    Submit text and receive fact-check results with verified claims.
    """
    if not request.text_content:
        raise HTTPException(status_code=400, detail="text_content is required")

    try:
        result = await fact_checker.check_text(
            text=request.text_content,
            media_type=MediaType.TEXT,
            context=request.options.get("context"),
        )

        return FactCheckResponse(success=True, data=result)

    except Exception as e:
        return FactCheckResponse(
            success=False,
            message=f"Fact-check failed: {str(e)}"
        )


@router.post("/file", response_model=FactCheckResponse)
async def check_file(
    file: UploadFile = File(...),
    context: str = Form(None),
):
    """
    Fact-check an uploaded file (audio, video, image, or document).

    Supported formats:
    - Audio: mp3, wav, m4a, ogg, flac
    - Video: mp4, avi, mov, mkv, webm
    - Documents: pdf, docx, txt
    - Images: png, jpg, jpeg
    """
    # Determine file type
    filename = file.filename or "unknown"
    extension = Path(filename).suffix.lower().lstrip(".")

    # Map extension to media type
    audio_formats = {"mp3", "wav", "m4a", "ogg", "flac", "webm"}
    video_formats = {"mp4", "avi", "mov", "mkv", "webm"}
    image_formats = {"png", "jpg", "jpeg", "gif", "bmp", "tiff"}
    doc_formats = {"pdf", "docx", "doc", "txt", "md"}

    if extension in audio_formats:
        media_type = MediaType.AUDIO
    elif extension in video_formats:
        media_type = MediaType.VIDEO
    elif extension in image_formats:
        media_type = MediaType.IMAGE
    elif extension in doc_formats:
        media_type = MediaType.DOCUMENT
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {extension}"
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

        # Extract text based on media type
        extracted_text = ""

        if media_type == MediaType.AUDIO:
            transcription = await audio_processor.transcribe_file(file_path)
            extracted_text = transcription.text

        elif media_type == MediaType.VIDEO:
            video_result = await video_processor.process_video(file_path)
            parts = []
            if video_result["transcription"]:
                parts.append(video_result["transcription"].text)
            for frame_text in video_result["frame_texts"]:
                parts.append(frame_text["text"])
            extracted_text = "\n\n".join(parts)

        elif media_type == MediaType.IMAGE:
            ocr_result = await video_processor.extract_text_from_image(file_path)
            extracted_text = ocr_result.text

        elif media_type == MediaType.DOCUMENT:
            extracted_text = await document_processor.extract_text(file_path)

        # Clean up uploaded file
        file_path.unlink(missing_ok=True)

        if not extracted_text.strip():
            return FactCheckResponse(
                success=True,
                data=FactCheckResult(
                    request_id=file_id,
                    status=ProcessingStatus.COMPLETED,
                    media_type=media_type,
                    extracted_text="",
                    summary="No text could be extracted from the file.",
                ),
            )

        # Fact-check extracted text
        result = await fact_checker.check_text(
            text=extracted_text,
            media_type=media_type,
            context=context,
        )

        return FactCheckResponse(success=True, data=result)

    except HTTPException:
        raise
    except Exception as e:
        return FactCheckResponse(
            success=False,
            message=f"Processing failed: {str(e)}"
        )


@router.post("/url", response_model=FactCheckResponse)
async def check_url(request: FactCheckRequest):
    """
    Fact-check content from a URL (web page, video, etc.).
    """
    if not request.url:
        raise HTTPException(status_code=400, detail="url is required")

    # TODO: Implement URL fetching and processing
    raise HTTPException(
        status_code=501,
        detail="URL fact-checking not yet implemented"
    )


@router.get("/status/{request_id}")
async def get_status(request_id: str):
    """
    Get the status of a fact-check request.

    For long-running requests, poll this endpoint for updates.
    """
    # TODO: Implement request tracking with database
    raise HTTPException(
        status_code=501,
        detail="Status tracking requires database implementation"
    )
