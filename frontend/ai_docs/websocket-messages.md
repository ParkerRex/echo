# WebSocket Message Format Documentation

This document outlines the expected WebSocket message formats for communication between the frontend and the FastAPI backend. These messages are used to provide real-time updates on video processing status, metadata generation, and error conditions.

## Message Structure

All WebSocket messages follow a consistent JSON structure:

```typescript
interface BaseWebSocketMessage {
  type: string;          // Message type identifier
  job_id: string;        // Unique identifier for the video job
  data: unknown;         // Type-specific payload
  timestamp: string;     // ISO-8601 timestamp
}
```

## Message Types

### 1. JOB_UPDATE

Provides updates on the overall status of a video processing job.

```typescript
interface JobUpdateMessage extends BaseWebSocketMessage {
  type: "JOB_UPDATE";
  data: {
    status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
    progress_percent: number;  // 0-100
    error_message?: string;    // Present only if status is FAILED
  };
}
```

**Usage Example:**
- Dashboard UI updates job status card
- Video detail view updates overall progress indicator
- If status is "FAILED", display error message

### 2. STAGE_UPDATE

Provides updates on a specific processing stage within a job.

```typescript
interface StageUpdateMessage extends BaseWebSocketMessage {
  type: "STAGE_UPDATE";
  data: {
    stage_id: string;    // E.g., "THUMBNAIL_GENERATION", "TRANSCRIPTION", etc.
    status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
    progress_percent: number;  // 0-100
    error_message?: string;    // Present only if status is FAILED
  };
}
```

**Usage Example:**
- Video detail view updates specific stage progress
- If stage fails, display specific error for that stage

### 3. METADATA_UPDATE

Notifies when new or updated metadata is available for a video.

```typescript
interface MetadataUpdateMessage extends BaseWebSocketMessage {
  type: "METADATA_UPDATE";
  data: {
    metadata_type: "TITLE" | "DESCRIPTION" | "TAGS" | "TRANSCRIPT" | "CHAPTERS";
    content: string | string[] | object;  // Depends on metadata_type
  };
}
```

**Usage Example:**
- Video detail view updates specific metadata field
- Enable editing if processing of that metadata type is complete

### 4. THUMBNAIL_GENERATED

Notifies when a new thumbnail has been generated.

```typescript
interface ThumbnailGeneratedMessage extends BaseWebSocketMessage {
  type: "THUMBNAIL_GENERATED";
  data: {
    thumbnail_url: string;    // Full GCS URL to the thumbnail
    thumbnail_id: string;     // Unique identifier for the thumbnail
    width: number;            // Width in pixels
    height: number;           // Height in pixels
    timestamp_seconds?: number; // Optional: Video timestamp this thumbnail represents
  };
}
```

**Usage Example:**
- Thumbnail gallery adds new thumbnail to the display
- If first thumbnail, update job card with thumbnail preview

### 5. ERROR

Provides information about errors that occurred during processing.

```typescript
interface ErrorMessage extends BaseWebSocketMessage {
  type: "ERROR";
  data: {
    error_code: string;        // Machine-readable error code
    error_message: string;     // Human-readable error message
    recoverable: boolean;      // Whether the error allows processing to continue
    affected_stage?: string;   // Optional: The specific stage affected by this error
  };
}
```

**Usage Example:**
- Display error message to user
- If non-recoverable, show job as failed
- If recoverable, show warning but allow continued interaction

## WebSocket Connection Management

### Connection Lifecycle

1. **Initial Connection**:
   - Connect to `wss://[backend-url]/ws` with Supabase JWT for authentication
   - Upon successful connection, send a message to subscribe to specific job updates (if applicable)

2. **Reconnection Strategy**:
   - Implement exponential backoff for reconnection attempts
   - Start with 1 second delay, double until reaching a maximum of 30 seconds
   - Reset backoff counter after successful reconnection

3. **Heartbeat**:
   - Expect backend to send periodic heartbeat messages (every 30 seconds)
   - If no heartbeat received for 60 seconds, attempt reconnection
   - Send heartbeat responses to keep connection alive

### Subscription Message

To subscribe to updates for specific jobs:

```typescript
interface SubscriptionMessage {
  action: "subscribe";
  job_ids: string[];  // Array of job IDs to subscribe to
}
```

## Integration with TanStack Query

The WebSocket hook should integrate with TanStack Query in the following ways:

1. **Direct Cache Updates**:
   For incremental updates like new thumbnails or metadata changes, directly modify the cache:

   ```typescript
   queryClient.setQueryData(['video', jobId], (oldData) => {
     // Update only the relevant portion of the data
     return {
       ...oldData,
       thumbnails: [...oldData.thumbnails, newThumbnailData]
     };
   });
   ```

2. **Cache Invalidation**:
   For major status changes that affect multiple aspects of the data:

   ```typescript
   // For significant changes, invalidate the query to trigger a refetch
   queryClient.invalidateQueries(['video', jobId]);
   ```

3. **Optimistic Updates**:
   For user actions with immediate feedback needs:

   ```typescript
   // When saving metadata
   queryClient.setQueryData(['video', jobId], (oldData) => {
     return {
       ...oldData,
       metadata: {
         ...oldData.metadata,
         title: newTitle
       }
     };
   });
   ```

## Error Handling

WebSocket-specific error handling should include:

1. **Connection Errors**:
   - Display connection status indicator
   - Attempt reconnection with backoff
   - Fall back to polling API if connection fails repeatedly

2. **Message Parsing Errors**:
   - Log invalid messages for debugging
   - Implement defensive parsing with fallbacks
   - Continue processing valid messages

3. **Authentication Errors**:
   - Redirect to login if authentication fails
   - Attempt to refresh token if expired
   - Provide clear feedback about connection status 