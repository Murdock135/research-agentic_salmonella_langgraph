Docker: Development and Production

Overview
- Supports two images: `agentic_test` (production) and `agentic_dev` (development).
- Use `uv` for running the project in development. The production image runs the app directly with Python to keep it small.
- Secrets can be provided via `.env` or `~/.secrets/.llm_apis` (mounted in Docker).

Prerequisites
- Docker installed and running.
- API keys set in either:
  - `~/.secrets/.llm_apis` (preferred), or
  - a project `.env` file.

Images
- Production: `docker build -t agentic_test .`
- Development: `docker build --target dev -t agentic_dev .`

Production Usage
- Run the test query (choose one way to supply secrets):
  - `.env` file: `docker run -it --rm --env-file .env agentic_test python -m core.main -t`
  - Secrets dir: `docker run -it --rm -v ~/.secrets:/root/.secrets agentic_test python -m core.main -t`
- Run with your own query:
  - `.env`: `docker run -it --rm --env-file .env agentic_test python -m core.main`
- Persist outputs to the host:
  - Mount the project root: `docker run -it --rm -v "$PWD:/app" --env-file .env agentic_test python -m core.main -t`
  - Or mount just the output dir: `docker run -it --rm -v "$PWD/output:/app/output" --env-file .env agentic_test python -m core.main -t`
- Start and exit:
  - Start: any of the `docker run ...` commands above.
  - Exit: Ctrl+C for foreground runs, or `docker stop <container>` for detached runs.

Notes on uv vs python in production
- The production image does not include `uv` to keep size minimal. It runs the app via `python -m core.main`.
- For local development (inside or outside Docker), prefer `uv run ...`.

Development Workflow
- Build dev image: `docker build --target dev -t agentic_dev .`
- Ephemeral interactive session with live editing:
  - `docker run -it --rm -v "$PWD:/app" --env-file .env agentic_dev`
  - Inside the container (first run when mounting host code):
    - `uv sync --frozen`
    - `uv run -m core.main -t`
- Persistent background container (good for VS Code attach):
  - Start: `docker run -d --name agent_dev -v "$PWD:/app" --env-file .env agentic_dev sleep infinity`
  - Exec a shell: `docker exec -it agent_dev bash`
  - Stop/Remove: `docker stop agent_dev && docker rm agent_dev`
- Start and exit:
  - Start: one of the `docker run ...` variants above.
  - Exit: `exit` or Ctrl+D from the interactive shell; or stop/remove the named container as shown.

Secrets and Configuration
- App loads env vars from both locations (in order):
  1) `~/.secrets/.llm_apis`
  2) Project `.env`
- Use either approach in Docker:
  - Mount secrets directory: `-v ~/.secrets:/root/.secrets`
  - Or supply a `.env` file: `--env-file .env`

Git Options
- Recommended: use Git on the host while bind-mounting your repo into the dev container (`-v "$PWD:/app"`).
- If you prefer Git inside the container (dev image):
  - Install once per container: `apt-get update && apt-get install -y git`
  - Configure as needed: `git config --global user.name "Your Name" && git config --global user.email you@example.com`
  - Clone/pull inside `/app` or operate on the mounted repo.

VS Code
- Best experience: use the “Dev Containers” (aka “Remote - Containers”) extension.
- Option A: Attach to a running dev container
  - Start a persistent container: `docker run -d --name agent_dev -v "$PWD:/app" --env-file .env agentic_dev sleep infinity`
  - In VS Code: Command Palette → “Dev Containers: Attach to Running Container…” → select `agent_dev`.
  - Open `/app`, then use the VS Code terminal:
    - `uv sync --frozen` (first time)
    - `uv run -m core.main -t`
- Option B: Attach quickly with the Docker extension
  - Install “Docker” extension → Containers view → right-click `agent_dev` → “Attach Visual Studio Code”.
- Exiting
  - Close VS Code window to detach; container keeps running.
  - Stop/remove with `docker stop agent_dev && docker rm agent_dev` when done.

Common Tasks
- Rebuild images when dependencies change: `docker build --no-cache -t agentic_test .` or for dev `--target dev -t agentic_dev .`
- Run tests (if present) in dev container:
  - `uv run -m pytest -q`
- Download datasets in dev container:
  - `uv run -m utils.download_data`

Troubleshooting
- Lockfile mismatch during `uv sync --frozen`:
  - Regenerate lock locally (`uv lock` or `uv sync`) and commit `uv.lock`.
- “command not found: uv” in production image:
  - Use dev image for `uv` commands, or run the production image’s default app command.
- Permission errors writing to `output/`:
  - Ensure you run as the provided non-root user in prod; bind-mount project root or output dir to the host.

