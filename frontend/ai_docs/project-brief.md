# Video Processing Pipeline - Frontend Project Brief

## Project Overview
The Video Processing Pipeline frontend provides content creators with an intuitive interface to upload videos, monitor AI-powered processing in real-time, review and edit generated metadata, and publish content to platforms like YouTube.

## Core Requirements

1. **Authentication**: Implement Supabase Google OAuth for user authentication, replacing Firebase.
2. **Video Upload**: Direct uploads to Google Cloud Storage via signed URLs from backend.
3. **Real-time Monitoring**: Display processing status and updates via FastAPI WebSockets.
4. **Metadata Management**: Allow users to review, edit, and save AI-generated metadata.
5. **Thumbnail Selection**: View gallery of AI-generated thumbnails and select preferred option.
6. **Publishing Control**: Trigger publishing process to distribution platforms.

## Key Deliverables

1. Complete migration from Firebase to Supabase for authentication
2. Implementation of WebSocket client for real-time updates
3. Refactored dashboard and video detail views
4. Enhanced metadata editor with thumbnail gallery
5. Responsive design for all core features
6. Removal of unused example code and Firebase dependencies

## Technical Constraints

- Must integrate with existing Supabase client setup in `db/supabase/clients/`
- Must communicate with FastAPI backend via authenticated API requests
- Must handle WebSocket connections for real-time updates
- Must support direct uploads to GCS via signed URLs

## Success Criteria

- Successful authentication via Supabase
- Real-time updates appearing within 1 second of backend events
- Complete Firebase removal
- Successful uploads, metadata editing, and publishing functionality
- High user satisfaction with interface usability (4.5/5 target) 