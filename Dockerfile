# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.13.3

# ---------- uv base (tools only) ----------
FROM python:${PYTHON_VERSION}-slim AS uv-base
WORKDIR /app
ENV UV_LINK_MODE=copy 

# Minimal system deps for building wheels; add more if required
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl ca-certificates build-essential \
  && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# ---------- deps (prod) ----------
FROM uv-base AS deps-prod
WORKDIR /app

# Cache-friendly: copy only manifests first
COPY pyproject.toml uv.lock ./

# Install production dependencies into a project-local venv
RUN --mount=type=cache,target=/root/.cache/uv bash -euxo pipefail -c '\
  if [ -f pyproject.toml ]; then \
  uv sync --frozen --no-dev; \
  elif [ -f requirements.txt ]; then \
  uv venv && . .venv/bin/activate && pip install --no-cache-dir -r requirements.txt; \
  else \
  echo "No pyproject.toml or requirements.txt found" >&2; exit 1; \
  fi'

# ---------- deps (dev) ----------
FROM deps-prod AS deps-dev
# Install dev groups for local development/testing
RUN --mount=type=cache,target=/root/.cache/uv \
  if [ -f pyproject.toml ]; then uv sync --frozen; fi

# ---------- build (optional compile) ----------
FROM deps-prod AS build
WORKDIR /app
COPY . .
# Optional: precompile app bytecode (usually skip unless measured benefit)
# RUN . .venv/bin/activate && python -m compileall -q -j 0 /app

# ---------- runtime (prod) ----------
FROM python:${PYTHON_VERSION}-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# Create non-root user (Debian/Ubuntu)
RUN groupadd -g 10001 app && useradd -u 10001 -g app -m -s /usr/sbin/nologin -c "App user" app
WORKDIR /app

# Copy built app (includes .venv and source)
COPY --from=build /app /app

# Ensure writable workspace for the app user (e.g., creating output/)
RUN chown -R app:app /app

ENV PATH="/app/.venv/bin:${PATH}"
USER app
CMD ["python", "-m", "core.main"]

# ---------- dev (developer image) ----------
FROM deps-dev AS dev
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# Copy source; override with -v "$PWD:/app" for live editing
COPY . .

# Tell python to use the app's venv by default
ENV PATH="/app/.venv/bin:${PATH}"

# Default to bash
CMD ["bash"]

