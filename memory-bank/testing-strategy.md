# Comprehensive Testing Strategy & Atomic Checklist

_Last updated: 2025-04-30 11:39 EDT_

---

## Overview

This document defines the unified testing strategy for the Video Upload + AI Metadata Pipeline project, covering backend, frontend, and E2E (end-to-end) testing. It includes an atomic, checkable list of steps to ensure all critical paths are tested and the system can be validated in a way that replicates real-world usage.

---

## Testing Strategy

### 1. Backend

- **Unit tests:** Continue for isolated logic (already good coverage).
- **Integration tests:** Add tests for Firestore trigger listener (simulate Firestore document changes, assert pipeline is called).
- **Reduce redundant mocks:** Where possible, use real GCS/Firestore in integration tests (with test buckets/collections).

### 2. Frontend

- **Component tests:** For upload drop zone, metadata editing, thumbnail regeneration.
- **Integration tests:** Simulate user actions and assert Firestore is updated.
- **E2E tests:** Use Cypress/Playwright to automate the full user flow (upload, edit, observe status).

### 3. E2E (Full System)

- **Automated E2E test** (Cypress/Playwright or custom script):
  - Upload video via drop zone.
  - Edit metadata in UI.
  - Trigger thumbnail regeneration.
  - Observe Firestore and UI for real-time updates.
  - Assert backend pipeline is triggered and completes.

### 4. Tooling

- **Test GCS bucket and Firestore collection:** Use separate resources for tests to avoid polluting production data.
- **Test harness:** Script or framework to orchestrate E2E tests, clean up test data, and report results.

---

## Atomic Checklist

### Backend

- [x] Add integration tests for Firestore trigger listener (simulate document changes, assert pipeline is called)
- [ ] Reduce redundant mocks in backend tests; use real GCS/Firestore where feasible
- [ ] Ensure all backend modules have unit tests with clear, non-overlapping coverage

### Frontend

- [ ] Implement/verify upload drop zone in frontend
- [ ] Add component tests for upload drop zone, metadata editing, thumbnail regeneration
- [ ] Add integration tests for Firestore updates from UI actions

### E2E

- [ ] Set up E2E test harness (Cypress/Playwright or custom)
- [ ] Write E2E test: upload video via drop zone, edit metadata, trigger thumbnail regeneration, observe Firestore/UI updates
- [ ] Use test GCS bucket and Firestore collection for E2E tests
- [ ] Add cleanup logic for test data after E2E runs
- [ ] Document and automate E2E test flow (local and CI)

### General

- [ ] Review and update documentation for running all tests
- [ ] Track progress in progress.md and activeContext.md

---

## Summary Table

| Layer    | Current State       | Gaps/Redundancy          | Needed for E2E       |
| -------- | ------------------- | ------------------------ | -------------------- |
| Backend  | Unit tests (mocked) | No Firestore trigger/E2E | Integration tests    |
| Frontend | UI, some tests      | No upload E2E            | Drop zone, E2E tests |
| E2E      | None                | N/A                      | Full pipeline test   |

---

## Next Steps

1. Implement/verify upload drop zone in frontend.
2. Add backend integration tests for Firestore trigger listener.
3. Set up E2E test harness (Cypress/Playwright).
4. Document and automate E2E test flow.
5. Iterate: Fill gaps as new features are added.
