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

function normalizeEvent(apiEvent: any, clubSlug: string): UiEvent {
  return {
    id: String(apiEvent.id),
    club_id: String(apiEvent.club_id),
    name: apiEvent.title ?? "Untitled Event",
    slug: clubSlug,
    status: "active",
    created_at: apiEvent.start_date ?? new Date().toISOString(),
  };
}

function normalizeQueue(raw: any): UiQueueItem[] {
  const items = Array.isArray(raw?.items) ? raw.items : [];

  return items.map((item: any, index: number) => {
    const trackId = String(item.track_id ?? item.track?.track_id ?? item.track?.id ?? item.id ?? index);

    return {
      id: String(item.id ?? trackId),
      track: {
        id: trackId,
        title: item.title ?? item.track?.title ?? "Unknown title",
        artist: item.artist ?? item.track?.artist ?? "Unknown artist",
        source: item.track?.source ?? item.source ?? "custom",
        cover_url: item.cover_url ?? item.track?.cover_url ?? null,
        duration_sec: item.duration_sec ?? item.track?.duration_sec ?? null,
      },
      position: index + 1,
      status: index === 0 ? "playing" : "queued",
      votes_count: Number(item.votes ?? item.votes_count ?? item.score ?? 0),
    };
  });
}

function normalizeSearch(raw: any): UiSearchResult[] {
  const items = Array.isArray(raw) ? raw : [];

  return items.map((item: any, index: number) => ({
    id: String(item.track_id ?? item.id ?? index),
    title: item.title ?? "Unknown title",
    artist: item.artist ?? "Unknown artist",
    cover_url: item.cover_url ?? null,
    duration_sec: item.duration_sec ?? null,
    source: item.source ?? "search",
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

  const fetchInitial = useCallback(async () => {
    setIsLoading(true);

    try {
      const [eventResponse, queueResponse] = await Promise.all([
        getEventByClubSlug(clubSlug),
        getEventQueue(clubSlug, 20),
      ]);

      const normalizedEvent = normalizeEvent(eventResponse, clubSlug);
      setEvent(normalizedEvent);
      setQueue(normalizeQueue(queueResponse));
    } finally {
      setIsLoading(false);
    }
  }, [clubSlug]);

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

        if (msg?.type === "queue_snapshot" && Array.isArray(msg.items)) {
          setQueue(normalizeQueue({ items: msg.items }));
          return;
        }

        if (msg?.type === "queue_updated" && Array.isArray(msg.items)) {
          setQueue(normalizeQueue({ items: msg.items }));
          return;
        }

        if (msg?.type === "track_voted" && msg.track_id) {
          setQueue((prev) =>
            prev.map((item) =>
              item.track.id === String(msg.track_id)
                ? { ...item, votes_count: Number(msg.votes ?? item.votes_count + 1) }
                : item
            )
          );
        }
      } catch {
      }
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
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);

    try {
      const response = await searchTracks(query, 15);
      setSearchResults(normalizeSearch(response));
    } finally {
      setIsSearching(false);
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