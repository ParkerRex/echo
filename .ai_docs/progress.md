Project Progress ­— Structured for Product-Owner Review

Last updated 2025-05-14

⸻

Project Progress ­— for Product-Owner Review

Last updated 2025-05-14

⸻

0. Priority Roadmap — “Light It Up” Plan

Rank-ordered by dependency & impact

Step	Goal	Owner	Key Deliverables
1 Supabase Bootstrap	Core tables + RLS	DB	videos table, RLS, first migration, local reset verified
2 Backend ⇄ Supabase Wiring	Auth path proven	API	supabase_client.py, get_current_user, GET /auth/me
3 Frontend Auth Flow	Login + token passthrough	Web	GoogleLoginButton, callback, protected layout, /auth/me call
4 Signed-URL Upload P.O.C.	Smallest video workflow	API + Web	POST /videos/upload-url ✅, drop-zone PUT, upload-complete, dashboard list
5 Local E2E Smoke Test	End-to-end validation	All	Script / Vitest or Cypress runs login→upload→dashboard
6 Incremental Expansions	Scale slice	All	Task queue, WebSockets, metadata editor, publisher adapter

⚡ This Sprint (must finish)

A. Supabase migration files (tables + RLS) ✅ (done)
B. Backend Supabase client & /auth/me ✅ (done)
C. Frontend Google OAuth → /auth/me round-trip ✅ (done)
  • GoogleLoginButton implemented and integrated
  • OAuth callback handler implemented at /auth/callback (Supabase session processed, redirects to dashboard)
  • Protected layout and /auth/me call implemented and integrated

These three unblock every other feature.

⸻

1. Backend API (FastAPI / Python)

Phase	Completion	Next Milestone
Validation	85 %	Smoke-test passes (Step 5)

1.1 Ready

Infra, domain layers, adapters, DTOs, endpoints, video services (see previous list).

1.2 In Progress
	•	Supabase client DI (Roadmap 2.2)
	•	JWT dependency + /auth/me (2.3 – 2.4)
	•	Signed-URL endpoints (upload-url ✅, upload-complete) (4.1 – 4.3)
	•	Observability & security review
	•	GET /videos/my endpoint for dashboard list (Supabase, no Firebase)

1.3 Blocked / Not Started

Advanced video features, CI/CD hardening, WebSockets (expand after Roadmap 6).

⸻

2. Frontend Web (React + TanStack)

Phase	Target MVP	Current Focus
Initial build	2025-06-21	Roadmap Steps 3–4

2.1 Ready

Project scaffold, Memory-Bank docs, Google OAuth button, OAuth callback handler, protected layout, /auth/me call.

2.2 In Progress
	•	API wrapper with Supabase JWT
	•	Drop-zone → fetch signed URL → PUT upload (4.2)
	•	Dashboard list (/videos/my-videos) (4.4)

	─────────────────────────────
	Remove Firebase & Switch Dashboard to Supabase

	| Sub-Step | Goal | Owner | Deliverable |
	|---|---|---|---|
	| 4.1 | Backend: `GET /videos/my` list endpoint | API | `routes/videos.py` + Pydantic `VideoSummary` |
	| 4.2 | Frontend: useQuery hook via TanStack Query | Web | `fetchMyVideos` in `lib/api.ts`, dashboard uses `useQuery` |
	| 4.3 | Replace Firestore code in `dashboard.tsx` | Web | Dashboard lists from API, no Firebase imports |
	| 4.4 | Polling for progress (10s) | Web | TanStack Query polling in dashboard |
	| 4.5 | Delete Firebase deps & `firebase.ts` | Web | package.json cleanup, dead-code removed |
	| 4.6 | Install & configure TanStack Query provider | Web | `@tanstack/react-query` installed, provider in `__root.tsx` |
	| 4.7 | Docs: update diagrams + README | Docs | Updated architecture docs |

	Milestone: **Dashboard lists videos from Supabase using TanStack Query, real-time refresh (polling), Firebase fully removed, TanStack Query provider installed**
	─────────────────────────────

2.3 Next

WebSocket hook, thumbnail gallery, metadata editor (Roadmap 6).

⸻

3. Database (Supabase / Postgres)

Phase	Focus	Due
Schema build	Roadmap Step 1	May 14

3.1 This Sprint
	•	videos table (id, user_id, original_video_gcs_path, processing_status, timestamps) ✅
	•	RLS: user CRUD own rows ✅
	•	Commit first migration → supabase db reset && supabase start verified ✅

3.2 Next

user_profiles, payment tables, backups.

⸻

4. Cross-Cutting Tasks

Area	Owner	Status
Local E2E test (login→upload→dashboard)	—	scheduled after Step 4
Security audit	Backend	queued
CI/CD pipeline	DevOps	not started
Docs & diagrams	All	updating with each merge
Firebase removal	Web	✅ complete (all code, deps, and config removed)


⸻

Overall Health

Foundations are solid; auth + signed-URL slice is the critical path. Hitting Sprint goals A–C lights the system end-to-end and unlocks real feature work.

1. Backend API (FastAPI / Python)

Phase	Completion	Next Milestone
Validation	85 %	Full test-suite + security audit

1.1 What Works
	•	Infrastructure — pyproject.toml, pre-commit, full test bed, FastAPI scaffold
	•	Core — domain model, app-services, adapters, repos, DTOs
	•	Public APIs — endpoints, Pydantic schemas, Swagger, health checks
	•	Services — video-processor, transcription, subtitles, metadata

1.2 In Progress

Area	Items
Quality & Ops	End-to-end tests · perf tests · security review · observability · error recovery
Docs	README refresh · arch diagrams · onboarding
Implementation Checklist	Auth → Supabase • Signed-URL flow • Upload-complete trigger • JWT middleware • /auth/me route

1.3 Not Started

Advanced video algorithms · real-time analysis · custom AI training · extra publisher integrations · analytics/reporting · CI/CD hardening

1.4 Recent Wins
	1.	Legacy monolith removed
	2.	Clean-architecture layers finished
	3.	FastAPI endpoints validated
	4.	External adapters shipped
	5.	POST /videos/upload-url endpoint implemented and tested

1.5 Known Issues
	•	Docs lag codebase
	•	Security audit pending
	•	Extra test coverage required

1.6 Key Decisions
	•	Flask → FastAPI for perf + docs
	•	setup.py → pyproject.toml
	•	Full DI + DDD layers
	•	Future: deeper telemetry, more publisher hooks, optimise video engine

⸻

2. Frontend Web (React + TanStack Router)

Phase	Target MVP	Current Focus
Initial build	2025-06-21	Auth + Signed-URL upload

2.1 What Works
	•	Directory scaffold
	•	Memory-Bank docs setup
	•	High-level architecture drafted
	•	GoogleLoginButton and OAuth callback handler implemented and integrated
	•	Protected layout and /auth/me call implemented and integrated

2.2 In Progress

Stream	Key Tasks
Auth	Google OAuth button (done) · /auth/callback (done) · logout · route protection (done)
API Client	Wrapper w/ Supabase JWT · std error handling
Video Flow	Dropzone → signed PUT URL → upload-complete call
Real-time	WebSocket hook · TanStack-Query cache updates
UI	Dashboard cards · detail view · thumbnail gallery/metadata editor

2.3 Not Started

Publishing UI · responsive polish · Firebase removal · E2E tests · cleanup of sample routes

2.4 Milestones

Milestone	Date	Status
Dev env up	—	✅
Auth flow	May 18	✅
Signed-URL upload	May 24	🔄
Real-time dashboard	May 31	🔄

2.5 Issues / Debt

Env config incomplete · no blockers yet — keep tests high

⸻

3. Database (Supabase / Postgres)

Phase	Focus	Next Step
Schema build-out	videos table & RLS	finish by May 14

3.1 In Progress
	•	videos table + trigger + RLS
	•	Supabase client wired into API/Web
	•	JWT validation dependency

3.2 Next Up

user_profiles & payment tables · migrations · backups

3.3 Core Schema (draft)

CREATE TABLE videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT,
  description TEXT,
  tags TEXT[],
  subtitles TEXT,
  thumbnail_gcs_path TEXT,
  original_video_gcs_path TEXT NOT NULL,
  processing_status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT timezone('utc', now()),
  updated_at TIMESTAMPTZ DEFAULT timezone('utc', now())
);
-- trigger + RLS policies follow

3.4 API Endpoints Backed by DB

GET /videos/my-videos · POST /videos/upload-complete · GET /videos/{id}/view-url · PUT /videos/{id}/metadata

⸻

4. Cross-Cutting Tasks

Area	Owner	Status
Security Audit	Backend	🔄
CI/CD Strategy	DevOps	❌
Monitoring (Prometheus/OTEL)	Backend	🔄
Docs & Diagrams	All	🔄
Automated Tests in CI	DevOps	⏳


⸻

Overall Health

On-track for architecture and service scaffolding.
Watch-list: Auth integration, test coverage, security audit.
Primary risk: WebSocket reliability & GCS signed-URL flow.

⸻
