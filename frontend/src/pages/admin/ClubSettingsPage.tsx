import { useEffect, useMemo, useState } from 'react';
import { GlassCard } from '@/components/shared/GlassCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { useAdminAuth } from '@/hooks/useAdminAuth';
import { getClubSettings, updateClubSettings } from '@/services/api/admin';

type ClubSettingsForm = {
    name: string;
    slug: string;
    description: string;
    backgroundImageUrl: string;
    maxSuggestions: number;
    votingDuration: number;
    allowExplicit: boolean;
    autoPlay: boolean;
};

const DEFAULT_FORM: ClubSettingsForm = {
    name: '',
    slug: '',
    description: '',
    backgroundImageUrl: '',
    maxSuggestions: 3,
    votingDuration: 60,
    allowExplicit: false,
    autoPlay: false,
};

function normalizeSlug(value: string): string {
    return value
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-+|-+$/g, '');
}

export default function ClubSettingsPage() {
    const { toast } = useToast();
    const { selectedClubId } = useAdminAuth();

    const [form, setForm] = useState<ClubSettingsForm>(DEFAULT_FORM);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [isDirty, setIsDirty] = useState(false);

    const canSave = useMemo(() => {
        return !isLoading && !isSaving && !!selectedClubId;
    }, [isLoading, isSaving, selectedClubId]);

    const updateField = <K extends keyof ClubSettingsForm>(
        key: K,
        value: ClubSettingsForm[K]
    ) => {
        setForm((prev) => ({ ...prev, [key]: value }));
        setIsDirty(true);
    };

    useEffect(() => {
        if (!selectedClubId) {
            setForm(DEFAULT_FORM);
            setIsLoading(false);
            return;
        }

        let isMounted = true;

        const loadSettings = async () => {
            try {
                setIsLoading(true);

                const response = await getClubSettings(selectedClubId);

                if (!isMounted) return;

                setForm({
                    name: response?.club?.name ?? '',
                    slug: response?.club?.slug ?? '',
                    description: response?.settings?.description ?? '',
                    backgroundImageUrl: response?.settings?.background_image_url ?? '',
                    maxSuggestions: response?.settings?.max_suggestions_per_user ?? 3,
                    votingDuration: response?.settings?.voting_duration_sec ?? 60,
                    allowExplicit: response?.settings?.allow_explicit ?? false,
                    autoPlay: response?.settings?.auto_play ?? false,
                });

                setIsDirty(false);
            } catch (error) {
                console.error('Failed to load club settings:', error);

                if (!isMounted) return;

                setForm(DEFAULT_FORM);

                toast({
                    title: 'Failed to load settings',
                    description: 'Could not fetch club settings from server.',
                    variant: 'destructive',
                });
            } finally {
                if (isMounted) {
                    setIsLoading(false);
                }
            }
        };

        loadSettings();

        return () => {
            isMounted = false;
        };
    }, [selectedClubId, toast]);

    const handleNameChange = (value: string) => {
        setForm((prev) => {
            const shouldAutofillSlug =
                !prev.slug || prev.slug === normalizeSlug(prev.name);

            return {
                ...prev,
                name: value,
                slug: shouldAutofillSlug ? normalizeSlug(value) : prev.slug,
            };
        });
        setIsDirty(true);
    };

    const handleSlugChange = (value: string) => {
        updateField('slug', normalizeSlug(value));
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!selectedClubId) {
            toast({
                title: 'Club not selected',
                description: 'Please select a club first.',
                variant: 'destructive',
            });
            return;
        }

        if (!form.name.trim()) {
            toast({
                title: 'Club name is required',
                description: 'Please enter club name before saving.',
                variant: 'destructive',
            });
            return;
        }

        if (form.maxSuggestions < 1) {
            toast({
                title: 'Invalid value',
                description: 'Max suggestions per user must be at least 1.',
                variant: 'destructive',
            });
            return;
        }

        if (form.votingDuration < 10) {
            toast({
                title: 'Invalid value',
                description: 'Voting duration must be at least 10 seconds.',
                variant: 'destructive',
            });
            return;
        }

        try {
            setIsSaving(true);

            await updateClubSettings(
                {
                    name: form.name.trim(),
                    slug: form.slug.trim() || normalizeSlug(form.name),
                    description: form.description.trim() || null,
                    background_image_url: form.backgroundImageUrl.trim() || null,
                    max_suggestions_per_user: form.maxSuggestions,
                    voting_duration_sec: form.votingDuration,
                    allow_explicit: form.allowExplicit,
                    auto_play: form.autoPlay,
                },
                selectedClubId
            );

            setForm((prev) => ({
                ...prev,
                slug: prev.slug.trim() || normalizeSlug(prev.name),
            }));
            setIsDirty(false);

            toast({
                title: 'Settings saved',
                description: 'Club settings have been updated successfully.',
            });
        } catch (error) {
            console.error('Failed to save club settings:', error);

            toast({
                title: 'Save failed',
                description: 'Could not save club settings.',
                variant: 'destructive',
            });
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="p-4 sm:p-6 max-w-2xl mx-auto">
                <div className="text-sm text-muted-foreground">Loading club settings...</div>
            </div>
        );
    }

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
                            <Input
                                id="clubName"
                                value={form.name}
                                placeholder="Введіть назву клубу"
                                onChange={(e) => handleNameChange(e.target.value)}
                                className="bg-card/60 border-border/50 mt-1"
                            />
                        </div>

                        <div>
                            <Label htmlFor="clubSlug">Slug</Label>
                            <Input
                                id="clubSlug"
                                value={form.slug}
                                placeholder="club-slug"
                                onChange={(e) => handleSlugChange(e.target.value)}
                                className="bg-card/60 border-border/50 mt-1"
                            />
                        </div>

                        <div>
                            <Label htmlFor="desc">Description</Label>
                            <Textarea
                                id="desc"
                                value={form.description}
                                placeholder="Опис клубу"
                                onChange={(e) => updateField('description', e.target.value)}
                                className="bg-card/60 border-border/50 mt-1"
                                rows={3}
                            />
                        </div>
                        <div>
                            <Label htmlFor="backgroundImageUrl">Background Image URL</Label>

                            <Input
                                id="backgroundImageUrl"
                                value={form.backgroundImageUrl}
                                placeholder="https://example.com/club-background.jpg"
                                onChange={(e) => updateField("backgroundImageUrl", e.target.value)}
                                className="bg-card/60 border-border/50 mt-1"
                            />
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
                                <Label htmlFor="maxSuggestions">Max Suggestions per User</Label>
                                <Input
                                    id="maxSuggestions"
                                    type="number"
                                    min={1}
                                    max={50}
                                    value={form.maxSuggestions}
                                    onChange={(e) =>
                                        updateField('maxSuggestions', Number(e.target.value) || 1)
                                    }
                                    className="bg-card/60 border-border/50 mt-1"
                                />
                            </div>

                            <div>
                                <Label htmlFor="votingDuration">Voting Duration (sec)</Label>
                                <Input
                                    id="votingDuration"
                                    type="number"
                                    min={10}
                                    max={3600}
                                    value={form.votingDuration}
                                    onChange={(e) =>
                                        updateField('votingDuration', Number(e.target.value) || 10)
                                    }
                                    className="bg-card/60 border-border/50 mt-1"
                                />
                            </div>
                        </div>

                        {/*<div className="flex items-center justify-between gap-4">*/}
                        {/*    <div>*/}
                        {/*        <p className="text-sm font-medium">Allow Explicit</p>*/}
                        {/*        <p className="text-xs text-muted-foreground">*/}
                        {/*            Enable explicit content*/}
                        {/*        </p>*/}
                        {/*    </div>*/}
                        {/*    <Switch*/}
                        {/*        checked={form.allowExplicit}*/}
                        {/*        onCheckedChange={(checked) => updateField('allowExplicit', checked)}*/}
                        {/*    />*/}
                        {/*</div>*/}

                        {/*<div className="flex items-center justify-between gap-4">*/}
                        {/*    <div>*/}
                        {/*        <p className="text-sm font-medium">Auto-Play</p>*/}
                        {/*        <p className="text-xs text-muted-foreground">*/}
                        {/*            Auto-start winning tracks*/}
                        {/*        </p>*/}
                        {/*    </div>*/}
                        {/*    <Switch*/}
                        {/*        checked={form.autoPlay}*/}
                        {/*        onCheckedChange={(checked) => updateField('autoPlay', checked)}*/}
                        {/*    />*/}
                        {/*</div>*/}
                    </div>
                </GlassCard>

                <Button
                    type="submit"
                    variant="glow"
                    className="w-full"
                    disabled={!canSave}
                >
                    {isSaving ? 'Saving...' : isDirty ? 'Save Settings' : 'Saved'}
                </Button>
            </form>
        </div>
    );
}