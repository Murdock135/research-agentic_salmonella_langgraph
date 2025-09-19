# Repository Guidelines

## Project Structure & Module Organization
- `core/`: entry (`main.py`) and graph orchestration (`system.py`).
- `nodes/`: agent nodes (router, planner, executor, aggregator, saver).
- `schemas/`: pydantic/typing schemas for state and outputs.
- `config/`: runtime config, env loading, prompts lookup, output dirs.
- `sys_messages/`: system prompts and archives used by nodes.
- `tools/`: LangChain/utility tools callable by agents.
- `utils/`: helpers (data loading, LLM setup, downloads).
- `data/`: manifests and local metadata (no large data checked in).
- `output/`: time-stamped run outputs (auto-created).
- `experiments/`, `notebooks/`: ad-hoc scripts and exploration.

## Build, Test, and Development Commands
- Run test query: `uv run -m core.main -t` (uses `config/config.toml` test query).
- Run custom query: `uv run -m core.main` (prompts for input).
- Download datasets: `uv run -m utils.download_data` (requires HF access/token).
- Docker (optional): see `docs/docker_usage.md` for build/run commands and workflows.
- Tests (if added): `uv run -m pytest -q`.

## Coding Style & Naming Conventions
- Python 3.13, 4-space indentation, PEP8, type hints required.
- Modules/files/functions: `snake_case`; classes: `PascalCase`.
- Keep nodes pure; side effects limited to `saver` and `output/` writes.
- Docstrings for public functions; prefer small, composable helpers in `utils/`.

## Testing Guidelines
- Prefer `pytest`; place tests in `tests/` as `test_<module>.py`.
- Focus on `nodes/*` behaviors and `utils/helpers.py`.
- Validate end-to-end by running `-t` and inspecting `output/<run>/`.

## Commit & Pull Request Guidelines
- Commits: short, imperative, scoped (e.g., `core: add async run`).
- PRs include: purpose, summary of changes, reproduction steps, logs/screenshots of a `-t` run, and linked issues.
- Update `readme.md`/`config.toml` when user-facing behavior changes.

## Security & Configuration Tips
- Secrets: use `~/.secrets/.llm_apis` or `.env` (not committed).
- Common vars: `GOOGLE_GENAI_API_KEY`, `OPENAI_API_KEY`, `HF_TOKEN`, `LANGSMITH_*`.
- Models/providers configured in `config/config.toml`.

## Agent-Specific Notes
- Graph: `router → planner → executor → aggregator → saver`.
- Prompts live in `sys_messages/`; adjust responsibly and keep diffs small.
- Outputs are time-stamped; avoid writing outside `output/`.
