import { apiRequest } from './client';

export type AdminClub = {
    id: number;
    name: string;
    slug: string;
};

export type AdminMe = {
    id: number;
    username: string;
    display_name?: string | null;
    telegram_id?: number | null;
    role: string;
    is_active: boolean;
    max_club_count: number;
    clubs: AdminClub[];
};

export type DashboardAdmin = {
    id: number;
    username: string;
    display_name?: string | null;
    telegram_id?: number | null;
    role: string;
    club_id: number;
    is_active: boolean;
};

export type AdminEvent = {
    id: number;
    club_id: number;
    title: string;
    preview?: string | null;
    start_date?: string | null;
    end_date?: string | null;
    created_at: string;
    dj_ids: number[];
};

export type DashboardResponse = {
    admin: DashboardAdmin;
    club: AdminClub;
    total_events: number;
    live_events: number;
    upcoming_events: number;
    recent_events: AdminEvent[];
};

export type CreateEventPayload = {
    title: string;
    preview?: string | null;
    start_date?: string | null;
    end_date?: string | null;
    dj_ids?: number[];
};

export type UpdateEventPayload = Partial<CreateEventPayload>;

export type ClubSettingsResponse = {
    club: {
        id: number;
        name: string | null;
        slug: string | null;
    };
    settings: {
        description: string | null;
        background_image_url?: string | null;
        max_suggestions_per_user: number;
        voting_duration_sec: number;
        allow_explicit: boolean;
        auto_play: boolean;
    };
};

export type UpdateClubSettingsPayload = {
    name?: string;
    slug?: string;
    description?: string | null;
    background_image_url?: string | null;
    max_suggestions_per_user?: number;
    voting_duration_sec?: number;
    allow_explicit?: boolean;
    auto_play?: boolean;
};

function withClubQuery(path: string, clubId?: number): string {
    if (!clubId) {
        return path;
    }

    const separator = path.includes('?') ? '&' : '?';
    return `${path}${separator}club_id=${clubId}`;
}

export async function getAdminDashboard(clubId?: number): Promise<DashboardResponse> {
    return apiRequest<DashboardResponse>(withClubQuery('/api/v1/admin/dashboard', clubId), {
        method: 'GET',
    });
}

export async function getAdminMe(): Promise<AdminMe> {
    return apiRequest<AdminMe>('/api/v1/admin/me', {
        method: 'GET',
    });
}

export async function listAdminEvents(clubId?: number): Promise<AdminEvent[]> {
    return apiRequest<AdminEvent[]>(withClubQuery('/api/v1/admin/events', clubId), {
        method: 'GET',
    });
}

export async function getAdminEvent(
    eventId: string | number,
    clubId?: number
): Promise<AdminEvent> {
    return apiRequest<AdminEvent>(
        withClubQuery(`/api/v1/admin/events/${eventId}`, clubId),
        {
            method: 'GET',
        }
    );
}

export async function createAdminEvent(
    payload: CreateEventPayload,
    clubId?: number
): Promise<AdminEvent> {
    return apiRequest<AdminEvent>(withClubQuery('/api/v1/admin/events', clubId), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });
}

export async function updateAdminEvent(
    eventId: string | number,
    payload: UpdateEventPayload,
    clubId?: number
): Promise<AdminEvent> {
    return apiRequest<AdminEvent>(
        withClubQuery(`/api/v1/admin/events/${eventId}`, clubId),
        {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        }
    );
}

export async function endAdminEvent(eventId: string | number, clubId?: number) {
    return apiRequest<{ status: string; event_id: number; end_date: string | null }>(
        withClubQuery(`/api/v1/admin/events/${eventId}/end`, clubId),
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        }
    );
}

export async function deleteAdminEvent(eventId: string | number, clubId?: number) {
    return apiRequest<{ status: string; deleted_id: number }>(
        withClubQuery(`/api/v1/admin/events/${eventId}`, clubId),
        {
            method: 'DELETE',
        }
    );
}

export async function getClubSettings(clubId?: number): Promise<ClubSettingsResponse> {
    return apiRequest<ClubSettingsResponse>(
        withClubQuery('/api/v1/admin/club-settings', clubId),
        {
            method: 'GET',
        }
    );
}

export async function updateClubSettings(
    payload: UpdateClubSettingsPayload,
    clubId?: number
) {
    return apiRequest<{ status: string }>(
        withClubQuery('/api/v1/admin/club-settings', clubId),
        {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        }
    );
}