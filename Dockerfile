# ── Build stage ───────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy source and install the project
COPY src/ src/
COPY README.md LICENSE ./
RUN uv sync --frozen --no-dev

# ── Runtime stage ────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Ensure data directories exist
RUN mkdir -p data/json data/db

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8501

ENTRYPOINT ["project"]
CMD ["run"]
