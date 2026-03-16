import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GlassCard } from '@/components/shared/GlassCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { ArrowLeft } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { createAdminEvent } from '@/services/api/admin';

export default function CreateEventPage() {
    const navigate = useNavigate();
    const { toast } = useToast();

    const [submitting, setSubmitting] = useState(false);
    const [form, setForm] = useState({
        name: '',
        slug: '',
        djName: '',
        preview: '',
        startDate: '',
        endDate: '',
        maxSuggestions: 3,
        votingDuration: 60,
        allowExplicit: true,
        autoPlay: false,
    });

    const updateField = (key: string, value: string | number | boolean) =>
        setForm((prev) => ({ ...prev, [key]: value }));

    const generateSlug = (name: string) =>
        name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!form.name.trim()) {
            toast({ title: 'Event name is required' });
            return;
        }

        try {
            setSubmitting(true);

            await createAdminEvent({
                title: form.name.trim(),
                preview: form.preview.trim() || null,
                start_date: form.startDate ? new Date(form.startDate).toISOString() : null,
                end_date: form.endDate ? new Date(form.endDate).toISOString() : null,
                dj_ids: [],
            });

            toast({ title: 'Event created!', description: form.name });
            navigate('/admin/events');
        } catch (error) {
            console.error(error);
            toast({ title: 'Failed to create event' });
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="p-4 sm:p-6 space-y-6 max-w-2xl mx-auto">
            <div className="flex items-center gap-3">
                <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                    <ArrowLeft className="h-4 w-4" />
                </Button>
                <h1 className="text-2xl font-display font-bold">Create Event</h1>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <GlassCard className="space-y-4">
                    <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                        Event Details
                    </h2>

                    <div className="space-y-3">
                        <div>
                            <Label htmlFor="name">Event Name</Label>
                            <Input
                                id="name"
                                placeholder="Friday Night Vibes"
                                value={form.name}
                                onChange={(e) => {
                                    updateField('name', e.target.value);
                                    updateField('slug', generateSlug(e.target.value));
                                }}
                                className="bg-card/60 border-border/50 mt-1"
                                required
                            />
                        </div>

                        <div>
                            <Label htmlFor="slug">Slug</Label>
                            <Input
                                id="slug"
                                placeholder="friday-night-vibes"
                                value={form.slug}
                                onChange={(e) => updateField('slug', e.target.value)}
                                className="bg-card/60 border-border/50 mt-1"
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                                URL preview: /event/{form.slug || '...'}
                            </p>
                        </div>

                        <div>
                            <Label htmlFor="preview">Preview / Description</Label>
                            <Input
                                id="preview"
                                placeholder="Club event preview"
                                value={form.preview}
                                onChange={(e) => updateField('preview', e.target.value)}
                                className="bg-card/60 border-border/50 mt-1"
                            />
                        </div>

                        <div>
                            <Label htmlFor="dj">DJ Name (UI only for now)</Label>
                            <Input
                                id="dj"
                                placeholder="DJ Pulse"
                                value={form.djName}
                                onChange={(e) => updateField('djName', e.target.value)}
                                className="bg-card/60 border-border/50 mt-1"
                            />
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <Label htmlFor="startDate">Start date</Label>
                                <Input
                                    id="startDate"
                                    type="datetime-local"
                                    value={form.startDate}
                                    onChange={(e) => updateField('startDate', e.target.value)}
                                    className="bg-card/60 border-border/50 mt-1"
                                />
                            </div>

                            <div>
                                <Label htmlFor="endDate">End date</Label>
                                <Input
                                    id="endDate"
                                    type="datetime-local"
                                    value={form.endDate}
                                    onChange={(e) => updateField('endDate', e.target.value)}
                                    className="bg-card/60 border-border/50 mt-1"
                                />
                            </div>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="space-y-4">
                    <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                        Settings
                    </h2>

                    <div className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <Label htmlFor="maxSugg">Max Suggestions per User</Label>
                                <Input
                                    id="maxSugg"
                                    type="number"
                                    min={1}
                                    max={10}
                                    value={form.maxSuggestions}
                                    onChange={(e) => updateField('maxSuggestions', Number(e.target.value))}
                                    className="bg-card/60 border-border/50 mt-1"
                                />
                            </div>

                            <div>
                                <Label htmlFor="voteDur">Voting Duration (sec)</Label>
                                <Input
                                    id="voteDur"
                                    type="number"
                                    min={10}
                                    max={300}
                                    value={form.votingDuration}
                                    onChange={(e) => updateField('votingDuration', Number(e.target.value))}
                                    className="bg-card/60 border-border/50 mt-1"
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium">Allow Explicit Tracks</p>
                                <p className="text-xs text-muted-foreground">Enable explicit content in suggestions</p>
                            </div>
                            <Switch checked={form.allowExplicit} onCheckedChange={(v) => updateField('allowExplicit', v)} />
                        </div>

                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium">Auto-Play</p>
                                <p className="text-xs text-muted-foreground">Automatically start winning tracks</p>
                            </div>
                            <Switch checked={form.autoPlay} onCheckedChange={(v) => updateField('autoPlay', v)} />
                        </div>
                    </div>
                </GlassCard>

                <div className="flex gap-3">
                    <Button type="button" variant="ghost" onClick={() => navigate(-1)}>
                        Cancel
                    </Button>
                    <Button type="submit" variant="glow" className="flex-1" disabled={submitting}>
                        {submitting ? 'Creating...' : 'Create Event'}
                    </Button>
                </div>
            </form>
        </div>
    );
}