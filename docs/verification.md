# Verification record

Verified 2026-08-13 on the build workstation.

- `pytest`: **7 passed** — validation, timestamp conversion, Markdown/VTT/SRT/JSON output, and failed job persistence.
- End-to-end local inference: **passed** using faster-whisper `base`, CPU `int8`, four threads, automatic language detection, and a 13.08-second public JFK speech sample packaged as a local MP4. It produced 2 segments and all four required outputs with `REVIEW_REQUIRED` status.
- Input SHA-256: `f2d12c18987341fca9e6f00a957aeb5deb357a43291a864bf7e3fe82c733c9d6`.
- Markdown transcript SHA-256: `ce2e6f4fe58f2479b3844ed76a2419fe296d3f80a4b10bc6fcb2a7d87b3de1dc`.

The sample MP4 and generated outputs are intentionally Git-ignored and are not distributed with this repository. The model-only initial cache population required an explicit temporary opt-out of local-files-only mode; the actual MP4 was read and processed locally.

Docker Compose validation could not run on this development WSL instance because Docker Desktop WSL integration is not enabled here. The Compose file was designed from the active T480 lab conventions and should be checked with `docker compose --profile transcribe config` on the T480 before its first job.

## T480 on-demand folder workflow verification

The governed T480 adapter was extended with fixed transcription deployment, model-prefetch, preflight, and single-item processing operations, plus a human-triggered `submit-transcription-folder` action. On 2026-08-13, the T480 deployment was updated to commit `c5018ec`; its Compose image built successfully, the `base` model cache prefetch completed, and final preflight reported `transcriber_image=present`, `incoming_count=0`, and `transcriber_preflight=ok`.

The initial model prefetch correctly exposed a read-only filesystem conflict in Hugging Face/Xet's default cache location. It was corrected by routing `HF_HOME` and `XDG_CACHE_HOME` to the persistent writable model-cache volume, while retaining a read-only worker filesystem. No source MP4 was involved in either model-cache attempt.
