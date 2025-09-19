Dockerfile Design and Rationale

Overview
- This project uses a multi-stage Dockerfile to keep the production image small and reproducible while providing a convenient development image.
- Package management uses uv (https://docs.astral.sh/uv/), which installs dependencies from `pyproject.toml` and `uv.lock`.
- For build/run commands, mounting, and troubleshooting, see `docs/docker_usage.md`.

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

Changing Python version
- Update the `PYTHON_VERSION` build argument at the top of the Dockerfile (e.g., `ARG PYTHON_VERSION=3.13.3`).
- Rebuild the images to apply the change.
