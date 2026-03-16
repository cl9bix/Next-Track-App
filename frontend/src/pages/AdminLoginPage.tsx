import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { GlassCard } from '@/components/shared/GlassCard';
import { Music, Loader2 } from 'lucide-react';
import { useAdminAuth } from '@/hooks/useAdminAuth';

export default function AdminLoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [localError, setLocalError] = useState('');
    const navigate = useNavigate();
    const { login, isLoading, error } = useAdminAuth();

    const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLocalError('');

        const cleanUsername = username.trim();
        const cleanPassword = password.trim();

        if (!cleanUsername || !cleanPassword) {
            setLocalError('Enter username and password');
            return;
        }

        try {
            const result = await login(cleanUsername, cleanPassword);

            if (result?.access_token) {
                localStorage.setItem('admin_access_token', result.access_token);
            }

            navigate('/admin/dashboard', { replace: true });
        } catch (err) {
            console.error('Admin login failed:', err);
        }
    };

    const uiError = localError || error;

    return (
        <div className="min-h-screen gradient-bg flex items-center justify-center px-4">
            <GlassCard className="w-full max-w-md p-8 space-y-6">
                <div className="text-center space-y-2">
                    <div className="w-14 h-14 rounded-2xl bg-primary/20 flex items-center justify-center mx-auto glow-cyan">
                        <Music className="h-7 w-7 text-primary" />
                    </div>
                    <h1 className="text-2xl font-display font-bold">Next Track</h1>
                    <p className="text-sm text-muted-foreground">Admin Dashboard</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-4">
                    <Input
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="bg-card/60 border-border/50"
                        autoComplete="username"
                        disabled={isLoading}
                    />

                    <Input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="bg-card/60 border-border/50"
                        autoComplete="current-password"
                        disabled={isLoading}
                    />

                    {uiError && (
                        <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-red-300">
                            {uiError}
                        </div>
                    )}

                    <Button type="submit" className="w-full" variant="glow" disabled={isLoading}>
                        {isLoading ? (
                            <span className="inline-flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Signing in...
              </span>
                        ) : (
                            'Sign In'
                        )}
                    </Button>
                </form>
            </GlassCard>
        </div>
    );
}