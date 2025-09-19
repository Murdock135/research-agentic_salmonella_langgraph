#!/usr/bin/env bash
set -euo pipefail

# Prod workflow helper for running the project with the production image.
# - Mounts HF cache (required for datasets)
# - Asks how to provide secrets: ~/.secrets/.llm_apis, .env, or both
# - Optionally runs test query (-t) or custom query
# - Optional: mount output back to host

IMAGE_NAME="agentic_test"

echo "[docker-prod] Checking for Docker..."
command -v docker >/dev/null 2>&1 || {
  echo >&2 "Docker is required but not found."
  exit 1
}

if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "[docker-prod] Production image not found. Building..."
  docker build --target runtime -t "$IMAGE_NAME" .
fi

echo "[docker-prod] Select secrets source:"
echo "  1) ~/.secrets/.llm_apis"
echo "  2) .env"
echo "  3) both"
read -p "Enter choice [1-3]: " CHOICE

SECRETS_ARGS=()
case "$CHOICE" in
1)
  SECRETS_ARGS+=("-v" "$HOME/.secrets:/root/.secrets")
  if [ ! -f "$HOME/.secrets/.llm_apis" ]; then
    echo "[docker-prod] Warning: $HOME/.secrets/.llm_apis not found." >&2
  fi
  ;;
2)
  SECRETS_ARGS+=("--env-file" ".env")
  if [ ! -f ".env" ]; then
    echo "[docker-prod] Warning: .env not found in current directory." >&2
  fi
  ;;
3)
  SECRETS_ARGS+=("--env-file" ".env" "-v" "$HOME/.secrets:/root/.secrets")
  if [ ! -f "$HOME/.secrets/.llm_apis" ]; then
    echo "[docker-prod] Warning: $HOME/.secrets/.llm_apis not found." >&2
  fi
  if [ ! -f ".env" ]; then
    echo "[docker-prod] Warning: .env not found in current directory." >&2
  fi
  ;;
*)
  echo "Invalid choice." >&2
  exit 1
  ;;
esac

HF_CACHE_MOUNT=("-v" "$HOME/.cache/huggingface:/home/app/.cache/huggingface")

read -p "Run test query (-t)? [Y/n]: " RUN_TEST
RUN_TEST=${RUN_TEST:-Y}

CMD_ARGS=("python" "-m" "core.main")
if [[ "$RUN_TEST" =~ ^[Yy]$ ]]; then
  CMD_ARGS+=("-t")
fi

read -p "Persist outputs to host? [y/N]: " PERSIST
PERSIST=${PERSIST:-N}

MOUNT_ARGS=()
if [[ "$PERSIST" =~ ^[Yy]$ ]]; then
  echo "[docker-prod] Persisting outputs by mounting ./output to /app/output"
  mkdir -p output
  MOUNT_ARGS+=("-v" "$PWD/output:/app/output")
fi

echo "[docker-prod] Running container..."
exec docker run -it --rm \
  "${SECRETS_ARGS[@]}" \
  "${HF_CACHE_MOUNT[@]}" \
  "${MOUNT_ARGS[@]}" \
  "$IMAGE_NAME" \
  "${CMD_ARGS[@]}"
