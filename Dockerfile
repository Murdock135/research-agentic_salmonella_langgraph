# Use a slim Python base image
FROM python:3.12-slim

# Install pip (should already be present) and uv
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir uv

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install project dependencies from pyproject.toml using uv
RUN uv pip install -r pyproject.toml --system

# Default command (optional)
CMD ["uv", "run", "-m", "core.main", "-t"]
