import React, { useEffect, useState } from 'react';
import './ProgressOverlay.css';

const ProgressOverlay = ({ duration = 3000, processDone = false, customMessage = 'AI가 결과를 준비 중이에요' }) => {
  const [width, setWidth] = useState(0);
  const [seconds, setSeconds] = useState((duration / 1000).toFixed(1));
  const [isOverDuration, setIsOverDuration] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const start = Date.now();

    const timer = setInterval(() => {
      const elapsed = Date.now() - start;
      const remaining = Math.max(duration - elapsed, 0);
      const progress = Math.min((elapsed / duration) * 100, 100);

      setWidth(progress);
      setSeconds((remaining / 1000).toFixed(1));

      if (progress >= 100) {
        clearInterval(timer);
        setIsOverDuration(true);
      }
    }, 50);

    return () => clearInterval(timer);
  }, [duration]);

  // processDone이 true이고 duration도 지났다면 종료
  useEffect(() => {
    if (processDone && isOverDuration) {
      const timeout = setTimeout(() => {
        setDone(true);
      }, 300); // 살짝 지연시켜 자연스럽게

      return () => clearTimeout(timeout);
    }
  }, [processDone, isOverDuration]);

  if (done) return null;

  return (
    <div className="progress-overlay">
      <div className="progress-bar" style={{ width: `${width}%` }}></div>
      <div className="progress-time">
        {isOverDuration && !processDone ? customMessage : `예상 소요시간 : ${seconds}s`}
      </div>
    </div>
  );
};

export default ProgressOverlay;
