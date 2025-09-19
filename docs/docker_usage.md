Docker Usage

Development Workflow
- Build dev image: `docker build --target dev -t agentic_dev .`
- First-time setup: make scripts executable: `chmod +x scripts/docker_*.sh`
- Easiest: run `scripts/docker_dev.sh` and follow prompts.
  - Prompts for secrets source (`~/.secrets/.llm_apis`, `.env`, or both).
  - Mounts your code for live editing and the HF cache for datasets.
- Manual example (Power users):
  - `.env` + secrets + cache: `docker run -it --rm -v "$PWD:/app" --env-file .env -v ~/.secrets:/root/.secrets -v ~/.cache/huggingface:/root/.cache/huggingface agentic_dev`
  - Inside: run `uv sync --frozen` once, then `uv run -m core.main -t`.

Production Workflow
- Build prod image: `docker build -t agentic_test .`
- First-time setup: make scripts executable: `chmod +x scripts/docker_*.sh`
- Easiest: run `scripts/docker_prod.sh` and follow prompts.
  - Prompts for secrets source and mounts the HF cache; can also mount `output/` back to host.
- Manual examples:
  - Test query with `.env` + secrets + cache: `docker run -it --rm --env-file .env -v ~/.secrets:/root/.secrets -v ~/.cache/huggingface:/home/app/.cache/huggingface agentic_test python -m core.main -t`
  - Custom query: replace `-t` with nothing.

Notes
- Datasets are required. The container uses the Hugging Face cache; scripts mount it automatically.
- Windows (PowerShell): use `${PWD}` instead of `$PWD` in `-v` mounts.
- Windows scripts: run via Bash (WSL or Git Bash), e.g.: `bash scripts/docker_dev.sh`
