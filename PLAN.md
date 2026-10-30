# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

project-skeleton

## Roadmap

### project-skeleton — Project skeleton with FastAPI backend and React frontend

Status: done

Acceptance:
- FastAPI app starts and serves health endpoint
- React app builds and serves
- Docker compose starts backend, frontend, and Keycloak
- SQLite database initializes with migrations
- Basic OIDC authentication flow works

Implementation: `backend/app/main.py`, `backend/app/core/database.py`, `backend/app/core/config.py`, `backend/app/api/routes.py`, `backend/app/api/routers/auth.py`, `backend/app/api/routers/sessions.py`, `backend/app/api/routers/decisions.py`, `backend/app/api/routers/issues.py`, `backend/app/api/routers/prds.py`, `backend/app/api/routers/verification.py`, `frontend/src/App.tsx`, `frontend/src/main.tsx`, `frontend/vite.config.ts`, `frontend/Dockerfile`, `frontend/nginx.conf`, `backend/Dockerfile`, `compose.yaml`, `keycloak/realm-export.json`

Tests: `backend/app/tests/test_api.py`, `frontend/src/App.test.tsx`

### decision-ledger — Decision ledger engine for traceable requirements

Status: planned

Acceptance:
- Create/append decision records with stable IDs
- Normalize answers to testable requirements with constraints
- Version records on revision
- Query ledger by ID, status, tags
- Coverage check: all records referenced in PRD/issues

### grilling-workflow — Grilling workflow with frontier/pivot ordering

Status: planned

Acceptance:
- Start grilling session with design tree
- Present frontier questions with pivot-first ordering
- Record answers as decision ledger entries
- Support assumptions with veto capability
- Exit gate requires explicit 'confirmed'

### prd-generation — PRD generation with decision traceability

Status: planned

Acceptance:
- Generate PRD referencing all decision ledger IDs
- Map each record to user stories, constraints, acceptance criteria
- Flag stale references when decisions revised
- Export PRD as Markdown

### issue-tracking — Issue tracking with completion signals

Status: planned

Acceptance:
- Generate issues from PRD covering all decision records
- Track issue status (open, in-progress, done)
- Mark issues done with commit reference on completion
- Support local markdown and GitHub tracker modes
- Frontier visualization shows unblocked issues

### implementation-verification — Implementation verification against decisions

Status: planned

Acceptance:
- Link implementation commits to decision records
- Verify acceptance criteria per decision
- Report coverage gaps
- Evidence trail from decision to test result

### desktop-compatibility — Desktop app compatibility layer

Status: planned

Acceptance:
- Export skills as portable format
- Web-based UI works in desktop webview
- Offline-capable core workflows

