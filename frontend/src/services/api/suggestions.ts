import { apiClient } from './client';
import type { Suggestion, SearchResult } from '@/types';

export const suggestionsApi = {
  suggest: (eventId: string, trackData: SearchResult) =>
    apiClient.post<Suggestion>(`/events/${eventId}/suggestions`, trackData).then(r => r.data),

  list: (eventId: string) =>
    apiClient.get<Suggestion[]>(`/events/${eventId}/suggestions`).then(r => r.data),

  // DJ actions
  accept: (suggestionId: string) =>
    apiClient.post<Suggestion>(`/suggestions/${suggestionId}/accept`).then(r => r.data),

  reject: (suggestionId: string) =>
    apiClient.post<Suggestion>(`/suggestions/${suggestionId}/reject`).then(r => r.data),

  // Search
  search: (query: string, source: 'deezer' | 'itunes' = 'deezer') =>
    apiClient.get<SearchResult[]>('/search/tracks', { params: { q: query, source } }).then(r => r.data),
};
