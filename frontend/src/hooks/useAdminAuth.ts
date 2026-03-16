import { useCallback, useEffect, useState } from 'react';
import { adminLogin, adminLogout, adminMe, type AdminLoginResponse, type AdminUser } from '@/services/api/auth';
import { getAdminToken, removeAdminToken } from '@/lib/storage';

const CLUB_KEY = 'selected_admin_club_id';

export function useAdminAuth() {
    const [user, setUser] = useState<AdminUser | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isBootstrapping, setIsBootstrapping] = useState(true);
    const [error, setError] = useState('');
    const [selectedClubId, setSelectedClubIdState] = useState<number | null>(null);

    const setSelectedClubId = (clubId: number) => {
        localStorage.setItem(CLUB_KEY, String(clubId));
        setSelectedClubIdState(clubId);
    };

    const login = useCallback(async (username: string, password: string): Promise<AdminLoginResponse> => {
        try {
            setIsLoading(true);
            setError('');

            const result = await adminLogin({ username, password });
            setUser(result.admin);

            const savedClubId = localStorage.getItem(CLUB_KEY);
            const firstClubId = result.admin.clubs?.[0]?.id ?? null;
            const validClubId =
                savedClubId && result.admin.clubs?.some((c) => c.id === Number(savedClubId))
                    ? Number(savedClubId)
                    : firstClubId;

            if (validClubId) {
                setSelectedClubId(validClubId);
            }

            return result;
        } catch (err: any) {
            setError(err?.message || 'Login failed');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const logout = useCallback(async () => {
        try {
            await adminLogout();
        } catch {
        } finally {
            removeAdminToken();
            localStorage.removeItem(CLUB_KEY);
            setUser(null);
            setSelectedClubIdState(null);
        }
    }, []);

    const refreshMe = useCallback(async () => {
        const token = getAdminToken();

        if (!token) {
            setUser(null);
            setIsBootstrapping(false);
            return;
        }

        try {
            const me = await adminMe();
            setUser(me);

            const savedClubId = localStorage.getItem(CLUB_KEY);
            const firstClubId = me.clubs?.[0]?.id ?? null;
            const validClubId =
                savedClubId && me.clubs?.some((c) => c.id === Number(savedClubId))
                    ? Number(savedClubId)
                    : firstClubId;

            setSelectedClubIdState(validClubId);
        } catch {
            removeAdminToken();
            localStorage.removeItem(CLUB_KEY);
            setUser(null);
            setSelectedClubIdState(null);
        } finally {
            setIsBootstrapping(false);
        }
    }, []);

    useEffect(() => {
        refreshMe();
    }, [refreshMe]);

    return {
        user,
        selectedClubId,
        setSelectedClubId,
        isAuthenticated: !!user,
        isLoading,
        isBootstrapping,
        error,
        login,
        logout,
        refreshMe,
    };
}