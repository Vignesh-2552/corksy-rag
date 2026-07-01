## ADDED Requirements

### Requirement: Canonical application package layout
The repository SHALL organize all application source code under `app/` with the following top-level sub-packages: `core/`, `api/`, `services/`, `workflow/`, `db/`, and `schemas/`.

#### Scenario: Application bootstrap location
- **WHEN** a developer inspects the repository root
- **THEN** the FastAPI application factory and lifespan logic SHALL reside in `app/main.py`, not at the repository root

#### Scenario: Core infrastructure isolation
- **WHEN** a developer looks for configuration, dependency injection, or logging setup
- **THEN** those modules SHALL be located under `app/core/` (`config.py`, `containers.py`, `logger.py`)

#### Scenario: API schema separation
- **WHEN** a developer looks for Pydantic request/response models used by HTTP endpoints
- **THEN** those models SHALL be located under `app/schemas/`, not mixed with service or workflow internals

### Requirement: API layer versioning
The HTTP layer SHALL be organized under `app/api/v1/` with one router module per endpoint group (`upload.py`, `ask.py`, `health.py`).

#### Scenario: Versioned router placement
- **WHEN** a new v1 endpoint is added
- **THEN** its router module SHALL be placed in `app/api/v1/` and registered from `app/main.py`

#### Scenario: Package init files present
- **WHEN** any Python package directory exists under `app/`
- **THEN** it SHALL contain an `__init__.py` file, including `app/api/v1/` and `app/workflow/nodes/`

### Requirement: Service and workflow boundaries
Business logic SHALL be separated from HTTP routing and infrastructure concerns.

#### Scenario: Service placement
- **WHEN** a module implements domain logic (embedding, indexing, retrieval, generation, LLM factory)
- **THEN** it SHALL reside under `app/services/`

#### Scenario: Workflow placement
- **WHEN** a module defines LangGraph state, nodes, or graph compilation
- **THEN** it SHALL reside under `app/workflow/` with individual nodes in `app/workflow/nodes/`

#### Scenario: Database client placement
- **WHEN** a module wraps an external datastore client (Qdrant)
- **THEN** it SHALL reside under `app/db/`

### Requirement: Test directory structure
The repository SHALL include a `tests/` directory with `unit/` and `integration/` subdirectories.

#### Scenario: Unit test placement
- **WHEN** a developer writes a test that mocks external dependencies
- **THEN** the test file SHALL be placed under `tests/unit/`

#### Scenario: Integration test placement
- **WHEN** a developer writes a test that exercises HTTP endpoints or real service wiring
- **THEN** the test file SHALL be placed under `tests/integration/`

#### Scenario: Pytest discovery
- **WHEN** `pytest` is run from the repository root
- **THEN** it SHALL discover tests under `tests/` without additional path configuration beyond `pyproject.toml`

### Requirement: Docker deployment scaffold
The repository SHALL include a `docker/` directory with a `Dockerfile` and `docker-compose.yml` for running the API and Qdrant locally.

#### Scenario: Dockerfile present
- **WHEN** a developer inspects `docker/`
- **THEN** a `Dockerfile` SHALL exist that builds the FastAPI application from `app/main.py`

#### Scenario: Compose stack present
- **WHEN** a developer runs `docker compose -f docker/docker-compose.yml up`
- **THEN** the compose file SHALL define services for the API and Qdrant with appropriate port mappings

### Requirement: Documented placement conventions
The repository SHALL include documented rules for where new code belongs.

#### Scenario: Contributing guide present
- **WHEN** a developer reads `CONTRIBUTING.md` or the README structure section
- **THEN** it SHALL describe the canonical folder layout and placement rules for each layer (api, services, workflow, schemas, tests)

#### Scenario: System design alignment
- **WHEN** a developer reads `SYSTEM_DESIGN.md` Section 13 (Folder Structure)
- **THEN** the documented tree SHALL match the actual repository layout after this change is applied

### Requirement: Import path consistency
All internal imports SHALL use the `app.` package prefix reflecting the canonical layout.

#### Scenario: Core module imports
- **WHEN** any module imports configuration, the DI container, or the logger
- **THEN** it SHALL use `from app.core.config`, `from app.core.containers`, or `from app.core.logger` respectively

#### Scenario: Schema imports
- **WHEN** any API router imports request or response models
- **THEN** it SHALL use `from app.schemas.request` or `from app.schemas.response`

#### Scenario: No stale import paths
- **WHEN** the restructure is complete
- **THEN** no module SHALL import from removed paths such as `app.config`, `app.containers`, `app.logger`, or `app.models`
