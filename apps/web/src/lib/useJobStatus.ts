import { useState, useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAppWebSocket } from './useAppWebSocket';
import { supabase } from '@echo/db/clients';
import type { Session, AuthChangeEvent } from '@supabase/supabase-js';
import type { VideoJobSchema as VideoJob, ProcessingStatus, VideoSummary, WebSocketJobUpdate } from '@echo/types';

export function useJobStatusManager() {
  const queryClient = useQueryClient();
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const prevUserIdRef = useRef<string | null>(null);

  useEffect(() => {
    supabase().auth.getSession().then(({ data }: { data: { session: Session | null } }) => {
      setCurrentSession(data.session);
      const currentUserId = data.session?.user?.id ?? null;
      if (currentUserId) {
        console.log("JobStatusManager: Initial session found, user ID:", currentUserId);
      } else {
        console.log("JobStatusManager: No initial session found.");
      }
      prevUserIdRef.current = currentUserId;
    });

    const { data: authListenerData } = supabase().auth.onAuthStateChange(
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
          return updatedData as VideoJob;
        }
        return oldData;
      }
    );

    const myVideosQueryKey = ['myVideos'];
    queryClient.setQueryData<VideoSummary[] | undefined>(
      myVideosQueryKey,
      (oldVideoList) => {
        if (!oldVideoList) return undefined;
        return oldVideoList.map(videoSummary => {
          if (wsUpdateData.video_id && videoSummary.id === wsUpdateData.video_id) {
            const newStatus = wsUpdateData.status as ProcessingStatus | undefined;
            return {
              ...videoSummary,
              status: newStatus || videoSummary.status,
              title: wsUpdateData.title ?? videoSummary.title,
            };
          }
          return videoSummary;
        });
      }
    );
    console.log(`JobStatusManager: Updated cache for job ${wsUpdateData.job_id} and potentially related lists.`);
  };

  const { isConnected, lastJsonMessage } = useAppWebSocket({
    onOpen: () => console.log("JobStatusManager: WebSocket connection established."),
    onClose: (event) => console.log("JobStatusManager: WebSocket connection closed.", event),
    onError: (event) => console.error("JobStatusManager: WebSocket error.", event),
  });

  useEffect(() => {
    if (lastJsonMessage) {
        if (typeof lastJsonMessage === 'object' && lastJsonMessage !== null && ('job_id' in lastJsonMessage || 'video_id' in lastJsonMessage)) {
            const updateData = lastJsonMessage as WebSocketJobUpdate;
            handleTypedWebSocketMessage(updateData);
        } else {
            console.warn("JobStatusManager: Received WebSocket message of unexpected shape:", lastJsonMessage);
        }
    }
  }, [lastJsonMessage]);

  useEffect(() => {
    const currentUserId = prevUserIdRef.current;
    if (currentUserId) {
      console.log(`JobStatusManager: Active for user ${currentUserId}. WebSocket connected: ${isConnected}`);
    } else {
      console.log("JobStatusManager: Waiting for user ID to be determined. WebSocket connected: ${isConnected}");
    }
  }, [isConnected]);

  return { isWebSocketConnected: isConnected, currentUserId: prevUserIdRef.current, session: currentSession };
}