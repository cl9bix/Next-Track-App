import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import UserEventPage from "./pages/UserEventPage";
import AdminLoginPage from "./pages/AdminLoginPage";
import DJLoginPage from "./pages/DJLoginPage";

import AdminLayout from "./components/admin/AdminLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminEventsPage from "./pages/admin/AdminEventsPage";
import CreateEventPage from "./pages/admin/CreateEventPage";
import EventDetailPage from "./pages/admin/EventDetailPage";
import AdminAnalyticsPage from "./pages/admin/AdminAnalyticsPage";
import ClubSettingsPage from "./pages/admin/ClubSettingsPage";

import DJLayout from "./components/dj/DJLayout";
import DJDashboard from "./pages/dj/DJDashboard";
import DJEventPage from "./pages/dj/DJEventPage";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/event/:slug" element={<UserEventPage />} />

          <Route path="/admin/login" element={<AdminLoginPage />} />
          <Route path="/admin" element={<AdminLayout />}>
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="events" element={<AdminEventsPage />} />
            <Route path="events/new" element={<CreateEventPage />} />
            <Route path="events/:id" element={<EventDetailPage />} />
            <Route path="analytics" element={<AdminAnalyticsPage />} />
            <Route path="settings" element={<ClubSettingsPage />} />
          </Route>

          <Route path="/dj/login" element={<DJLoginPage />} />
          <Route path="/dj" element={<DJLayout />}>
            <Route path="dashboard" element={<DJDashboard />} />
            <Route path="event/:id" element={<DJEventPage />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;