import { FloatingOrb } from './FloatingOrb';
import { motion } from 'framer-motion';

export function AnimatedBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.14),_transparent_30%),radial-gradient(circle_at_80%_20%,_rgba(168,85,247,0.14),_transparent_28%),radial-gradient(circle_at_50%_80%,_rgba(59,130,246,0.10),_transparent_30%)]" />

      <FloatingOrb className="left-[8%] top-[12%] h-56 w-56 bg-cyan-400/18" />
      <FloatingOrb className="right-[10%] top-[18%] h-72 w-72 bg-fuchsia-500/14" delay={0.8} />
      <FloatingOrb className="bottom-[10%] left-[24%] h-64 w-64 bg-blue-500/12" delay={1.4} />

      <motion.div
        className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"
        animate={{
          opacity: [0.2, 0.5, 0.2],
          scaleX: [0.9, 1, 0.9],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      <div className="absolute inset-0 opacity-[0.06] [background-image:radial-gradient(rgba(255,255,255,0.7)_0.6px,transparent_0.6px)] [background-size:24px_24px]" />

      <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(255,255,255,0.03),transparent_25%,transparent_75%,rgba(255,255,255,0.02))]" />
    </div>
  );
}