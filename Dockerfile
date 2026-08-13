# Pin the Python minor release for repeatable CPU-only builds. Update deliberately.
FROM python:3.12-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /data/outputs /data/model-cache \
    && chown -R appuser:appuser /data
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=2 CMD mp4-to-transcript health || exit 1

ENTRYPOINT ["mp4-to-transcript"]
CMD ["health"]
