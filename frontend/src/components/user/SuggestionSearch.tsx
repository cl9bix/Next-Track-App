import { useState } from 'react';
import { Search, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { GlassCard } from '@/components/shared/GlassCard';
import { Button } from '@/components/ui/button';
import type { SearchResult } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';

interface SuggestionSearchProps {
  results: SearchResult[];
  isLoading: boolean;
  onSearch: (query: string) => void;
  onSuggest: (track: SearchResult) => void;
}

export function SuggestionSearch({ results, isLoading, onSearch, onSuggest }: SuggestionSearchProps) {
  const [query, setQuery] = useState('');

  const handleSearch = (value: string) => {
    setQuery(value);
    if (value.length >= 2) onSearch(value);
  };

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground px-1">
        Suggest a Track
      </h2>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-9 pr-9 bg-card/60 border-border/50 backdrop-blur"
          placeholder="Search tracks..."
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
        />
        {query && (
          <button
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            onClick={() => { setQuery(''); onSearch(''); }}
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <AnimatePresence>
        {query.length >= 2 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-1.5 max-h-64 overflow-y-auto"
          >
            {isLoading ? (
              <p className="text-sm text-muted-foreground text-center py-4">Searching...</p>
            ) : results.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No results found</p>
            ) : (
              results.map((track) => (
                <GlassCard key={track.id} className="flex items-center gap-3 py-2.5 px-3">
                  {track.cover_url && (
                    <img src={track.cover_url} alt="" className="w-9 h-9 rounded object-cover" />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{track.title}</p>
                    <p className="text-xs text-muted-foreground truncate">{track.artist}</p>
                  </div>
                  <Button variant="glow" size="sm" onClick={() => onSuggest(track)}>
                    Suggest
                  </Button>
                </GlassCard>
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
