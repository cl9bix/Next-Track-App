import { Variants } from 'framer-motion';

export const fadeUp = (delay = 0): Variants => ({
  hidden: {
    opacity: 0,
    y: 24,
    filter: 'blur(8px)',
  },
  visible: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: {
      duration: 0.8,
      delay,
      ease: [0.22, 1, 0.36, 1],
    },
  },
});

export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.14,
      delayChildren: 0.12,
    },
  },
};

export const scaleIn: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.92,
    y: 18,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.7,
      ease: [0.22, 1, 0.36, 1],
    },
  },
};

export const floating: Variants = {
  animate: {
    y: [0, -10, 0, 8, 0],
    x: [0, 6, 0, -6, 0],
    transition: {
      duration: 10,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

export const rotateSlow: Variants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 18,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};