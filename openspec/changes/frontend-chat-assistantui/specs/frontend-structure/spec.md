## ADDED Requirements

### Requirement: Frontend package location
The repository SHALL contain a self-contained frontend application under `frontend/` at the repository root, separate from the Python `app/` backend.

#### Scenario: Frontend root present
- **WHEN** a developer inspects the repository root
- **THEN** a `frontend/` directory SHALL exist with its own `package.json`, `tsconfig.json`, and build configuration

#### Scenario: Backend unaffected
- **WHEN** the frontend package is added
- **THEN** no Python source files SHALL be moved into `frontend/` and no frontend source files SHALL be placed under `app/`

---

### Requirement: Source directory layout
The frontend source code SHALL follow a layered layout under `frontend/src/`.

#### Scenario: Application entry and routing
- **WHEN** a developer looks for the app bootstrap and route definitions
- **THEN** they SHALL be located under `frontend/src/app/` (`main.tsx`, `App.tsx`, route pages)

#### Scenario: Assistant-ui components isolated
- **WHEN** a developer looks for assistant-ui styled primitives (`thread.tsx`, `composer.tsx`, etc.)
- **THEN** they SHALL be located under `frontend/src/components/assistant-ui/`

#### Scenario: Shared UI components
- **WHEN** a developer adds a reusable non-assistant-ui component (e.g., layout shell, source card)
- **THEN** it SHALL be placed under `frontend/src/components/` (not inside `assistant-ui/`)

#### Scenario: API client placement
- **WHEN** a module wraps HTTP calls to the FastAPI backend
- **THEN** it SHALL reside under `frontend/src/lib/api/` (e.g., `ask.ts`, `types.ts`)

#### Scenario: Custom hooks placement
- **WHEN** a module provides React hooks for chat runtime or session state
- **THEN** it SHALL reside under `frontend/src/hooks/` (e.g., `use-chat-runtime.ts`, `use-session-id.ts`)

#### Scenario: Utility functions placement
- **WHEN** a module provides pure helper functions (UUID generation, SSE parsing)
- **THEN** it SHALL reside under `frontend/src/lib/` (not in `components/` or `hooks/`)

---

### Requirement: Build tooling and output
The frontend SHALL use Vite as the build tool and produce a static production bundle.

#### Scenario: Dev server command
- **WHEN** a developer runs `npm run dev` inside `frontend/`
- **THEN** a local dev server SHALL start with hot module replacement

#### Scenario: Production build command
- **WHEN** a developer runs `npm run build` inside `frontend/`
- **THEN** Vite SHALL emit optimized static assets to `frontend/dist/`

#### Scenario: Type checking
- **WHEN** a developer runs `npm run typecheck` (or `tsc --noEmit`)
- **THEN** TypeScript SHALL validate all source files without errors

---

### Requirement: Environment configuration
The frontend SHALL read API connection settings from environment variables prefixed with `VITE_`.

#### Scenario: API base URL configured
- **WHEN** the frontend makes API calls in development
- **THEN** it SHALL use `VITE_API_BASE_URL` (defaulting to `http://localhost:8000`) to construct request URLs

#### Scenario: Example env file present
- **WHEN** a developer clones the repository
- **THEN** `frontend/.env.example` SHALL document all required `VITE_*` variables

---

### Requirement: Styling conventions
The frontend SHALL use Tailwind CSS with shadcn/ui design tokens for consistent styling.

#### Scenario: Tailwind configured
- **WHEN** a developer inspects `frontend/`
- **THEN** `tailwind.config.ts` and `postcss.config.js` SHALL be present and configured for the `src/` directory

#### Scenario: Global styles location
- **WHEN** a developer looks for base CSS or Tailwind directives
- **THEN** they SHALL be in `frontend/src/app/index.css`

---

### Requirement: Documented frontend conventions
The repository SHALL document where new frontend code belongs.

#### Scenario: Contributing guide updated
- **WHEN** a developer reads `CONTRIBUTING.md` or the README
- **THEN** it SHALL describe the `frontend/` folder layout and placement rules for components, hooks, API clients, and pages
