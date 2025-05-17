import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAppWebSocket, WebSocketJobUpdate } from './useAppWebSocket';
import { supabase } from '@echo/db';
import type { Session, AuthChangeEvent } from '@supabase/supabase-js';
import type { VideoSummary, VideoJob, ProcessingStatus } from '../types/api';

export function useJobStatusManager() {
  const queryClient = useQueryClient();
  const [userId, setUserId] = useState<string | null>(null);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }: { data: { session: Session | null } }) => {
      setCurrentSession(data.session);
      setUserId(data.session?.user?.id ?? null);
      if (data.session?.user?.id) {
        console.log("JobStatusManager: Initial session found, user ID:", data.session.user.id);
      } else {
        console.log("JobStatusManager: No initial session found.");
      }
    });

    const { data: authListener } = supabase.auth.onAuthStateChange(
      (_event: AuthChangeEvent, session: Session | null) => {
        setCurrentSession(session);
        setUserId(session?.user?.id ?? null);
        if (session?.user?.id) {
          console.log("JobStatusManager: Auth state changed, new user ID:", session.user.id);
        } else {
          console.log("JobStatusManager: Auth state changed, user logged out or no session.");
        }
      }
    );

    return () => {
      authListener?.unsubscribe();
    };
  }, []);

  const handleWebSocketMessage = (wsUpdateData: WebSocketJobUpdate) => {
    console.log("JobStatusManager: Received job update via WebSocket", wsUpdateData);

    const jobDetailsQueryKey = ['jobDetails', String(wsUpdateData.job_id)];
    queryClient.setQueryData<VideoJob | undefined>(
      jobDetailsQueryKey,
      (oldData) => {
        if (oldData) {
          return { ...oldData, ...wsUpdateData } as VideoJob;
        }
        return wsUpdateData as VideoJob;
      }
    );

    const myVideosQueryKey = ['myVideos'];
    queryClient.setQueryData<VideoSummary[] | undefined>(
      myVideosQueryKey,
      (oldVideoList) => {
        if (!oldVideoList) return undefined;
        return oldVideoList.map(videoSummary => {
          if (wsUpdateData.video_id && String(wsUpdateData.video_id) === videoSummary.id) {
            const newStatus = wsUpdateData.status as ProcessingStatus | undefined;
            return {
              ...videoSummary,
              status: newStatus ? newStatus.toString() : videoSummary.status,
              title: (wsUpdateData as any).title ?? videoSummary.title,
            };
          }
          return videoSummary;
        });
      }
    );
    console.log(`JobStatusManager: Updated cache for job ${wsUpdateData.job_id} and potentially related lists.`);
  };

  const { isConnected } = useAppWebSocket({
    userId: userId,
    onMessage: handleWebSocketMessage,
    onOpen: () => console.log("JobStatusManager: WebSocket connection established."),
    onClose: (event) => console.log("JobStatusManager: WebSocket connection closed.", event),
    onError: (event) => console.error("JobStatusManager: WebSocket error.", event),
  });

  useEffect(() => {
    if (userId) {
      console.log(`JobStatusManager: Active for user ${userId}. WebSocket connected: ${isConnected}`);
    } else {
      console.log("JobStatusManager: Waiting for user ID. WebSocket connected: ${isConnected}");
    }
  }, [userId, isConnected]);

  return { isWebSocketConnected: isConnected, currentUserId: userId, session: currentSession };
} 