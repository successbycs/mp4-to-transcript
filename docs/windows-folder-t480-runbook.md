# Windows folder → T480 transcription runbook

Use this runbook when a human operator has a folder in Windows Explorer containing videos to be transcribed. It is a deliberate batch action, not an always-on service or folder watcher.

## What happens

```text
Windows source folder (unchanged)
        │  one MP4 at a time, SSH key + host verification
        ▼
T480 transient inbox: incoming/<filename>.mp4
        │  one-shot, CPU-only Docker worker
        ▼
T480 outputs/<job_id>/{transcript.md,.vtt,.srt,segments.json,job.json}
```

The original video stays in the Windows folder. A T480 inbox copy is removed only after a successful job. The worker exits after each video; no container, web server, or folder watcher remains running.

## First-time readiness

The T480 checkout, image, and approved model cache have been prepared and verified. To reproduce that setup after a rebuild or an intentional cache deletion, run these governed actions from `cs-ai-lab-infra`:

```bash
python3 scripts/t480_adapter.py execute --operation transcription_deploy --approve
python3 scripts/t480_adapter.py execute --operation transcription_model_prefetch --approve
python3 scripts/t480_adapter.py execute --operation transcription_preflight
```

`transcription_model_prefetch` downloads the open-source faster-whisper `base` model into the T480's persistent private cache. It handles no media. Normal jobs retain `WHISPER_LOCAL_FILES_ONLY=true` and do not contact a cloud service.

## Submit a folder

1. Put only the intended direct MP4 files in a Windows folder. Subfolders are not scanned.
2. Use portable names consisting of letters, numbers, spaces, dots, underscores, hyphens, and parentheses. Rename unusual names before submission.
3. Request the batch explicitly, or run:

   ```bash
   cd /home/chris/projects/cs-ai-lab-infra
   python3 scripts/t480_adapter.py submit-transcription-folder \
     --source-folder 'C:\Users\chris\Videos\To Transcribe' --approve
   ```

The adapter sorts direct `.mp4` files by filename. For every file it uploads, waits for the job, confirms its success, and only then submits the next. It refuses to start when an earlier failed file is still in the T480 inbox.

## Review and handoff

Each success is stored on the T480 at `outputs/<job_id>/`. Review `transcript.md` against the original video. The transcript remains `REVIEW_REQUIRED` until a human corrects and approves it. Do not ingest raw output into Solution 2 or any knowledge base.

The initial MVP keeps outputs on the T480. A separate governed retrieval/export operation is required before copying review files back to the laptop; do not use an ad-hoc remote shell command for this.

## Failure recovery

If an upload fails, no remote job starts and the Windows source remains intact. If transcription fails, the adapter stops the batch immediately and leaves that one T480 inbox copy in place. Inspect its associated `job.json` (when present), resolve the issue, then intentionally rerun or remove that exact inbox file through a future governed recovery action. Do not submit a second folder until the inbox is empty.

## Safety boundaries

- Source media is never sent to a cloud transcription service.
- The adapter reuses its Windows OpenSSH key authentication and strict host-key checking.
- It transfers only MP4 files from the operator-selected folder; it does not recurse or watch for later changes.
- The shared T480 PostgreSQL, n8n, and Ollama services are not used or modified.
- Four CPU threads and a 5 GiB memory limit protect the T480's shared capacity.
- Transcription quality is not guaranteed; human review is mandatory.
