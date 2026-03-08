import { motion } from 'framer-motion';
import { floating } from '@/animations/variants';
import { cn } from '@/lib/utils';

type FloatingOrbProps = {
  className?: string;
  delay?: number;
};

export function FloatingOrb({ className, delay = 0 }: FloatingOrbProps) {
  return (
    <motion.div
      variants={floating}
      animate="animate"
      transition={{ delay }}
      className={cn(
        'absolute rounded-full blur-3xl will-change-transform',
        className
      )}
    />
  );
}