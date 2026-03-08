import { useParams, useNavigate } from 'react-router-dom';
import { GlassCard } from '@/components/shared/GlassCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Users, BarChart3, Music, Copy, Play, Square, Share2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const mockEvent = {
  id: '1', name: 'Friday Night Vibes', slug: 'friday-night', status: 'active' as const,
  dj: 'DJ Pulse', attendees: 47, totalVotes: 342, totalTracks: 18, totalRounds: 6,
  createdAt: '2025-03-07T20:00:00Z',
};

const mockTopTracks = [
  { title: 'Blinding Lights', artist: 'The Weeknd', votes: 24 },
  { title: 'Levitating', artist: 'Dua Lipa', votes: 18 },
  { title: 'Save Your Tears', artist: 'The Weeknd', votes: 12 },
  { title: 'Heat Waves', artist: 'Glass Animals', votes: 8 },
  { title: 'Watermelon Sugar', artist: 'Harry Styles', votes: 5 },
];

export default function EventDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();

  const copyLink = () => {
    navigator.clipboard.writeText(`${window.location.origin}/event/${mockEvent.slug}`);
    toast({ title: 'Link copied!' });
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <Button variant="ghost" size="icon" className="shrink-0" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-display font-bold truncate">{mockEvent.name}</h1>
              <StatusBadge status={mockEvent.status} />
            </div>
            <p className="text-sm text-muted-foreground">DJ: {mockEvent.dj}</p>
          </div>
        </div>
        <div className="flex gap-2 self-end sm:self-center">
          <Button variant="glass" size="sm" onClick={copyLink}>
            <Share2 className="h-3.5 w-3.5 mr-1" /> Share
          </Button>
          {mockEvent.status === 'active' ? (
            <Button variant="destructive" size="sm"><Square className="h-3 w-3 mr-1" /> End Event</Button>
          ) : mockEvent.status === 'draft' ? (
            <Button variant="glow" size="sm"><Play className="h-3 w-3 mr-1" /> Start Event</Button>
          ) : null}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Attendees', value: mockEvent.attendees, icon: Users, color: 'text-primary' },
          { label: 'Total Votes', value: mockEvent.totalVotes, icon: BarChart3, color: 'text-secondary' },
          { label: 'Tracks Played', value: mockEvent.totalTracks, icon: Music, color: 'text-accent' },
          { label: 'Rounds', value: mockEvent.totalRounds, icon: BarChart3, color: 'text-primary' },
        ].map(({ label, value, icon: Icon, color }) => (
          <GlassCard key={label} className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
              <Icon className={`h-4 w-4 ${color}`} />
            </div>
            <p className="text-2xl font-display font-bold">{value}</p>
          </GlassCard>
        ))}
      </div>

      {/* Top Tracks */}
      <GlassCard className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Top Tracks
        </h2>
        <div className="space-y-2">
          {mockTopTracks.map((track, i) => (
            <div key={i} className="flex items-center gap-3 py-2 border-b border-border/30 last:border-0">
              <span className="w-6 text-center text-xs font-bold text-muted-foreground">
                {i + 1}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{track.title}</p>
                <p className="text-xs text-muted-foreground">{track.artist}</p>
              </div>
              <span className="text-xs text-primary font-bold">{track.votes} votes</span>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
