# mp4-to-transcript

`mp4-to-transcript` is a deliberately small, private preparation tool: it turns **one local MP4** into timestamped transcript files that a human must review before the material enters any knowledge base.

It is not a knowledge base, chat app, RAG system, video library, translation service, diarisation system, or cloud transcription client.

## What it produces

Each job creates a private directory under `outputs/<job_id>/`:

- `transcript.md` — readable Markdown with `REVIEW_REQUIRED` front matter
- `transcript.vtt` — WebVTT captions
- `transcript.srt` — SRT subtitles
- `segments.json` — segment `start`, `end`, and `text`
- `job.json` — audit metadata and job state

Generated material and input media are ignored by Git. Do not commit them.

## Quick start (local CLI)

Prerequisites: Python 3.11+, `ffmpeg` (including `ffprobe`), and a locally cached faster-whisper model.

```bash
cp .env.example .env
# export the values in .env with your preferred local environment loader
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
mp4-to-transcript health
mp4-to-transcript transcribe /private/path/lesson-01.mp4
```

The default `WHISPER_MODEL=base` and `WHISPER_COMPUTE_TYPE=int8` are chosen for CPU-only T480 operation. `small` can be more accurate but needs more time and memory. There is no promise of perfect transcription: review and edit the Markdown before any downstream use.

### Model cache and offline policy

`WHISPER_LOCAL_FILES_ONLY=true` is the default. It means transcription never needs a network connection and fails safely if the configured model is absent from `WHISPER_MODEL_CACHE`.

If a model cache needs seeding, explicitly run a model-only prefetch on a controlled machine by temporarily setting `WHISPER_LOCAL_FILES_ONLY=false`. That fetches model artefacts only; the MP4 is never uploaded or sent to a transcription service. Copy the resulting cache to the T480 before normal offline use.

## T480 Docker operation

This repository deliberately does not join or recreate the `cs-ai-lab-infra` Compose stack. It has no PostgreSQL, n8n, Ollama, ports, or persistent worker. Start it only for a job:

```bash
mkdir -p inputs outputs
cp .env.example .env
# Place the private MP4 in ./inputs; it remains a read-only container mount.
docker compose --profile transcribe build
docker compose --profile transcribe run --rm transcriber health
docker compose --profile transcribe run --rm transcriber transcribe /input/lesson-01.mp4
```

The Compose worker is capped at four CPUs and 5 GiB memory, uses a one-worker CPU-only faster-whisper runtime, and exits when the job completes. The named `whisper_model_cache` volume persists model files while private media and outputs remain host-mounted, ignored directories.

Before the first offline transcription, seed the named model cache by an explicit, model-only action (no MP4 mount is used by the command):

```bash
docker compose --profile transcribe run --rm \
  -e WHISPER_LOCAL_FILES_ONLY=false transcriber health
```

`health` itself does not load a model; use the first real job to fetch a model if this temporary setting is used. Set the variable back to `true` immediately afterward. Alternatively, pre-populate the cache from a trusted offline source.

### Submit a Windows Explorer folder to the T480

For repeat use, do not copy files by hand. The governed T480 adapter provides a serial folder submission command. Give it the Windows folder that contains the MP4s; it processes direct `.mp4` files in filename order, one at a time:

```bash
cd /home/chris/projects/cs-ai-lab-infra
python3 scripts/t480_adapter.py submit-transcription-folder \
  --source-folder 'C:\Users\chris\Videos\To Transcribe' --approve
```

It uses the adapter's existing SSH host-key and key-authentication configuration. Each file is copied to the fixed private T480 inbox, run through this repository's one-shot Compose worker, and removed from the T480 inbox only after a successful job. Original videos stay in the Windows source folder; transcript outputs remain on the T480 under `outputs/<job_id>/`. It never starts a permanent worker and does not upload media to a cloud service.

The command refuses subfolders and filenames outside a conservative portable character set (`A–Z`, `a–z`, `0–9`, spaces, `.`, `_`, `-`). Rename unusual filenames first. Run its preflight before the first batch:

```bash
python3 scripts/t480_adapter.py execute --operation transcription_deploy --approve
python3 scripts/t480_adapter.py execute --operation transcription_model_prefetch --approve
python3 scripts/t480_adapter.py execute --operation transcription_preflight
```

See the complete [Windows-folder T480 runbook](docs/windows-folder-t480-runbook.md), [T480 assessment](docs/t480-assessment.md), [operations](docs/operations.md), and [output format](docs/output-format.md).

## Testing

```bash
pytest
```

Tests cover validation decisions, timestamp conversion, all output formats, and persisted failed-job metadata. They do not download a model or submit media anywhere.

## Solution 2 handoff

This MVP ends at a human-reviewed transcript. Solution 2 may ingest only reviewed, approved Markdown plus its provenance metadata. It should preserve `source_sha256`, transcript SHA-256, model settings, and review decision; it must not treat raw or `REVIEW_REQUIRED` output as knowledge-base content.
