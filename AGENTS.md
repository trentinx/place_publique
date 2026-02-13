# Repository Guidelines

## Project Structure & Module Organization
Core inference logic lives in `src/place_publique/` (graph utilities, metrics, YOLO weights). Flask UI code sits in `app/`, the FastAPI backend in `api/`, and shared docs or assets in `documentation/`, `img/`, and `dump/`. Keep helper scripts inside `scripts/`, extend shared modules instead of reimplementing handlers, and stash temporary datasets under `datasets/`.

## Build, Test, and Development Commands
- `make install MODE=dev` → installs the editable package with `uv pip install -e .`.
- `make flask-up` / `make flask-down` → run or stop the Flask dashboard for manual validation.
- `make fastapi-up` / `make fastapi-down` → start the Hypercorn-served API defined in `api/hypercorn.toml`.
- `./train.sh <dataset>` → pulls the Roboflow dataset (using `env`), fixes YAML paths, and trains YOLO into `datasets/<dataset>`.

## Coding Style & Naming Conventions
Stick to Python 3.13 and 4-space indentation. Use snake_case for modules, functions, and variables, PascalCase for classes and Pydantic models, and ALL_CAPS for configuration constants. Keep routes thin, push complex logic into `src/place_publique`, and add docstrings plus type hints for any exported surface.

## Testing Guidelines
Place `pytest` modules under a top-level `tests/` tree mirroring the package layout (for example, `tests/test_metrics.py`). Name cases `test_<behavior>`, rely on fixtures, and keep small sample media in `dump/tests/`. Use FastAPI’s `TestClient` and Flask’s `app.test_client()` for endpoint coverage. Run `pytest -q` (or `uv run pytest`) before each PR and aim for ≥80% line coverage on new logic.

## Commit & Pull Request Guidelines
Follow the current history by prefixing commits with concise verbs (e.g., `Update: refine graph metrics`) and keep scope focused. Reference issue IDs or dataset sources in the summary when relevant. Pull requests should explain the change, list verification commands (`make fastapi-up`, `pytest`), and attach screenshots or sample JSON for UI/API work.

## Security & Configuration Tips
Keep secrets such as `ROBOFLOW_API_KEY` in local env files sourced by `train.sh` and never commit them. Store large checkpoints under `src/place_publique/`, documenting provenance before pushing new ones. Scrub media placed in `dump/` or created by `scripts/scrapper.py`, and reuse the Hypercorn settings plus your reverse proxy to lock down ports and TLS.
