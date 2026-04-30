# syntax=docker/dockerfile:1.7

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ffmpeg \
        libgl1 \
        libglib2.0-0 \
        ca-certificates \
        curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /usr/local/bin/

WORKDIR /app

# ---- deps layer (cached when only app code changes)
FROM base AS deps
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ---- runtime
FROM base AS runtime

# Bring over the resolved venv from the deps layer
COPY --from=deps /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

COPY pyproject.toml uv.lock ./
COPY app ./app

RUN mkdir -p /app/data/uploads /app/data/outputs /app/data/samples

# Optional: drop *.mp4 files into backend/samples-seed/ before building to bake
# them into /app/data/samples/. Useful on platforms where the data dir is on a
# fresh persistent volume and you want the picker to have content out of the box.
COPY samples-seed/ /app/data/samples/

RUN groupadd --system --gid 1001 appuser \
 && useradd --system --uid 1001 --gid appuser --no-create-home appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -fsS http://localhost:8000/health || exit 1

# --proxy-headers + --forwarded-allow-ips=* so X-Forwarded-* from Fly's edge
# proxy is honored (correct scheme/host in any redirects we generate).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
