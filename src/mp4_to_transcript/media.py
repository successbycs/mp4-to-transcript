"""ffprobe/ffmpeg boundary: inspect media before local inference."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .models import MediaInfo


class MediaValidationError(ValueError):
    """The supplied file is not a usable MP4 with an audio stream."""


def validate_mp4(path: Path) -> MediaInfo:
    if not path.is_file():
        raise MediaValidationError(f"Input file does not exist: {path}")
    if path.suffix.lower() != ".mp4":
        raise MediaValidationError("Input must have an .mp4 extension")
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=format_name,duration", "-show_streams", "-of", "json", str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
    except FileNotFoundError as error:
        raise MediaValidationError("ffprobe is required but was not found") from error
    except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
        raise MediaValidationError("ffprobe could not read a valid MP4") from error

    format_data = payload.get("format", {})
    format_name = str(format_data.get("format_name", ""))
    if "mp4" not in format_name.split(","):
        raise MediaValidationError("Media container is not MP4")
    try:
        duration = float(format_data["duration"])
    except (KeyError, TypeError, ValueError) as error:
        raise MediaValidationError("Media duration is unavailable") from error
    if duration <= 0:
        raise MediaValidationError("Media duration must be positive")
    has_audio = any(stream.get("codec_type") == "audio" for stream in payload.get("streams", []))
    if not has_audio:
        raise MediaValidationError("MP4 has no audio stream to transcribe")
    return MediaInfo(duration_seconds=duration, format_name=format_name, has_audio=True)


def extract_mono_wav(input_path: Path, output_path: Path) -> None:
    """Extract a 16 kHz mono WAV locally for a predictable Whisper input."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-nostdin", "-y", "-i", str(input_path), "-vn", "-ac", "1",
                "-ar", "16000", "-c:a", "pcm_s16le", str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError("ffmpeg is required but was not found") from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError("ffmpeg could not extract the MP4 audio stream") from error
