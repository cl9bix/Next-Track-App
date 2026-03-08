import type { QueueItem } from '@/types';
import { GlassCard } from '@/components/shared/GlassCard';
import { Button } from '@/components/ui/button';
import { ThumbsUp, Music } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface QueueListProps {
  items: QueueItem[];
  votedTrackId?: string | null;
  onVote?: (trackId: string) => void;
  canVote?: boolean;
}

export function QueueList({ items, votedTrackId, onVote, canVote = false }: QueueListProps) {
  const queuedItems = items.filter(i => i.status === 'queued');

  if (queuedItems.length === 0) {
    return (
      <GlassCard className="text-center py-6">
        <p className="text-muted-foreground text-sm">Queue is empty</p>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-2">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground px-1">
        Up Next
      </h2>
      <AnimatePresence>
        {queuedItems.map((item, idx) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
            transition={{ delay: idx * 0.05 }}
          >
            <GlassCard className="flex items-center gap-3">
              <span className="text-xs font-bold text-muted-foreground w-6 text-center">
                {idx + 1}
              </span>
              {item.track.cover_url ? (
                <img src={item.track.cover_url} alt="" className="w-10 h-10 rounded-md object-cover" />
              ) : (
                <div className="w-10 h-10 rounded-md bg-muted flex items-center justify-center">
                  <Music className="h-4 w-4 text-muted-foreground" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{item.track.title}</p>
                <p className="text-xs text-muted-foreground truncate">{item.track.artist}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-primary font-bold">{item.votes_count}</span>
                {canVote && onVote && (
                  <Button
                    variant="vote"
                    size="icon"
                    className="h-8 w-8"
                    disabled={votedTrackId === item.track.id}
                    onClick={() => onVote(item.track.id)}
                  >
                    <ThumbsUp className={`h-3.5 w-3.5 ${votedTrackId === item.track.id ? 'fill-primary' : ''}`} />
                  </Button>
                )}
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
