import json
from pathlib import Path

from mp4_to_transcript.models import Segment
from mp4_to_transcript.outputs import write_outputs


def test_output_formats_are_reviewable_and_consistent(tmp_path: Path) -> None:
    paths = write_outputs(
        tmp_path,
        source_filename="lesson-01.mp4",
        source_sha256="abc123",
        model="base",
        transcribed_at="2026-08-13T00:00:00Z",
        segments=[Segment(10, 12.5, " Hello world. "), Segment(85, 90, "Second line.")],
    )
    markdown = paths["markdown"].read_text()
    assert "status: REVIEW_REQUIRED" in markdown
    assert "[00:00:10] Hello world." in markdown
    assert paths["vtt"].read_text().startswith("WEBVTT\n")
    assert "00:00:10,000 --> 00:00:12,500" in paths["srt"].read_text()
    assert json.loads(paths["segments_json"].read_text()) == [
        {"start": 10, "end": 12.5, "text": "Hello world."},
        {"start": 85, "end": 90, "text": "Second line."},
    ]


def test_markdown_front_matter_quotes_untrusted_values(tmp_path: Path) -> None:
    paths = write_outputs(
        tmp_path,
        source_filename='lesson: "one".mp4',
        source_sha256="abc123",
        model="base",
        transcribed_at="2026-08-13T00:00:00Z",
        segments=[Segment(0, 1, "Text.")],
    )
    assert 'source_filename: "lesson: \\"one\\".mp4"' in paths["markdown"].read_text()


def test_json_keeps_transcript_unicode_readable(tmp_path: Path) -> None:
    paths = write_outputs(
        tmp_path,
        source_filename="lesson.mp4",
        source_sha256="abc123",
        model="base",
        transcribed_at="2026-08-13T00:00:00Z",
        segments=[Segment(0, 1, "Kia ora — welcome.")],
    )
    assert "Kia ora — welcome." in paths["segments_json"].read_text(encoding="utf-8")
