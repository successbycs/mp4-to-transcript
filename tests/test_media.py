import json
import subprocess
from pathlib import Path

import pytest

from mp4_to_transcript.media import MediaValidationError, validate_mp4


def test_validate_mp4_requires_mp4_suffix(tmp_path: Path) -> None:
    path = tmp_path / "audio.wav"
    path.write_bytes(b"not media")
    with pytest.raises(MediaValidationError, match=".mp4"):
        validate_mp4(path)


def test_validate_mp4_reads_duration_and_audio(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path = tmp_path / "lesson.mp4"
    path.write_bytes(b"placeholder")
    payload = {"format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": "10.5"}, "streams": [{"codec_type": "audio"}]}

    def fake_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 0, json.dumps(payload), "")

    monkeypatch.setattr("mp4_to_transcript.media.subprocess.run", fake_run)
    media = validate_mp4(path)
    assert media.duration_seconds == 10.5
    assert media.has_audio is True


def test_validate_mp4_rejects_no_audio(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path = tmp_path / "silent.mp4"
    path.write_bytes(b"placeholder")
    payload = {"format": {"format_name": "mp4", "duration": "10"}, "streams": [{"codec_type": "video"}]}
    monkeypatch.setattr(
        "mp4_to_transcript.media.subprocess.run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, json.dumps(payload), ""),
    )
    with pytest.raises(MediaValidationError, match="no audio"):
        validate_mp4(path)
