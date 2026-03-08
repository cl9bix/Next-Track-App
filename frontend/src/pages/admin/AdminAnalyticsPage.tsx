import { GlassCard } from '@/components/shared/GlassCard';
import { BarChart3, TrendingUp, Users, Music, Calendar } from 'lucide-react';

const stats = [
  { label: 'Total Events', value: '24', change: '+3 this week', icon: Calendar, color: 'text-primary' },
  { label: 'Total Votes', value: '12,438', change: '+1.2K this week', icon: BarChart3, color: 'text-secondary' },
  { label: 'Unique Users', value: '1,247', change: '+89 this week', icon: Users, color: 'text-accent' },
  { label: 'Tracks Played', value: '892', change: '+47 this week', icon: Music, color: 'text-primary' },
];

const weeklyData = [
  { day: 'Mon', votes: 120 },
  { day: 'Tue', votes: 85 },
  { day: 'Wed', votes: 210 },
  { day: 'Thu', votes: 340 },
  { day: 'Fri', votes: 890 },
  { day: 'Sat', votes: 1200 },
  { day: 'Sun', votes: 560 },
];

const maxVotes = Math.max(...weeklyData.map((d) => d.votes));

export default function AdminAnalyticsPage() {
  return (
    <div className="p-4 sm:p-6 space-y-6 sm:space-y-8 max-w-7xl mx-auto">
      <h1 className="text-2xl font-display font-bold">Analytics</h1>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ label, value, change, icon: Icon, color }) => (
          <GlassCard key={label} className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
              <Icon className={`h-4 w-4 ${color}`} />
            </div>
            <p className="text-2xl font-display font-bold">{value}</p>
            <p className="text-xs text-primary flex items-center gap-1">
              <TrendingUp className="h-3 w-3" /> {change}
            </p>
          </GlassCard>
        ))}
      </div>

      {/* Simple bar chart */}
      <GlassCard className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Votes This Week
        </h2>
        <div className="flex items-end gap-2 h-40">
          {weeklyData.map((d) => (
            <div key={d.day} className="flex-1 flex flex-col items-center gap-1">
              <span className="text-xs text-muted-foreground">{d.votes}</span>
              <div
                className="w-full rounded-t-md bg-gradient-to-t from-primary/60 to-primary transition-all duration-500"
                style={{ height: `${(d.votes / maxVotes) * 100}%` }}
              />
              <span className="text-xs text-muted-foreground">{d.day}</span>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Top DJs */}
      <GlassCard className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Top DJs
        </h2>
        <div className="space-y-3">
          {[
            { name: 'DJ Pulse', events: 8, votes: 3420 },
            { name: 'DJ Retro', events: 6, votes: 2891 },
            { name: 'DJ Fuego', events: 5, votes: 2150 },
          ].map((dj, i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-secondary/20 flex items-center justify-center text-xs font-bold text-secondary">
                {i + 1}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">{dj.name}</p>
                <p className="text-xs text-muted-foreground">{dj.events} events • {dj.votes} votes</p>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
