"""Configuration loaded from local environment variables only."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("WHISPER_LOCAL_FILES_ONLY must be a boolean value")


@dataclass(frozen=True)
class Settings:
    output_dir: Path
    model_cache: Path
    model_name: str
    compute_type: str
    language: str | None
    cpu_threads: int
    local_files_only: bool

    def __post_init__(self) -> None:
        if not self.model_name.strip():
            raise ValueError("WHISPER_MODEL cannot be blank")
        if not self.compute_type.strip():
            raise ValueError("WHISPER_COMPUTE_TYPE cannot be blank")
        if self.cpu_threads < 1:
            raise ValueError("TRANSCRIBE_CPU_THREADS must be at least 1")

    @classmethod
    def from_environment(cls) -> "Settings":
        language = os.getenv("WHISPER_LANGUAGE", "").strip() or None
        try:
            cpu_threads = int(os.getenv("TRANSCRIBE_CPU_THREADS", "4"))
        except ValueError as error:
            raise ValueError("TRANSCRIBE_CPU_THREADS must be an integer") from error
        return cls(
            output_dir=Path(os.getenv("TRANSCRIPT_OUTPUT_DIR", "./outputs")),
            model_cache=Path(os.getenv("WHISPER_MODEL_CACHE", "./model-cache")),
            model_name=os.getenv("WHISPER_MODEL", "base"),
            compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
            language=language,
            cpu_threads=cpu_threads,
            local_files_only=_as_bool(os.getenv("WHISPER_LOCAL_FILES_ONLY", "true")),
        )
