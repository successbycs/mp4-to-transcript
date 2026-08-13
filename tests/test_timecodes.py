import pytest

from mp4_to_transcript.timecodes import markdown_timestamp, srt_timestamp, vtt_timestamp


def test_timestamp_formats_and_rounding() -> None:
    assert markdown_timestamp(0) == "00:00:00"
    assert markdown_timestamp(3723.9) == "01:02:03"
    assert vtt_timestamp(65.125) == "00:01:05.125"
    assert srt_timestamp(65.125) == "00:01:05,125"
    assert vtt_timestamp(0.9996) == "00:00:01.000"


def test_negative_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError):
        vtt_timestamp(-0.1)
