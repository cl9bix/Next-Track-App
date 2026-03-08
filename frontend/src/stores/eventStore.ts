import { create } from 'zustand';
import type { Event, Round, QueueItem } from '@/types';

interface EventStore {
  currentEvent: Event | null;
  currentRound: Round | null;
  queue: QueueItem[];
  nowPlaying: QueueItem | null;
  setEvent: (event: Event) => void;
  setRound: (round: Round | null) => void;
  setQueue: (queue: QueueItem[]) => void;
  setNowPlaying: (item: QueueItem | null) => void;
  reset: () => void;
}

export const useEventStore = create<EventStore>((set) => ({
  currentEvent: null,
  currentRound: null,
  queue: [],
  nowPlaying: null,

  setEvent: (event) => set({ currentEvent: event }),
  setRound: (round) => set({ currentRound: round }),
  setQueue: (queue) => set({ queue }),
  setNowPlaying: (item) => set({ nowPlaying: item }),
  reset: () => set({ currentEvent: null, currentRound: null, queue: [], nowPlaying: null }),
}));
