## Why

The codebase has grown organically — `main.py` lives at the repo root while `SYSTEM_DESIGN.md` documents `app/main.py`, there are no `tests/` or `docker/` directories despite being specified in the design doc, and several `__init__.py` packages are missing. This drift makes onboarding harder and invites inconsistent placement of new code as features are added. Now is the right time to align the repo with a single canonical layout before more modules land.

## What Changes

- Move application bootstrap from root `main.py` into `app/main.py` and add a thin root entrypoint (`main.py` or `run.py`) that delegates to it
- Add missing top-level directories: `tests/unit/`, `tests/integration/`, and `docker/`
- Reorganize `app/` internals into clear layers: `core/` (config, DI, logging), keep `api/`, `services/`, `workflow/`, `db/`, and split `models/` into `schemas/` (API contracts) and keep domain types where needed
- Add missing `__init__.py` files in all Python packages (including `app/api/v1/` and `app/workflow/nodes/`)
- Add a `CONTRIBUTING.md` (or extend README) with folder-placement rules so future code follows the same conventions
- Update `SYSTEM_DESIGN.md` Section 13 to reflect the final, authoritative structure
- Update all import paths and DI wiring config to match the new layout
- Add a minimal `docker/Dockerfile` and `docker/docker-compose.yml` scaffold matching the design doc

## Capabilities

### New Capabilities

- `project-structure`: Canonical folder layout, module boundaries, naming conventions, and placement rules for all Python source, tests, and Docker assets in corksy-rag

### Modified Capabilities

<!-- No existing main specs in openspec/specs/ — this change is organizational, not behavioral -->

## Impact

- **Moved files**: `main.py` → `app/main.py`; `app/config.py`, `app/containers.py`, `app/logger.py` → `app/core/`; `app/models/request.py` + `response.py` → `app/schemas/`
- **New files**: `tests/` scaffold, `docker/` scaffold, missing `__init__.py` files, `CONTRIBUTING.md` structure section
- **Modified files**: All files that import from moved modules (`containers`, `config`, `logger`, `models`); `pyproject.toml` test paths; `.vscode/launch.json` if it references `main.py`
- **No API behavior changes** — endpoints, services, and workflow logic remain functionally identical
- **No new runtime dependencies**
