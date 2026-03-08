import { GlassCard } from '@/components/shared/GlassCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { Radio, Calendar, Music, Users, BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';

const mockEvents = [
  { id: '1', name: 'Friday Night Vibes', status: 'active' as const, attendees: 47, votes: 342 },
  { id: '2', name: 'Saturday Beats', status: 'draft' as const, attendees: 0, votes: 0 },
];

const recentStats = [
  { label: 'Events Played', value: '12', icon: Calendar, color: 'text-secondary' },
  { label: 'Total Votes', value: '3,420', icon: BarChart3, color: 'text-primary' },
  { label: 'Tracks Played', value: '186', icon: Music, color: 'text-accent' },
  { label: 'Peak Attendees', value: '156', icon: Users, color: 'text-secondary' },
];

export default function DJDashboard() {
  return (
    <div className="p-4 sm:p-6 space-y-6 sm:space-y-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-display font-bold">Dashboard</h1>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {recentStats.map(({ label, value, icon: Icon, color }) => (
          <GlassCard key={label} className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
              <Icon className={`h-4 w-4 ${color}`} />
            </div>
            <p className="text-2xl font-display font-bold">{value}</p>
          </GlassCard>
        ))}
      </div>

      {/* Assigned Events */}
      <div className="space-y-4">
        <h2 className="text-lg font-display font-semibold">Your Events</h2>
        <div className="grid gap-3">
          {mockEvents.map((event) => (
            <GlassCard key={event.id} className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-medium truncate">{event.name}</h3>
                  <StatusBadge status={event.status} />
                </div>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1"><Users className="h-3 w-3" />{event.attendees} attendees</span>
                  <span className="flex items-center gap-1"><BarChart3 className="h-3 w-3" />{event.votes} votes</span>
                </div>
              </div>
              {event.status === 'active' && (
                <Button variant="magenta" size="sm" asChild>
                  <Link to={`/dj/event/${event.id}`}>
                    <Radio className="h-3.5 w-3.5 mr-1" /> Go Live
                  </Link>
                </Button>
              )}
            </GlassCard>
          ))}
        </div>
      </div>
    </div>
  );
}
