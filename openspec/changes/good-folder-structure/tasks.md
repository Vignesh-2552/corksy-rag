## 1. Create Directory Scaffold

- [x] 1.1 Create `app/core/` directory with `__init__.py`
- [x] 1.2 Create `app/schemas/` directory with `__init__.py`
- [x] 1.3 Create `tests/unit/` and `tests/integration/` with `__init__.py`
- [x] 1.4 Create `docker/` directory
- [x] 1.5 Add missing `__init__.py` to `app/api/v1/` and `app/workflow/nodes/`

## 2. Move Core Infrastructure

- [x] 2.1 `git mv app/config.py app/core/config.py`
- [x] 2.2 `git mv app/containers.py app/core/containers.py`
- [x] 2.3 `git mv app/logger.py app/core/logger.py`
- [x] 2.4 Update internal imports within moved core files (`config` → `app.core.config`, etc.)

## 3. Move API Schemas

- [x] 3.1 `git mv app/models/request.py app/schemas/request.py`
- [x] 3.2 `git mv app/models/response.py app/schemas/response.py`
- [x] 3.3 Remove empty `app/models/` directory
- [x] 3.4 Update all imports from `app.models.*` to `app.schemas.*` across routers and services

## 4. Relocate Application Bootstrap

- [x] 4.1 Move `create_app()`, lifespan, and router registration from root `main.py` to `app/main.py`
- [x] 4.2 Replace root `main.py` with thin shim: `from app.main import app  # noqa: F401`
- [x] 4.3 Update imports in `app/main.py` to use `app.core.containers`, `app.core.logger`

## 5. Update Imports Project-Wide

- [x] 5.1 Replace `from app.config` → `from app.core.config` in all files
- [x] 5.2 Replace `from app.containers` → `from app.core.containers` in all files
- [x] 5.3 Replace `from app.logger` → `from app.core.logger` in all files
- [x] 5.4 Update `app/core/containers.py` wiring_config module paths if needed
- [x] 5.5 Verify no stale imports remain (`rg "from app\.(config|containers|logger|models)"`)

## 6. Test Scaffold

- [x] 6.1 Create `tests/conftest.py` with shared `TestClient` fixture using `app.main.create_app`
- [x] 6.2 Add `[tool.pytest.ini_options]` to `pyproject.toml` (`testpaths = ["tests"]`, `asyncio_mode = "auto"`)
- [x] 6.3 Run `pytest` and confirm discovery works (0 tests, no errors)

## 7. Docker Scaffold

- [x] 7.1 Create `docker/Dockerfile` — Python 3.12, install deps, `CMD uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [x] 7.2 Create `docker/docker-compose.yml` — `api` and `qdrant` services with port mappings and env vars
- [x] 7.3 Add `.dockerignore` at repo root (exclude `.venv`, `__pycache__`, `.git`)

## 8. Documentation & Tooling

- [x] 8.1 Update `SYSTEM_DESIGN.md` Section 13 to reflect final folder tree (`app/core/`, `app/schemas/`, `tests/`, `docker/`)
- [x] 8.2 Create `CONTRIBUTING.md` with folder placement rules for each layer
- [x] 8.3 Update `.vscode/launch.json` if it references old `main.py` paths

## 9. Verification

- [x] 9.1 Start app with `uvicorn main:app` and confirm `/api/v1/health` returns 200
- [x] 9.2 Confirm upload and ask endpoints still import and wire correctly (smoke test via Swagger or curl)
- [x] 9.3 Run `pytest` — passes with no collection errors
