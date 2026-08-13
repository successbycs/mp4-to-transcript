import pytest

from mp4_to_transcript.config import Settings
from mp4_to_transcript.models import Segment


def test_settings_reject_invalid_boolean(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHISPER_LOCAL_FILES_ONLY", "sometimes")
    with pytest.raises(ValueError, match="boolean"):
        Settings.from_environment()


def test_settings_rejects_invalid_thread_count(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRANSCRIBE_CPU_THREADS", "four")
    with pytest.raises(ValueError, match="integer"):
        Settings.from_environment()


def test_segment_normalizes_text_and_rejects_invalid_values() -> None:
    assert Segment(0, 1, " text ").text == "text"
    with pytest.raises(ValueError, match="timestamps"):
        Segment(2, 1, "text")
    with pytest.raises(ValueError, match="empty"):
        Segment(0, 1, " \t ")
