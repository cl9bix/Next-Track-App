import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { WebSocketClient } from './client';
import type { WSEventType, WSMessage } from '@/types';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8110/ws';

let sharedClient: WebSocketClient | null = null;

function getClient(): WebSocketClient {
  if (!sharedClient) {
    const token = localStorage.getItem('next_track_token') || '';
    sharedClient = new WebSocketClient({ url: WS_URL, token });
  }
  return sharedClient;
}

export function useWebSocket(eventId?: string) {
  const client = useRef(getClient());
  const queryClient = useQueryClient();

  useEffect(() => {
    if (eventId) {
      client.current.connect(eventId);
      return () => client.current.disconnect();
    }
  }, [eventId]);

  const subscribe = useCallback(
    (type: WSEventType, handler: (msg: WSMessage) => void) => {
      return client.current.on(type, handler);
    },
    []
  );

  const send = useCallback(
    (type: WSEventType, payload: unknown) => {
      client.current.send(type, payload);
    },
    []
  );

  // Auto-invalidate queries on certain events
  useEffect(() => {
    const unsubs = [
      client.current.on('queue_added', () => queryClient.invalidateQueries({ queryKey: ['queue'] })),
      client.current.on('queue_updated', () => queryClient.invalidateQueries({ queryKey: ['queue'] })),
      client.current.on('track_started', () => queryClient.invalidateQueries({ queryKey: ['queue', 'round'] })),
      client.current.on('track_finished', () => queryClient.invalidateQueries({ queryKey: ['queue', 'round'] })),
      client.current.on('voting_open', () => queryClient.invalidateQueries({ queryKey: ['round'] })),
      client.current.on('voting_closed', () => queryClient.invalidateQueries({ queryKey: ['round'] })),
      client.current.on('vote', () => queryClient.invalidateQueries({ queryKey: ['round', 'queue'] })),
      client.current.on('suggestion_added', () => queryClient.invalidateQueries({ queryKey: ['suggestions'] })),
    ];
    return () => unsubs.forEach(u => u());
  }, [queryClient]);

  return { subscribe, send, isConnected: client.current.isConnected };
}
