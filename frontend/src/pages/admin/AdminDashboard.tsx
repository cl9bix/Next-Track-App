import { GlassCard } from '@/components/shared/GlassCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { Plus, Users, Music, BarChart3, Calendar, Copy } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';

const mockEvents = [
  { id: '1', name: 'Friday Night Vibes', status: 'active' as const, votes: 342, attendees: 47, dj: 'DJ Pulse' },
  { id: '2', name: 'Saturday Beats', status: 'draft' as const, votes: 0, attendees: 0, dj: 'Unassigned' },
  { id: '3', name: 'Throwback Thursday', status: 'ended' as const, votes: 891, attendees: 112, dj: 'DJ Retro' },
];

const kpis = [
  { label: 'Total Events', value: '24', icon: Calendar, color: 'text-primary' },
  { label: 'Active Users', value: '1,247', icon: Users, color: 'text-secondary' },
  { label: 'Votes Cast', value: '12.4K', icon: BarChart3, color: 'text-accent' },
  { label: 'Tracks Played', value: '892', icon: Music, color: 'text-primary' },
];

export default function AdminDashboard() {
  const { toast } = useToast();

  const copyLink = (slug: string) => {
    navigator.clipboard.writeText(`${window.location.origin}/event/${slug}`);
    toast({ title: 'Link copied!' });
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 sm:space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-display font-bold">Dashboard</h1>
        <Button variant="glow" size="sm" asChild>
          <Link to="/admin/events/new"><Plus className="h-4 w-4 mr-1" /> New Event</Link>
        </Button>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map(({ label, value, icon: Icon, color }) => (
          <GlassCard key={label} className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
              <Icon className={`h-4 w-4 ${color}`} />
            </div>
            <p className="text-2xl font-display font-bold">{value}</p>
          </GlassCard>
        ))}
      </div>

      {/* Recent Events */}
      <div className="space-y-4">
        <h2 className="text-lg font-display font-semibold">Recent Events</h2>
        <div className="grid gap-3">
          {mockEvents.map((event) => (
            <GlassCard key={event.id} className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-medium truncate">{event.name}</h3>
                  <StatusBadge status={event.status} />
                </div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1"><Music className="h-3 w-3" />{event.dj}</span>
                  <span className="flex items-center gap-1"><Users className="h-3 w-3" />{event.attendees}</span>
                  <span className="flex items-center gap-1"><BarChart3 className="h-3 w-3" />{event.votes} votes</span>
                </div>
              </div>
              <div className="flex items-center gap-1 self-end sm:self-center">
                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => copyLink('friday-night')}>
                  <Copy className="h-3.5 w-3.5" />
                </Button>
                <Button variant="outline" size="sm" asChild>
                  <Link to={`/admin/events/${event.id}`}>Manage</Link>
                </Button>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    </div>
  );
}
