import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { GlassCard } from '@/components/shared/GlassCard';
import { Disc3 } from 'lucide-react';

export default function DJLoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();

    // TODO:
    // OpenAPI spec currently does not provide a DJ login endpoint.
    // Add backend route, e.g. POST /dj/login, then wire it here.
    alert('DJ auth endpoint is not available yet in backend spec.');
  };

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center px-4">
      <GlassCard className="w-full max-w-md p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-secondary/20 flex items-center justify-center mx-auto glow-magenta">
            <Disc3 className="h-7 w-7 text-secondary" />
          </div>
          <h1 className="text-2xl font-display font-bold">Next Track</h1>
          <p className="text-sm text-muted-foreground">DJ Console</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <Input
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            className="bg-card/60 border-border/50"
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="bg-card/60 border-border/50"
          />
          <Button type="submit" className="w-full" variant="magenta">
            Sign In
          </Button>
        </form>
      </GlassCard>
    </div>
  );
}