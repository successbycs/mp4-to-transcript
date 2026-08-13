"""Small, explicit data contracts for a transcription job."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Literal


JobStatus = Literal["RUNNING", "REVIEW_REQUIRED", "FAILED"]


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str

    def __post_init__(self) -> None:
        if not math.isfinite(self.start) or not math.isfinite(self.end):
            raise ValueError("segment timestamps must be finite")
        if self.start < 0 or self.end < self.start:
            raise ValueError("segment timestamps must satisfy 0 <= start <= end")
        text = self.text.strip()
        if not text:
            raise ValueError("segment text cannot be empty")
        object.__setattr__(self, "text", text)

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
    status: JobStatus
    segment_count: int
    transcript_sha256: str | None
    output_paths: dict[str, str]
    error_summary: str | None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def complete(
        self,
        *,
        segment_count: int,
        transcript_sha256: str,
        output_paths: dict[str, str],
        completed_at: str,
    ) -> None:
        self.completed_at = completed_at
        self.status = "REVIEW_REQUIRED"
        self.segment_count = segment_count
        self.transcript_sha256 = transcript_sha256
        self.output_paths = output_paths

    def fail(self, error_summary: str, completed_at: str) -> None:
        self.completed_at = completed_at
        self.status = "FAILED"
        self.error_summary = error_summary
