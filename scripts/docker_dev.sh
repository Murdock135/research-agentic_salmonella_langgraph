#!/usr/bin/env bash
set -euo pipefail

# Dev workflow helper for running the project inside the dev image.
# - Mounts project for live editing
# - Mounts HF cache (required for datasets)
# - Asks how to provide secrets: ~/.secrets/.llm_apis, .env, or both

IMAGE_NAME="agentic_dev"

echo "[docker-dev] Checking for Docker..."
command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is required but not found."; exit 1; }

if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "[docker-dev] Dev image not found. Building..."
  docker build --target dev -t "$IMAGE_NAME" .
fi

echo "[docker-dev] Select secrets source:"
echo "  1) ~/.secrets/.llm_apis"
echo "  2) .env"
echo "  3) both"
read -p "Enter choice [1-3]: " CHOICE

SECRETS_ARGS=()
case "$CHOICE" in
  1)
    SECRETS_ARGS+=("-v" "$HOME/.secrets:/root/.secrets")
    if [ ! -f "$HOME/.secrets/.llm_apis" ]; then
      echo "[docker-dev] Warning: $HOME/.secrets/.llm_apis not found." >&2
      exit 1
    fi
    ;;
  2)
    SECRETS_ARGS+=("--env-file" ".env")
    if [ ! -f ".env" ]; then
      echo "[docker-dev] Warning: .env not found in current directory." >&2
      exit 1
    fi
    ;;
  3)
    SECRETS_ARGS+=("--env-file" ".env" "-v" "$HOME/.secrets:/root/.secrets")
    if [ ! -f "$HOME/.secrets/.llm_apis" ]; then
      echo "[docker-dev] Warning: $HOME/.secrets/.llm_apis not found." >&2
      exit 1
    fi
    if [ ! -f ".env" ]; then
      echo "[docker-dev] Warning: .env not found in current directory." >&2
      exit 1
    fi
    ;;
  *)
    echo "Invalid choice." >&2; exit 1;
    ;;
esac

HF_CACHE_MOUNT=("-v" "$HOME/.cache/huggingface:/root/.cache/huggingface")

echo "[docker-dev] Starting interactive dev container..."
echo "Tip: First run inside the container: 'uv sync --frozen' then 'uv run -m core.main -t'"

exec docker run -it --rm \
  -v "$PWD:/app" \
  "${SECRETS_ARGS[@]}" \
  "${HF_CACHE_MOUNT[@]}" \
  "$IMAGE_NAME"

