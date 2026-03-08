import { cn } from '@/lib/utils';
import type { EventStatus, RoundStatus } from '@/types';

interface StatusBadgeProps {
  status: EventStatus | RoundStatus | string;
  className?: string;
}

const statusStyles: Record<string, string> = {
  active: 'bg-primary/20 text-primary border-primary/30',
  open: 'bg-primary/20 text-primary border-primary/30',
  voting: 'bg-secondary/20 text-secondary border-secondary/30',
  playing: 'bg-primary/20 text-primary border-primary/30 animate-pulse-glow',
  draft: 'bg-muted text-muted-foreground border-muted',
  paused: 'bg-accent/20 text-accent border-accent/30',
  ended: 'bg-muted text-muted-foreground border-muted',
  closed: 'bg-muted text-muted-foreground border-muted',
  pending: 'bg-accent/20 text-accent border-accent/30',
  accepted: 'bg-primary/20 text-primary border-primary/30',
  rejected: 'bg-destructive/20 text-destructive border-destructive/30',
  queued: 'bg-muted text-muted-foreground border-muted',
  played: 'bg-muted/50 text-muted-foreground/60 border-muted/30',
  skipped: 'bg-destructive/10 text-destructive/60 border-destructive/20',
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider',
        statusStyles[status] || 'bg-muted text-muted-foreground border-muted',
        className
      )}
    >
      {status}
    </span>
  );
}
