export type AdminLoginResponse = {
    status?: string;
    success?: boolean;
    access_token?: string;
    token_type?: string;
    admin?: {
        id: number;
        username: string;
        display_name?: string | null;
        telegram_id?: number | null;
        role: string;
        is_active: boolean;
        max_club_count?: number;
        clubs?: Array<{
            id: number;
            name: string;
            slug: string;
        }>;
    };
};

export type EventResponse = {
    id: number;
    club_id: number;
    title: string;
    preview?: string | null;
    start_date?: string | null;
    end_date?: string | null;
    created_at?: string;
    slug?: string;
    attendees_count?: number;
    background_image_url?: string | null;
    club?: {
        id: number;
        name: string;
        slug: string;
    } | null;
};

export type QueueTrack = {
    id?: string;
    track_id?: string;
    title?: string;
    artist?: string;
    cover_url?: string | null;
    duration_sec?: number | null;
    source?: string;
};

export type QueueItemApi = {
    id?: string | number;
    track_id?: string;
    title?: string;
    artist?: string;
    cover_url?: string | null;
    duration_sec?: number | null;
    votes?: number;
    votes_count?: number;
    score?: number;
    status?: string;
    suggested_by?: number | null;
    created_at?: number;
    track?: QueueTrack;
};

export type SearchResultApi = {
    id?: string;
    track_id?: string;
    title?: string;
    artist?: string;
    album?: string;
    cover_url?: string | null;
    duration_sec?: number | null;
    source?: string;
};

export type VotePayload = {
    track_id: string;
};

export type SuggestPayload = {
    track_id: string;
    title: string;
    artist?: string | null;
    cover_url?: string | null;
    duration_sec?: number | null;
    telegram_id?: number | null;
};