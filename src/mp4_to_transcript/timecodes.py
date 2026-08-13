"""Subtitle timestamp conversion with millisecond precision."""

from __future__ import annotations


def _milliseconds(seconds: float) -> int:
    if seconds < 0:
        raise ValueError("timestamp cannot be negative")
    return round(seconds * 1000)


def _parts(seconds: float) -> tuple[int, int, int, int]:
    total = _milliseconds(seconds)
    hours, remainder = divmod(total, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds_part, millis = divmod(remainder, 1_000)
    return hours, minutes, seconds_part, millis


def markdown_timestamp(seconds: float) -> str:
    hours, minutes, seconds_part, _ = _parts(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds_part:02d}"


def vtt_timestamp(seconds: float) -> str:
    hours, minutes, seconds_part, millis = _parts(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds_part:02d}.{millis:03d}"


def srt_timestamp(seconds: float) -> str:
    return vtt_timestamp(seconds).replace(".", ",")
