import { useState } from "react";
import { useParams } from "react-router-dom";
import { EventHeader } from "@/components/user/EventHeader";
import { NowPlayingCard } from "@/components/user/NowPlayingCard";
import { QueueList } from "@/components/user/QueueList";
import { SuggestionSearch } from "@/components/user/SuggestionSearch";
import { BottomNav } from "@/components/user/BottomNav";
import { useEventData } from "@/hooks/useEventData";

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

  const handleSuggest = async (track: any) => {
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
            <EventHeader event={event} attendees={47} />
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