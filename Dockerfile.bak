# syntax=docker/dockerfile:1
# escape=`

# Use a slim Python base image
FROM python:3.13-slim AS base

# Install pip (should already be present) and uv
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir uv

# Set work directory
WORKDIR /SPARQ

# Copy project files
COPY . /SPARQ

# Install project dependencies from pyproject.toml using uv
# RUN uv pip install -r pyproject.toml --system


# Default command (optional)
# CMD ["uv", "run", "-m", "core.main", "-t"]
