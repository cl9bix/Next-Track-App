import { Music, ArrowRight, Disc3, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/shared/GlassCard';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function Index() {
  return (
    <div className="min-h-screen gradient-bg flex flex-col">
      {/* Hero */}
      <div className="flex-1 flex items-center justify-center px-4 py-16">
        <div className="max-w-2xl mx-auto text-center space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-4"
          >
            <div className="w-20 h-20 rounded-3xl bg-primary/20 flex items-center justify-center mx-auto glow-cyan">
              <Music className="h-10 w-10 text-primary" />
            </div>
            <h1 className="text-5xl md:text-6xl font-display font-bold leading-tight">
              <span className="text-gradient">Next Track</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-md mx-auto">
              Real-time music voting for clubs, bars & events.
              Your audience picks the vibe.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-3"
          >
            <Button variant="glow" size="lg" asChild>
              <Link to="/event/demo">
                Try Demo <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </Button>
            <Button variant="glass" size="lg" asChild>
              <Link to="/admin/login">Admin Panel</Link>
            </Button>
          </motion.div>

          {/* Role Cards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-8"
          >
            <GlassCard className="space-y-3 text-center">
              <Music className="h-8 w-8 text-primary mx-auto" />
              <h3 className="font-display font-semibold">Visitors</h3>
              <p className="text-xs text-muted-foreground">Vote for tracks, suggest songs, enjoy the vibe</p>
              <Button variant="vote" size="sm" asChild>
                <Link to="/event/demo">Join Event</Link>
              </Button>
            </GlassCard>

            <GlassCard className="space-y-3 text-center">
              <Shield className="h-8 w-8 text-accent mx-auto" />
              <h3 className="font-display font-semibold">Club Owners</h3>
              <p className="text-xs text-muted-foreground">Manage events, assign DJs, view analytics</p>
              <Button variant="outline" size="sm" asChild>
                <Link to="/admin/login">Admin Login</Link>
              </Button>
            </GlassCard>

            <GlassCard className="space-y-3 text-center">
              <Disc3 className="h-8 w-8 text-secondary mx-auto" />
              <h3 className="font-display font-semibold">DJs</h3>
              <p className="text-xs text-muted-foreground">Control rounds, manage queue, play winners</p>
              <Button variant="outline" size="sm" asChild>
                <Link to="/dj/login">DJ Login</Link>
              </Button>
            </GlassCard>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center py-6 text-xs text-muted-foreground">
        Next Track — Real-time music democracy
      </footer>
    </div>
  );
}
