# Job lifecycle

## States

```text
DISCOVERED → STAGED → RUNNING → REVIEW_REQUIRED → human review / Solution 2 decision
                    └────────→ FAILED
```

Only `REVIEW_REQUIRED` jobs have all four transcript outputs and are eligible for governed export to the Windows `Transcripts` folder. `REVIEW_REQUIRED` is a mandatory human-review gate, not a quality guarantee or approval.

## Per-file processing

1. The adapter finds direct `.mp4` files in the selected Windows folder, in lexical filename order.
2. It hashes each local source. A hash with an existing successful job is skipped, making a resumed batch idempotent.
3. It uploads one source to fixed T480 Windows staging, then moves it through a fixed WSL operation to the temporary inbox.
4. The worker validates MP4/audio with `ffprobe`, calculates source SHA-256, extracts a temporary 16 kHz mono WAV with `ffmpeg`, and invokes faster-whisper on CPU.
5. The worker creates `job.json` with `RUNNING` before inference. On success it writes the transcript formats, calculates the Markdown transcript SHA-256, and changes the status to `REVIEW_REQUIRED`. On error it writes `FAILED` with a bounded error summary.
6. The successful temporary inbox file is deleted. Original Windows media remains unchanged.

## Artefacts

`outputs/<job_id>/` is the canonical T480 job record:

- `transcript.md` — primary human-review file, with `REVIEW_REQUIRED` front matter
- `transcript.vtt` and `transcript.srt` — timestamped caption formats
- `segments.json` — start/end/text segment list
- `job.json` — source hash, duration, engine/model settings, timestamps, status, counts, output paths, and error summary

The governed retrieval flow copies only successful review jobs to `C:\Users\chris\Videos\Transcripts\<source stem>\`.

## Interruption and recovery

An interrupted remote control session must not cause duplicate completed work. The adapter checks completed source SHA-256 values before a new submission and skips matches. Its diagnostics operation reports active worker containers, temporary inbox contents, and the latest job metadata. Completed temporary inbox copies can be cleaned only when their hashes exactly match successful job metadata.

If an interrupted submission leaves exactly one unprocessed inbox file, the fixed `transcription_process_existing_inbox` operation can recover it. If an inbox file is associated with a failed job, the batch stops and requires deliberate operator recovery; later source files are not processed automatically.

## Solution 2 handoff

Solution 2 may consume only a human-reviewed and separately approved Markdown transcript. It must retain provenance from `job.json`—at minimum source filename/SHA-256, transcript SHA-256, model configuration, and review decision—and must not treat raw `REVIEW_REQUIRED` output as approved knowledge.
