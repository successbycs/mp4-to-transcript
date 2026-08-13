"""CLI entry point for a local, review-first transcription workflow."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import typer

from .config import Settings
from .worker import TranscriptionService

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def health() -> None:
    """Check local prerequisites without loading a Whisper model."""
    settings = Settings.from_environment()
    for path in (settings.output_dir, settings.model_cache):
        path.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "ok" if shutil.which("ffmpeg") and shutil.which("ffprobe") else "degraded",
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "ffprobe": bool(shutil.which("ffprobe")),
        "output_dir": str(settings.output_dir.resolve()),
        "model_cache": str(settings.model_cache.resolve()),
        "cpu_only": True,
        "model": settings.model_name,
        "compute_type": settings.compute_type,
        "local_files_only": settings.local_files_only,
    }
    typer.echo(json.dumps(report, indent=2))
    if report["status"] != "ok":
        raise typer.Exit(code=1)


@app.command()
def transcribe(input_mp4: Path = typer.Argument(..., exists=True, readable=True)) -> None:
    """Validate one MP4, then create reviewable local transcript artefacts."""
    metadata = TranscriptionService(Settings.from_environment()).run(input_mp4)
    typer.echo(json.dumps(metadata.as_dict(), indent=2))
    if metadata.status == "FAILED":
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
