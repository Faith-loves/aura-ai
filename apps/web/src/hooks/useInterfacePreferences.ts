"use client";

import { useCallback, useEffect, useState } from "react";

import { DEFAULT_INTERFACE_PREFERENCES, type InterfacePreferences } from "@/types/settings";

const STORAGE_KEY = "aura-interface-preferences";

function parsePreferences(value: string | null): InterfacePreferences {
  if (!value) return DEFAULT_INTERFACE_PREFERENCES;
  try {
    const parsed = JSON.parse(value) as Partial<InterfacePreferences>;
    return { ...DEFAULT_INTERFACE_PREFERENCES, ...parsed };
  } catch {
    return DEFAULT_INTERFACE_PREFERENCES;
  }
}

function applyPreferences(preferences: InterfacePreferences) {
  document.documentElement.dataset.auraReduceMotion = preferences.reduceMotion ? "true" : "false";
  document.documentElement.dataset.auraCompactNavigation = preferences.compactNavigation ? "true" : "false";
  document.documentElement.dataset.auraShowTechnicalIds = preferences.showTechnicalIds ? "true" : "false";
  document.documentElement.dataset.auraDashboardAutoRefresh = preferences.dashboardAutoRefresh ? "true" : "false";
}

export function useInterfacePreferences() {
  const [preferences, setPreferences] = useState<InterfacePreferences>(DEFAULT_INTERFACE_PREFERENCES);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      const stored = parsePreferences(window.localStorage.getItem(STORAGE_KEY));
      setPreferences(stored);
      applyPreferences(stored);
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, []);

  const persist = useCallback((next: InterfacePreferences) => {
    setPreferences(next);
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    applyPreferences(next);
  }, []);

  const updatePreference = useCallback(<K extends keyof InterfacePreferences>(key: K, value: InterfacePreferences[K]) => {
    setPreferences((current) => {
      const next = { ...current, [key]: value };
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      applyPreferences(next);
      return next;
    });
  }, []);

  const resetPreferences = useCallback(() => {
    window.localStorage.removeItem(STORAGE_KEY);
    persist(DEFAULT_INTERFACE_PREFERENCES);
  }, [persist]);

  return { preferences, updatePreference, resetPreferences };
}

export { STORAGE_KEY as INTERFACE_PREFERENCES_STORAGE_KEY };
