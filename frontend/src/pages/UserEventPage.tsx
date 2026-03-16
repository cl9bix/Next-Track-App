import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { CalendarDays, MapPin, Users, Music2 } from "lucide-react";
import { EventHeader } from "@/components/user/EventHeader";
import { NowPlayingCard } from "@/components/user/NowPlayingCard";
import { QueueList } from "@/components/user/QueueList";
import { SuggestionSearch } from "@/components/user/SuggestionSearch";
import { BottomNav } from "@/components/user/BottomNav";
import { useEventData } from "@/hooks/useEventData";

function formatEventDate(value?: string | null) {
    if (!value) return "Live now";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "Live now";

    return new Intl.DateTimeFormat("uk-UA", {
        day: "2-digit",
        month: "long",
        hour: "2-digit",
        minute: "2-digit",
    }).format(date);
}

export default function UserEventPage() {
    const { slug = "demo" } = useParams<{ slug: string }>();
    const [activeTab, setActiveTab] = useState("home");
    const [votedTrackId, setVotedTrackId] = useState<string | null>(null);

    const {
        event,
        queue,
        nowPlaying,
        searchResults,
        isLoading,
        isSearching,
        isSuggesting,
        vote,
        search,
        suggest,
    } = useEventData(slug);

    const heroStyle = useMemo(() => {
        if (!event?.background_image_url) return undefined;

        return {
            backgroundImage: `linear-gradient(to top, rgba(10,10,15,0.92), rgba(10,10,15,0.35)), url(${event.background_image_url})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
        } as React.CSSProperties;
    }, [event?.background_image_url]);

    const handleVote = async (trackId: string) => {
        try {
            await vote(trackId);
            setVotedTrackId(trackId);
        } catch (error) {
            console.error("Vote failed:", error);
        }
    };

    const handleSearch = async (query: string) => {
        try {
            await search(query);
        } catch (error) {
            console.error("Search failed:", error);
        }
    };

    const handleSuggest = async (track: {
        id: string;
        title: string;
        artist?: string;
        cover_url?: string;
        duration_sec?: number;
    }) => {
        try {
            await suggest(track);
        } catch (error) {
            console.error("Suggest failed:", error);
        }
    };

    if (isLoading || !event) {
        return (
            <div className="min-h-screen gradient-bg pb-20">
                <div className="max-w-lg mx-auto px-4 pt-4 space-y-4">
                    <div className="glass rounded-3xl p-6 animate-pulse">
                        <div className="h-6 w-40 rounded bg-white/10" />
                        <div className="mt-3 h-4 w-24 rounded bg-white/10" />
                    </div>
                    <div className="glass rounded-3xl p-6 animate-pulse">
                        <div className="h-24 rounded bg-white/10" />
                    </div>
                    <div className="glass rounded-3xl p-6 animate-pulse">
                        <div className="h-56 rounded bg-white/10" />
                    </div>
                </div>

                <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
            </div>
        );
    }

    return (
        <div className="min-h-screen gradient-bg pb-20">
            <div className="max-w-lg mx-auto px-4 pt-4 space-y-4">
                {activeTab === "home" && (
                    <>
                        <section
                            className="relative overflow-hidden rounded-3xl border border-white/10 p-5 text-white shadow-2xl"
                            style={heroStyle}
                        >
                            {!event.background_image_url && (
                                <div className="absolute inset-0 bg-gradient-to-br from-fuchsia-500/20 via-cyan-500/10 to-transparent" />
                            )}

                            <div className="relative z-10 space-y-4">
                                <div className="flex items-start justify-between gap-4">
                                    <div>
                                        <div className="text-xs uppercase tracking-[0.22em] text-white/60">
                                            Now at {event.club?.name || "Next Track"}
                                        </div>
                                        <h1 className="mt-1 text-2xl font-display font-bold leading-tight">
                                            {event.name}
                                        </h1>
                                        {event.preview ? (
                                            <p className="mt-2 text-sm text-white/75 line-clamp-3">
                                                {event.preview}
                                            </p>
                                        ) : null}
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <div className="rounded-2xl bg-white/10 backdrop-blur-sm p-3">
                                        <div className="flex items-center gap-2 text-white/70 text-xs uppercase tracking-wide">
                                            <Users className="h-4 w-4" />
                                            Crowd
                                        </div>
                                        <div className="mt-1 text-lg font-bold">{event.attendees_count ?? 0}</div>
                                    </div>

                                    <div className="rounded-2xl bg-white/10 backdrop-blur-sm p-3">
                                        <div className="flex items-center gap-2 text-white/70 text-xs uppercase tracking-wide">
                                            <CalendarDays className="h-4 w-4" />
                                            Start
                                        </div>
                                        <div className="mt-1 text-sm font-semibold">
                                            {formatEventDate(event.created_at)}
                                        </div>
                                    </div>

                                    <div className="rounded-2xl bg-white/10 backdrop-blur-sm p-3">
                                        <div className="flex items-center gap-2 text-white/70 text-xs uppercase tracking-wide">
                                            <Music2 className="h-4 w-4" />
                                            Queue
                                        </div>
                                        <div className="mt-1 text-lg font-bold">{queue.length}</div>
                                    </div>

                                    <div className="rounded-2xl bg-white/10 backdrop-blur-sm p-3">
                                        <div className="flex items-center gap-2 text-white/70 text-xs uppercase tracking-wide">
                                            <MapPin className="h-4 w-4" />
                                            Club
                                        </div>
                                        <div className="mt-1 text-sm font-semibold truncate">
                                            {event.club?.name || slug}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </section>

                        <EventHeader event={event} attendees={event.attendees_count ?? 0} />
                        <NowPlayingCard item={nowPlaying} />
                        <QueueList
                            items={queue}
                            votedTrackId={votedTrackId}
                            onVote={handleVote}
                            canVote
                        />
                    </>
                )}

                {activeTab === "queue" && (
                    <>
                        <h1 className="text-xl font-display font-bold pt-2">Full Queue</h1>
                        <QueueList
                            items={queue}
                            votedTrackId={votedTrackId}
                            onVote={handleVote}
                            canVote
                        />
                    </>
                )}

                {activeTab === "search" && (
                    <SuggestionSearch
                        results={searchResults}
                        isLoading={isSearching || isSuggesting}
                        onSearch={handleSearch}
                        onSuggest={handleSuggest}
                    />
                )}

                {activeTab === "profile" && (
                    <div className="pt-8 text-center space-y-3">
                        <div className="w-16 h-16 rounded-full bg-muted mx-auto flex items-center justify-center text-2xl">
                            🎵
                        </div>
                        <h2 className="text-lg font-display font-bold">Guest User</h2>
                        <p className="text-sm text-muted-foreground">Connected via Telegram</p>
                    </div>
                )}
            </div>

            <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
        </div>
    );
}