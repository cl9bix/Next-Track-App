import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
    createEventWsUrl,
    getEventByClubSlug,
    getEventQueue,
    searchTracks,
    suggestTrack,
    voteForTrack,
} from "@/api/events";

type UiEvent = {
    id: string;
    club_id: string;
    name: string;
    slug: string;
    status: "active" | "inactive";
    created_at: string;
    attendees_count: number;
    preview?: string | null;
    background_image_url?: string | null;
    club?: {
        id: number;
        name: string;
        slug: string;
    } | null;
};

type UiQueueItem = {
    id: string;
    track: {
        id: string;
        title: string;
        artist: string;
        source: string;
        cover_url?: string | null;
        duration_sec?: number | null;
    };
    position: number;
    status: "playing" | "queued" | "completed";
    votes_count: number;
};

type UiSearchResult = {
    id: string;
    title: string;
    artist: string;
    cover_url?: string | null;
    duration_sec?: number | null;
    source: string;
};

function normalizeEvent(apiEvent: any, clubSlug: string, attendeesCount = 0): UiEvent {
    return {
        id: String(apiEvent?.id ?? ""),
        club_id: String(apiEvent?.club_id ?? ""),
        name: apiEvent?.title ?? apiEvent?.name ?? "Untitled Event",
        slug: apiEvent?.slug ?? clubSlug,
        status: apiEvent?.end_date ? "inactive" : "active",
        created_at:
            apiEvent?.start_date ??
            apiEvent?.created_at ??
            new Date().toISOString(),
        attendees_count: Number(apiEvent?.attendees_count ?? attendeesCount ?? 0),
        preview: apiEvent?.preview ?? null,
        background_image_url: apiEvent?.background_image_url ?? null,
        club: apiEvent?.club ?? null,
    };
}
function normalizeQueue(raw: any): UiQueueItem[] {
    const items = Array.isArray(raw?.items) ? raw.items : Array.isArray(raw) ? raw : [];

    return items.map((item: any, index: number) => {
        const trackId = String(
            item?.track_id ??
            item?.track?.track_id ??
            item?.track?.id ??
            item?.id ??
            index
        );

        return {
            id: String(item?.id ?? trackId),
            track: {
                id: trackId,
                title: item?.title ?? item?.track?.title ?? "Unknown title",
                artist: item?.artist ?? item?.track?.artist ?? "Unknown artist",
                source: item?.source ?? item?.track?.source ?? "custom",
                cover_url: item?.cover_url ?? item?.track?.cover_url ?? null,
                duration_sec: item?.duration_sec ?? item?.track?.duration_sec ?? null,
            },
            position: index + 1,
            status: index === 0 ? "playing" : "queued",
            votes_count: Number(item?.votes ?? item?.votes_count ?? item?.score ?? 0),
        };
    });
}

function normalizeSearch(raw: any): UiSearchResult[] {
    const items = Array.isArray(raw?.items) ? raw.items : Array.isArray(raw) ? raw : [];

    return items.map((item: any, index: number) => ({
        id: String(item?.track_id ?? item?.id ?? index),
        title: item?.title ?? "Unknown title",
        artist: item?.artist ?? "Unknown artist",
        cover_url: item?.cover_url ?? null,
        duration_sec: item?.duration_sec ?? null,
        source: item?.source ?? "search",
    }));
}

export function useEventData(clubSlug: string, token?: string | null) {
    const [event, setEvent] = useState<UiEvent | null>(null);
    const [queue, setQueue] = useState<UiQueueItem[]>([]);
    const [searchResults, setSearchResults] = useState<UiSearchResult[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSearching, setIsSearching] = useState(false);
    const [isSuggesting, setIsSuggesting] = useState(false);
    const [isVoting, setIsVoting] = useState<string | null>(null);

    const wsRef = useRef<WebSocket | null>(null);
    const searchTimeoutRef = useRef<number | null>(null);
    const lastSearchRef = useRef("");

    const fetchInitial = useCallback(async () => {
        setIsLoading(true);

        try {
            const [eventResponse, queueResponse] = await Promise.all([
                getEventByClubSlug(clubSlug, token ?? null),
                getEventQueue(clubSlug, 20, token ?? null),
            ]);

            const attendeesCount = Number(
                queueResponse?.attendees_count ??
                eventResponse?.attendees_count ??
                0
            );

            setEvent(normalizeEvent(eventResponse, clubSlug, attendeesCount));
            setQueue(normalizeQueue(queueResponse));
        } catch (error) {
            console.error("Failed to fetch event data:", error);
            setEvent(null);
            setQueue([]);
        } finally {
            setIsLoading(false);
        }
    }, [clubSlug, token]);

    useEffect(() => {
        void fetchInitial();
    }, [fetchInitial]);

    useEffect(() => {
        if (!event?.id) return;

        const ws = new WebSocket(createEventWsUrl(event.id));
        wsRef.current = ws;

        ws.onmessage = (ev) => {
            try {
                const msg = JSON.parse(ev.data);

                if (msg?.type === "queue_snapshot" && Array.isArray(msg?.items)) {
                    setQueue(normalizeQueue({ items: msg.items }));
                    return;
                }

                if (msg?.type === "queue_updated" && Array.isArray(msg?.items)) {
                    setQueue(normalizeQueue({ items: msg.items }));
                    return;
                }

                if (msg?.type === "track_added" && Array.isArray(msg?.items)) {
                    setQueue(normalizeQueue({ items: msg.items }));
                    return;
                }

                if (msg?.type === "track_voted" && msg?.track_id) {
                    const nextVotes = Number(msg?.votes);

                    setQueue((prev) =>
                        prev.map((item) =>
                            item.track.id === String(msg.track_id)
                                ? {
                                    ...item,
                                    votes_count: Number.isFinite(nextVotes)
                                        ? nextVotes
                                        : item.votes_count + 1,
                                }
                                : item
                        )
                    );
                }
            } catch (error) {
                console.error("Failed to parse WS message:", error);
            }
        };

        ws.onerror = (error) => {
            console.error("Event WS error:", error);
        };

        return () => {
            ws.close();
            wsRef.current = null;
        };
    }, [event?.id]);

    const nowPlaying = useMemo(
        () => queue.find((item) => item.status === "playing") ?? queue[0] ?? null,
        [queue]
    );

    const vote = useCallback(
        async (trackId: string) => {
            setIsVoting(trackId);

            try {
                await voteForTrack(clubSlug, { track_id: trackId }, token ?? null);

                setQueue((prev) =>
                    prev.map((item) =>
                        item.track.id === trackId
                            ? { ...item, votes_count: item.votes_count + 1 }
                            : item
                    )
                );
            } finally {
                setIsVoting(null);
            }
        },
        [clubSlug, token]
    );

    const search = useCallback(async (query: string) => {
        const trimmed = query.trim();

        if (searchTimeoutRef.current) {
            window.clearTimeout(searchTimeoutRef.current);
            searchTimeoutRef.current = null;
        }

        if (trimmed.length < 2) {
            lastSearchRef.current = "";
            setSearchResults([]);
            setIsSearching(false);
            return;
        }

        lastSearchRef.current = trimmed;
        setIsSearching(true);

        await new Promise<void>((resolve) => {
            searchTimeoutRef.current = window.setTimeout(() => resolve(), 250);
        });

        if (lastSearchRef.current !== trimmed) {
            return;
        }

        try {
            const response = await searchTracks(trimmed, 15);
            if (lastSearchRef.current === trimmed) {
                setSearchResults(normalizeSearch(response));
            }
        } catch (error) {
            console.error("Search failed:", error);
            if (lastSearchRef.current === trimmed) {
                setSearchResults([]);
            }
        } finally {
            if (lastSearchRef.current === trimmed) {
                setIsSearching(false);
            }
        }
    }, []);

    const suggest = useCallback(
        async (track: UiSearchResult) => {
            setIsSuggesting(true);

            try {
                await suggestTrack(
                    clubSlug,
                    {
                        track_id: track.id,
                        title: track.title,
                        artist: track.artist,
                        cover_url: track.cover_url ?? null,
                        duration_sec: track.duration_sec ?? null,
                    },
                    token ?? null
                );

                await fetchInitial();
            } finally {
                setIsSuggesting(false);
            }
        },
        [clubSlug, token, fetchInitial]
    );

    useEffect(() => {
        return () => {
            if (searchTimeoutRef.current) {
                window.clearTimeout(searchTimeoutRef.current);
            }
        };
    }, []);

    return {
        event,
        queue,
        nowPlaying,
        searchResults,
        isLoading,
        isSearching,
        isSuggesting,
        isVoting,
        refetch: fetchInitial,
        vote,
        search,
        suggest,
    };
}