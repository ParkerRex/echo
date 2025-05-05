# Frontend Overview

This document provides a high-level overview of the frontend application for the Video Processing Pipeline project.

## Purpose

The frontend serves as the user interface for content creators and administrators to:
*   Upload video files for processing.
*   Monitor the real-time progress of video analysis and metadata generation.
*   Review, edit, and approve AI-generated metadata (titles, descriptions, tags, transcripts, chapters).
*   Trigger the final publishing process (e.g., to YouTube).

## Technology Stack

*   **Framework:** React (using Vite for development and build)
*   **Language:** TypeScript
*   **Routing:** TanStack Router
*   **UI Components:** shadcn/ui library, supplemented with custom components.
*   **API Communication:** A custom client wrapper (`src/api.ts`) interacts with the backend FastAPI.
*   **Real-time:** FastAPI WebSockets (currently migrating away from a legacy Firebase implementation).
*   **State Management:** To be defined/implemented (potential candidates: Zustand, Jotai, TanStack Query).
*   **Package Management:** PNPM

## Project Structure Highlights

*   `src/`: Contains all source code.
    *   `components/`: Reusable React components, including UI elements (`ui/`) and feature-specific components (`video/`, `home/`, `shared/`).
    *   `routes/`: Defines application routes using TanStack Router's file-based routing convention. Includes authentication layout (`_authed/`) and placeholder routes.
    *   `lib/`: Utility functions (`utils.ts`).
    *   `hooks/`: Custom React hooks.
    *   `services/`: Potential location for business logic services (e.g., WebSocket client, GCS interactions).
    *   `api.ts`: Wrapper for making backend API calls.
    *   `router.tsx`: TanStack Router setup.
    *   `client.tsx`/`ssr.tsx`: Application entry points for client/server.
*   `public/`: Static assets.
*   `docs/`: Project documentation, including this overview, PRD (`fe-prd.txt`), and implementation tasks (`fe-implementation-tasks.md`).
*   `firebase.ts`: Legacy Firebase configuration (to be removed).

## Current Status

The frontend is undergoing a migration from Firebase-based real-time updates to a FastAPI WebSocket architecture, integrating with a new backend API. Many core components and routes exist, but some are placeholders or require refactoring to align with the new architecture as detailed in `fe-implementation-tasks.md`.
