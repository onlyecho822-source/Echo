"""
Video and image processing API routes.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.config import settings
from app.models.schemas import OCRResult
from app.services.video_processor import video_processor

router = APIRouter()


@router.post("/ocr", response_model=OCRResult)
async def extract_text_from_image(
    file: UploadFile = File(...),
    language: str = "eng",
):
    """
    Extract text from an image using OCR.

    Supports: png, jpg, jpeg, gif, bmp, tiff

    Args:
        file: Image file
        language: Tesseract language code (default: eng)

    Returns:
        OCR result with extracted text
    """
    # Validate file extension
    filename = file.filename or "image"
    extension = Path(filename).suffix.lower().lstrip(".")
    valid_extensions = {"png", "jpg", "jpeg", "gif", "bmp", "tiff"}

    if extension not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image format: {extension}. Supported: {', '.join(valid_extensions)}"
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
        result = await video_processor.extract_text_from_image(file_path, language)

        # Clean up
        file_path.unlink(missing_ok=True)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR failed: {str(e)}"
        )


@router.post("/process")
async def process_video(
    file: UploadFile = File(...),
    extract_frames: bool = True,
    transcribe_audio: bool = True,
    frame_interval: float = 5.0,
):
    """
    Process a video file for text and audio extraction.

    Supports: mp4, avi, mov, mkv, webm

    Args:
        file: Video file
        extract_frames: Whether to OCR video frames
        transcribe_audio: Whether to transcribe audio track
        frame_interval: Seconds between frame captures

    Returns:
        Processing result with transcription and frame texts
    """
    # Validate file extension
    filename = file.filename or "video"
    extension = Path(filename).suffix.lower().lstrip(".")
    valid_extensions = {"mp4", "avi", "mov", "mkv", "webm"}

    if extension not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid video format: {extension}. Supported: {', '.join(valid_extensions)}"
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

        # Process video
        result = await video_processor.process_video(
            file_path,
            extract_frames=extract_frames,
            transcribe_audio=transcribe_audio,
            frame_interval_seconds=frame_interval,
        )

        # Clean up
        file_path.unlink(missing_ok=True)

        # Format response
        response = {
            "duration_seconds": result["duration_seconds"],
            "transcription": None,
            "frame_texts": result["frame_texts"],
        }

        if result["transcription"]:
            response["transcription"] = {
                "text": result["transcription"].text,
                "segments": result["transcription"].segments,
                "language": result["transcription"].language,
            }

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video processing failed: {str(e)}"
        )


@router.get("/config")
async def get_video_config():
    """Get video processing configuration."""
    return {
        "supported_video_formats": ["mp4", "avi", "mov", "mkv", "webm"],
        "supported_image_formats": ["png", "jpg", "jpeg", "gif", "bmp", "tiff"],
        "max_duration_seconds": settings.max_video_duration_seconds,
        "max_file_size_mb": settings.max_upload_size_mb,
    }
