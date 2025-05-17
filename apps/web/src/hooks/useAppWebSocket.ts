import { useState, useEffect, useRef, useCallback } from 'react';
// Assuming your job status updates will have a structure.
// This should align with what the backend sends over WebSocket.
// Let's use the VideoJob type from our API types for now, or a subset.
import type { VideoJob, ProcessingStatus } from '../types/api';

export interface WebSocketJobUpdate extends Partial<VideoJob> {
  job_id: number; // Ensure job_id is always present for identification
  // any other specific fields expected in a WebSocket message for job updates
  // e.g., status, progress_percentage, error_message
}

interface UseAppWebSocketOptions {
  userId: string | null | undefined; // User ID to include in the WebSocket URL
  onMessage?: (data: WebSocketJobUpdate) => void; // Callback for when a message is received
  onError?: (event: Event) => void; // Callback for WebSocket errors
  onOpen?: (event: Event) => void; // Callback for when connection opens
  onClose?: (event: CloseEvent) => void; // Callback for when connection closes
}

const WEBSOCKET_RECONNECT_INTERVAL = 5000; // 5 seconds

export function useAppWebSocket({
  userId,
  onMessage,
  onError,
  onOpen,
  onClose,
}: UseAppWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const webSocketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const VITE_WS_BASE_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

  const connect = useCallback(() => {
    if (!userId) {
      console.log("WebSocket: User ID not provided, not connecting.");
      return;
    }

    if (webSocketRef.current && webSocketRef.current.readyState === WebSocket.OPEN) {
      console.log("WebSocket: Already connected.");
      return;
    }

    // Clear any existing reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    const wsUrl = `${VITE_WS_BASE_URL}/ws/jobs/status/${userId}`;
    console.log(`WebSocket: Connecting to ${wsUrl}`);
    const ws = new WebSocket(wsUrl);
    webSocketRef.current = ws;

    ws.onopen = (event) => {
      console.log("WebSocket: Connection opened", event);
      setIsConnected(true);
      if (onOpen) onOpen(event);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data as string) as WebSocketJobUpdate;
        // console.log("WebSocket: Message received", data);
        if (onMessage) onMessage(data);
      } catch (error) {
        console.error("WebSocket: Error parsing message data", error);
      }
    };

    ws.onerror = (event) => {
      console.error("WebSocket: Error", event);
      setIsConnected(false);
      if (onError) onError(event);
      // Don't attempt to reconnect immediately on error, let onClose handle it or specific error handling
    };

    ws.onclose = (event) => {
      console.log("WebSocket: Connection closed", event);
      setIsConnected(false);
      webSocketRef.current = null; // Clear the ref
      if (onClose) onClose(event);

      // Attempt to reconnect if userId is still present (e.g., user hasn't logged out)
      if (userId && !event.wasClean) { // Don't reconnect if closed cleanly
        console.log(`WebSocket: Attempting to reconnect in ${WEBSOCKET_RECONNECT_INTERVAL / 1000} seconds...`);
        if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = setTimeout(connect, WEBSOCKET_RECONNECT_INTERVAL);
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId, onMessage, onError, onOpen, onClose, VITE_WS_BASE_URL]); // VITE_WS_BASE_URL is stable

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (webSocketRef.current) {
        console.log("WebSocket: Closing connection due to component unmount or userId change.");
        webSocketRef.current.close(1000); // 1000 is a normal closure
        webSocketRef.current = null;
      }
    };
  }, [connect]); // Re-run connect if any of its dependencies change (esp. userId)

  const sendMessage = useCallback((message: string | object) => {
    if (webSocketRef.current && webSocketRef.current.readyState === WebSocket.OPEN) {
      const messageToSend = typeof message === 'string' ? message : JSON.stringify(message);
      webSocketRef.current.send(messageToSend);
    } else {
      console.warn("WebSocket: Not connected. Cannot send message.");
    }
  }, []);

  return { isConnected, sendMessage };
} 