import { useEffect, useState } from 'react';

interface CountdownProps {
  targetDate: string;
  onComplete?: () => void;
  className?: string;
}

export function Countdown({ targetDate, onComplete, className }: CountdownProps) {
  const [timeLeft, setTimeLeft] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      const diff = new Date(targetDate).getTime() - Date.now();
      if (diff <= 0) {
        setTimeLeft('0:00');
        onComplete?.();
        clearInterval(interval);
        return;
      }
      const minutes = Math.floor(diff / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      setTimeLeft(`${minutes}:${seconds.toString().padStart(2, '0')}`);
    }, 1000);
    return () => clearInterval(interval);
  }, [targetDate, onComplete]);

  return (
    <span className={className}>
      {timeLeft}
    </span>
  );
}
