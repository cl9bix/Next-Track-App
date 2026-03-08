import { apiClient } from './client';
import type { Vote } from '@/types';

export const votesApi = {
  vote: (roundId: string, trackId: string) =>
    apiClient.post<Vote>(`/rounds/${roundId}/vote`, { track_id: trackId }).then(r => r.data),

  getMyVote: (roundId: string) =>
    apiClient.get<Vote | null>(`/rounds/${roundId}/my-vote`).then(r => r.data),
};
