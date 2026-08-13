"""Render the four review artefacts from the same segment list."""

from __future__ import annotations

import hashlib
import json
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
        f"source_filename: {source_filename}",
        f"source_sha256: {source_sha256}",
        f"transcription_model: {model}",
        f"transcribed_at: {transcribed_at}",
        "status: REVIEW_REQUIRED",
        "---",
        "",
    ]
    markdown_lines.extend(
        f"[{markdown_timestamp(segment.start)}] {segment.text.strip()}" for segment in segment_list
    )
    markdown_path.write_text("\n".join(markdown_lines).rstrip() + "\n", encoding="utf-8")

    vtt_lines = ["WEBVTT", ""]
    for segment in segment_list:
        vtt_lines.extend(
            [
                f"{vtt_timestamp(segment.start)} --> {vtt_timestamp(segment.end)}",
                segment.text.strip(),
                "",
            ]
        )
    vtt_path.write_text("\n".join(vtt_lines), encoding="utf-8")

    srt_lines: list[str] = []
    for index, segment in enumerate(segment_list, start=1):
        srt_lines.extend(
            [
                str(index),
                f"{srt_timestamp(segment.start)} --> {srt_timestamp(segment.end)}",
                segment.text.strip(),
                "",
            ]
        )
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    json_path.write_text(
        json.dumps([segment.as_dict() for segment in segment_list], indent=2) + "\n", encoding="utf-8"
    )
    return {"markdown": markdown_path, "vtt": vtt_path, "srt": srt_path, "segments_json": json_path}
