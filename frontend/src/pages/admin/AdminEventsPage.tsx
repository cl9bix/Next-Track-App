import { useState } from 'react';
import { GlassCard } from '@/components/shared/GlassCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Search, Users, BarChart3, Music, Copy, Play, Square, Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';

const mockEvents = [
  { id: '1', name: 'Friday Night Vibes', slug: 'friday-night', status: 'active' as const, votes: 342, attendees: 47, dj: 'DJ Pulse', date: '2025-03-07' },
  { id: '2', name: 'Saturday Beats', slug: 'saturday-beats', status: 'draft' as const, votes: 0, attendees: 0, dj: 'Unassigned', date: '2025-03-08' },
  { id: '3', name: 'Throwback Thursday', slug: 'throwback-thursday', status: 'ended' as const, votes: 891, attendees: 112, dj: 'DJ Retro', date: '2025-03-06' },
  { id: '4', name: 'Sunday Chill', slug: 'sunday-chill', status: 'draft' as const, votes: 0, attendees: 0, dj: 'Unassigned', date: '2025-03-09' },
  { id: '5', name: 'Latin Heat Night', slug: 'latin-heat', status: 'ended' as const, votes: 564, attendees: 85, dj: 'DJ Fuego', date: '2025-03-05' },
];

type FilterStatus = 'all' | 'active' | 'draft' | 'ended';

export default function AdminEventsPage() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<FilterStatus>('all');
  const { toast } = useToast();

  const filtered = mockEvents.filter((e) => {
    const matchSearch = e.name.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === 'all' || e.status === filter;
    return matchSearch && matchFilter;
  });

  const filters: { label: string; value: FilterStatus }[] = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Draft', value: 'draft' },
    { label: 'Ended', value: 'ended' },
  ];

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-display font-bold">Events</h1>
        <Button variant="glow" size="sm" asChild>
          <Link to="/admin/events/new"><Plus className="h-4 w-4 mr-1" /> New Event</Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search events..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 bg-card/60 border-border/50"
          />
        </div>
        <div className="flex gap-1">
          {filters.map((f) => (
            <Button
              key={f.value}
              variant={filter === f.value ? 'glow' : 'ghost'}
              size="sm"
              onClick={() => setFilter(f.value)}
            >
              {f.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Events list */}
      <div className="grid gap-3">
        {filtered.map((event) => (
          <GlassCard key={event.id} className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-medium truncate">{event.name}</h3>
                <StatusBadge status={event.status} />
              </div>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                <span>{event.date}</span>
                <span className="flex items-center gap-1"><Music className="h-3 w-3" />{event.dj}</span>
                <span className="flex items-center gap-1"><Users className="h-3 w-3" />{event.attendees}</span>
                <span className="flex items-center gap-1"><BarChart3 className="h-3 w-3" />{event.votes} votes</span>
              </div>
            </div>
            <div className="flex items-center gap-1 self-end sm:self-center">
              {event.status === 'draft' && (
                <Button variant="glow" size="sm">
                  <Play className="h-3 w-3 mr-1" /> Start
                </Button>
              )}
              {event.status === 'active' && (
                <Button variant="destructive" size="sm">
                  <Square className="h-3 w-3 mr-1" /> End
                </Button>
              )}
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => {
                  navigator.clipboard.writeText(`${window.location.origin}/event/${event.slug}`);
                  toast({ title: 'Link copied!' });
                }}
              >
                <Copy className="h-3.5 w-3.5" />
              </Button>
              <Button variant="outline" size="sm" asChild>
                <Link to={`/admin/events/${event.id}`}>Manage</Link>
              </Button>
            </div>
          </GlassCard>
        ))}
        {filtered.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            <p>No events found</p>
          </div>
        )}
      </div>
    </div>
  );
}
