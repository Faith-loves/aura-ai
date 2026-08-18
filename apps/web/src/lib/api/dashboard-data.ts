import type {
  ApprovalResponse,
  ExecutionResponse,
  HealthResponse,
  MemoryStatsResponse,
  ModelsResponse,
  ReliabilityStateResponse,
  SafetyPolicyResponse,
  ToolResponse,
} from "@/types/api";
import type {
  ActiveExecutionSummary,
  DashboardData,
  DashboardSubsystemStatus,
  SystemStatusItem,
} from "@/types/dashboard";

import {
  getApprovals,
  getAuditRecords,
  getExecutions,
  getHealth,
  getMemoryStats,
  getModels,
  getReliabilityStates,
  getSafetyPolicy,
  getTools,
} from "./dashboard";

type EndpointKey =
  | "health"
  | "models"
  | "tools"
  | "executions"
  | "memory"
  | "policy"
  | "approvals"
  | "audit"
  | "reliability";

type EndpointMap = {
  health: HealthResponse;
  models: ModelsResponse;
  tools: ToolResponse[];
  executions: ExecutionResponse[];
  memory: MemoryStatsResponse;
  policy: SafetyPolicyResponse;
  approvals: ApprovalResponse[];
  audit: Awaited<ReturnType<typeof getAuditRecords>>;
  reliability: ReliabilityStateResponse[];
};

type EndpointResult<K extends EndpointKey> = {
  key: K;
  result: PromiseSettledResult<EndpointMap[K]>;
};

const endpointLabels: Record<EndpointKey, string> = {
  health: "API",
  models: "Model",
  tools: "Tools",
  executions: "Executions",
  memory: "Memory",
  policy: "Safety policy",
  approvals: "Approvals",
  audit: "Audit",
  reliability: "Reliability",
};

function fulfilled<K extends EndpointKey>(entry: EndpointResult<K>) {
  return entry.result.status === "fulfilled";
}

function value<K extends EndpointKey>(entry: EndpointResult<K>) {
  return entry.result.status === "fulfilled" ? entry.result.value : null;
}

function errorMessage(reason: unknown) {
  if (reason instanceof Error) {
    return reason.message;
  }

  if (typeof reason === "string") {
    return reason;
  }

  return "Unexpected response from AURA API.";
}

function resultError<K extends EndpointKey>(entry: EndpointResult<K>) {
  return entry.result.status === "rejected" ? errorMessage(entry.result.reason) : null;
}

function formatNumber(valueToFormat: number | null) {
  if (valueToFormat === null) {
    return "--";
  }

  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(valueToFormat);
}

function displayProvider(models: ModelsResponse | null) {
  if (!models?.default_provider) {
    return "Unavailable";
  }

  return models.default_provider;
}

function modelStatus(models: ModelsResponse | null): DashboardSubsystemStatus {
  if (!models) {
    return "unavailable";
  }

  const defaultProvider = models.providers.find((provider) => provider.default);

  if (defaultProvider?.healthy) {
    return "healthy";
  }

  return models.providers.some((provider) => provider.healthy) ? "degraded" : "unavailable";
}

function toolsHealth(
  tools: ToolResponse[] | null,
  reliability: ReliabilityStateResponse[] | null,
): {
  toolCount: number;
  healthyToolCount: number;
  status: DashboardSubsystemStatus;
} {
  const toolCount = tools?.length ?? 0;

  if (!tools) {
    return {
      toolCount: 0,
      healthyToolCount: 0,
      status: "unavailable" as DashboardSubsystemStatus,
    };
  }

  if (!reliability) {
    return {
      toolCount,
      healthyToolCount: toolCount,
      status: "healthy" as DashboardSubsystemStatus,
    };
  }

  const openCircuits = new Set(
    reliability
      .filter((state) => state.circuit_open)
      .map((state) => state.tool_name),
  );
  const healthyToolCount = tools.filter((tool) => !openCircuits.has(tool.name)).length;
  const status: DashboardSubsystemStatus = healthyToolCount === toolCount ? "healthy" : healthyToolCount > 0 ? "degraded" : "unavailable";

  return {
    toolCount,
    healthyToolCount,
    status,
  };
}

function latestExecution(executions: ExecutionResponse[]) {
  return [...executions].sort((first, second) => {
    const firstTime = Date.parse(first.started_at ?? first.completed_at ?? "");
    const secondTime = Date.parse(second.started_at ?? second.completed_at ?? "");

    return (Number.isNaN(secondTime) ? 0 : secondTime) - (Number.isNaN(firstTime) ? 0 : firstTime);
  })[0] ?? null;
}

function selectActiveExecution(executions: ExecutionResponse[]) {
  return (
    executions.find((execution) => execution.status === "running") ??
    executions.find((execution) => execution.status === "paused") ??
    latestExecution(executions)
  );
}

function titleCase(valueToFormat: string) {
  return valueToFormat
    .split("_")
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(" ");
}

function elapsedLabel(execution: ExecutionResponse) {
  if (execution.duration_ms !== null) {
    return `${Math.max(0, Math.round(execution.duration_ms / 1000))}s elapsed`;
  }

  if (!execution.started_at) {
    return "Not started";
  }

  const startedAt = Date.parse(execution.started_at);

  if (Number.isNaN(startedAt)) {
    return "Elapsed unavailable";
  }

  const elapsedSeconds = Math.max(0, Math.round((Date.now() - startedAt) / 1000));
  const minutes = Math.floor(elapsedSeconds / 60).toString().padStart(2, "0");
  const seconds = (elapsedSeconds % 60).toString().padStart(2, "0");

  return `${minutes}:${seconds} elapsed`;
}

function currentStep(execution: ExecutionResponse) {
  if (execution.current_step_id) {
    return (
      execution.step_executions.find((step) => step.plan_step_id === execution.current_step_id) ??
      execution.step_executions.find((step) => step.id === execution.current_step_id) ??
      null
    );
  }

  return (
    execution.step_executions.find((step) => step.status === "running") ??
    execution.step_executions.find((step) => step.status === "ready") ??
    execution.step_executions.find((step) => step.status === "pending") ??
    null
  );
}

function safetyLabel(execution: ExecutionResponse) {
  const step = currentStep(execution);
  const metadata = step?.metadata ?? execution.metadata;
  const approvalStatus = metadata.approval_status;
  const decision = metadata.decision;
  const allowed = metadata.allowed;
  const requiresApproval = metadata.requires_approval;

  if (approvalStatus === "approved") {
    return "Approved";
  }

  if (approvalStatus === "rejected") {
    return "Denied";
  }

  if (approvalStatus === "pending" || decision === "require_approval" || requiresApproval === true) {
    return "Approval required";
  }

  if (decision === "deny" || allowed === false) {
    return "Denied";
  }

  if (decision === "allow" || allowed === true) {
    return "Allowed";
  }

  return "Not evaluated";
}

function summarizeExecution(execution: ExecutionResponse | null): ActiveExecutionSummary {
  if (!execution) {
    return null;
  }

  const totalSteps = execution.step_executions.length;
  const completedSteps = execution.step_executions.filter((step) =>
    ["completed", "skipped"].includes(step.status),
  ).length;
  const progress = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;
  const step = currentStep(execution);

  return {
    id: execution.id,
    goal: execution.goal,
    status: execution.status,
    statusLabel: titleCase(execution.status),
    elapsedLabel: elapsedLabel(execution),
    progress,
    planLabel: totalSteps > 0 ? `${completedSteps} / ${totalSteps} steps` : "No steps",
    currentLabel: step?.title ?? (execution.status === "completed" ? "Complete" : "No current step"),
    safetyLabel: safetyLabel(execution),
  };
}

function systemStatusItems({
  health,
  models,
  memory,
  policy,
  toolsLabel,
  toolsStatus,
}: {
  health: HealthResponse | null;
  models: ModelsResponse | null;
  memory: MemoryStatsResponse | null;
  policy: SafetyPolicyResponse | null;
  toolsLabel: string;
  toolsStatus: DashboardSubsystemStatus;
}): SystemStatusItem[] {
  const apiStatus: DashboardSubsystemStatus = health?.status === "healthy" ? "healthy" : health ? "degraded" : "unavailable";

  return [
    {
      label: "API",
      value: health?.status === "healthy" ? "Healthy" : health ? titleCase(health.status) : "Unavailable",
      status: apiStatus,
    },
    {
      label: "Model",
      value: displayProvider(models),
      status: modelStatus(models),
    },
    {
      label: "Memory",
      value: memory ? "Connected" : "Unavailable",
      status: memory ? "healthy" : "unavailable",
    },
    {
      label: "Safety",
      value: policy ? "Active" : "Unavailable",
      status: policy ? "healthy" : "unavailable",
    },
    {
      label: "Tools",
      value: toolsLabel,
      status: toolsStatus,
    },
  ];
}

export async function getDashboardData(): Promise<DashboardData> {
  const settled = await Promise.allSettled([
    getHealth(),
    getModels(),
    getTools(),
    getExecutions(),
    getMemoryStats(),
    getSafetyPolicy(),
    getApprovals(),
    getAuditRecords(),
    getReliabilityStates(),
  ]);

  const results: {
    [K in EndpointKey]: EndpointResult<K>;
  } = {
    health: { key: "health", result: settled[0] as PromiseSettledResult<HealthResponse> },
    models: { key: "models", result: settled[1] as PromiseSettledResult<ModelsResponse> },
    tools: { key: "tools", result: settled[2] as PromiseSettledResult<ToolResponse[]> },
    executions: { key: "executions", result: settled[3] as PromiseSettledResult<ExecutionResponse[]> },
    memory: { key: "memory", result: settled[4] as PromiseSettledResult<MemoryStatsResponse> },
    policy: { key: "policy", result: settled[5] as PromiseSettledResult<SafetyPolicyResponse> },
    approvals: { key: "approvals", result: settled[6] as PromiseSettledResult<ApprovalResponse[]> },
    audit: { key: "audit", result: settled[7] as PromiseSettledResult<Awaited<ReturnType<typeof getAuditRecords>>> },
    reliability: { key: "reliability", result: settled[8] as PromiseSettledResult<ReliabilityStateResponse[]> },
  };

  const health = value(results.health);
  const models = value(results.models);
  const tools = value(results.tools);
  const executions = value(results.executions) ?? [];
  const memory = value(results.memory);
  const policy = value(results.policy);
  const approvals = value(results.approvals);
  const audit = value(results.audit);
  const reliability = value(results.reliability);

  const endpointErrors = Object.fromEntries(
    (Object.keys(results) as EndpointKey[])
      .map((key) => [key, resultError(results[key])])
      .filter((entry): entry is [EndpointKey, string] => typeof entry[1] === "string"),
  );
  const unavailableSections = (Object.keys(endpointErrors) as EndpointKey[]).map((key) => endpointLabels[key]);
  const activeExecutionCount = executions.filter((execution) => ["running", "paused"].includes(execution.status)).length;
  const selectedExecution = selectActiveExecution(executions);
  const toolHealth = toolsHealth(tools, reliability);
  const memoryCount = memory?.total ?? health?.kernel.memory_count ?? null;
  const pendingApprovalCount = approvals?.filter((approval) => approval.status === "pending").length ?? null;
  const openCircuitCount = reliability?.filter((state) => state.circuit_open).length ?? 0;
  const toolsLabel = tools ? `${toolHealth.healthyToolCount} / ${toolHealth.toolCount} healthy` : "Unavailable";
  const systemStatus = systemStatusItems({
    health,
    models,
    memory,
    policy,
    toolsLabel,
    toolsStatus: toolHealth.status,
  });
  const kernelStatus: DashboardSubsystemStatus = health?.kernel.ready ? "healthy" : health ? "degraded" : "unavailable";
  const backendStatus: DashboardSubsystemStatus = health?.status === "healthy" ? "healthy" : health ? "degraded" : "unavailable";
  const memoryStatus: DashboardSubsystemStatus = memory ? "healthy" : "unavailable";
  const safetyStatus: DashboardSubsystemStatus = policy ? "healthy" : "unavailable";
  const executionsStatus: DashboardSubsystemStatus = fulfilled(results.executions) ? "healthy" : "unavailable";

  return {
    systemHealthy: health?.status === "healthy",
    serviceName: health?.service ?? "AURA",
    kernelStatus,
    backendStatus,
    defaultModel: models?.default_provider ?? null,
    fallbackModel: models?.fallback_provider ?? null,
    modelStatus: modelStatus(models),
    providerCount: models?.providers.length ?? 0,
    toolCount: toolHealth.toolCount,
    healthyToolCount: toolHealth.healthyToolCount,
    executionCount: executions.length,
    activeExecutionCount,
    memoryCount,
    memoryStatus,
    safetyActive: policy !== null,
    safetyStatus,
    pendingApprovalCount,
    auditCount: audit?.length ?? null,
    reliabilityStateCount: reliability?.length ?? 0,
    openCircuitCount,
    activeExecution: summarizeExecution(selectedExecution),
    metrics: [
      {
        label: "Active Tasks",
        value: formatNumber(activeExecutionCount),
        detail: activeExecutionCount === 1 ? "running now" : "active now",
        status: executionsStatus,
      },
      {
        label: "Executions",
        value: formatNumber(executions.length),
        detail: "total executions",
        status: executionsStatus,
      },
      {
        label: "Memory Items",
        value: formatNumber(memoryCount),
        detail: memory ? "stored memories" : "memory unavailable",
        status: memoryStatus,
      },
      {
        label: "Tools Ready",
        value: tools ? formatNumber(toolHealth.toolCount) : "--",
        detail: tools ? `${toolHealth.healthyToolCount} / ${toolHealth.toolCount} healthy` : "tools unavailable",
        status: toolHealth.status,
      },
    ],
    systemStatus,
    unavailableSections,
    endpointErrors,
    rawExecutions: executions,
  };
}


