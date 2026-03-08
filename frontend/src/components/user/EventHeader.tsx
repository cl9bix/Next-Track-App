import type { Event } from '@/types';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Users, Music } from 'lucide-react';

interface EventHeaderProps {
  event: Event;
  attendees?: number;
}

export function EventHeader({ event, attendees = 0 }: EventHeaderProps) {
  return (
    <div className="glass-strong rounded-2xl p-5 space-y-3">
      <div className="flex items-center justify-between">
        <StatusBadge status={event.status} />
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <Users className="h-4 w-4" />
          <span>{attendees}</span>
        </div>
      </div>
      <h1 className="text-2xl font-display font-bold">{event.name}</h1>
      {event.dj_name && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Music className="h-4 w-4 text-primary" />
          <span>DJ {event.dj_name}</span>
        </div>
      )}
    </div>
  );
}
