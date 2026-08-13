# User instructions

## Transcribe a folder of MP4 videos

1. In Windows Explorer, put MP4 files directly into:

   ```text
   C:\Users\chris\Videos\To Transcribe
   ```

2. Tell Codex:

   > Process `C:\Users\chris\Videos\To Transcribe`

3. Codex sends videos to the T480 one at a time. The service is on demand: it does not remain running between videos or batches.

4. Ask for progress whenever needed:

   > How are the videos coming along?

## Find and review the result

Completed outputs are pulled to:

```text
C:\Users\chris\Videos\Transcripts
```

Each folder is named after its source MP4. Open `transcript.md` first and check it against the video. It is deliberately labelled `REVIEW_REQUIRED`.

Each transcript folder includes:

- `transcript.md` — review and edit this
- `transcript.vtt` — WebVTT captions
- `transcript.srt` — subtitle file
- `segments.json` — timestamped transcript data
- `job.json` — job and provenance record

## If something pauses or outputs are missing

Tell Codex one of these:

> Process the same folder again.

Completed videos are detected by SHA-256 and skipped; the batch continues with remaining videos.

> Pull the completed transcript outputs.

This copies only completed review jobs from the T480 to your fixed Windows `Transcripts` folder.

> Inspect the transcription job.

Codex checks the T480 worker, temporary inbox, and job metadata before taking recovery action.

## Important rules

- Original MP4s are never moved or deleted.
- Video/audio stays local; it is not sent to a cloud transcription service.
- Whisper is local speech-to-text software, not a guarantee of perfect transcription.
- Review and correct every transcript before it enters Solution 2 or any knowledge base.
- Do not commit source videos or generated transcripts to Git.

For more detail, read the [full user guide](USER_GUIDE.md).
