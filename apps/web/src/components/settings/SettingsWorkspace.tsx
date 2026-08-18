"use client";

import Link from "next/link";
import { ExternalLink, RefreshCw, RotateCcw, Server, ShieldCheck } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import SettingRow from "@/components/settings/SettingRow";
import SettingsSection from "@/components/settings/SettingsSection";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Switch from "@/components/ui/Switch";
import { useInterfacePreferences } from "@/hooks/useInterfacePreferences";
import { API_BASE_URL, getModelProviders, getRuntimeInfo, getSettingsHealth, getSettingsReliabilityStates, getSettingsSafetyPolicy } from "@/lib/api/settings";
import type { HealthResponse, ModelsResponse, ReliabilityStateResponse, RootResponse, SafetyPolicyResponse } from "@/types/api";

const sections = ["General", "Models", "Execution", "Safety", "Interface", "About"] as const;

type Section = typeof sections[number];

type SettingsData = {
  runtime: RootResponse | null;
  health: HealthResponse | null;
  models: ModelsResponse | null;
  safety: SafetyPolicyResponse | null;
  reliability: ReliabilityStateResponse[] | null;
};

function title(value: string) {
  return value.split("_").map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`).join(" ");
}

function policyValue(enabled: boolean, trueText: string, falseText: string) {
  return <Badge variant={enabled ? "success" : "danger"}>{enabled ? trueText : falseText}</Badge>;
}

function statusBadge(healthy?: boolean | null) {
  if (healthy === true) return <Badge variant="success">Online</Badge>;
  if (healthy === false) return <Badge variant="danger">Unavailable</Badge>;
  return <Badge variant="warning">Unknown</Badge>;
}

export default function SettingsWorkspace() {
  const { preferences, updatePreference, resetPreferences } = useInterfacePreferences();
  const [active, setActive] = useState<Section>("General");
  const [data, setData] = useState<SettingsData>({ runtime: null, health: null, models: null, safety: null, reliability: null });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [connectionMessage, setConnectionMessage] = useState<string | null>(null);
  const [lastHealthCheck, setLastHealthCheck] = useState<Date | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const loadSettings = useCallback(async ({ refresh = false }: { refresh?: boolean } = {}) => {
    if (refresh) setRefreshing(true);
    else setLoading(true);
    const settled = await Promise.allSettled([getRuntimeInfo(), getSettingsHealth(), getModelProviders(), getSettingsSafetyPolicy(), getSettingsReliabilityStates()]);
    setData({
      runtime: settled[0].status === "fulfilled" ? settled[0].value : null,
      health: settled[1].status === "fulfilled" ? settled[1].value : null,
      models: settled[2].status === "fulfilled" ? settled[2].value : null,
      safety: settled[3].status === "fulfilled" ? settled[3].value : null,
      reliability: settled[4].status === "fulfilled" ? settled[4].value : null,
    });
    setErrors(Object.fromEntries(settled.map((result, index) => [String(index), result.status === "rejected" ? (result.reason instanceof Error ? result.reason.message : "Unavailable") : ""]).filter(([, value]) => value)));
    if (settled[1].status === "fulfilled") setLastHealthCheck(new Date());
    setLoading(false);
    setRefreshing(false);
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => { void loadSettings(); }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadSettings]);

  async function testConnection() {
    setConnectionMessage("Testing connection...");
    try {
      const health = await getSettingsHealth();
      setData((current) => ({ ...current, health }));
      setLastHealthCheck(new Date());
      setConnectionMessage("Connection successful.");
    } catch {
      setConnectionMessage("Unable to reach AURA backend.");
    }
  }

  const openCircuits = useMemo(() => data.reliability?.filter((state) => state.circuit_open).length ?? 0, [data.reliability]);
  const apiOnline = data.health?.status === "healthy";

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <section className="rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Badge variant="purple">AURA / Settings</Badge>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-[#F8FAFC]">Settings</h1>
            <p className="mt-2 text-sm text-[#94A3B8]">Configure and inspect the AURA runtime.</p>
          </div>
          <div className="flex flex-wrap items-center gap-3"><Badge variant="info">Local Runtime</Badge><Button variant="secondary" onClick={() => loadSettings({ refresh: true })} disabled={refreshing}><RefreshCw size={16} className={refreshing && !preferences.reduceMotion ? "animate-spin" : ""} />Refresh</Button></div>
        </div>
      </section>

      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Settings sections">{sections.map((section) => <button key={section} type="button" onClick={() => setActive(section)} aria-pressed={active === section} className={`rounded-full border px-4 py-2 text-sm transition ${active === section ? "border-[#7C5CFC] bg-[#7C5CFC]/18 text-white" : "border-[#26334D] bg-[#111A2E] text-[#94A3B8] hover:text-white"}`}>{section}</button>)}</div>

      {loading ? <div className="h-96 animate-pulse rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78" /> : (
        <>
          {Object.keys(errors).length > 0 && <p className="rounded-xl border border-[#F59E0B]/30 bg-[#F59E0B]/10 px-3 py-2 text-sm text-[#FCD34D]">Some settings data is unavailable. Loaded sections remain visible.</p>}

          {active === "General" && <SettingsSection title="General" description="Runtime identity and API connection state.">
            <SettingRow label="Application" value={data.runtime?.name ?? "AURA"} readOnly />
            <SettingRow label="Version" value={data.runtime?.version ?? "Unavailable"} readOnly />
            <SettingRow label="Environment" value={title(data.runtime?.environment ?? "unknown")} readOnly />
            <SettingRow label="Backend API" description="Configured frontend API base URL." value={API_BASE_URL} readOnly />
            <SettingRow label="API Status" value={statusBadge(apiOnline)} readOnly />
            <SettingRow label="Last successful health check" value={lastHealthCheck ? lastHealthCheck.toLocaleTimeString() : "Not checked"} readOnly />
            <div className="mt-5 flex flex-wrap items-center gap-3"><Button onClick={testConnection}><Server size={16} />Test Connection</Button>{connectionMessage && <span className="text-sm text-[#94A3B8]">{connectionMessage}</span>}</div>
          </SettingsSection>}

          {active === "Models" && <SettingsSection title="Models" description="Model provider status exposed by the backend.">
            <SettingRow label="Default Provider" value={data.models?.default_provider ?? "Unavailable"} readOnly />
            <SettingRow label="Fallback Provider" value={data.models?.fallback_provider ?? "Unavailable"} readOnly />
            <p className="mt-5 rounded-xl border border-[#26334D] bg-[#111A2E] px-4 py-3 text-sm text-[#94A3B8]">Provider selection is currently configured by the AURA backend.</p>
            <div className="mt-5 grid gap-4 md:grid-cols-2">{data.models?.providers.map((provider) => <div key={provider.name} className="rounded-2xl border border-[#162036] bg-[#0A1020] p-4"><div className="flex items-start justify-between gap-3"><h3 className="text-lg font-semibold text-white">{title(provider.name)}</h3>{statusBadge(provider.healthy)}</div><p className="mt-2 text-sm text-[#94A3B8]">Model: {provider.model}</p><div className="mt-4 flex flex-wrap gap-2">{provider.default && <Badge variant="purple">Default</Badge>}{provider.fallback && <Badge variant="info">Fallback</Badge>}</div></div>) ?? <p className="text-sm text-[#94A3B8]">Model provider data unavailable.</p>}</div>
          </SettingsSection>}

          {active === "Execution" && <SettingsSection title="Execution Protection" description="Runtime-enforced execution limits verified from backend implementation. No public settings API currently exposes edits.">
            <SettingRow label="Maximum Steps" value="50" readOnly />
            <SettingRow label="Maximum Iterations" value="100" readOnly />
            <SettingRow label="Maximum Failures" value="3" readOnly />
            <SettingRow label="Status" value={<Badge variant="success">Runtime enforced</Badge>} readOnly />
          </SettingsSection>}

          {active === "Safety" && <SettingsSection title="Safety" description="Concise safety and reliability summary. Full controls remain in Safety Center.">
            <SettingRow label="Policy" value={title(data.safety?.name ?? "unavailable")} readOnly />
            <SettingRow label="Low Risk" value={data.safety ? policyValue(data.safety.allow_low_risk, "Allowed", "Blocked") : "Unavailable"} readOnly />
            <SettingRow label="Medium Risk" value={data.safety ? policyValue(data.safety.allow_medium_risk, "Allowed", "Blocked") : "Unavailable"} readOnly />
            <SettingRow label="High Risk" value={data.safety ? policyValue(data.safety.require_approval_for_high_risk, "Approval Required", "Allowed") : "Unavailable"} readOnly />
            <SettingRow label="Critical Risk" value={data.safety ? policyValue(data.safety.block_critical_risk, "Blocked", "Allowed") : "Unavailable"} readOnly />
            <SettingRow label="Reliability State" description="Policy values are not exposed publicly; tool state is available." value={`${data.reliability?.length ?? 0} tracked tools · ${openCircuits} open circuits`} readOnly />
            <div className="mt-5 flex flex-wrap gap-2"><Link href="/system"><Button variant="secondary"><ShieldCheck size={16} />Open Safety Center</Button></Link><Link href="/approvals"><Button variant="secondary">View Approvals</Button></Link><Link href="/audit"><Button variant="secondary">View Audit Log</Button></Link></div>
          </SettingsSection>}

          {active === "Interface" && <SettingsSection title="Interface" description="Frontend-only preferences stored safely in this browser.">
            <Preference label="Compact Navigation" description="Sets a local preference flag for compact navigation layouts." checked={preferences.compactNavigation} onChange={(value) => updatePreference("compactNavigation", value)} />
            <Preference label="Show Technical IDs" description="Sets a local preference flag for full technical identifiers where supported." checked={preferences.showTechnicalIds} onChange={(value) => updatePreference("showTechnicalIds", value)} />
            <Preference label="Reduce Motion" description="Reduces decorative motion in settings and shared preference-aware UI." checked={preferences.reduceMotion} onChange={(value) => updatePreference("reduceMotion", value)} />
            <Preference label="Dashboard Auto Refresh" description="Controls the dashboard active-execution auto-refresh loop." checked={preferences.dashboardAutoRefresh} onChange={(value) => updatePreference("dashboardAutoRefresh", value)} />
            <Button className="mt-5" variant="secondary" onClick={() => { if (window.confirm("Reset only frontend interface preferences?")) resetPreferences(); }}><RotateCcw size={16} />Reset Interface Preferences</Button>
          </SettingsSection>}

          {active === "About" && <SettingsSection title="About AURA" description="Public application/runtime information.">
            <SettingRow label="Application Name" value={data.runtime?.name ?? "AURA"} readOnly />
            <SettingRow label="Version" value={data.runtime?.version ?? "Unavailable"} readOnly />
            <SettingRow label="Frontend" value="Next.js" readOnly />
            <SettingRow label="Backend" value="FastAPI" readOnly />
            <SettingRow label="Runtime" value="AURA autonomous AI system" readOnly />
            <SettingRow label="API Documentation" value={<a href={`${API_BASE_URL}/docs`} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-[#9B87FF] hover:text-white">Open Swagger Docs <ExternalLink size={14} /></a>} readOnly />
          </SettingsSection>}
        </>
      )}
    </div>
  );
}

function Preference({ label, description, checked, onChange }: { label: string; description: string; checked: boolean; onChange: (value: boolean) => void }) {
  return <SettingRow label={label} description={description} value={<Switch label={label} checked={checked} onCheckedChange={onChange} />} />;
}
