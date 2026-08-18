"use client";

import { useEffect, useState } from "react";

function formatElapsed(totalSeconds: number) {
  const seconds = Math.max(0, totalSeconds);
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;

  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
}

function elapsedSeconds(startedAt: string | null, completedAt: string | null, durationMs: number | null) {
  if (durationMs !== null) return Math.round(durationMs / 1000);
  if (!startedAt) return 0;

  const startTime = Date.parse(startedAt);
  if (Number.isNaN(startTime)) return 0;

  const endTime = completedAt ? Date.parse(completedAt) : Date.now();
  if (Number.isNaN(endTime)) return 0;

  return Math.round((endTime - startTime) / 1000);
}

type ElapsedTimeProps = {
  startedAt: string | null;
  completedAt: string | null;
  durationMs: number | null;
  running: boolean;
};

export default function ElapsedTime({ startedAt, completedAt, durationMs, running }: ElapsedTimeProps) {
  const [, setTick] = useState(0);

  useEffect(() => {
    if (!running || !startedAt || completedAt || durationMs !== null) return;
    const intervalId = window.setInterval(() => setTick((current) => current + 1), 1000);
    return () => window.clearInterval(intervalId);
  }, [completedAt, durationMs, running, startedAt]);

  const label = formatElapsed(elapsedSeconds(startedAt, completedAt, durationMs));

  return <span>{startedAt ? label : "Not started"}</span>;
}


