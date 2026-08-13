"""Small, explicit data contracts for a transcription job."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MediaInfo:
    duration_seconds: float
    format_name: str
    has_audio: bool


@dataclass
class JobMetadata:
    job_id: str
    input_filename: str
    input_sha256: str | None
    media_duration_seconds: float | None
    transcription_engine: str
    engine_version: str
    model: str
    model_version: str
    compute_type: str
    language_setting: str | None
    started_at: str
    completed_at: str | None
    status: str
    segment_count: int
    transcript_sha256: str | None
    output_paths: dict[str, str]
    error_summary: str | None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
