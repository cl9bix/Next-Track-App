// ============================================
// Next Track — Shared TypeScript Types
// ============================================

// --- Roles ---
export type UserRole = 'user' | 'dj' | 'admin' | 'owner';

// --- Auth ---
export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  language_code?: string;
}

export interface AuthState {
  token: string | null;
  role: UserRole | null;
  user: TelegramUser | null;
  isAuthenticated: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
}

// --- Club ---
export interface Club {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  description?: string;
  settings: ClubSettings;
  created_at: string;
}

export interface ClubSettings {
  max_suggestions_per_user: number;
  voting_duration_seconds: number;
  allow_explicit: boolean;
  auto_play: boolean;
}

// --- Event ---
export type EventStatus = 'draft' | 'active' | 'paused' | 'ended';

export interface Event {
  id: string;
  club_id: string;
  name: string;
  slug: string;
  status: EventStatus;
  dj_id?: string;
  dj_name?: string;
  current_round?: Round;
  created_at: string;
  started_at?: string;
  ended_at?: string;
}

export interface EventSummary {
  id: string;
  name: string;
  status: EventStatus;
  total_votes: number;
  total_suggestions: number;
  attendees: number;
}

// --- Round ---
export type RoundStatus = 'open' | 'voting' | 'closed' | 'playing';

export interface Round {
  id: string;
  event_id: string;
  number: number;
  status: RoundStatus;
  tracks: Track[];
  winner?: Track;
  voting_ends_at?: string;
  created_at: string;
}

// --- Track ---
export interface Track {
  id: string;
  title: string;
  artist: string;
  album?: string;
  cover_url?: string;
  preview_url?: string;
  duration_ms?: number;
  external_id?: string;
  source: 'deezer' | 'itunes' | 'manual';
}

// --- Queue ---
export interface QueueItem {
  id: string;
  track: Track;
  position: number;
  status: 'queued' | 'playing' | 'played' | 'skipped';
  votes_count: number;
  added_at: string;
  played_at?: string;
}

// --- Vote ---
export interface Vote {
  id: string;
  user_id: number;
  track_id: string;
  round_id: string;
  created_at: string;
}

// --- Suggestion ---
export interface Suggestion {
  id: string;
  track: Track;
  user_id: number;
  user_name: string;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
}

// --- Search ---
export interface SearchResult {
  id: string;
  title: string;
  artist: string;
  album?: string;
  cover_url?: string;
  preview_url?: string;
  source: 'deezer' | 'itunes';
}

// --- WebSocket ---
export type WSEventType =
  | 'voting_open'
  | 'voting_closed'
  | 'vote'
  | 'queue_added'
  | 'queue_updated'
  | 'track_started'
  | 'track_finished'
  | 'suggestion_added'
  | 'suggestion_accepted'
  | 'suggestion_rejected'
  | 'event_started'
  | 'event_ended'
  | 'round_created'
  | 'round_closed'
  | 'attendee_joined'
  | 'attendee_left';

export interface WSMessage<T = unknown> {
  type: WSEventType;
  payload: T;
  timestamp: string;
}

// --- Analytics ---
export interface EventAnalytics {
  total_votes: number;
  total_suggestions: number;
  total_rounds: number;
  peak_attendees: number;
  top_tracks: Array<{ track: Track; votes: number }>;
  votes_timeline: Array<{ time: string; count: number }>;
}

// --- API ---
export interface ApiError {
  detail: string;
  status_code: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
}
