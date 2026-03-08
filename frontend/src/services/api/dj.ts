import { apiClient } from './client';
import type { Round, QueueItem } from '@/types';

export const djApi = {
  openRound: (eventId: string) =>
    apiClient.post<Round>(`/dj/events/${eventId}/rounds/open`).then(r => r.data),

  closeVoting: (roundId: string) =>
    apiClient.post<Round>(`/dj/rounds/${roundId}/close`).then(r => r.data),

  startTrack: (queueItemId: string) =>
    apiClient.post<QueueItem>(`/dj/queue/${queueItemId}/start`).then(r => r.data),

  endTrack: (queueItemId: string) =>
    apiClient.post<QueueItem>(`/dj/queue/${queueItemId}/end`).then(r => r.data),

  skipTrack: (queueItemId: string) =>
    apiClient.post<QueueItem>(`/dj/queue/${queueItemId}/skip`).then(r => r.data),

  reorderQueue: (eventId: string, order: string[]) =>
    apiClient.put(`/dj/events/${eventId}/queue/reorder`, { order }).then(r => r.data),
};
