"""
Video and image processing service for frame extraction and OCR.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from app.config import settings
from app.models.schemas import OCRResult, TranscriptionResult
from app.services.audio_processor import audio_processor


class VideoProcessor:
    """Process video files and images for text extraction and analysis."""

    def __init__(self):
        self._tesseract_available = None

    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is available."""
        if self._tesseract_available is None:
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                self._tesseract_available = True
            except Exception:
                self._tesseract_available = False
        return self._tesseract_available

    async def extract_text_from_image(
        self,
        image_path: str | Path,
        language: str = "eng",
    ) -> OCRResult:
        """
        Extract text from an image using OCR.

        Args:
            image_path: Path to the image file
            language: Tesseract language code

        Returns:
            OCRResult with extracted text
        """
        import pytesseract

        if not self._check_tesseract():
            raise RuntimeError("Tesseract OCR is not installed")

        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load and preprocess image
        image = Image.open(image_path)

        # Get detailed OCR data
        ocr_data = pytesseract.image_to_data(
            image,
            lang=language,
            output_type=pytesseract.Output.DICT
        )

        # Extract text
        text = pytesseract.image_to_string(image, lang=language).strip()

        # Calculate average confidence
        confidences = [
            int(conf) for conf in ocr_data["conf"]
            if conf != "-1" and str(conf).isdigit()
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Extract text regions
        regions = []
        n_boxes = len(ocr_data["text"])
        for i in range(n_boxes):
            if int(ocr_data["conf"][i]) > 0:
                regions.append({
                    "text": ocr_data["text"][i],
                    "x": ocr_data["left"][i],
                    "y": ocr_data["top"][i],
                    "width": ocr_data["width"][i],
                    "height": ocr_data["height"][i],
                    "confidence": int(ocr_data["conf"][i]),
                })

        return OCRResult(
            text=text,
            confidence=avg_confidence / 100,  # Normalize to 0-1
            regions=regions,
        )

    async def extract_text_from_image_bytes(
        self,
        image_data: bytes,
        language: str = "eng",
    ) -> OCRResult:
        """Extract text from image bytes."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_data)
            tmp_path = tmp.name

        try:
            return await self.extract_text_from_image(tmp_path, language)
        finally:
            os.unlink(tmp_path)

    async def process_video(
        self,
        video_path: str | Path,
        extract_frames: bool = True,
        transcribe_audio: bool = True,
        frame_interval_seconds: float = 5.0,
    ) -> dict:
        """
        Process a video file for text and audio extraction.

        Args:
            video_path: Path to the video file
            extract_frames: Whether to extract and OCR frames
            transcribe_audio: Whether to transcribe audio
            frame_interval_seconds: Interval between frame captures

        Returns:
            Dictionary with transcription and frame OCR results
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        results = {
            "transcription": None,
            "frame_texts": [],
            "duration_seconds": 0,
        }

        # Open video
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        results["duration_seconds"] = duration

        # Check duration limit
        if duration > settings.max_video_duration_seconds:
            cap.release()
            raise ValueError(
                f"Video duration ({duration:.1f}s) exceeds maximum "
                f"({settings.max_video_duration_seconds}s)"
            )

        # Extract frames for OCR
        if extract_frames and self._check_tesseract():
            frame_interval = int(fps * frame_interval_seconds)
            frame_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    timestamp = frame_count / fps

                    # Save frame to temp file
                    with tempfile.NamedTemporaryFile(
                        suffix=".png",
                        delete=False
                    ) as tmp:
                        cv2.imwrite(tmp.name, frame)

                        try:
                            ocr_result = await self.extract_text_from_image(tmp.name)
                            if ocr_result.text.strip():
                                results["frame_texts"].append({
                                    "timestamp": timestamp,
                                    "text": ocr_result.text,
                                    "confidence": ocr_result.confidence,
                                })
                        finally:
                            os.unlink(tmp.name)

                frame_count += 1

        cap.release()

        # Extract and transcribe audio
        if transcribe_audio:
            audio_path = await self._extract_audio(video_path)
            if audio_path:
                try:
                    results["transcription"] = await audio_processor.transcribe_file(
                        audio_path
                    )
                finally:
                    os.unlink(audio_path)

        return results

    async def _extract_audio(self, video_path: Path) -> Optional[str]:
        """Extract audio track from video file."""
        try:
            import subprocess

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as tmp:
                # Use ffmpeg to extract audio
                result = subprocess.run(
                    [
                        "ffmpeg", "-i", str(video_path),
                        "-vn", "-acodec", "pcm_s16le",
                        "-ar", "16000", "-ac", "1",
                        "-y", tmp.name
                    ],
                    capture_output=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    return tmp.name
                else:
                    os.unlink(tmp.name)
                    return None
        except Exception:
            return None

    async def capture_frame(
        self,
        video_path: str | Path,
        timestamp_seconds: float,
    ) -> np.ndarray:
        """Capture a specific frame from a video."""
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp_seconds * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise ValueError(f"Could not capture frame at {timestamp_seconds}s")

        return frame


# Global instance
video_processor = VideoProcessor()
