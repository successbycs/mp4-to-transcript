# Output format and review contract

Every completed transcription has the job status `REVIEW_REQUIRED`. It is an explicit human-review gate, not a statement of transcription quality.

`transcript.md` is the primary review file:

```markdown
---
source_filename: lesson-01.mp4
source_sha256: 8c...
transcription_model: base
transcribed_at: 2026-08-13T00:00:00Z
status: REVIEW_REQUIRED
---

[00:00:10] Transcript text.

[00:01:25] Transcript text.
```

`transcript.vtt` uses `HH:MM:SS.mmm` timing; `transcript.srt` uses `HH:MM:SS,mmm`; and `segments.json` contains only this repeatable segment contract:

```json
[
  {"start": 10.0, "end": 12.5, "text": "Transcript text."}
]
```

`job.json` is the job record. It contains `job_id`, input filename and SHA-256, duration, `transcription_engine` and `engine_version`, configured model/version, compute type, language setting, start/completion timestamps, status, segment count, Markdown transcript SHA-256, output paths, and an error summary. Failed jobs write `job.json` with `status: FAILED` and no output paths.

The Markdown text is deliberately not automatically summarised, translated, diarised, embedded, indexed, or approved. A reviewer must correct it and record the later approval in Solution 2.
