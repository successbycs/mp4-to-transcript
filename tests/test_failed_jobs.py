import json
from pathlib import Path

from mp4_to_transcript.config import Settings
from mp4_to_transcript.worker import TranscriptionService


def test_failed_job_persists_metadata(monkeypatch, tmp_path: Path) -> None:
    input_path = tmp_path / "bad.mp4"
    input_path.write_bytes(b"not an mp4")
    settings = Settings(
        output_dir=tmp_path / "outputs",
        model_cache=tmp_path / "cache",
        model_name="base",
        compute_type="int8",
        language=None,
        cpu_threads=1,
        local_files_only=True,
    )
    monkeypatch.setattr("mp4_to_transcript.worker.validate_mp4", lambda _path: (_ for _ in ()).throw(ValueError("bad media")))
    result = TranscriptionService(settings).run(input_path)
    persisted = json.loads((settings.output_dir / result.job_id / "job.json").read_text())
    assert result.status == "FAILED"
    assert result.completed_at is not None
    assert result.error_summary == "ValueError: bad media"
    assert persisted["status"] == "FAILED"
    assert persisted["output_paths"] == {}
