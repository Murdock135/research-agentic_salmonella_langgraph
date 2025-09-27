#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="sparq_production"
STAGE_NAME="prod"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKERFILE_PATH="$PROJECT_ROOT/Dockerfile"

echo "[run.sh] Project root: $PROJECT_ROOT"

# Check if .env exists
[[ -f "$PROJECT_ROOT/.env" ]] || {
  echo "[run.sh] .env file not found in project root ($PROJECT_ROOT). Please create it before proceeding."
  exit 1
}
SET_ENV="--env-file $PROJECT_ROOT/.env"

# Check if the user is a developer
DEVELOPER=false
CHOICE=0
while ((CHOICE != 1 && CHOICE != 2)); do
  echo "Choose 1/2"
  echo "1) I am a developer (coder) for this project"
  echo "2) I am simply running and testing this project"
  read CHOICE

  if ((CHOICE != 1 && CHOICE != 2)); then
    echo "[run.sh] Invalid option. Please choose 1 or 2 (the integers)."
  fi
done

[[ $CHOICE -eq 1 ]] && DEVELOPER=true && IMAGE_NAME="sparq_development" && STAGE_NAME="dev"

# Build the Docker image
echo "[run.sh] Building Docker image: $STAGE_NAME"
docker build --target "$STAGE_NAME" -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" "$PROJECT_ROOT"

# Mount HF data if it exists
MOUNT_HF=""
if [[ -d "$HOME/.cache/huggingface" ]]; then
  MOUNT_HF="--mount type=bind,source=$HOME/.cache/huggingface,target=/root/.cache/huggingface,readonly"
else
  echo "[run.sh] No Hugging Face cache directory found at $HOME/.cache/huggingface. Continuing without mounting it."
fi

# Mount ~/.secrets/.llm_apis if it exists
MOUNT_SECRETS=""
if [[ -f "$HOME/.secrets/.llm_apis" ]]; then
  MOUNT_SECRETS="--mount type=bind,source=$HOME/.secrets/.llm_apis,target=/root/.secrets/.llm_apis,readonly"
else
  echo "[run.sh] ~/.secrets/.llm_apis file not found. Continuing without mounting it."
fi

# Mount venv (in a docker volume)
docker volume create sparq_venv
MOUNT_VENV="--mount type=volume,source=sparq_venv,target=/app/.venv"

# Mount project if developer
MOUNT_PROJECT=""
[[ "$DEVELOPER" = true ]] && MOUNT_PROJECT="--mount type=bind,source=$PROJECT_ROOT,target=/app"

# TODO: Turn this into a heredoc that only displays when DEVELOPER=true
if $DEVELOPER; then
  echo "=============================="
  echo " Developer Mode Activated"
  echo "=============================="
  echo "You are running the container in developer mode."
  echo "This means your local project directory ($PROJECT_ROOT) is mounted inside the container."
  echo "Any changes you make to the code will be reflected inside the container immediately."
  echo ""
  echo "To install new dependencies, run:"
  echo "  uv sync --frozen"
  echo ""
  echo "To start the application, run:"
  echo "  uv run -m core.main -t"
  echo ""
  echo "Happy coding!"
  echo "=============================="
fi

exec docker run -it --rm \
  $SET_ENV \
  $MOUNT_HF \
  $MOUNT_SECRETS \
  $MOUNT_VENV \
  $MOUNT_PROJECT \
  "$IMAGE_NAME"
