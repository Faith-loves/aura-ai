import type {
  ExecutionResponse,
} from "./api";

export type DashboardSubsystemStatus = "healthy" | "degraded" | "unavailable";

export type DashboardMetric = {
  label: string;
  value: string;
  detail: string;
  status: DashboardSubsystemStatus;
};

export type SystemStatusItem = {
  label: "API" | "Model" | "Memory" | "Safety" | "Tools";
  value: string;
  status: DashboardSubsystemStatus;
};

export type ActiveExecutionSummary = {
  id: string;
  goal: string;
  status: string;
  statusLabel: string;
  elapsedLabel: string;
  progress: number;
  planLabel: string;
  currentLabel: string;
  safetyLabel: string;
} | null;

export type DashboardData = {
  systemHealthy: boolean;
  serviceName: string;
  kernelStatus: DashboardSubsystemStatus;
  backendStatus: DashboardSubsystemStatus;
  defaultModel: string | null;
  fallbackModel: string | null;
  modelStatus: DashboardSubsystemStatus;
  providerCount: number;
  toolCount: number;
  healthyToolCount: number;
  executionCount: number;
  activeExecutionCount: number;
  memoryCount: number | null;
  memoryStatus: DashboardSubsystemStatus;
  safetyActive: boolean;
  safetyStatus: DashboardSubsystemStatus;
  pendingApprovalCount: number | null;
  auditCount: number | null;
  reliabilityStateCount: number;
  openCircuitCount: number;
  activeExecution: ActiveExecutionSummary;
  metrics: DashboardMetric[];
  systemStatus: SystemStatusItem[];
  unavailableSections: string[];
  endpointErrors: Record<string, string>;
  rawExecutions: ExecutionResponse[];
};
