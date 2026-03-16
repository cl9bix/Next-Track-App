import { apiRequest } from "./client";
import type { EventResponse, SuggestPayload, VotePayload } from "./types";

export type SearchTrack = {
    id: string;
    title: string;
    artist?: string;
    album?: string;
    cover_url?: string;
    duration_sec?: number;
    source: string;
};

export type EventSummary = {
    id: number;
    club_id: number;
    title: string;
    preview?: string | null;
    start_date?: string | null;
    end_date?: string | null;
    created_at: string;
    slug: string;
    attendees_count: number;
};

export type QueueItem = {
    track_id: string;
    title: string;
    artist?: string | null;
    cover_url?: string | null;
    duration_sec?: number | null;
    votes: number;
    suggested_by?: number | null;
    created_at: number;
};

function telegramHeaders(tgUserId?: number) {
    return tgUserId ? { "X-Telegram-User-Id": String(tgUserId) } : undefined;
}

export async function getEventByClubSlug(
    clubSlug: string,
    token?: string | null
) {
    return apiRequest<EventResponse>(`/api/v1/events/${clubSlug}`, {
        method: "GET",
        authToken: token ?? undefined,
    });
}

export async function getEventSummary(
    slug: string,
    tgUserId?: number,
    token?: string | null
) {
    return apiRequest<EventSummary>(`/api/v1/events/${slug}`, {
        method: "GET",
        headers: telegramHeaders(tgUserId),
        authToken: token ?? undefined,
    });
}

export async function getEventState(
    clubSlug: string,
    token?: string | null
) {
    return apiRequest<{ state?: Record<string, unknown> }>(
        `/api/v1/events/${clubSlug}/state`,
        {
            method: "GET",
            authToken: token ?? undefined,
        }
    );
}

export async function getEventQueue(
    slug: string,
    limit = 20,
    tgUserId?: number,
    token?: string | null
) {
    return apiRequest<{ items: QueueItem[]; attendees_count: number }>(
        `/api/v1/events/${slug}/queue?limit=${limit}`,
        {
            method: "GET",
            headers: telegramHeaders(tgUserId),
            authToken: token ?? undefined,
        }
    );
}

export async function searchTracks(query: string, limit = 15) {
    const params = new URLSearchParams({
        q: query,
        limit: String(limit),
    });

    return apiRequest<{ items: SearchTrack[] }>(
        `/api/v1/search/?${params.toString()}`,
        {
            method: "GET",
        }
    );
}

export async function voteForTrack(
    clubSlug: string,
    payload: VotePayload,
    token?: string | null
) {
    return apiRequest<{ ok?: boolean; status?: string }>(
        `/api/v1/events/${clubSlug}/vote`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
            authToken: token ?? undefined,
        }
    );
}

export async function suggestTrack(
    clubSlug: string,
    payload: SuggestPayload,
    token?: string | null
) {
    return apiRequest<{ ok?: boolean; status?: string; event_id?: number; track_id?: string }>(
        `/api/v1/events/${clubSlug}/queue`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
            authToken: token ?? undefined,
        }
    );
}

export async function addTrackToQueue(
    slug: string,
    payload: {
        track_id: string;
        title: string;
        artist?: string;
        cover_url?: string;
        duration_sec?: number;
        telegram_id?: number;
    },
    tgUserId?: number,
    token?: string | null
) {
    return apiRequest<{ status: string; event_id: number; track_id: string }>(
        `/api/v1/events/${slug}/queue`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(tgUserId ? { "X-Telegram-User-Id": String(tgUserId) } : {}),
            },
            body: JSON.stringify(payload),
            authToken: token ?? undefined,
        }
    );
}

export function createEventWsUrl(eventId: number | string) {
    const base = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8950").replace(/\/+$/, "");
    const wsBase = base.replace(/^http/i, "ws");
    return `${wsBase}/ws/events/${eventId}`;
}