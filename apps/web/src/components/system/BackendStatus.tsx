"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  getHealth,
} from "@/lib/api/dashboard";
import type {
  DashboardSubsystemStatus,
} from "@/types/dashboard";

import StatusIndicator from "./StatusIndicator";

function labelForStatus(status: DashboardSubsystemStatus) {
  if (status === "healthy") {
    return "Online";
  }

  if (status === "degraded") {
    return "Degraded";
  }

  return "Offline";
}

export default function BackendStatus() {
  const [status, setStatus] = useState<DashboardSubsystemStatus>("degraded");

  useEffect(() => {
    let cancelled = false;

    async function checkHealth() {
      try {
        const health = await getHealth();

        if (!cancelled) {
          setStatus(health.status === "healthy" ? "healthy" : "degraded");
        }
      } catch {
        if (!cancelled) {
          setStatus("unavailable");
        }
      }
    }

    checkHealth();
    const intervalId = window.setInterval(checkHealth, 30000);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, []);

  return (
    <div className="hidden items-center gap-2 rounded-full border border-[#1D2942] bg-[#0D1321] px-3 py-2 text-xs font-medium text-[#94A3B8] sm:flex">
      <StatusIndicator status={status} label={labelForStatus(status)} />
    </div>
  );
}
