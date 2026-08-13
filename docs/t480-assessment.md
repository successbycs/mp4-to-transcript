# T480 assessment and deployment decision

Inspected 2026-08-13 through `cs-ai-lab-infra/scripts/t480_adapter.py`, using its governed read-only `health`, `storage`, and `lab_runtime_diagnostics` operations.

| Resource | Observed | MVP decision |
| --- | ---: | --- |
| Physical memory | 15.8 GiB | The worker requests no GPU and is capped at 5 GiB. |
| WSL memory ceiling | 9.7 GiB | Leave room for the existing private lab services. |
| Memory available at inspection | 8.9 GiB | Run one transcription at a time. |
| WSL CPU capacity | 6 threads | Limit faster-whisper/Compose to 4 CPU threads. |
| Main disk free space | 60.5 GiB | Keep inputs and outputs out of Git; monitor video and cache growth. |
| GPU | none detected | Use `device=cpu`, `compute_type=int8`; no GPU support. |

The existing `cs-ai-lab-infra` stack owns its PostgreSQL, n8n, and optional Ollama services. This tool is a separate one-shot Compose worker that shares none of them and exposes no port. The prevailing Compose conventions—named persistent volumes, loopback/no external exposure, health checks, explicit operations, and non-destructive lifecycle—are retained where applicable.

Recommended initial model: faster-whisper `base`, `int8`, four CPU threads, one worker, cached locally. `tiny` is useful for a connectivity/performance smoke test; `small` may improve some material but should be measured before standardising because it increases T480 latency and memory pressure.
