Dockerfile Design and Usage

Overview
- This project uses a multi-stage Dockerfile to keep the production image small and reproducible while providing a convenient development image.
- Package management uses uv (https://docs.astral.sh/uv/), which installs dependencies from `pyproject.toml` and `uv.lock`.

Local development without Docker
- You can use uv locally to manage a virtual environment and run the app without activating the venv manually:
  - Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Create venv and install deps: `uv sync`
  - Run commands: `uv run -m core.main -t` or `uv run -m utils.download_data`

Stages
- uv-base: Installs uv and minimal build tools (curl, build-essential). Nothing from your app is copied here yet.
- deps-prod: Installs only production dependencies into a local virtual environment (`/app/.venv`). Uses `uv sync --frozen --no-dev` for deterministic, smaller installs. Falls back to `requirements.txt` if `pyproject.toml` is not present.
- deps-dev: Builds on deps-prod and installs development/test dependencies. Useful for running tests and local development.
- build: Copies your source code into the image. Optionally precompiles Python bytecode (disabled by default).
- runtime: The final, slim production image. Copies the app and the prebuilt `.venv`, creates a non-root user, and runs `python -m core.main`.
- dev: A developer-friendly image with dev dependencies and the source code. Default command is `bash` so you can work interactively.

Why `--frozen --no-dev` in production
- `--frozen` ensures the dependency versions match the committed lockfile exactly. This makes builds reproducible and fail fast if the lockfile is out of sync with `pyproject.toml`.
- `--no-dev` keeps the production image small by skipping test/formatting tools and other dev-only packages.

About Python bytecode (`.pyc`)
- CPython compiles modules on import and caches `.pyc` automatically. Precompiling during build rarely helps and increases image size.
- The Dockerfile leaves precompilation commented out. Only enable it if you’ve measured a cold-start win or need a read-only filesystem where runtime caching isn’t possible.

Quick Start (Production)
1) Build the image
   - `docker build -t agentic_test .`
2) Run the test query
   - Using a `.env` file in the project root: `docker run -it --rm --env-file .env agentic_test python -m core.main -t`
   - Or mount a secrets directory: `docker run -it --rm -v ~/.secrets:/root/.secrets agentic_test python -m core.main -t`
3) Run a custom query
   - `docker run -it --rm --env-file .env agentic_test python -m core.main`

Quick Start (Development)
- Build the dev image (includes dev dependencies):
  - `docker build --target dev -t agentic_dev .`
- Run with your local code mounted (live editing):
  - `docker run -it --rm -v "$PWD:/app" --env-file .env agentic_dev`
- When mounting the project, your host files overlay the image’s `/app`. If the `.venv` in the image is hidden by your host mount, run `uv sync --frozen` inside the container once to (re)create a working `.venv`.

Secrets and configuration
- The examples mount secrets from `~/.secrets` into the container. The app reads provider API keys from that folder or from a `.env` file in the project root.
- See `readme.md` for environment variable details.

Changing Python version
- Update the `PYTHON_VERSION` build argument at the top of the Dockerfile (e.g., `ARG PYTHON_VERSION=3.13.3`).
- Rebuild the images to apply the change.

Troubleshooting
- Lockfile mismatch: If `uv sync --frozen` fails, update the lockfile locally via `uv lock` (or `uv sync`) and commit the changes.
- Permission errors writing to `output/`: The runtime image runs as a non-root user and owns `/app`. If you add new directories at runtime, ensure they are created within `/app` or adjust ownership appropriately.
- Missing `pyproject.toml`: The Dockerfile falls back to `requirements.txt`. Prefer committing `pyproject.toml` and `uv.lock` for reproducible builds.
- Architecture issues (e.g., on Apple Silicon building for amd64): Add `--platform linux/amd64` to `docker build` and `docker run` if your runtime target requires it.
