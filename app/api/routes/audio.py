"""
Audio processing API routes.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.config import settings
from app.models.schemas import TranscriptionResult
from app.services.audio_processor import audio_processor

router = APIRouter()


@router.post("/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = None,
):
    """
    Transcribe an audio file to text.

    Supports: mp3, wav, m4a, ogg, flac

    Args:
        file: Audio file to transcribe
        language: Optional language code (e.g., 'en', 'es', 'fr')

    Returns:
        Transcription with text and timestamps
    """
    # Validate file extension
    filename = file.filename or "audio"
    extension = Path(filename).suffix.lower().lstrip(".")
    valid_extensions = {"mp3", "wav", "m4a", "ogg", "flac", "webm"}

    if extension not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format: {extension}. Supported: {', '.join(valid_extensions)}"
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

        # Validate audio duration
        try:
            audio_processor.validate_audio_file(file_path)
        except ValueError as e:
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=str(e))

        # Transcribe
        result = await audio_processor.transcribe_file(file_path, language)

        # Clean up
        file_path.unlink(missing_ok=True)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.get("/config")
async def get_audio_config():
    """Get audio processing configuration."""
    return {
        "supported_formats": ["mp3", "wav", "m4a", "ogg", "flac"],
        "max_duration_seconds": settings.max_audio_duration_seconds,
        "max_file_size_mb": settings.max_upload_size_mb,
        "whisper_model": settings.whisper_model,
    }
