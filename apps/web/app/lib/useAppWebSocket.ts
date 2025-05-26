import { useState, useEffect, useRef, useCallback } from 'react';
// Assuming your job status updates will have a structure.
// This should align with what the backend sends over WebSocket.
// Let's use the VideoJob type from our API types for now, or a subset.
import type { VideoJobSchema as VideoJob, ProcessingStatus } from '../types/api';
import { useAuth } from './useAuth'; // Assuming useAuth provides user and session

export interface WebSocketJobUpdate extends Partial<VideoJob> {
  job_id: number; // Ensure job_id is always present for identification
  // any other specific fields expected in a WebSocket message for job updates
  // e.g., status, progress_percentage, error_message
}

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'; // Example, ensure this is in your .env

export type WebSocketStatus = 'connecting' | 'open' | 'closing' | 'closed' | 'uninstantiated';

interface UseAppWebSocketOptions {
  onOpen?: (event: Event) => void;
  onMessage?: (event: MessageEvent) => void;
  onError?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  reconnectLimit?: number;
  reconnectIntervalMs?: number;
  // Path to append after WS_BASE_URL, e.g., /ws/jobs/status/
  // If it needs dynamic parts like user_id, the hook will append it.
  path?: string;
}

interface UseAppWebSocketReturn {
  sendJsonMessage: (data: any) => void;
  lastJsonMessage: any | null;
  connectionStatus: WebSocketStatus;
  isConnected: boolean;
  socketRef: React.MutableRefObject<WebSocket | null>;
}

export function useAppWebSocket(options?: UseAppWebSocketOptions): UseAppWebSocketReturn {
  const { session, user } = useAuth();
  const [lastJsonMessage, setLastJsonMessage] = useState<any | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<WebSocketStatus>('uninstantiated');
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);

  const {
    onOpen,
    onMessage,
    onError,
    onClose,
    reconnectLimit = 5,
    reconnectIntervalMs = 3000,
    path = '/ws/jobs/status/' // Default path, user_id will be appended
  } = options || {};

  const connect = useCallback(async () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      return; // Already connected
    }
    if (!session?.access_token || !user?.id) {
      console.log('WebSocket: No session or user ID, not connecting.');
      setConnectionStatus('closed'); // Or some other appropriate status
      return;
    }

    setConnectionStatus('connecting');

    const wsUrl = `${WS_BASE_URL.replace(/^http/, 'ws')}${path}${user.id}?token=${session.access_token}`;

    try {
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = (event) => {
        console.log('WebSocket: Connection opened');
        setConnectionStatus('open');
        reconnectAttemptsRef.current = 0; // Reset reconnect attempts on successful open
        if (onOpen) onOpen(event);
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastJsonMessage(message);
          if (onMessage) onMessage(event); // Pass the raw event too
        } catch (e) {
          console.error('WebSocket: Error parsing JSON message', e);
          // Handle non-JSON messages or pass raw data if needed
          if (onMessage) onMessage(event);
        }
      };

      socket.onerror = (event) => {
        console.error('WebSocket: Error', event);
        setConnectionStatus('closed'); // Or a specific error status
        if (onError) onError(event);
        // Reconnect logic will be triggered by onclose
      };

      socket.onclose = (event) => {
        console.log(`WebSocket: Connection closed (code: ${event.code}, reason: ${event.reason})`);
        setConnectionStatus('closed');
        if (onClose) onClose(event);

        // Reconnect logic
        if (reconnectAttemptsRef.current < reconnectLimit) {
          reconnectAttemptsRef.current++;
          console.log(`WebSocket: Attempting to reconnect (${reconnectAttemptsRef.current}/${reconnectLimit})...`);
          setTimeout(connect, reconnectIntervalMs);
        } else {
          console.log('WebSocket: Reconnect limit reached.');
        }
      };
    } catch (err) {
      console.error('WebSocket: Instantiation failed', err);
      setConnectionStatus('closed'); // Or a specific error status
    }
  }, [session, user, onOpen, onMessage, onError, onClose, reconnectLimit, reconnectIntervalMs, path]);

  useEffect(() => {
    if (session?.access_token && user?.id) {
      connect();
    } else {
      // If no session, ensure any existing socket is closed
      if (socketRef.current) {
        socketRef.current.close(1000, 'User logged out or session expired');
        socketRef.current = null;
      }
      setConnectionStatus('closed');
    }

    return () => {
      if (socketRef.current) {
        console.log('WebSocket: Cleaning up connection.');
        // Prevent reconnect attempts on component unmount
        reconnectAttemptsRef.current = reconnectLimit + 1;
        socketRef.current.close(1000, 'Component unmounted');
        socketRef.current = null;
      }
    };
  }, [session, user, connect, reconnectLimit]); // connect is stable due to useCallback with its own deps

  const sendJsonMessage = useCallback((data: any) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        socketRef.current.send(JSON.stringify(data));
      } catch (e) {
        console.error("WebSocket: Error sending JSON message", e);
      }
    } else {
      console.warn("WebSocket: Connection not open. Message not sent.", data);
    }
  }, []);

  return {
    sendJsonMessage,
    lastJsonMessage,
    connectionStatus,
    isConnected: connectionStatus === 'open',
    socketRef,
  };
} 