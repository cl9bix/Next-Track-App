import { Outlet, Link, useLocation } from 'react-router-dom';
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
import { Disc3, LayoutDashboard, Radio, LogOut } from 'lucide-react';

const navItems = [
  { title: 'Dashboard', url: '/dj/dashboard', icon: LayoutDashboard },
  { title: 'Live Event', url: '/dj/event/1', icon: Radio },
];

function DJSidebar() {
  const { state } = useSidebar();
  const collapsed = state === 'collapsed';

  return (
    <Sidebar collapsible="icon" className="border-r border-sidebar-border">
      <SidebarContent>
        <div className="px-4 py-5 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-secondary/20 flex items-center justify-center shrink-0">
            <Disc3 className="h-4 w-4 text-secondary" />
          </div>
          {!collapsed && <span className="font-display font-bold text-sm">DJ Console</span>}
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
                      end={item.url === '/dj/dashboard'}
                      className="hover:bg-sidebar-accent/50"
                      activeClassName="bg-sidebar-accent text-secondary font-medium"
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
                <Link to="/dj/login" className="text-muted-foreground hover:text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  {!collapsed && <span>Logout</span>}
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </div>
      </SidebarContent>
    </Sidebar>
  );
}

export default function DJLayout() {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full gradient-bg">
        <DJSidebar />
        <div className="flex-1 flex flex-col">
          <header className="h-12 flex items-center border-b border-border/50 glass-strong px-4">
            <SidebarTrigger className="mr-4" />
            <span className="text-sm text-muted-foreground">DJ Console</span>
          </header>
          <main className="flex-1 overflow-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
