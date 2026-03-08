import { motion, useSpring } from 'framer-motion';
import { useEffect } from 'react';
import { useMousePosition } from '@/hooks/useMousePosition';

export function MouseGlow() {
  const { x, y } = useMousePosition();

  const springX = useSpring(x, {
    stiffness: 90,
    damping: 20,
    mass: 0.4,
  });

  const springY = useSpring(y, {
    stiffness: 90,
    damping: 20,
    mass: 0.4,
  });

  useEffect(() => {
    springX.set(x);
    springY.set(y);
  }, [x, y, springX, springY]);

  return (
    <motion.div
      className="pointer-events-none fixed left-0 top-0 z-0 hidden h-80 w-80 rounded-full bg-cyan-400/12 blur-3xl md:block"
      style={{
        x: springX,
        y: springY,
        translateX: '-50%',
        translateY: '-50%',
      }}
    />
  );
}