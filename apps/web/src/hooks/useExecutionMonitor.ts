"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { getExecution } from "@/lib/api/executions";
import { isExecutionActive, isExecutionTerminal } from "@/lib/executions/status";
import type { ExecutionResponse } from "@/types/api";

const ACTIVE_POLL_MS = 2000;
const PAUSED_POLL_MS = 6000;
const HIDDEN_POLL_MS = 10000;
const MAX_DEGRADED_FAILURES = 3;

type RefreshOptions = {
  refresh?: boolean;
};

export function useExecutionMonitor(executionId: string) {
  const [data, setData] = useState<ExecutionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [failureCount, setFailureCount] = useState(0);
  const mountedRef = useRef(true);
  const fetchingRef = useRef(false);

  const refresh = useCallback(async ({ refresh = true }: RefreshOptions = {}) => {
    if (fetchingRef.current) return;
    fetchingRef.current = true;

    if (refresh) setRefreshing(true);
    else setLoading(true);

    try {
      const execution = await getExecution(executionId);
      if (!mountedRef.current) return;
      setData(execution);
      setError(null);
      setFailureCount(0);
      setLastUpdated(new Date());
    } catch (nextError) {
      if (!mountedRef.current) return;
      setFailureCount((current) => current + 1);
      setError(nextError instanceof Error ? nextError.message : "Unable to refresh execution.");
    } finally {
      if (mountedRef.current) {
        setLoading(false);
        setRefreshing(false);
      }
      fetchingRef.current = false;
    }
  }, [executionId]);

  useEffect(() => {
    mountedRef.current = true;

    const timeoutId = window.setTimeout(() => {
      setData(null);
      setLoading(true);
      setRefreshing(false);
      setError(null);
      setLastUpdated(null);
      setFailureCount(0);
      void refresh({ refresh: false });
    }, 0);

    return () => {
      mountedRef.current = false;
      window.clearTimeout(timeoutId);
    };
  }, [executionId, refresh]);

  useEffect(() => {
    if (!data || isExecutionTerminal(data.status)) return;
    if (!isExecutionActive(data.status)) return;
    if (failureCount >= MAX_DEGRADED_FAILURES) return;

    const intervalMs = document.visibilityState === "hidden" ? HIDDEN_POLL_MS : data.status === "paused" ? PAUSED_POLL_MS : ACTIVE_POLL_MS;
    const intervalId = window.setInterval(() => {
      void refresh({ refresh: true });
    }, intervalMs);

    return () => window.clearInterval(intervalId);
  }, [data?.id, data?.status, failureCount, refresh, data]);

  useEffect(() => {
    function handleVisibilityChange() {
      if (document.visibilityState === "visible" && data && !isExecutionTerminal(data.status)) {
        void refresh({ refresh: true });
      }
    }

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [data, refresh]);

  const isMonitoring = Boolean(data && isExecutionActive(data.status) && !isExecutionTerminal(data.status) && failureCount < MAX_DEGRADED_FAILURES);
  const monitoringUnavailable = failureCount >= MAX_DEGRADED_FAILURES;

  return {
    data,
    loading,
    error,
    refreshing,
    isMonitoring,
    monitoringUnavailable,
    lastUpdated,
    refresh,
    updateSnapshot: setData,
  };
}

export { ACTIVE_POLL_MS };

