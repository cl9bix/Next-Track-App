import { useEffect, useMemo, useState } from 'react';
import { GlassCard } from '@/components/shared/GlassCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { Plus, Users, Music, BarChart3, Calendar, Copy } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { getAdminDashboard, type AdminEvent } from '@/services/api/admin';

type EventCardStatus = 'active' | 'draft' | 'ended';

type DashboardEventCard = {
    id: string;
    name: string;
    slug: string;
    status: EventCardStatus;
    votes: number;
    attendees: number;
    dj: string;
};

function mapEventStatus(event: AdminEvent): EventCardStatus {
    const now = Date.now();
    const start = event.start_date ? new Date(event.start_date).getTime() : 0;
    const end = event.end_date ? new Date(event.end_date).getTime() : 0;

    if (end && now > end) return 'ended';
    if (start && now >= start && (!end || now <= end)) return 'active';
    return 'draft';
}

function mapDashboardEvent(event: AdminEvent, clubSlug?: string): DashboardEventCard {
    return {
        id: String(event.id),
        name: event.title,
        slug: clubSlug ? `${clubSlug}?event=${event.id}` : String(event.id),
        status: mapEventStatus(event),
        votes: 0,
        attendees: 0,
        dj: event.dj_ids?.length ? `Assigned DJs: ${event.dj_ids.length}` : 'Unassigned',
    };
}

export default function AdminDashboard() {
    const { toast } = useToast();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [clubName, setClubName] = useState('Your club');
    const [clubSlug, setClubSlug] = useState<string>('');
    const [events, setEvents] = useState<DashboardEventCard[]>([]);
    const [kpis, setKpis] = useState({
        total_events: 0,
        live_events: 0,
        upcoming_events: 0,
    });

    useEffect(() => {
        let mounted = true;

        async function loadDashboard() {
            try {
                setLoading(true);
                const data = await getAdminDashboard();

                if (!mounted) return;

                setClubName(data.club.name);
                setClubSlug(data.club.slug);
                setKpis({
                    total_events: data.total_events,
                    live_events: data.live_events,
                    upcoming_events: data.upcoming_events,
                });
                setEvents(data.recent_events.map((event) => mapDashboardEvent(event, data.club.slug)));
            } catch (error) {
                console.error(error);
                toast({
                    title: 'Failed to load dashboard',
                    description: 'Please log in again.',
                });
                navigate('/admin/login');
            } finally {
                if (mounted) setLoading(false);
            }
        }

        loadDashboard();
        return () => {
            mounted = false;
        };
    }, [navigate, toast]);

    const uiKpis = useMemo(
        () => [
            { label: 'Total Events', value: String(kpis.total_events), icon: Calendar, color: 'text-primary' },
            { label: 'Live Events', value: String(kpis.live_events), icon: Users, color: 'text-secondary' },
            { label: 'Upcoming', value: String(kpis.upcoming_events), icon: BarChart3, color: 'text-accent' },
            { label: 'Recent Loaded', value: String(events.length), icon: Music, color: 'text-primary' },
        ],
        [events.length, kpis]
    );

    const copyLink = async (eventId: string) => {
        const link = `${window.location.origin}/event/${clubSlug}?event=${eventId}`;
        await navigator.clipboard.writeText(link);
        toast({ title: 'Link copied!' });
    };

    return (
        <div className="p-4 sm:p-6 space-y-6 sm:space-y-8 max-w-7xl mx-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-display font-bold">Dashboard</h1>
                    <p className="text-sm text-muted-foreground">{clubName}</p>
                </div>

                <Button variant="glow" size="sm" asChild>
                    <Link to="/admin/events/new">
                        <Plus className="h-4 w-4 mr-1" /> New Event
                    </Link>
                </Button>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {uiKpis.map(({ label, value, icon: Icon, color }) => (
                    <GlassCard key={label} className="space-y-2">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
                            <Icon className={`h-4 w-4 ${color}`} />
                        </div>
                        <p className="text-2xl font-display font-bold">{loading ? '—' : value}</p>
                    </GlassCard>
                ))}
            </div>

            <div className="space-y-4">
                <h2 className="text-lg font-display font-semibold">Recent Events</h2>

                <div className="grid gap-3">
                    {!loading && events.length === 0 && (
                        <GlassCard>
                            <p className="text-sm text-muted-foreground">No events yet.</p>
                        </GlassCard>
                    )}

                    {events.map((event) => (
                        <GlassCard key={event.id} className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <h3 className="font-medium truncate">{event.name}</h3>
                                    <StatusBadge status={event.status} />
                                </div>

                                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Music className="h-3 w-3" />
                      {event.dj}
                  </span>
                                    <span className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                                        {event.attendees}
                  </span>
                                    <span className="flex items-center gap-1">
                    <BarChart3 className="h-3 w-3" />
                                        {event.votes} votes
                  </span>
                                </div>
                            </div>

                            <div className="flex items-center gap-1 self-end sm:self-center">
                                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => copyLink(event.id)}>
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