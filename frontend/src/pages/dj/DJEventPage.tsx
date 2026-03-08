import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { GlassCard } from '@/components/shared/GlassCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Countdown } from '@/components/shared/Countdown';
import { Button } from '@/components/ui/button';
import { Play, Pause, SkipForward, Vote, Check, X, ThumbsUp, Clock, Trophy, Music } from 'lucide-react';

const mockQueue = [
  { id: '1', title: 'Blinding Lights', artist: 'The Weeknd', votes: 24, status: 'playing' },
  { id: '2', title: 'Levitating', artist: 'Dua Lipa', votes: 18, status: 'queued' },
  { id: '3', title: 'Save Your Tears', artist: 'The Weeknd', votes: 12, status: 'queued' },
  { id: '4', title: 'Heat Waves', artist: 'Glass Animals', votes: 8, status: 'queued' },
  { id: '5', title: 'Watermelon Sugar', artist: 'Harry Styles', votes: 5, status: 'queued' },
];

const mockSuggestions = [
  { id: 's1', title: 'As It Was', artist: 'Harry Styles', user: '@alex', status: 'pending' },
  { id: 's2', title: 'Anti-Hero', artist: 'Taylor Swift', user: '@maria', status: 'pending' },
  { id: 's3', title: 'Unholy', artist: 'Sam Smith', user: '@john', status: 'pending' },
];

const mockLiveVotes = [
  { user: '@alex', track: 'Levitating', time: '2s ago' },
  { user: '@maria', track: 'Save Your Tears', time: '5s ago' },
  { user: '@john', track: 'Levitating', time: '8s ago' },
  { user: '@kate', track: 'Heat Waves', time: '12s ago' },
];

export default function DJEventPage() {
  const { id } = useParams();
  const [roundStatus, setRoundStatus] = useState<'closed' | 'open' | 'voting'>('open');
  const [winner, setWinner] = useState<{ title: string; artist: string; votes: number } | null>(null);

  const handleCloseVoting = () => {
    setRoundStatus('closed');
    setWinner({ title: 'Levitating', artist: 'Dua Lipa', votes: 18 });
  };

  const handleStartWinner = () => {
    setWinner(null);
    setRoundStatus('closed');
  };

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6 max-w-7xl mx-auto">
      {/* Event header */}
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-xl sm:text-2xl font-display font-bold truncate">Friday Night Vibes</h1>
          <p className="text-sm text-muted-foreground">Event #{id} • 47 attendees online</p>
        </div>
        <StatusBadge status={roundStatus} />
      </div>

      {/* Winner announcement */}
      {winner && (
        <GlassCard glow="magenta" className="text-center space-y-3">
          <Trophy className="h-8 w-8 text-secondary mx-auto" />
          <div>
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Winner</p>
            <p className="text-xl font-display font-bold">{winner.title}</p>
            <p className="text-sm text-muted-foreground">{winner.artist} • {winner.votes} votes</p>
          </div>
          <Button variant="magenta" onClick={handleStartWinner}>
            <Play className="h-4 w-4 mr-1" /> Start Track
          </Button>
        </GlassCard>
      )}

      {/* Controls row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Round Controls */}
        <GlassCard glow="magenta" className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Round Controls
          </h2>
          <div className="flex flex-wrap gap-2">
            {roundStatus === 'closed' && (
              <Button variant="glow" onClick={() => setRoundStatus('open')}>
                <Vote className="h-4 w-4 mr-1" /> Open Round
              </Button>
            )}
            {roundStatus === 'open' && (
              <Button variant="magenta" onClick={() => setRoundStatus('voting')}>
                <Clock className="h-4 w-4 mr-1" /> Start Voting
              </Button>
            )}
            {roundStatus === 'voting' && (
              <>
                <Button variant="destructive" onClick={handleCloseVoting}>
                  Close Voting
                </Button>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  <Countdown
                    targetDate={new Date(Date.now() + 60000).toISOString()}
                    className="font-mono text-primary font-bold"
                  />
                </div>
              </>
            )}
          </div>
        </GlassCard>

        {/* Now Playing */}
        <GlassCard glow="cyan" className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Now Playing
          </h2>
          <div>
            <p className="font-display font-bold text-lg">Blinding Lights</p>
            <p className="text-sm text-muted-foreground">The Weeknd</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="icon"><Pause className="h-4 w-4" /></Button>
            <Button variant="glow" size="icon"><SkipForward className="h-4 w-4" /></Button>
          </div>
        </GlassCard>

        {/* Stats */}
        <GlassCard className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Live Stats
          </h2>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <p className="text-2xl font-display font-bold text-primary">47</p>
              <p className="text-xs text-muted-foreground">Online</p>
            </div>
            <div>
              <p className="text-2xl font-display font-bold text-secondary">342</p>
              <p className="text-xs text-muted-foreground">Votes</p>
            </div>
            <div>
              <p className="text-2xl font-display font-bold text-accent">6</p>
              <p className="text-xs text-muted-foreground">Rounds</p>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Three-column layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Live Queue */}
        <div className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Live Queue
          </h2>
          {mockQueue.map((track) => (
            <GlassCard key={track.id} className="flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-sm truncate">{track.title}</p>
                  {track.status === 'playing' && <StatusBadge status="playing" />}
                </div>
                <p className="text-xs text-muted-foreground">{track.artist}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-primary font-bold flex items-center gap-1">
                  <ThumbsUp className="h-3 w-3" /> {track.votes}
                </span>
                {track.status === 'queued' && (
                  <Button variant="glow" size="sm">
                    <Play className="h-3 w-3 mr-1" /> Play
                  </Button>
                )}
              </div>
            </GlassCard>
          ))}
        </div>

        {/* Suggestions */}
        <div className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Suggestions ({mockSuggestions.length})
          </h2>
          {mockSuggestions.map((s) => (
            <GlassCard key={s.id} className="flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{s.title}</p>
                <p className="text-xs text-muted-foreground">{s.artist} • {s.user}</p>
              </div>
              <div className="flex gap-1">
                <Button variant="glow" size="icon" className="h-8 w-8">
                  <Check className="h-3.5 w-3.5" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive">
                  <X className="h-3.5 w-3.5" />
                </Button>
              </div>
            </GlassCard>
          ))}
          {mockSuggestions.length === 0 && (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No pending suggestions
            </div>
          )}
        </div>

        {/* Live Votes Feed */}
        <div className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Live Votes
          </h2>
          {mockLiveVotes.map((v, i) => (
            <GlassCard key={i} className="flex items-center gap-3 py-3">
              <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
                {v.user[1]?.toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm">
                  <span className="font-medium">{v.user}</span>
                  <span className="text-muted-foreground"> voted for </span>
                  <span className="text-primary font-medium">{v.track}</span>
                </p>
              </div>
              <span className="text-xs text-muted-foreground">{v.time}</span>
            </GlassCard>
          ))}
        </div>
      </div>
    </div>
  );
}
