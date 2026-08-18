from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
)
from fastapi.middleware.cors import CORSMiddleware

from aura.core.config import settings
from aura.core.container import container
from aura.core.logger import logger
from aura.models.execution_api import (
    CreateExecutionRequest,
    ExecutionResponse,
    StepExecutionResponse,
)
from aura.models.memory_api import (
    CreateMemoryRequest,
    ImportMemoryRequest,
    MemoryResponse,
    MemorySearchResult,
    RestoreMemoryRequest,
    SearchMemoryRequest,
)
from aura.models.planning_api import (
    CreatePlanRequest,
    PlanResponse,
    PlanStepResponse,
    UpdateStepPriorityRequest,
)
from aura.models.requests import AuraRequest
from aura.models.responses import AuraResponse
from aura.models.tool_api import (
    ExecuteToolRequest,
    ToolExecutionResponse,
    ToolResponse,
)

from aura.models.safety_api import (
    ApprovalDecisionRequest,
    ApprovalResponse,
    AuditResponse,
    ReliabilityStateResponse,
    SafetyPolicyResponse,
)

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    logger.info(
        "Starting AURA API"
    )

    container.initialize()

    yield

    container.shutdown()

    logger.info(
        "AURA API stopped"
    )


app = FastAPI(
    title=f"{settings.app_name} API",
    description=(
        "API for the AURA autonomous AI system"
    ),
    version=settings.app_version,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# SERIALIZERS
# =========================================================

def serialize_plan(
    plan,
) -> PlanResponse:
    return PlanResponse(
        id=plan.id,
        goal=plan.goal,
        status=plan.status,
        steps=[
            PlanStepResponse(
                id=step.id,
                title=step.title,
                description=step.description,
                status=step.status,
                priority=step.priority,
                dependencies=step.dependencies,
                metadata=step.metadata,
            )
            for step in plan.steps
        ],
        metadata=plan.metadata,
    )


def serialize_tool(
    tool_schema: dict,
) -> ToolResponse:
    return ToolResponse(
        name=tool_schema["name"],
        description=tool_schema[
            "description"
        ],
        category=tool_schema[
            "category"
        ],
        version=tool_schema[
            "version"
        ],
        dangerous=tool_schema[
            "dangerous"
        ],
        requires_confirmation=(
            tool_schema[
                "requires_confirmation"
            ]
        ),
        tags=tool_schema["tags"],
        parameters=tool_schema[
            "parameters"
        ],
    )


def serialize_tool_result(
    result,
) -> ToolExecutionResponse:
    return ToolExecutionResponse(
        execution_id=result.execution_id,
        tool_name=result.tool_name,
        status=result.status,
        success=result.success,
        output=result.output,
        error=result.error,
        error_code=result.error_code,
        started_at=(
            result.started_at.isoformat()
        ),
        completed_at=(
            result.completed_at.isoformat()
            if result.completed_at
            else None
        ),
        duration_ms=result.duration_ms,
        metadata=result.metadata,
    )


def serialize_execution(
    execution,
) -> ExecutionResponse:
    return ExecutionResponse(
        id=execution.id,
        plan_id=execution.plan_id,
        goal=execution.goal,
        status=execution.status,
        step_executions=[
            StepExecutionResponse(
                id=step.id,
                plan_step_id=(
                    step.plan_step_id
                ),
                title=step.title,
                status=step.status,
                tool_name=step.tool_name,
                arguments=step.arguments,
                tool_execution_id=(
                    step.tool_execution_id
                ),
                output=step.output,
                error=step.error,
                error_code=step.error_code,
                started_at=step.started_at,
                completed_at=(
                    step.completed_at
                ),
                duration_ms=(
                    step.duration_ms
                ),
                metadata=step.metadata,
            )
            for step
            in execution.step_executions
        ],
        current_step_id=(
            execution.current_step_id
        ),
        started_at=(
            execution.started_at
        ),
        completed_at=(
            execution.completed_at
        ),
        duration_ms=(
            execution.duration_ms
        ),
        error=execution.error,
        error_code=(
            execution.error_code
        ),
        metadata=execution.metadata,
    )




def serialize_approval(
    approval,
) -> ApprovalResponse:
    return ApprovalResponse(
        id=approval.id,
        status=approval.status,
        risk_level=approval.risk_level,
        reason=approval.reason,
        safety_decision_id=(
            approval.safety_decision_id
        ),
        tool_name=(
            approval.context.tool_name
        ),
        execution_id=(
            approval.context.execution_id
        ),
        plan_id=(
            approval.context.plan_id
        ),
        step_id=(
            approval.context.step_id
        ),
        requested_at=(
            approval.requested_at
        ),
        resolved_at=(
            approval.resolved_at
        ),
        resolved_by=(
            approval.resolved_by
        ),
        resolution_reason=(
            approval.resolution_reason
        ),
        metadata=(
            approval.metadata
        ),
    )


def serialize_audit_record(
    record,
) -> AuditResponse:
    return AuditResponse(
        id=record.id,
        event_type=record.event_type,
        message=record.message,
        execution_id=(
            record.execution_id
        ),
        plan_id=record.plan_id,
        step_id=record.step_id,
        tool_name=record.tool_name,
        approval_id=(
            record.approval_id
        ),
        risk_level=(
            record.risk_level
        ),
        success=record.success,
        error=record.error,
        metadata=record.metadata,
        created_at=(
            record.created_at
        ),
    )


def serialize_reliability_state(
    state,
) -> ReliabilityStateResponse:
    return ReliabilityStateResponse(
        tool_name=state.tool_name,
        failure_count=(
            state.failure_count
        ),
        success_count=(
            state.success_count
        ),
        circuit_open=(
            state.circuit_open
        ),
        opened_at=(
            state.opened_at
        ),
        last_failure_at=(
            state.last_failure_at
        ),
        last_success_at=(
            state.last_success_at
        ),
        last_error=(
            state.last_error
        ),
        metadata=(
            state.metadata
        ),
    )


# =========================================================
# ROOT / HEALTH
# =========================================================

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment":
            settings.environment,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    kernel_status = (
        await container.kernel
        .get_status()
    )

    return {
        "status": (
            "healthy"
            if container.is_ready()
            else "unavailable"
        ),
        "service": settings.app_name,
        "kernel": kernel_status,
    }


@app.get("/models")
async def models():
    providers = (
        await container.model_manager
        .get_provider_statuses()
    )

    return {
        "default_provider":
            container.model_manager
            .default_provider,
        "fallback_provider":
            container.model_manager
            .fallback_provider,
        "providers": providers,
    }


# =========================================================
# TOOLS
# =========================================================

@app.get(
    "/tools",
    response_model=list[
        ToolResponse
    ],
)
async def list_tools():
    try:
        tools = (
            container.kernel
            .list_tools()
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return [
        serialize_tool(tool)
        for tool in tools
    ]


@app.get(
    "/tools/search",
    response_model=list[
        ToolResponse
    ],
)
async def search_tools(
    query: str = Query(
        ...,
        min_length=1,
    ),
):
    try:
        tools = (
            container.kernel
            .discover_tools(
                query
            )
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return [
        serialize_tool(tool)
        for tool in tools
    ]


@app.post(
    "/tools/{tool_name}/execute",
    response_model=(
        ToolExecutionResponse
    ),
)
async def execute_tool(
    tool_name: str,
    request: ExecuteToolRequest,
):
    try:
        result = (
            await container.kernel
            .execute_tool(
                tool_name=tool_name,
                arguments=(
                    request.arguments
                ),
            )
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return serialize_tool_result(
        result
    )


# =========================================================
# EXECUTIONS
# =========================================================

@app.post(
    "/executions",
    response_model=ExecutionResponse,
)
async def create_execution(
    request: CreateExecutionRequest,
):
    plan = container.plan_store.get(
        request.plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    try:
        execution = (
            container.execution_manager
            .create_execution(
                plan=plan,
                metadata=request.metadata,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return serialize_execution(
        execution
    )


@app.get(
    "/executions",
    response_model=list[
        ExecutionResponse
    ],
)
async def list_executions():
    executions = (
        container.execution_manager
        .list_executions()
    )

    return [
        serialize_execution(
            execution
        )
        for execution
        in executions
    ]


@app.get(
    "/executions/{execution_id}",
    response_model=ExecutionResponse,
)
async def get_execution(
    execution_id: str,
):
    try:
        execution = (
            container.execution_manager
            .get_execution(
                execution_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return serialize_execution(
        execution
    )


@app.post(
    "/executions/{execution_id}/start",
    response_model=ExecutionResponse,
)
async def start_execution(
    execution_id: str,
):
    try:
        execution = (
            container.execution_manager
            .get_execution(
                execution_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    plan = container.plan_store.get(
        execution.plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    try:
        (
            container.execution_manager
            .start_execution(
                execution=execution,
                plan=plan,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    container.plan_store.save(
        plan
    )

    return serialize_execution(
        execution
    )


@app.post(
    "/executions/{execution_id}/run",
    response_model=ExecutionResponse,
)
async def run_execution(
    execution_id: str,
):
    try:
        execution = (
            container.execution_manager
            .get_execution(
                execution_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    plan = container.plan_store.get(
        execution.plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    try:
        await (
            container.execution_runner
            .run_execution(
                execution=execution,
                plan=plan,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    container.plan_store.save(
        plan
    )

    return serialize_execution(
        execution
    )


@app.post(
    "/executions/{execution_id}/pause",
    response_model=ExecutionResponse,
)
async def pause_execution(
    execution_id: str,
):
    try:
        execution = (
            container.execution_manager
            .get_execution(
                execution_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    try:
        (
            container.execution_manager
            .pause_execution(
                execution
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return serialize_execution(
        execution
    )


@app.post(
    "/executions/{execution_id}/resume",
    response_model=ExecutionResponse,
)
async def resume_execution(
    execution_id: str,
):
    try:
        execution = (
            container.execution_manager
            .get_execution(
                execution_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    try:
        (
            container.execution_manager
            .resume_execution(
                execution
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return serialize_execution(
        execution
    )


@app.post(
    "/executions/{execution_id}/cancel",
    response_model=ExecutionResponse,
)
async def cancel_execution(
    execution_id: str,
):
    try:
        execution = (
            container.execution_manager
            .get_execution(
                execution_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    plan = container.plan_store.get(
        execution.plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    try:
        (
            container.execution_manager
            .cancel_execution(
                execution=execution,
                plan=plan,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    container.plan_store.save(
        plan
    )

    return serialize_execution(
        execution
    )


@app.delete(
    "/executions/{execution_id}"
)
async def delete_execution(
    execution_id: str,
):
    deleted = (
        container.execution_manager
        .delete_execution(
            execution_id
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Execution not found.",
        )

    return {
        "success": True,
        "execution_id": execution_id,
    }

# =========================================================
# PLANNING
# =========================================================

@app.post(
    "/plans",
    response_model=PlanResponse,
)
async def create_plan(
    request: CreatePlanRequest,
):
    plan = container.kernel.create_plan(
        goal=request.goal,
        metadata=request.metadata,
    )

    container.plan_store.save(
        plan
    )

    return serialize_plan(
        plan
    )


@app.get(
    "/plans",
    response_model=list[
        PlanResponse
    ],
)
async def list_plans():
    plans = (
        container.plan_store
        .list_all()
    )

    return [
        serialize_plan(plan)
        for plan in plans
    ]


@app.get(
    "/plans/{plan_id}",
    response_model=PlanResponse,
)
async def get_plan(
    plan_id: str,
):
    plan = container.plan_store.get(
        plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    return serialize_plan(
        plan
    )


@app.post(
    "/plans/{plan_id}/start",
    response_model=PlanResponse,
)
async def start_plan(
    plan_id: str,
):
    plan = container.plan_store.get(
        plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    try:
        container.kernel.start_plan(
            plan
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    container.plan_store.save(
        plan
    )

    return serialize_plan(
        plan
    )


@app.post(
    "/plans/{plan_id}/steps/"
    "{step_id}/start",
    response_model=PlanResponse,
)
async def start_plan_step(
    plan_id: str,
    step_id: str,
):
    plan = container.plan_store.get(
        plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    try:
        container.planner.start_step(
            plan,
            step_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    container.plan_store.save(
        plan
    )

    return serialize_plan(
        plan
    )


@app.post(
    "/plans/{plan_id}/steps/"
    "{step_id}/complete",
    response_model=PlanResponse,
)
async def complete_plan_step(
    plan_id: str,
    step_id: str,
):
    plan = container.plan_store.get(
        plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    try:
        container.planner.complete_step(
            plan,
            step_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    container.plan_store.save(
        plan
    )

    return serialize_plan(
        plan
    )


@app.patch(
    "/plans/{plan_id}/steps/"
    "{step_id}/priority",
    response_model=PlanResponse,
)
async def update_step_priority(
    plan_id: str,
    step_id: str,
    request: UpdateStepPriorityRequest,
):
    plan = container.plan_store.get(
        plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    try:
        container.planner.set_step_priority(
            plan=plan,
            step_id=step_id,
            priority=request.priority,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    container.plan_store.save(
        plan
    )

    return serialize_plan(
        plan
    )


@app.post(
    "/plans/{plan_id}/complete",
    response_model=PlanResponse,
)
async def complete_plan(
    plan_id: str,
):
    plan = container.plan_store.get(
        plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    try:
        container.planner.complete_plan(
            plan
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    container.plan_store.save(
        plan
    )

    return serialize_plan(
        plan
    )


@app.delete(
    "/plans/{plan_id}"
)
async def delete_plan(
    plan_id: str,
):
    deleted = (
        container.plan_store.delete(
            plan_id
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Plan not found.",
        )

    return {
        "success": True,
        "plan_id": plan_id,
    }


# =========================================================
# MEMORY
# =========================================================

@app.get(
    "/memory",
    response_model=list[
        MemoryResponse
    ],
)
async def list_memories():
    memories = (
        container.memory_manager
        .list_memories()
    )

    return [
        MemoryResponse(
            id=memory.id,
            memory_type=(
                memory.memory_type
            ),
            content=memory.content,
            importance=(
                memory.importance
            ),
            access_count=(
                memory.access_count
            ),
            metadata=memory.metadata,
        )
        for memory in memories
    ]


@app.get("/memory/stats")
async def memory_statistics():
    return (
        container.memory_manager
        .get_statistics()
    )


@app.get("/memory/export")
async def export_memory():
    return (
        container.memory_manager
        .export_memories()
    )


@app.post("/memory/backup")
async def backup_memory():
    path = (
        container.memory_manager
        .create_backup()
    )

    return {
        "success": True,
        "path": str(path),
    }


@app.post("/memory/import")
async def import_memory(
    request: ImportMemoryRequest,
):
    imported = (
        container.memory_manager
        .import_memories(
            request.model_dump()
        )
    )

    return {
        "success": True,
        "imported": imported,
    }


@app.post("/memory/restore")
async def restore_memory(
    request: RestoreMemoryRequest,
):
    try:
        result = (
            container.memory_manager
            .restore_from_file(
                file_path=(
                    request.file_path
                ),
                clear_existing=(
                    request.clear_existing
                ),
            )
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "success": True,
        **result,
    }


@app.post("/memory/cleanup")
async def cleanup_memory(
    min_importance: float = 0.3,
    max_access_count: int = 0,
    older_than_days: int = 30,
):
    deleted = (
        container.memory_manager
        .cleanup(
            min_importance=(
                min_importance
            ),
            max_access_count=(
                max_access_count
            ),
            older_than_days=(
                older_than_days
            ),
        )
    )

    return {
        "success": True,
        "deleted": deleted,
    }


@app.post(
    "/memory/cleanup-contaminated"
)
async def cleanup_contaminated_memory():
    deleted = (
        container.memory_manager
        .cleanup_contaminated_memories()
    )

    return {
        "success": True,
        "deleted": deleted,
    }


@app.post(
    "/memory/search",
    response_model=list[
        MemorySearchResult
    ],
)
async def search_memories(
    request: SearchMemoryRequest,
):
    results = (
        container.memory_manager
        .search(
            query=request.query,
            limit=request.limit,
            memory_type=(
                request.memory_type
            ),
            mark_accessed=False,
        )
    )

    return [
        MemorySearchResult(
            memory=MemoryResponse(
                id=memory.id,
                memory_type=(
                    memory.memory_type
                ),
                content=memory.content,
                importance=(
                    memory.importance
                ),
                access_count=(
                    memory.access_count
                ),
                metadata=(
                    memory.metadata
                ),
            ),
            score=score,
        )
        for memory, score in results
    ]


@app.post(
    "/memory",
    response_model=MemoryResponse,
)
async def create_memory(
    request: CreateMemoryRequest,
):
    memory = (
        container.memory_manager
        .remember(
            content=request.content,
            memory_type=(
                request.memory_type
            ),
            importance=(
                request.importance
            ),
            metadata=request.metadata,
        )
    )

    return MemoryResponse(
        id=memory.id,
        memory_type=memory.memory_type,
        content=memory.content,
        importance=memory.importance,
        access_count=(
            memory.access_count
        ),
        metadata=memory.metadata,
    )


@app.delete("/memory")
async def clear_all_memory():
    deleted = (
        container.memory_manager
        .clear_all_memories()
    )

    return {
        "success": True,
        "deleted": deleted,
    }


@app.get(
    "/memory/{memory_id}",
    response_model=MemoryResponse,
)
async def get_memory(
    memory_id: str,
):
    memory = (
        container.memory_manager
        .recall(
            memory_id,
            mark_accessed=False,
        )
    )

    if memory is None:
        raise HTTPException(
            status_code=404,
            detail="Memory not found.",
        )

    return MemoryResponse(
        id=memory.id,
        memory_type=memory.memory_type,
        content=memory.content,
        importance=memory.importance,
        access_count=memory.access_count,
        metadata=memory.metadata,
    )


@app.delete(
    "/memory/{memory_id}"
)
async def delete_memory(
    memory_id: str,
):
    deleted = (
        container.memory_manager
        .forget(
            memory_id
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Memory not found.",
        )

    return {
        "success": True,
        "message": (
            "Memory deleted successfully."
        ),
        "memory_id": memory_id,
    }



# =========================================================
# SAFETY
# =========================================================


@app.get(
    "/safety/policy",
    response_model=SafetyPolicyResponse,
)
async def get_safety_policy():
    policy = container.safety_policy

    return SafetyPolicyResponse(
        name=policy.name,
        allow_low_risk=(
            policy.allow_low_risk
        ),
        allow_medium_risk=(
            policy.allow_medium_risk
        ),
        require_approval_for_high_risk=(
            policy
            .require_approval_for_high_risk
        ),
        block_critical_risk=(
            policy.block_critical_risk
        ),
        metadata=policy.metadata,
    )


@app.get(
    "/safety/approvals",
    response_model=list[
        ApprovalResponse
    ],
)
async def list_approvals():
    approvals = (
        container.approval_manager
        .list_all()
    )

    return [
        serialize_approval(
            approval
        )
        for approval
        in approvals
    ]


@app.get(
    "/safety/approvals/{approval_id}",
    response_model=ApprovalResponse,
)
async def get_approval(
    approval_id: str,
):
    approval = (
        container.approval_manager
        .get(
            approval_id
        )
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Approval request not found."
            ),
        )

    return serialize_approval(
        approval
    )


@app.post(
    "/safety/approvals/{approval_id}/approve",
    response_model=ApprovalResponse,
)
async def approve_safety_request(
    approval_id: str,
    request: ApprovalDecisionRequest,
):
    try:
        approval = (
            container.approval_manager
            .approve(
                approval_id=approval_id,
                resolved_by=(
                    request.resolved_by
                ),
                reason=request.reason,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return serialize_approval(
        approval
    )


@app.post(
    "/safety/approvals/{approval_id}/reject",
    response_model=ApprovalResponse,
)
async def reject_safety_request(
    approval_id: str,
    request: ApprovalDecisionRequest,
):
    try:
        approval = (
            container.approval_manager
            .reject(
                approval_id=approval_id,
                resolved_by=(
                    request.resolved_by
                ),
                reason=request.reason,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return serialize_approval(
        approval
    )


@app.get(
    "/safety/audit",
    response_model=list[
        AuditResponse
    ],
)
async def list_safety_audit():
    records = (
        container.audit_logger
        .list_all()
    )

    return [
        serialize_audit_record(
            record
        )
        for record
        in records
    ]


@app.get(
    "/safety/reliability",
    response_model=list[
        ReliabilityStateResponse
    ],
)
async def list_reliability_state():
    states = (
        container.reliability_manager
        .list_states()
    )

    return [
        serialize_reliability_state(
            state
        )
        for state
        in states
    ]


@app.post(
    "/safety/reliability/{tool_name}/reset",
    response_model=ReliabilityStateResponse,
)
async def reset_reliability_state(
    tool_name: str,
):
    try:
        state = (
            container.reliability_manager
            .reset_tool(
                tool_name
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return serialize_reliability_state(
        state
    )


# =========================================================
# AURA
# =========================================================

@app.post(
    "/run",
    response_model=AuraResponse,
)
async def run_aura(
    request: AuraRequest,
):
    return await container.kernel.process(
        request
    )

