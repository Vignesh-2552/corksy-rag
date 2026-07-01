## Context

The corksy-rag project is a FastAPI + LangGraph RAG pipeline. `SYSTEM_DESIGN.md` Section 13 defines an ideal folder structure, but the live codebase has drifted:

| Documented | Actual |
|---|---|
| `app/main.py` | `main.py` at repo root |
| `app/models/` | `app/models/` (works, but name is ambiguous) |
| `tests/unit/`, `tests/integration/` | Missing entirely |
| `docker/` | Missing entirely |
| — | `app/logger.py` at app root (undocumented) |

As more features land (retriever agent, future auth, admin endpoints), inconsistent placement will compound. This change is a one-time structural alignment with no behavioral changes to the API.

## Goals / Non-Goals

**Goals:**
- Establish a single canonical layout that matches `SYSTEM_DESIGN.md` (updated)
- Move bootstrap code into `app/main.py`
- Group infrastructure into `app/core/`
- Rename `app/models/` → `app/schemas/` for API contracts
- Scaffold `tests/`, `docker/`, and missing `__init__.py` files
- Update all imports and DI wiring in one pass
- Document placement rules in `CONTRIBUTING.md`

**Non-Goals:**
- Refactoring service or workflow internals beyond import path updates
- Writing actual test cases or Docker production hardening
- Splitting services into sub-packages (e.g., `services/rag/`, `services/indexing/`) — defer until the service count grows
- Moving `openspec/` or `.claude/` directories
- Changing API routes, response shapes, or runtime behavior

## Decisions

### D1 — `app/main.py` with thin root entrypoint

**Decision:** Move `create_app()`, lifespan, and router registration to `app/main.py`. Keep a minimal root `main.py` that re-exports `app` for `uvicorn main:app` compatibility.

**Rationale:** Matches SYSTEM_DESIGN.md and keeps all application code under `app/`. A thin root shim avoids breaking existing `uvicorn main:app` invocations and VS Code launch configs.

**Alternative considered:** Delete root `main.py` and require `uvicorn app.main:app` — cleaner but breaks existing tooling without updating every reference.

---

### D2 — `app/core/` for cross-cutting infrastructure

**Decision:** Move `config.py`, `containers.py`, and `logger.py` into `app/core/`.

**Rationale:** These three modules are imported everywhere but contain no domain logic. Grouping them signals "infrastructure layer" and keeps `app/` root clean (only `main.py` and sub-packages).

**Alternative considered:** Leave them flat at `app/` root — simpler imports but doesn't scale as more infra modules appear (middleware, exceptions).

---

### D3 — `app/schemas/` instead of `app/models/`

**Decision:** Rename `app/models/` to `app/schemas/` with `request.py` and `response.py` unchanged in content.

**Rationale:** In FastAPI projects, `models` often implies ORM/database models. This project has no ORM — these are Pydantic API contracts. `schemas` is the conventional FastAPI term and avoids future confusion when a real data model layer is added.

**Alternative considered:** Keep `models/` — less churn but perpetuates ambiguity.

---

### D4 — Flat `services/` and `workflow/` (no further nesting)

**Decision:** Keep the current flat layout under `services/` and `workflow/nodes/`. Do not introduce `services/rag/` or `services/indexing/` sub-packages yet.

**Rationale:** Only 5 service files and 3 workflow nodes exist. Premature nesting adds import depth without clarity benefit. The spec documents placement rules so future services know where to go.

**Alternative considered:** Domain sub-packages now — better long-term but over-engineered for current size.

---

### D5 — Test scaffold only, no test implementation

**Decision:** Create `tests/unit/__init__.py`, `tests/integration/__init__.py`, and `tests/conftest.py` with a shared `client` fixture. Add `[tool.pytest.ini_options]` to `pyproject.toml`.

**Rationale:** Establishes the directory convention and pytest discovery without scope-creeping into writing tests (separate change).

**Alternative considered:** Write sample tests now — valuable but out of scope for a structure change.

---

### D6 — Minimal Docker scaffold

**Decision:** Add `docker/Dockerfile` (multi-stage, `uv` or `pip` install, `uvicorn app.main:app`) and `docker/docker-compose.yml` (API + Qdrant services).

**Rationale:** SYSTEM_DESIGN.md promises this layout. A working local compose stack is the minimum viable scaffold.

**Alternative considered:** Skip Docker — leaves the design doc inaccurate and blocks local onboarding.

## Risks / Trade-offs

- **Import churn across many files** → Mitigation: move files first, then run a project-wide search for old import paths (`app.config`, `app.containers`, `app.models`, `app.logger`) before committing
- **VS Code / CI references to old paths** → Mitigation: update `.vscode/launch.json` and any scripts in the same PR
- **`dependency-injector` wiring module paths** → Mitigation: update `wiring_config.modules` in `containers.py` to reflect any moved router paths (routers stay in place, only core imports change)
- **Root `main.py` shim confusion** → Mitigation: add a one-line comment in root `main.py` pointing to `app/main.py` as the real entrypoint

## Migration Plan

1. Create new directories: `app/core/`, `app/schemas/`, `tests/unit/`, `tests/integration/`, `docker/`
2. Move files with `git mv` to preserve history:
   - `app/config.py` → `app/core/config.py`
   - `app/containers.py` → `app/core/containers.py`
   - `app/logger.py` → `app/core/logger.py`
   - `app/models/request.py` → `app/schemas/request.py`
   - `app/models/response.py` → `app/schemas/response.py`
   - Root `main.py` body → `app/main.py`
3. Create thin root `main.py` shim: `from app.main import app`
4. Add missing `__init__.py` files
5. Update all imports project-wide
6. Update `containers.py` wiring config and `settings` import paths
7. Add `tests/conftest.py`, `pyproject.toml` pytest config
8. Add `docker/Dockerfile` and `docker/docker-compose.yml`
9. Update `SYSTEM_DESIGN.md` Section 13 and add `CONTRIBUTING.md`
10. Verify: `uvicorn main:app` starts, `/api/v1/health` returns 200, `pytest` discovers empty test suite

**Rollback:** Revert the single commit — no database or API contract changes.

## Open Questions

- Should root `main.py` be removed entirely in favor of documenting `uvicorn app.main:app` as the canonical run command?
- Should `CONTRIBUTING.md` be a standalone file or a section in README (currently empty)?
