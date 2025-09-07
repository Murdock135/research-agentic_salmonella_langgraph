FROM python:3.12-slim-trixie

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/0.8.15/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin:$PATH"

# Copy the project into the image

