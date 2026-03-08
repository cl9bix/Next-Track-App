import { GlassCard } from '@/components/shared/GlassCard';
import type { QueueItem } from '@/types';
import { motion } from 'framer-motion';
import { Volume2 } from 'lucide-react';

interface NowPlayingCardProps {
  item: QueueItem | null;
}

export function NowPlayingCard({ item }: NowPlayingCardProps) {
  if (!item) {
    return (
      <GlassCard className="text-center py-8">
        <p className="text-muted-foreground text-sm">No track playing</p>
      </GlassCard>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <GlassCard glow="cyan" className="relative overflow-hidden">
        <div className="flex items-center gap-4">
          {item.track.cover_url ? (
            <img
              src={item.track.cover_url}
              alt={item.track.title}
              className="w-16 h-16 rounded-lg object-cover"
            />
          ) : (
            <div className="w-16 h-16 rounded-lg bg-muted flex items-center justify-center">
              <Volume2 className="h-6 w-6 text-primary" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold uppercase tracking-wider text-primary mb-1">
              Now Playing
            </p>
            <h3 className="font-display font-bold text-lg truncate">{item.track.title}</h3>
            <p className="text-sm text-muted-foreground truncate">{item.track.artist}</p>
          </div>
        </div>
        {/* Animated equalizer bar */}
        <div className="absolute bottom-0 left-0 right-0 h-0.5 gradient-primary animate-pulse-glow" />
      </GlassCard>
    </motion.div>
  );
}
