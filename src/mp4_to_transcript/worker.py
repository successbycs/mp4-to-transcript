"""One-shot, CPU-only local transcription service."""

from __future__ import annotations

import json
import tempfile
import uuid
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Callable, Iterable

from .config import Settings
from .media import extract_mono_wav, validate_mp4
from .models import JobMetadata, Segment
from .outputs import sha256_file, write_outputs

Transcriber = Callable[[Path, Settings], Iterable[Segment]]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def faster_whisper_version() -> str:
    try:
        return version("faster-whisper")
    except PackageNotFoundError:
        return "unknown"


def transcribe_with_faster_whisper(audio_path: Path, settings: Settings) -> list[Segment]:
    """Load the model only for this job; no service remains running afterward."""
    from faster_whisper import WhisperModel

    settings.model_cache.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(
        settings.model_name,
        device="cpu",
        compute_type=settings.compute_type,
        download_root=str(settings.model_cache),
        local_files_only=settings.local_files_only,
        cpu_threads=settings.cpu_threads,
        num_workers=1,
    )
    segments, _info = model.transcribe(
        str(audio_path), language=settings.language, beam_size=1, vad_filter=False
    )
    return [
        Segment(start=float(segment.start), end=float(segment.end), text=segment.text.strip())
        for segment in segments
        if segment.text.strip()
    ]


class TranscriptionService:
    def __init__(self, settings: Settings, transcriber: Transcriber = transcribe_with_faster_whisper):
        self.settings = settings
        self.transcriber = transcriber

    def run(self, input_path: Path) -> JobMetadata:
        job_id = uuid.uuid4().hex
        job_dir = self.settings.output_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=False)
        started_at = utc_now()
        metadata = JobMetadata(
            job_id=job_id,
            input_filename=input_path.name,
            input_sha256=None,
            media_duration_seconds=None,
            transcription_engine="faster-whisper",
            engine_version=faster_whisper_version(),
            model=self.settings.model_name,
            model_version=self.settings.model_name,
            compute_type=self.settings.compute_type,
            language_setting=self.settings.language,
            started_at=started_at,
            completed_at=None,
            status="RUNNING",
            segment_count=0,
            transcript_sha256=None,
            output_paths={},
            error_summary=None,
        )
        self._write_metadata(job_dir, metadata)
        try:
            media_info = validate_mp4(input_path)
            input_sha256 = sha256_file(input_path)
            metadata.input_sha256 = input_sha256
            metadata.media_duration_seconds = media_info.duration_seconds
            self._write_metadata(job_dir, metadata)
            with tempfile.TemporaryDirectory(prefix="mp4-to-transcript-") as temp_dir:
                wav_path = Path(temp_dir) / "audio.wav"
                extract_mono_wav(input_path, wav_path)
                segments = list(self.transcriber(wav_path, self.settings))
            paths = write_outputs(
                job_dir,
                source_filename=input_path.name,
                source_sha256=input_sha256,
                model=self.settings.model_name,
                transcribed_at=utc_now(),
                segments=segments,
            )
            metadata.completed_at = utc_now()
            metadata.status = "REVIEW_REQUIRED"
            metadata.segment_count = len(segments)
            metadata.transcript_sha256 = sha256_file(paths["markdown"])
            metadata.output_paths = {key: str(path) for key, path in paths.items()}
            self._write_metadata(job_dir, metadata)
            return metadata
        except Exception as error:
            metadata.completed_at = utc_now()
            metadata.status = "FAILED"
            metadata.error_summary = _safe_error(error)
            self._write_metadata(job_dir, metadata)
            return metadata

    @staticmethod
    def _write_metadata(job_dir: Path, metadata: JobMetadata) -> None:
        (job_dir / "job.json").write_text(
            json.dumps(metadata.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def _safe_error(error: Exception) -> str:
    """Retain a short operational reason without leaking an arbitrary traceback."""
    message = " ".join(str(error).split())
    return f"{error.__class__.__name__}: {message}"[:500]
