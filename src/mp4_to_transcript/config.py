"""Configuration loaded from local environment variables only."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    output_dir: Path
    model_cache: Path
    model_name: str
    compute_type: str
    language: str | None
    cpu_threads: int
    local_files_only: bool

    @classmethod
    def from_environment(cls) -> "Settings":
        language = os.getenv("WHISPER_LANGUAGE", "").strip() or None
        cpu_threads = int(os.getenv("TRANSCRIBE_CPU_THREADS", "4"))
        if cpu_threads < 1:
            raise ValueError("TRANSCRIBE_CPU_THREADS must be at least 1")
        return cls(
            output_dir=Path(os.getenv("TRANSCRIPT_OUTPUT_DIR", "./outputs")),
            model_cache=Path(os.getenv("WHISPER_MODEL_CACHE", "./model-cache")),
            model_name=os.getenv("WHISPER_MODEL", "base"),
            compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
            language=language,
            cpu_threads=cpu_threads,
            local_files_only=_as_bool(os.getenv("WHISPER_LOCAL_FILES_ONLY", "true")),
        )
