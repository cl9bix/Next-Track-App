import { apiRequest } from "./client";
import type {
  EventResponse,
  QueueItemApi,
  SearchResultApi,
  SuggestPayload,
  VotePayload,
} from "./types";

export async function getEventByClubSlug(clubSlug: string) {
  return apiRequest<EventResponse>(`/api/v1/events/${clubSlug}`);
}

export async function getEventState(clubSlug: string) {
  return apiRequest<{ state?: Record<string, unknown> }>(`/api/v1/events/${clubSlug}/state`);
}

export async function getEventQueue(clubSlug: string, limit = 10) {
  return apiRequest<{ items?: QueueItemApi[] }>(`/api/v1/events/${clubSlug}/queue?limit=${limit}`);
}

export async function searchTracks(query: string, limit = 15) {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
  });

  return apiRequest<SearchResultApi[]>(`/api/v1/search/?${params.toString()}`);
}

export async function voteForTrack(
  clubSlug: string,
  payload: VotePayload,
  token?: string | null
) {
  return apiRequest<{ ok: boolean }>(`/api/v1/events/${clubSlug}/vote`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    authToken: token,
  });
}

export async function suggestTrack(
  clubSlug: string,
  payload: SuggestPayload,
  token?: string | null
) {
  return apiRequest<{ ok: boolean }>(`/api/v1/events/${clubSlug}/suggest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    authToken: token,
  });
}

export function createEventWsUrl(eventId: number | string) {
  const base = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");
  const wsBase = base.replace(/^http/i, "ws");
  return `${wsBase}/ws/events/${eventId}`;
}