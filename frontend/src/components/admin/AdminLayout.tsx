import { Outlet, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { NavLink } from '@/components/NavLink';
import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarProvider,
    SidebarTrigger,
    useSidebar,
} from '@/components/ui/sidebar';
import { LayoutDashboard, Calendar, Settings, BarChart3, Music, LogOut } from 'lucide-react';
import { useAdminAuth } from '@/hooks/useAdminAuth';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const navItems = [
    { title: 'Dashboard', url: '/admin/dashboard', icon: LayoutDashboard },
    { title: 'Events', url: '/admin/events', icon: Calendar },
    { title: 'Analytics', url: '/admin/analytics', icon: BarChart3 },
    { title: 'Club Settings', url: '/admin/settings', icon: Settings },
];

function AdminSidebar() {
    const { state, isMobile, setOpenMobile } = useSidebar();
    const collapsed = state === 'collapsed';

    const location = useLocation();
    const navigate = useNavigate();
    const { logout, user, selectedClubId, setSelectedClubId } = useAdminAuth();
    const [isLoggingOut, setIsLoggingOut] = useState(false);

    const clubs = user?.clubs || [];

    useEffect(() => {
        if (isMobile) {
            setOpenMobile(false);
        }
    }, [location.pathname, isMobile, setOpenMobile]);

    const handleNavigate = () => {
        if (isMobile) {
            setOpenMobile(false);
        }
    };

    const handleLogout = async () => {
        try {
            setIsLoggingOut(true);

            if (isMobile) {
                setOpenMobile(false);
            }

            await logout();
            navigate('/admin/login', { replace: true });
        } finally {
            setIsLoggingOut(false);
        }
    };

    return (
        <Sidebar collapsible="icon" className="border-r border-sidebar-border">
            <SidebarContent>
                <div className="px-4 py-5 flex flex-col gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0">
                            <Music className="h-4 w-4 text-primary" />
                        </div>

                        {!collapsed && (
                            <div className="min-w-0">
                                <div className="font-display font-bold text-sm">Next Track</div>
                                <div className="text-[11px] text-muted-foreground truncate">
                                    @{user?.username || 'admin'}
                                </div>
                            </div>
                        )}
                    </div>

                    {!collapsed && clubs.length > 0 && (
                        <div className="space-y-1">
                            <div className="text-[11px] text-muted-foreground">
                                Clubs {clubs.length}/{user?.max_club_count ?? 1}
                            </div>

                            <Select
                                value={selectedClubId ? String(selectedClubId) : undefined}
                                onValueChange={(value) => setSelectedClubId(Number(value))}
                            >
                                <SelectTrigger className="h-9">
                                    <SelectValue placeholder="Select club" />
                                </SelectTrigger>

                                <SelectContent>
                                    {clubs.map((club) => (
                                        <SelectItem key={club.id} value={String(club.id)}>
                                            {club.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    )}
                </div>

                <SidebarGroup>
                    <SidebarGroupLabel>Menu</SidebarGroupLabel>

                    <SidebarGroupContent>
                        <SidebarMenu>
                            {navItems.map((item) => (
                                <SidebarMenuItem key={item.title}>
                                    <SidebarMenuButton asChild>
                                        <NavLink
                                            to={item.url}
                                            end={item.url === '/admin/dashboard'}
                                            onClick={handleNavigate}
                                            className="hover:bg-sidebar-accent/50"
                                            activeClassName="bg-sidebar-accent text-sidebar-primary font-medium"
                                        >
                                            <item.icon className="mr-2 h-4 w-4" />
                                            {!collapsed && <span>{item.title}</span>}
                                        </NavLink>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>

                <div className="mt-auto p-4">
                    <SidebarMenu>
                        <SidebarMenuItem>
                            <SidebarMenuButton asChild>
                                <button
                                    type="button"
                                    onClick={handleLogout}
                                    disabled={isLoggingOut}
                                    className="w-full flex items-center text-left text-muted-foreground hover:text-destructive disabled:opacity-60"
                                >
                                    <LogOut className="mr-2 h-4 w-4" />
                                    {!collapsed && (
                                        <span>{isLoggingOut ? 'Logging out...' : 'Logout'}</span>
                                    )}
                                </button>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    </SidebarMenu>
                </div>
            </SidebarContent>
        </Sidebar>
    );
}

function AdminLayoutShell() {
    return (
        <SidebarProvider>
            <div className="min-h-screen flex w-full gradient-bg">
                <AdminSidebar />

                <div className="flex-1 flex flex-col min-w-0">
                    <header className="h-12 flex items-center border-b border-border/50 glass-strong px-4">
                        <SidebarTrigger className="mr-4" />
                        <span className="text-sm text-muted-foreground">Admin Panel</span>
                    </header>

                    <main className="flex-1 overflow-auto">
                        <Outlet />
                    </main>
                </div>
            </div>
        </SidebarProvider>
    );
}

export default function AdminLayout() {
    const { isAuthenticated, isBootstrapping } = useAdminAuth();

    if (isBootstrapping) {
        return (
            <div className="min-h-screen gradient-bg flex items-center justify-center px-4">
                <div className="text-sm text-muted-foreground">Loading admin panel...</div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/admin/login" replace />;
    }

    return <AdminLayoutShell />;
}