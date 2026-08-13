"""Render the four review artefacts from the same segment list."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable

from .models import Segment
from .timecodes import markdown_timestamp, srt_timestamp, vtt_timestamp


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_text_atomically(path: Path, content: str) -> None:
    """Replace one UTF-8 artefact without leaving a truncated final file."""
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    try:
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def write_json_atomically(path: Path, value: object, *, sort_keys: bool = False) -> None:
    content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=sort_keys) + "\n"
    _write_text_atomically(path, content)


def write_outputs(
    directory: Path,
    *,
    source_filename: str,
    source_sha256: str,
    model: str,
    transcribed_at: str,
    segments: Iterable[Segment],
) -> dict[str, Path]:
    """Write Markdown, VTT, SRT, and JSON segments; all are review-required."""
    directory.mkdir(parents=True, exist_ok=True)
    segment_list = list(segments)
    markdown_path = directory / "transcript.md"
    vtt_path = directory / "transcript.vtt"
    srt_path = directory / "transcript.srt"
    json_path = directory / "segments.json"

    markdown_lines = [
        "---",
        f"source_filename: {json.dumps(source_filename)}",
        f"source_sha256: {json.dumps(source_sha256)}",
        f"transcription_model: {json.dumps(model)}",
        f"transcribed_at: {json.dumps(transcribed_at)}",
        "status: REVIEW_REQUIRED",
        "---",
        "",
    ]
    markdown_lines.extend(
        f"[{markdown_timestamp(segment.start)}] {segment.text}" for segment in segment_list
    )
    _write_text_atomically(markdown_path, "\n".join(markdown_lines).rstrip() + "\n")

    vtt_lines = ["WEBVTT", ""]
    for segment in segment_list:
        vtt_lines.extend(
            [
                f"{vtt_timestamp(segment.start)} --> {vtt_timestamp(segment.end)}",
                segment.text,
                "",
            ]
        )
    _write_text_atomically(vtt_path, "\n".join(vtt_lines))

    srt_lines: list[str] = []
    for index, segment in enumerate(segment_list, start=1):
        srt_lines.extend(
            [
                str(index),
                f"{srt_timestamp(segment.start)} --> {srt_timestamp(segment.end)}",
                segment.text,
                "",
            ]
        )
    _write_text_atomically(srt_path, "\n".join(srt_lines))
    write_json_atomically(json_path, [segment.as_dict() for segment in segment_list])
    return {"markdown": markdown_path, "vtt": vtt_path, "srt": srt_path, "segments_json": json_path}
