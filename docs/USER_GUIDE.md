# User guide: MP4 transcription service

## What this service does

Give the service a Windows folder containing MP4 videos. It sends them to the private T480 one at a time and creates a set of timestamped transcript files for each video.

The T480 worker starts only when a transcription is requested and stops when that video finishes. Your videos are processed locally; they are not uploaded to a cloud transcription service.

The transcript is a draft. You must review and correct it before using it in a knowledge base or Solution 2.

## The normal workflow

### 1. Put videos in a source folder

In Windows Explorer, create or use this folder:

```text
C:\Users\chris\Videos\To Transcribe
```

Put the MP4s you want to process directly in that folder. Do not put them only inside subfolders; the batch scans the selected folder itself.

Normal Windows filenames are supported, including spaces, hyphens, underscores, and parentheses, for example:

```text
Lesson 01 - Introduction.mp4
Seminar (1).mp4
```

### 2. Ask for the folder to be processed

Tell Codex:

> Process `C:\Users\chris\Videos\To Transcribe`

Codex will submit each MP4 in filename order. It waits for one video to finish before starting the next, keeping the T480 resource-conscious.

You can ask for an update at any time:

> How are the videos coming along?

### 3. Find the transcripts

Completed review files appear on this laptop in:

```text
C:\Users\chris\Videos\Transcripts
```

Each folder is named after its original video (without `.mp4`):

```text
Transcripts\
└── Lesson 01 - Introduction\
    ├── transcript.md
    ├── transcript.vtt
    ├── transcript.srt
    ├── segments.json
    └── job.json
```

The original videos stay in `To Transcribe`; the service does not move or delete them.

### 4. Review the Markdown transcript

Open `transcript.md` first. It is the primary review file and is intentionally marked:

```yaml
status: REVIEW_REQUIRED
```

Correct transcription mistakes while checking against the original video. The `[HH:MM:SS]` markers show where each passage begins.

Do not treat the draft as approved knowledge. After review, keep a separate record of the human approval decision before handing it to Solution 2.

## What each file is for

| File | Use |
| --- | --- |
| `transcript.md` | Human review and editing; primary file for later knowledge preparation. |
| `transcript.vtt` | WebVTT captions for web video players. |
| `transcript.srt` | SRT subtitles for many video tools. |
| `segments.json` | Structured start/end timestamps and transcript text. |
| `job.json` | Job audit record: source SHA-256, model, duration, status, and output details. |

## What happens if something stops

The service is designed to resume safely.

- If the control connection ends after some successful videos, ask Codex to process the same folder again. Completed source SHA-256 values are skipped; it continues with the remaining videos.
- If a transcription genuinely fails, the batch stops at that file rather than silently moving on. Ask Codex to inspect the job and recover it.
- If outputs have completed on the T480 but are not yet visible on this laptop, ask:

  > Pull the completed transcript outputs

Only completed `REVIEW_REQUIRED` jobs are copied to the fixed `Transcripts` folder.

## Privacy, model, and limits

- Speech recognition uses the locally cached faster-whisper `base` model on the CPU-only T480.
- The Whisper model is already cached in the T480’s persistent WSL/Docker model storage.
- Transcription is not perfect. Technical terms, names, accents, crosstalk, and low-quality audio need careful review.
- The service does not translate, summarise, identify speakers, create embeddings, search content, or add anything to a knowledge base.
- Do not commit source videos or generated transcript files to Git.

## Optional technical commands

These are normally run by Codex, not required for the everyday workflow:

```bash
cd /home/chris/projects/cs-ai-lab-infra

# Submit a Windows folder explicitly.
python3 scripts/t480_adapter.py submit-transcription-folder \
  --source-folder 'C:\Users\chris\Videos\To Transcribe' --approve

# Copy completed review outputs to the fixed Windows folder.
python3 scripts/t480_adapter.py pull-transcription-outputs --approve

# Inspect worker, inbox, and job state.
python3 scripts/t480_adapter.py execute --operation transcription_diagnostics
```

For operational detail, see the [Windows-folder T480 runbook](windows-folder-t480-runbook.md) and [architecture](architecture/README.md).
