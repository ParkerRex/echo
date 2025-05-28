import { useState, useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAppWebSocket } from './useAppWebSocket';
import { supabase } from '@echo/db/clients';
import type { Session, AuthChangeEvent } from '@supabase/supabase-js';
// VideoSummary was re-added, VideoJobSchema aliased to VideoJob, WebSocketJobUpdate removed from this import
import type { VideoJobSchema as VideoJob, ProcessingStatus, VideoSummary } from '@echo/types';

// Define WebSocketJobUpdate locally
// It represents the expected shape of job update messages from the WebSocket.
// Ensures job_id is present for targeting cache updates, video_id for lists.
export type WebSocketJobUpdate = Partial<VideoJob> & {
  job_id: number;
  video_id?: number;
  // Include any other fields that are guaranteed or essential in a WS message for job updates.
  // For example, if status is always sent for an update:
  // status?: ProcessingStatus;
};

export function useJobStatusManager() {
  const queryClient = useQueryClient();
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const prevUserIdRef = useRef<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }: { data: { session: Session | null } }) => {
      setCurrentSession(data.session);
      const currentUserId = data.session?.user?.id ?? null;
      if (currentUserId) {
        console.log("JobStatusManager: Initial session found, user ID:", currentUserId);
      } else {
        console.log("JobStatusManager: No initial session found.");
      }
      prevUserIdRef.current = currentUserId;
    });

    const { data: authListenerData } = supabase.auth.onAuthStateChange(
      (_event: AuthChangeEvent, session: Session | null) => {
        setCurrentSession(session);
        const newUserId = session?.user?.id ?? null;
        if (newUserId) {
          console.log("JobStatusManager: Auth state changed, new user ID:", newUserId);
        } else {
          console.log("JobStatusManager: Auth state changed, user logged out or no session.");
        }
        prevUserIdRef.current = newUserId;
      }
    );

    return () => {
      authListenerData.subscription.unsubscribe();
    };
  }, []);

  const handleTypedWebSocketMessage = (wsUpdateData: WebSocketJobUpdate) => {
    console.log("JobStatusManager: Received parsed job update via WebSocket", wsUpdateData);

    if (!wsUpdateData.job_id) {
        console.warn("JobStatusManager: WebSocket update missing job_id, skipping cache update.", wsUpdateData);
        return;
    }

    const jobDetailsQueryKey = ['jobDetails', String(wsUpdateData.job_id)];
    queryClient.setQueryData<VideoJob | undefined>(
      jobDetailsQueryKey,
      (oldData) => {
        if (oldData) {
          const updatedData = { ...oldData, ...wsUpdateData };
          // Ensure all fields from VideoJob are potentially present if wsUpdateData is partial
          // This is a bit simplistic; a more robust merge might be needed depending on data structure
          return updatedData as VideoJob;
        }
        // If the job details were not already cached, we might not want to create it here,
        // or we might want to fetch it if it's a new job we should know about.
        // For now, only update if existing.
        return oldData;
      }
    );

    const myVideosQueryKey = ['myVideos'];
    queryClient.setQueryData<VideoSummary[] | undefined>(
      myVideosQueryKey,
      (oldVideoList) => {
        if (!oldVideoList) return undefined;
        return oldVideoList.map(videoSummary => {
          // Assuming video_id is present in wsUpdateData if it's relevant to a video entry
          if (wsUpdateData.video_id && videoSummary.id === wsUpdateData.video_id) {
            const newStatus = wsUpdateData.status as ProcessingStatus | undefined; // Type assertion
            return {
              ...videoSummary,
              // Only update fields that are present in the WebSocket update
              ...(wsUpdateData.metadata?.title && { title: wsUpdateData.metadata.title }),
              ...(newStatus && { status: newStatus }),
              // Add other relevant fields from VideoSummary that might be updated
            };
          }
          return videoSummary;
        });
      }
    );

    const processingJobsQueryKey = ['processingJobs'];
    queryClient.setQueryData<VideoJob[] | undefined>(
      processingJobsQueryKey,
      (oldData) => {
        if (!oldData) return undefined; // If no cache exists, do nothing or consider fetching

        const jobExists = oldData.some(job => job.id === wsUpdateData.job_id);

        if (jobExists) {
          return oldData.map(job => {
            if (job.id === wsUpdateData.job_id) {
              // Merge existing job data with update
              // Ensure status is correctly typed if present in wsUpdateData
              const updatedJob = { ...job, ...wsUpdateData };
              if (wsUpdateData.status) {
                updatedJob.status = wsUpdateData.status as ProcessingStatus;
              }
              return updatedJob;
            }
            return job;
          });
        } else {
          // If the job is new and its status implies it should be on the processing dashboard
          // (e.g., PENDING, PROCESSING), add it to the list.
          // This requires wsUpdateData to be a more complete representation of a VideoJob.
          // For now, we'll assume if it's a new job_id, we might want to add it if it's a full object.
          // This might need refinement based on what data the WS sends for "new" jobs.
          if (wsUpdateData.status && (wsUpdateData.status === "PENDING" || wsUpdateData.status === "PROCESSING")) {
             // We need to be careful about partial updates vs full new job objects.
             // Let's assume wsUpdateData could be a full new job if it's not in oldData.
             // The type WebSocketJobUpdate is Partial<VideoJob>, so we need to ensure
             // that if we add it, it has all necessary fields for a VideoJob.
             // This part is tricky without knowing the exact WS message contents for new jobs.
             // A safer approach for "new" jobs might be to invalidate the query and let it refetch,
             // or ensure the WS sends the full job object.
             // For now, let's try to add it if it has a status.
             // This cast might be unsafe if wsUpdateData is truly partial.
            return [...oldData, wsUpdateData as VideoJob];
          }
        }
        return oldData;
      }
    );

    console.log(`JobStatusManager: Updated cache for job ${wsUpdateData.job_id} and relevant lists (processingJobs, myVideos).`);
  };

  const { isConnected, lastJsonMessage } = useAppWebSocket({
    onOpen: () => console.log("JobStatusManager: WebSocket connection established."),
    onClose: (event) => console.log("JobStatusManager: WebSocket connection closed.", event),
    onError: (event) => console.error("JobStatusManager: WebSocket error.", event),
  });

  useEffect(() => {
    if (lastJsonMessage) {
        // Validate the structure of the message more carefully
        if (typeof lastJsonMessage === 'object' &&
            lastJsonMessage !== null &&
            'job_id' in lastJsonMessage &&
            typeof (lastJsonMessage as any).job_id === 'number' // Ensure job_id is a number
            // Potentially add more checks if other fields are critical for routing/typing
            ) {
            const updateData = lastJsonMessage as WebSocketJobUpdate;
            handleTypedWebSocketMessage(updateData);
        } else {
            console.warn("JobStatusManager: Received WebSocket message of unexpected shape or missing/invalid job_id:", lastJsonMessage);
        }
    }
  }, [lastJsonMessage, queryClient]); // Added queryClient to dependencies of useEffect if it's used in handleTypedWebSocketMessage through closure

  useEffect(() => {
    const currentUserId = prevUserIdRef.current;
    if (currentUserId) {
      console.log(`JobStatusManager: Active for user ${currentUserId}. WebSocket connected: ${isConnected}`);
    } else {
      console.log(`JobStatusManager: Waiting for user ID to be determined. WebSocket connected: ${isConnected}`);
    }
  }, [isConnected]); // Removed prevUserIdRef.current from deps as it's a ref.

  return { isWebSocketConnected: isConnected, currentUserId: prevUserIdRef.current, session: currentSession };
}