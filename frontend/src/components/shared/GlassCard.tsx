import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  glow?: 'cyan' | 'magenta' | 'purple' | 'none';
}

export function GlassCard({ children, className, glow = 'none' }: GlassCardProps) {
  return (
    <div
      className={cn(
        'glass rounded-xl p-4',
        glow === 'cyan' && 'glow-cyan',
        glow === 'magenta' && 'glow-magenta',
        glow === 'purple' && 'glow-purple',
        className
      )}
    >
      {children}
    </div>
  );
}
