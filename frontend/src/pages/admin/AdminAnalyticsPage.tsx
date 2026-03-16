import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { GlassCard } from '@/components/shared/GlassCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Users, BarChart3, Music, Square, Share2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { endAdminEvent, getAdminDashboard, getAdminEvent, type AdminEvent } from '@/services/api/admin';

type EventStatus = 'active' | 'draft' | 'ended';

function mapEventStatus(event: AdminEvent): EventStatus {
    const now = Date.now();
    const start = event.start_date ? new Date(event.start_date).getTime() : 0;
    const end = event.end_date ? new Date(event.end_date).getTime() : 0;

    if (end && now > end) return 'ended';
    if (start && now >= start && (!end || now <= end)) return 'active';
    return 'draft';
}

export default function EventDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { toast } = useToast();

    const [event, setEvent] = useState<AdminEvent | null>(null);
    const [clubSlug, setClubSlug] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;

        async function load() {
            if (!id) return;

            try {
                setLoading(true);
                const [eventData, dashboard] = await Promise.all([
                    getAdminEvent(id),
                    getAdminDashboard(),
                ]);

                if (!mounted) return;

                setEvent(eventData);
                setClubSlug(dashboard.club.slug);
            } catch (error) {
                console.error(error);
                toast({ title: 'Failed to load event' });
                navigate('/admin/events');
            } finally {
                if (mounted) setLoading(false);
            }
        }

        load();
        return () => {
            mounted = false;
        };
    }, [id, navigate, toast]);

    const status = useMemo(() => {
        if (!event) return 'draft' as EventStatus;
        return mapEventStatus(event);
    }, [event]);

    const copyLink = async () => {
        if (!event) return;
        await navigator.clipboard.writeText(`${window.location.origin}/event/${clubSlug}?event=${event.id}`);
        toast({ title: 'Link copied!' });
    };

    const handleEnd = async () => {
        if (!event) return;

        try {
            await endAdminEvent(event.id);
            setEvent((prev) =>
                prev
                    ? {
                        ...prev,
                        end_date: new Date().toISOString(),
                    }
                    : prev
            );
            toast({ title: 'Event ended' });
        } catch (error) {
            console.error(error);
            toast({ title: 'Failed to end event' });
        }
    };

    if (loading || !event) {
        return (
            <div className="p-4 sm:p-6 max-w-5xl mx-auto">
                <GlassCard>
                    <p className="text-sm text-muted-foreground">Loading event...</p>
                </GlassCard>
            </div>
        );
    }

    const stats = [
        { label: 'Assigned DJs', value: event.dj_ids.length, icon: Users, color: 'text-primary' },
        { label: 'Total Votes', value: 0, icon: BarChart3, color: 'text-secondary' },
        { label: 'Tracks Played', value: 0, icon: Music, color: 'text-accent' },
        { label: 'Rounds', value: 0, icon: BarChart3, color: 'text-primary' },
    ];

    return (
        <div className="p-4 sm:p-6 space-y-6 max-w-5xl mx-auto">
            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                    <Button variant="ghost" size="icon" className="shrink-0" onClick={() => navigate(-1)}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>

                    <div className="min-w-0">
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl sm:text-2xl font-display font-bold truncate">{event.title}</h1>
                            <StatusBadge status={status} />
                        </div>
                        <p className="text-sm text-muted-foreground">
                            DJs assigned: {event.dj_ids.length || 0}
                        </p>
                    </div>
                </div>

                <div className="flex gap-2 self-end sm:self-center">
                    <Button variant="glass" size="sm" onClick={copyLink}>
                        <Share2 className="h-3.5 w-3.5 mr-1" /> Share
                    </Button>

                    {status === 'active' && (
                        <Button variant="destructive" size="sm" onClick={handleEnd}>
                            <Square className="h-3 w-3 mr-1" /> End Event
                        </Button>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map(({ label, value, icon: Icon, color }) => (
                    <GlassCard key={label} className="space-y-1">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
                            <Icon className={`h-4 w-4 ${color}`} />
                        </div>
                        <p className="text-2xl font-display font-bold">{value}</p>
                    </GlassCard>
                ))}
            </div>

            <GlassCard className="space-y-4">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                    Event Info
                </h2>

                <div className="space-y-3 text-sm">
                    <div>
                        <span className="text-muted-foreground">Title:</span>{' '}
                        <span className="font-medium">{event.title}</span>
                    </div>
                    <div>
                        <span className="text-muted-foreground">Preview:</span>{' '}
                        <span>{event.preview || '—'}</span>
                    </div>
                    <div>
                        <span className="text-muted-foreground">Start:</span>{' '}
                        <span>{event.start_date ? new Date(event.start_date).toLocaleString() : '—'}</span>
                    </div>
                    <div>
                        <span className="text-muted-foreground">End:</span>{' '}
                        <span>{event.end_date ? new Date(event.end_date).toLocaleString() : '—'}</span>
                    </div>
                    <div>
                        <span className="text-muted-foreground">Created:</span>{' '}
                        <span>{new Date(event.created_at).toLocaleString()}</span>
                    </div>
                    <div>
                        <span className="text-muted-foreground">Event ID:</span>{' '}
                        <span>{event.id}</span>
                    </div>
                </div>
            </GlassCard>
        </div>
    );
}