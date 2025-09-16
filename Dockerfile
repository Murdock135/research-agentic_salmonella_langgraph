
ARG UV_VERSION=0.8.15
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim-trixie

# optimizations
# 1. compile bytecode for production time
# 2. use UV_LINK_MODE=copy to copy packages from the wheel to the site packages directory. Note that the cache and sync target are on separate file systems.
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y \
  build-essential \
  libpq-dev \
  curl \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/${UV_VERSION}/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin:$PATH"

# Copy packages from cache into a 'cache mount'
RUN --mount=type=cache, target=/root/.cache/uv \
  uv sync

# Install python and add to cache
RUN --mount=type=cache, target=/root/.cache/uv \
  uv python install

# Copy the project into the image


