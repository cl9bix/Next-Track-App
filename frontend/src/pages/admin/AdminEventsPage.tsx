import { useEffect, useMemo, useState } from 'react';
import { GlassCard } from '@/components/shared/GlassCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Search, Users, BarChart3, Music, Copy, Square, Trash2 } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import {
    deleteAdminEvent,
    endAdminEvent,
    getAdminDashboard,
    listAdminEvents,
    type AdminEvent,
} from '@/services/api/admin';

type FilterStatus = 'all' | 'active' | 'draft' | 'ended';

type EventCard = {
    id: string;
    name: string;
    slug: string;
    status: 'active' | 'draft' | 'ended';
    votes: number;
    attendees: number;
    dj: string;
    date: string;
};

function mapEventStatus(event: AdminEvent): 'active' | 'draft' | 'ended' {
    const now = Date.now();
    const start = event.start_date ? new Date(event.start_date).getTime() : 0;
    const end = event.end_date ? new Date(event.end_date).getTime() : 0;

    if (end && now > end) return 'ended';
    if (start && now >= start && (!end || now <= end)) return 'active';
    return 'draft';
}

function mapEventCard(event: AdminEvent, clubSlug: string): EventCard {
    return {
        id: String(event.id),
        name: event.title,
        slug: clubSlug,
        status: mapEventStatus(event),
        votes: 0,
        attendees: 0,
        dj: event.dj_ids?.length ? `Assigned DJs: ${event.dj_ids.length}` : 'Unassigned',
        date: event.start_date ? new Date(event.start_date).toLocaleDateString() : '—',
    };
}

export default function AdminEventsPage() {
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState<FilterStatus>('all');
    const [clubSlug, setClubSlug] = useState('');
    const [events, setEvents] = useState<EventCard[]>([]);
    const [loading, setLoading] = useState(true);

    const { toast } = useToast();
    const navigate = useNavigate();

    useEffect(() => {
        let mounted = true;

        async function load() {
            try {
                setLoading(true);

                const [dashboard, rawEvents] = await Promise.all([
                    getAdminDashboard(),
                    listAdminEvents(),
                ]);

                if (!mounted) return;

                setClubSlug(dashboard.club.slug);
                setEvents(rawEvents.map((event) => mapEventCard(event, dashboard.club.slug)));
            } catch (error) {
                console.error(error);
                toast({
                    title: 'Failed to load events',
                    description: 'Please log in again.',
                });
                navigate('/admin/login');
            } finally {
                if (mounted) setLoading(false);
            }
        }

        load();
        return () => {
            mounted = false;
        };
    }, [navigate, toast]);

    const filtered = useMemo(() => {
        return events.filter((e) => {
            const matchSearch = e.name.toLowerCase().includes(search.toLowerCase());
            const matchFilter = filter === 'all' || e.status === filter;
            return matchSearch && matchFilter;
        });
    }, [events, search, filter]);

    const filters: { label: string; value: FilterStatus }[] = [
        { label: 'All', value: 'all' },
        { label: 'Active', value: 'active' },
        { label: 'Draft', value: 'draft' },
        { label: 'Ended', value: 'ended' },
    ];

    const copyLink = async (eventId: string) => {
        await navigator.clipboard.writeText(`${window.location.origin}/event/${clubSlug}?event=${eventId}`);
        toast({ title: 'Link copied!' });
    };

    const handleEnd = async (eventId: string) => {
        try {
            await endAdminEvent(eventId);
            setEvents((prev) =>
                prev.map((event) =>
                    event.id === eventId ? { ...event, status: 'ended' } : event
                )
            );
            toast({ title: 'Event ended' });
        } catch (error) {
            console.error(error);
            toast({ title: 'Failed to end event' });
        }
    };

    const handleDelete = async (eventId: string) => {
        try {
            await deleteAdminEvent(eventId);
            setEvents((prev) => prev.filter((event) => event.id !== eventId));
            toast({ title: 'Event deleted' });
        } catch (error) {
            console.error(error);
            toast({ title: 'Failed to delete event' });
        }
    };

    return (
        <div className="p-4 sm:p-6 space-y-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-display font-bold">Events</h1>
                <Button variant="glow" size="sm" asChild>
                    <Link to="/admin/events/new">
                        <Plus className="h-4 w-4 mr-1" /> New Event
                    </Link>
                </Button>
            </div>

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

            <div className="grid gap-3">
                {!loading && filtered.map((event) => (
                    <GlassCard key={event.id} className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-medium truncate">{event.name}</h3>
                                <StatusBadge status={event.status} />
                            </div>

                            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                                <span>{event.date}</span>
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
                            {event.status === 'active' && (
                                <Button variant="destructive" size="sm" onClick={() => handleEnd(event.id)}>
                                    <Square className="h-3 w-3 mr-1" /> End
                                </Button>
                            )}

                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8"
                                onClick={() => copyLink(event.id)}
                            >
                                <Copy className="h-3.5 w-3.5" />
                            </Button>

                            <Button variant="outline" size="sm" asChild>
                                <Link to={`/admin/events/${event.id}`}>Manage</Link>
                            </Button>

                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-destructive"
                                onClick={() => handleDelete(event.id)}
                            >
                                <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                        </div>
                    </GlassCard>
                ))}

                {!loading && filtered.length === 0 && (
                    <div className="text-center py-12 text-muted-foreground">
                        <p>No events found</p>
                    </div>
                )}

                {loading && (
                    <GlassCard>
                        <p className="text-sm text-muted-foreground">Loading events...</p>
                    </GlassCard>
                )}
            </div>
        </div>
    );
}