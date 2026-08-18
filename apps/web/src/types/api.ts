export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export type RootResponse = {
  name: string;
  version: string;
  environment: string;
  status: string;
};

export type KernelStatus = {
  name: string;
  version: string;
  environment: string;
  ready: boolean;
  model_provider: string | null;
  model_provider_healthy: boolean;
  fallback_provider: string | null;
  memory_count: number;
  planner_available: boolean;
  tool_count: number;
  tool_executor_available: boolean;
};

export type HealthResponse = {
  status: "healthy" | "unavailable" | string;
  service: string;
  kernel: KernelStatus;
};

export type ModelProviderStatus = {
  name: string;
  model: string;
  healthy: boolean;
  default: boolean;
  fallback: boolean;
};

export type ModelsResponse = {
  default_provider: string | null;
  fallback_provider: string | null;
  providers: ModelProviderStatus[];
};

export type ToolParameterType = "string" | "integer" | "float" | "boolean" | "list" | "object";
export type ToolExecutionStatus = "success" | "failed";

export type ToolParameterResponse = {
  name: string;
  description: string;
  parameter_type: ToolParameterType;
  required: boolean;
  default: JsonValue;
  choices: JsonValue[] | null;
};

export type ToolResponse = {
  name: string;
  description: string;
  category: string;
  version: string;
  dangerous: boolean;
  requires_confirmation: boolean;
  tags: string[];
  parameters: ToolParameterResponse[];
};

export type ExecuteToolRequest = {
  arguments: Record<string, JsonValue>;
};

export type ToolExecutionResponse = {
  execution_id: string;
  tool_name: string | null;
  status: ToolExecutionStatus | null;
  success: boolean;
  output: JsonValue;
  error: string | null;
  error_code: string | null;
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  metadata: Record<string, JsonValue>;
};

export type PlanStatus = "pending" | "in_progress" | "completed" | "failed" | "cancelled";
export type PlanStepStatus = "pending" | "ready" | "in_progress" | "completed" | "failed" | "skipped";

export type CreatePlanRequest = {
  goal: string;
  metadata?: Record<string, JsonValue>;
};

export type UpdateStepPriorityRequest = {
  priority: number;
};

export type PlanStepResponse = {
  id: string;
  title: string;
  description: string;
  status: PlanStepStatus;
  priority: number;
  dependencies: string[];
  metadata: Record<string, JsonValue>;
};

export type PlanResponse = {
  id: string;
  goal: string;
  status: PlanStatus;
  steps: PlanStepResponse[];
  metadata: Record<string, JsonValue>;
};

export type ExecutionStatus = "pending" | "running" | "paused" | "completed" | "failed" | "cancelled";
export type StepExecutionStatus = "pending" | "ready" | "running" | "completed" | "failed" | "skipped";

export type CreateExecutionRequest = {
  plan_id: string;
  metadata?: Record<string, JsonValue>;
};

export type StepExecutionResponse = {
  id: string;
  plan_step_id: string;
  title: string;
  status: StepExecutionStatus;
  tool_name: string | null;
  arguments: Record<string, JsonValue>;
  tool_execution_id: string | null;
  output: JsonValue;
  error: string | null;
  error_code: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  metadata: Record<string, JsonValue>;
};

export type ExecutionResponse = {
  id: string;
  plan_id: string;
  goal: string;
  status: ExecutionStatus;
  step_executions: StepExecutionResponse[];
  current_step_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  error: string | null;
  error_code: string | null;
  metadata: Record<string, JsonValue>;
};

export type MemoryType = "conversation" | "fact" | "preference" | "project" | "task" | "system";

export type CreateMemoryRequest = {
  content: string;
  memory_type: MemoryType;
  importance?: number;
  metadata?: Record<string, JsonValue>;
};

export type SearchMemoryRequest = {
  query: string;
  limit?: number;
  memory_type?: MemoryType | null;
};

export type MemoryResponse = {
  id: string;
  memory_type: MemoryType;
  content: string;
  importance: number;
  access_count: number;
  metadata: Record<string, JsonValue>;
};

export type MemorySearchResult = {
  memory: MemoryResponse;
  score: number;
};

export type ImportMemoryRequest = {
  version?: number;
  memories: Record<string, JsonValue>[];
};

export type RestoreMemoryRequest = {
  file_path: string;
  clear_existing?: boolean;
};

export type MemoryExportResponse = {
  version: number;
  exported_at: string;
  count: number;
  memories: Record<string, JsonValue>[];
};

export type MemoryActionResponse = {
  success: boolean;
  deleted?: number;
  imported?: number;
  path?: string;
  message?: string;
  memory_id?: string;
  previous_count?: number;
  cleared?: number;
  current_count?: number;
};

export type MemoryStatsResponse = {
  total: number;
  by_type: Record<string, number>;
  most_accessed: {
    id: string;
    content: string;
    memory_type: string;
    access_count: number;
  }[];
  oldest: {
    id: string;
    content: string;
    memory_type: string;
    created_at: string;
  }[];
  average_importance: number;
};

export type SafetyPolicyResponse = {
  name: string;
  allow_low_risk: boolean;
  allow_medium_risk: boolean;
  require_approval_for_high_risk: boolean;
  block_critical_risk: boolean;
  metadata: Record<string, JsonValue>;
};

export type ApprovalStatus = "not_required" | "pending" | "approved" | "rejected";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type PermissionDecision = "allow" | "deny" | "require_approval";
export type AuditEventType =
  | "safety_allowed"
  | "safety_denied"
  | "approval_required"
  | "approval_created"
  | "approval_approved"
  | "approval_rejected"
  | "tool_execution_started"
  | "tool_execution_succeeded"
  | "tool_execution_failed"
  | "execution_paused"
  | "execution_resumed"
  | "execution_failed";

export type ApprovalDecisionRequest = {
  resolved_by?: string | null;
  reason?: string | null;
};

export type ApprovalResponse = {
  id: string;
  status: ApprovalStatus;
  risk_level: RiskLevel;
  reason: string;
  safety_decision_id: string | null;
  tool_name: string | null;
  execution_id: string | null;
  plan_id: string | null;
  step_id: string | null;
  requested_at: string;
  resolved_at: string | null;
  resolved_by: string | null;
  resolution_reason: string | null;
  metadata: Record<string, JsonValue>;
};

export type AuditResponse = {
  id: string;
  event_type: AuditEventType;
  message: string;
  execution_id: string | null;
  plan_id: string | null;
  step_id: string | null;
  tool_name: string | null;
  approval_id: string | null;
  risk_level: RiskLevel | string | null;
  success: boolean | null;
  error: string | null;
  metadata: Record<string, JsonValue>;
  created_at: string;
};

export type ReliabilityStateResponse = {
  tool_name: string;
  failure_count: number;
  success_count: number;
  circuit_open: boolean;
  opened_at: string | null;
  last_failure_at: string | null;
  last_success_at: string | null;
  last_error: string | null;
  metadata: Record<string, JsonValue>;
};

export type AuraRunRequest = {
  message: string;
};

export type AuraRunResponse = {
  success: boolean;
  message: string;
  result: string | null;
  provider: string | null;
  model: string | null;
  used_fallback: boolean;
};


