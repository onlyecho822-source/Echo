"""
Audio processing service for speech-to-text transcription.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

from app.config import settings
from app.models.schemas import TranscriptionResult


class AudioProcessor:
    """Process audio files and streams for transcription."""

    def __init__(self):
        self._model = None
        self._model_name = settings.whisper_model

    def _load_model(self):
        """Lazy load the Whisper model."""
        if self._model is None:
            try:
                import whisper
                self._model = whisper.load_model(self._model_name)
            except Exception as e:
                raise RuntimeError(f"Failed to load Whisper model: {e}")
        return self._model

    async def transcribe_file(
        self,
        file_path: str | Path,
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe an audio file to text.

        Args:
            file_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'es')

        Returns:
            TranscriptionResult with text and segments
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        model = self._load_model()

        # Transcribe with Whisper
        options = {}
        if language:
            options["language"] = language

        result = model.transcribe(str(file_path), **options)

        # Extract segments with timestamps
        segments = []
        for segment in result.get("segments", []):
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
            })

        return TranscriptionResult(
            text=result["text"].strip(),
            segments=segments,
            language=result.get("language"),
            duration_seconds=segments[-1]["end"] if segments else None,
        )

    async def transcribe_bytes(
        self,
        audio_data: bytes,
        file_extension: str = "wav",
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio from bytes.

        Args:
            audio_data: Raw audio bytes
            file_extension: File extension for temp file
            language: Optional language code

        Returns:
            TranscriptionResult
        """
        # Write to temp file for Whisper
        with tempfile.NamedTemporaryFile(
            suffix=f".{file_extension}",
            delete=False
        ) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            return await self.transcribe_file(tmp_path, language)
        finally:
            os.unlink(tmp_path)

    async def transcribe_stream_chunk(
        self,
        audio_chunk: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe a chunk of audio from a stream.

        Args:
            audio_chunk: Numpy array of audio samples
            sample_rate: Audio sample rate
            language: Optional language code

        Returns:
            TranscriptionResult
        """
        import soundfile as sf

        # Write chunk to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, audio_chunk, sample_rate)
            tmp_path = tmp.name

        try:
            return await self.transcribe_file(tmp_path, language)
        finally:
            os.unlink(tmp_path)

    def get_audio_duration(self, file_path: str | Path) -> float:
        """Get the duration of an audio file in seconds."""
        import soundfile as sf
        info = sf.info(str(file_path))
        return info.duration

    def validate_audio_file(self, file_path: str | Path) -> bool:
        """
        Validate that a file is a valid audio file.

        Returns:
            True if valid, raises exception otherwise
        """
        file_path = Path(file_path)

        # Check file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check duration
        duration = self.get_audio_duration(file_path)
        if duration > settings.max_audio_duration_seconds:
            raise ValueError(
                f"Audio duration ({duration:.1f}s) exceeds maximum "
                f"({settings.max_audio_duration_seconds}s)"
            )

        return True


# Global instance
audio_processor = AudioProcessor()
