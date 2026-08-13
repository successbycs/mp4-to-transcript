# Operations

## Normal job

1. Put one private MP4 outside the repository or in ignored `inputs/`.
2. Run `mp4-to-transcript health` to check `ffmpeg`, `ffprobe`, and writable local paths.
3. Run `mp4-to-transcript transcribe /path/to/video.mp4`.
4. Open `outputs/<job_id>/transcript.md`, correct it against the media, and make a separate human approval decision before Solution 2 ingestion.

The worker validates the MP4 and its audio stream with `ffprobe`, calculates an input SHA-256, extracts 16 kHz mono WAV locally with `ffmpeg`, runs faster-whisper on CPU, and deletes the temporary WAV when finished. It never sends media to a cloud service.

## Failure handling

The CLI exits non-zero for a failed job. Inspect `outputs/<job_id>/job.json`; its short `error_summary` is safe operational context, while source media is left untouched. Common causes are a missing audio stream, an invalid MP4, missing ffmpeg, or an absent offline model cache.

Do not retry concurrently on the T480. Jobs are intentionally one-at-a-time so the shared local lab remains usable.

## Cleanup

Outputs and model cache are intentionally persistent. Delete a specific completed job directory only after its review material is no longer needed; never run broad recursive deletion commands against the repository or an unresolved path. Container cleanup is safe with `docker compose --profile transcribe down`; it preserves the model-cache volume. Do not use `-v` unless deleting cached models is intentional.
