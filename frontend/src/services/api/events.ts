import { apiClient } from './client';
import type { Event, EventSummary, EventAnalytics, PaginatedResponse, Round, QueueItem } from '@/types';

export const eventsApi = {
  // Public
  getBySlug: (slug: string) =>
    apiClient.get<Event>(`/events/slug/${slug}`).then(r => r.data),

  getQueue: (eventId: string) =>
    apiClient.get<QueueItem[]>(`/events/${eventId}/queue`).then(r => r.data),

  getCurrentRound: (eventId: string) =>
    apiClient.get<Round>(`/events/${eventId}/round/current`).then(r => r.data),

  // Admin
  list: (page = 1, perPage = 20) =>
    apiClient.get<PaginatedResponse<EventSummary>>('/admin/events', { params: { page, per_page: perPage } }).then(r => r.data),

  create: (data: { name: string; club_id: string; dj_id?: string }) =>
    apiClient.post<Event>('/admin/events', data).then(r => r.data),

  update: (id: string, data: Partial<Event>) =>
    apiClient.patch<Event>(`/admin/events/${id}`, data).then(r => r.data),

  start: (id: string) =>
    apiClient.post<Event>(`/admin/events/${id}/start`).then(r => r.data),

  end: (id: string) =>
    apiClient.post<Event>(`/admin/events/${id}/end`).then(r => r.data),

  getAnalytics: (id: string) =>
    apiClient.get<EventAnalytics>(`/admin/events/${id}/analytics`).then(r => r.data),
};
