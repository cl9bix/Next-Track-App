import { useState } from 'react';
import { GlassCard } from '@/components/shared/GlassCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';

export default function ClubSettingsPage() {
  const { toast } = useToast();
  const [form, setForm] = useState({
    name: 'Club Neon',
    slug: 'club-neon',
    description: 'The hottest nightclub in town with live DJ sets every weekend.',
    maxSuggestions: 3,
    votingDuration: 60,
    allowExplicit: true,
    autoPlay: false,
  });

  const updateField = (key: string, value: string | number | boolean) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    toast({ title: 'Settings saved!' });
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-display font-bold">Club Settings</h1>

      <form onSubmit={handleSave} className="space-y-6">
        <GlassCard className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Club Profile
          </h2>
          <div className="space-y-3">
            <div>
              <Label htmlFor="clubName">Club Name</Label>
              <Input id="clubName" value={form.name} onChange={(e) => updateField('name', e.target.value)} className="bg-card/60 border-border/50 mt-1" />
            </div>
            <div>
              <Label htmlFor="clubSlug">Slug</Label>
              <Input id="clubSlug" value={form.slug} onChange={(e) => updateField('slug', e.target.value)} className="bg-card/60 border-border/50 mt-1" />
            </div>
            <div>
              <Label htmlFor="desc">Description</Label>
              <Textarea id="desc" value={form.description} onChange={(e) => updateField('description', e.target.value)} className="bg-card/60 border-border/50 mt-1" rows={3} />
            </div>
          </div>
        </GlassCard>

        <GlassCard className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Default Event Settings
          </h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label>Max Suggestions per User</Label>
                <Input type="number" min={1} max={10} value={form.maxSuggestions} onChange={(e) => updateField('maxSuggestions', Number(e.target.value))} className="bg-card/60 border-border/50 mt-1" />
              </div>
              <div>
                <Label>Voting Duration (sec)</Label>
                <Input type="number" min={10} max={300} value={form.votingDuration} onChange={(e) => updateField('votingDuration', Number(e.target.value))} className="bg-card/60 border-border/50 mt-1" />
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Allow Explicit</p>
                <p className="text-xs text-muted-foreground">Enable explicit content</p>
              </div>
              <Switch checked={form.allowExplicit} onCheckedChange={(v) => updateField('allowExplicit', v)} />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Auto-Play</p>
                <p className="text-xs text-muted-foreground">Auto-start winning tracks</p>
              </div>
              <Switch checked={form.autoPlay} onCheckedChange={(v) => updateField('autoPlay', v)} />
            </div>
          </div>
        </GlassCard>

        <Button type="submit" variant="glow" className="w-full">
          Save Settings
        </Button>
      </form>
    </div>
  );
}
