export type AdminLoginResponse = {
  success?: boolean;
};

export type EventResponse = {
  id: number;
  club_id: number;
  title: string;
  preview?: string | null;
  start_date?: string | null;
  end_date?: string | null;
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
  track?: QueueTrack;
};

export type SearchResultApi = {
  id?: string;
  track_id?: string;
  title?: string;
  artist?: string;
  cover_url?: string | null;
  duration_sec?: number | null;
  source?: string;
};

export type VotePayload = {
  track_id: string;
};

export type SuggestPayload = {
  track_id?: string | null;
  title: string;
  artist?: string | null;
  cover_url?: string | null;
  duration_sec?: number | null;
};