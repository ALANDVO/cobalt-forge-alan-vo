# Changelog

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-30

### Completed
- Project skeleton with FastAPI backend and React frontend
- Backend: 14 pytest tests pass (health, sessions, grilling workflow, decisions, versioning)
- Frontend: 2 Vitest tests pass (App rendering, navigation)
- Docker compose validates (backend, frontend, Keycloak services)
- SQLite database auto-initializes with migrations
- OIDC authentication flow (PKCE) with Keycloak realm configuration

### Implementation
- Backend API routers: auth, sessions, decisions, issues, PRDs, verification
- Frontend: React + TypeScript + Vite + Tailwind + React Router
- Database: SQLAlchemy async with SQLite (aiosqlite)
- Auth: PKCE flow via Keycloak

### Known Limitations
- Docker daemon not available in build environment for integration testing
- OIDC flow requires running Keycloak instance (compose provides this)
- PostgreSQL production config not yet implemented
- LLM adapters not yet implemented
- GitHub/GitLab issue tracker integration not yet implemented

## [1.0.0] - 2026-10-13

### Added
- **Project skeleton** — FastAPI backend with React + TypeScript + Vite frontend
- **Decision Ledger engine** — Stable IDs (DEC-001), versioned records, normalized requirements, explicit constraints, tags
- **Grilling workflow** — Design-tree interviews with frontier gate, pivot-first ordering, assumption tracking with veto
- **PRD generation** — Automatic traceability matrix mapping decisions to user stories, constraints, acceptance criteria
- **Issue tracking** — Local and GitHub tracker support, frontier visualization (unblocked issues), completion with commit references
- **Verification system** — Evidence linking (tests, code reviews, manual, automated, commits) with coverage reports
- **OIDC Authentication** — PKCE flow with Keycloak, sessionStorage for PKCE params, role-based access (viewer/operator/admin)
- **Docker support** — Multi-stage builds, compose.yaml with Keycloak, health checks
- **CI/CD** — GitHub Actions workflow for backend tests, frontend typecheck/build/test, Docker builds
- **Documentation** — README with architecture diagram, API reference, deployment guide, SAML setup

### Domain Models
- `User` — Keycloak-integrated with roles
- `GrillingSession` / `GrillingRound` / `GrillingQuestion` / `GrillingAssumption` — Interview workflow
- `DecisionRecord` / `DecisionVersion` — Versioned decision ledger
- `PRD` / `PRDDecisionMapping` — Requirements documents with traceability
- `Issue` — Work items with status, blockers, tracker support
- `VerificationEvidence` — Evidence linked to decisions and issues

### API Endpoints (15+)
- Sessions: CRUD, rounds, frontier preparation
- Questions: Create, answer (creates decision), assumptions with veto
- Decisions: CRUD, coverage reports
- PRDs: Generate from decisions, finalize, coverage check
- Issues: CRUD, status updates, completion with commit, frontier, generate from PRD
- Verification: Add evidence, coverage reports

### Tests
- Backend: 12+ pytest tests (domain logic, boundaries, persistence, auth, API workflows)
- Frontend: Vitest setup with component testing patterns

## [Unreleased]

### Planned
- PostgreSQL production configuration
- GitHub/GitLab issue tracker integration
- LLM adapter implementations (OpenAI-compatible, Anthropic, Gemini, Ollama)
- SAML broker configuration testing
- WebSocket support for real-time collaboration
- Export/import for decision ledger portability
