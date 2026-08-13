# System architecture

## Purpose and boundary

`mp4-to-transcript` prepares one local MP4 at a time for human review. It creates timestamped Markdown, WebVTT, SRT, JSON segments, and job metadata. It stops there: no embeddings, database, semantic search, chat, RAG, diarisation, translation, summaries, cloud transcription, or GPU execution.

## Deployment topology

```text
T16 / Windows laptop                                  T480 / private WSL + Docker
────────────────────                                  ──────────────────────────
Windows Explorer source folder                         fixed Windows SSH staging
C:\Users\chris\Videos\To Transcribe                  C:\Users\chris\TranscriptionInbox
          │  SSH key authentication + strict host key           │
          │  one MP4 at a time                                  │ fixed WSL move
          └────────────────────────────────────────────────────► /home/chris/projects/mp4-to-transcript/incoming
                                                                      │
                                                                      ▼
                                                       one-shot Docker Compose worker
                                                       faster-whisper / CPU / int8
                                                       ffprobe + ffmpeg temporary WAV
                                                                      │
                                                                      ▼
                                                       outputs/<job_id>/
                                                       transcript.md, .vtt, .srt,
                                                       segments.json, job.json
                                                                      │ completed jobs only
                                                                      ▼
                                                       fixed Windows export staging
                                                       C:\Users\chris\TranscriptionExports
                                                                      │ governed SCP retrieval
                                                                      ▼
Windows review folder
C:\Users\chris\Videos\Transcripts\<source MP4 stem>\
```

The governed operations live in `cs-ai-lab-infra/scripts/t480_adapter.py`; the transcriber repository owns the worker image, output contracts, and its documentation. They are separate Git repositories.

## On-demand execution

The worker is never configured as a daemon, scheduled task, or folder watcher. The human operator explicitly submits a folder. Each worker invocation validates one MP4, transcribes it, writes job artefacts, and exits. The Compose service has no published port, has `restart: "no"`, and is restricted to four CPUs and 5 GiB memory.

T480 PostgreSQL, n8n, and Ollama are owned by `cs-ai-lab-infra` and are not used, duplicated, or started by this service.

## Security and privacy

- MP4 media is read locally and never sent to a cloud transcription service.
- Normal transcription has `WHISPER_LOCAL_FILES_ONLY=true`; the only permitted network access is the explicit model-only cache prefetch.
- Model data survives in a named Docker volume. Inputs, outputs, and the temporary inbox are Git-ignored.
- The adapter is fixed-operation only. It exposes no free-form remote shell, arbitrary upload destination, or arbitrary output-download destination.
- Windows source videos are preserved. A T480 temporary inbox copy is removed only after a successful job whose output record exists.

## Configuration and persistence

| Location | Purpose | Persistence |
| --- | --- | --- |
| `.env` on T480 | model, compute type, CPU threads, local paths | local-only, never Git |
| `whisper_model_cache` Docker volume | faster-whisper plus Hugging Face cache | persistent |
| `incoming/` on T480 | one temporary source copy during a job | transient/recovery only |
| `outputs/<job_id>/` on T480 | canonical job artefacts | persistent |
| Windows `Transcripts/<source stem>/` | operator review copy | persistent |

Export folders use the source MP4 filename without its extension so an operator can correlate them directly. The immutable `job_id`, source SHA-256, and transcript SHA-256 remain in `job.json`.
