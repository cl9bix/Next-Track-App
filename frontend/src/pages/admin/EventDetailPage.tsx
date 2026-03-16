import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { GlassCard } from '@/components/shared/GlassCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Users, BarChart3, Music, Play, Square, Share2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAdminAuth } from '@/hooks/useAdminAuth';
import { getAdminEvent, endAdminEvent } from '@/services/api/admin';

type EventStats = {
    attendees: number;
    totalVotes: number;
    totalTracks: number;
    totalRounds: number;
};

type TopTrack = {
    title: string;
    artist?: string | null;
    votes: number;
};

type EventDetailState = {
    id: number;
    title: string;
    preview?: string | null;
    start_date?: string | null;
    end_date?: string | null;
    created_at: string;
    club_id: number;
    dj_ids: number[];
    status: 'active' | 'draft' | 'ended';
    slug: string;
    stats: EventStats;
    topTracks: TopTrack[];
};

function slugify(value: string): string {
    return value
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-+|-+$/g, '');
}

function mapBackendStatus(event: {
    start_date?: string | null;
    end_date?: string | null;
}): 'active' | 'draft' | 'ended' {
    const now = new Date();

    const start = event.start_date ? new Date(event.start_date) : null;
    const end = event.end_date ? new Date(event.end_date) : null;

    if (end && end < now) {
        return 'ended';
    }

    if (start && start <= now && (!end || end >= now)) {
        return 'active';
    }

    return 'draft';
}

export default function EventDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { toast } = useToast();
    const { selectedClubId } = useAdminAuth();

    const [event, setEvent] = useState<EventDetailState | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isEnding, setIsEnding] = useState(false);

    useEffect(() => {
        if (!id) {
            setIsLoading(false);
            return;
        }

        let mounted = true;

        const loadEvent = async () => {
            try {
                setIsLoading(true);

                const response = await getAdminEvent(id, selectedClubId ?? undefined);

                if (!mounted) return;

                setEvent({
                    id: response.id,
                    title: response.title,
                    preview: response.preview ?? null,
                    start_date: response.start_date ?? null,
                    end_date: response.end_date ?? null,
                    created_at: response.created_at,
                    club_id: response.club_id,
                    dj_ids: response.dj_ids ?? [],
                    status: mapBackendStatus(response),
                    slug: slugify(response.title),
                    stats: {
                        attendees: 0,
                        totalVotes: 0,
                        totalTracks: 0,
                        totalRounds: 0,
                    },
                    topTracks: [],
                });
            } catch (error) {
                console.error('Failed to load event:', error);
                toast({
                    title: 'Failed to load event',
                    description: 'Could not fetch event details from server.',
                    variant: 'destructive',
                });
            } finally {
                if (mounted) {
                    setIsLoading(false);
                }
            }
        };

        loadEvent();

        return () => {
            mounted = false;
        };
    }, [id, selectedClubId, toast]);

    const shareUrl = useMemo(() => {
        if (!event) return '';
        return `${window.location.origin}/event/${event.slug}`;
    }, [event]);

    const copyLink = async () => {
        if (!event) return;

        try {
            await navigator.clipboard.writeText(shareUrl);
            toast({ title: 'Link copied!' });
        } catch (error) {
            console.error('Clipboard error:', error);
            toast({
                title: 'Failed to copy link',
                description: 'Could not copy event link.',
                variant: 'destructive',
            });
        }
    };

    const handleEndEvent = async () => {
        if (!event || !selectedClubId) return;

        try {
            setIsEnding(true);

            const response = await endAdminEvent(event.id, selectedClubId);

            setEvent((prev) =>
                prev
                    ? {
                        ...prev,
                        status: 'ended',
                        end_date: response.end_date,
                    }
                    : prev
            );

            toast({
                title: 'Event ended',
                description: 'The event has been finished successfully.',
            });
        } catch (error) {
            console.error('Failed to end event:', error);
            toast({
                title: 'Failed to end event',
                description: 'Could not end the event.',
                variant: 'destructive',
            });
        } finally {
            setIsEnding(false);
        }
    };

    if (isLoading) {
        return (
            <div className="p-4 sm:p-6 max-w-5xl mx-auto">
                <div className="text-sm text-muted-foreground">Loading event...</div>
            </div>
        );
    }

    if (!event) {
        return (
            <div className="p-4 sm:p-6 max-w-5xl mx-auto space-y-4">
                <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back
                </Button>
                <div className="text-sm text-muted-foreground">Event not found.</div>
            </div>
        );
    }

    return (
        <div className="p-4 sm:p-6 space-y-6 max-w-5xl mx-auto">
            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="shrink-0"
                        onClick={() => navigate(-1)}
                    >
                        <ArrowLeft className="h-4 w-4" />
                    </Button>

                    <div className="min-w-0">
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl sm:text-2xl font-display font-bold truncate">
                                {event.title}
                            </h1>
                            <StatusBadge status={event.status} />
                        </div>

                        <p className="text-sm text-muted-foreground">
                            DJs assigned: {event.dj_ids.length}
                        </p>
                    </div>
                </div>

                <div className="flex gap-2 self-end sm:self-center">
                    <Button variant="glass" size="sm" onClick={copyLink}>
                        <Share2 className="h-3.5 w-3.5 mr-1" />
                        Share
                    </Button>

                    {event.status === 'active' ? (
                        <Button
                            variant="destructive"
                            size="sm"
                            onClick={handleEndEvent}
                            disabled={isEnding}
                        >
                            <Square className="h-3 w-3 mr-1" />
                            {isEnding ? 'Ending...' : 'End Event'}
                        </Button>
                    ) : event.status === 'draft' ? (
                        <Button
                            variant="glow"
                            size="sm"
                            onClick={() =>
                                toast({
                                    title: 'Start endpoint not ready',
                                    description: 'Backend start event action is not implemented yet.',
                                })
                            }
                        >
                            <Play className="h-3 w-3 mr-1" />
                            Start Event
                        </Button>
                    ) : null}
                </div>
            </div>

            {event.preview ? (
                <GlassCard>
                    <p className="text-sm text-muted-foreground">{event.preview}</p>
                </GlassCard>
            ) : null}

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                    {
                        label: 'Attendees',
                        value: event.stats.attendees,
                        icon: Users,
                        color: 'text-primary',
                    },
                    {
                        label: 'Total Votes',
                        value: event.stats.totalVotes,
                        icon: BarChart3,
                        color: 'text-secondary',
                    },
                    {
                        label: 'Tracks Played',
                        value: event.stats.totalTracks,
                        icon: Music,
                        color: 'text-accent',
                    },
                    {
                        label: 'Rounds',
                        value: event.stats.totalRounds,
                        icon: BarChart3,
                        color: 'text-primary',
                    },
                ].map(({ label, value, icon: Icon, color }) => (
                    <GlassCard key={label} className="space-y-1">
                        <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground uppercase tracking-wider">
                {label}
              </span>
                            <Icon className={`h-4 w-4 ${color}`} />
                        </div>
                        <p className="text-2xl font-display font-bold">{value}</p>
                    </GlassCard>
                ))}
            </div>

            <GlassCard className="space-y-4">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                    Top Tracks
                </h2>

                {event.topTracks.length === 0 ? (
                    <div className="text-sm text-muted-foreground">
                        No track analytics yet.
                    </div>
                ) : (
                    <div className="space-y-2">
                        {event.topTracks.map((track, index) => (
                            <div
                                key={`${track.title}-${track.artist ?? 'unknown'}-${index}`}
                                className="flex items-center gap-3 py-2 border-b border-border/30 last:border-0"
                            >
                <span className="w-6 text-center text-xs font-bold text-muted-foreground">
                  {index + 1}
                </span>

                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium truncate">{track.title}</p>
                                    <p className="text-xs text-muted-foreground">
                                        {track.artist || 'Unknown artist'}
                                    </p>
                                </div>

                                <span className="text-xs text-primary font-bold">
                  {track.votes} votes
                </span>
                            </div>
                        ))}
                    </div>
                )}
            </GlassCard>
        </div>
    );
}