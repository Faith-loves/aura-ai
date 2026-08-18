from datetime import UTC, datetime
from typing import Any

from aura.core.logger import logger
from aura.tools.errors import (
    InvalidToolResultError,
    ToolErrorCode,
    ToolExecutionError,
    ToolNotFoundError,
    ToolValidationError,
)
from aura.tools.models import (
    ToolExecutionStatus,
    ToolResult,
)
from aura.tools.registry import ToolRegistry
from aura.tools.validator import ToolArgumentValidator


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        validator: ToolArgumentValidator | None = None,
    ):
        self.registry = registry

        self.validator = (
            validator
            or ToolArgumentValidator()
        )

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> ToolResult:
        arguments = arguments or {}

        started_at = datetime.now(
            UTC
        )

        tool = self.registry.find(
            tool_name
        )

        if tool is None:
            error = ToolNotFoundError(
                tool_name
            )

            return self._build_failure_result(
                tool_name=tool_name,
                started_at=started_at,
                error=error.message,
                error_code=error.code,
                stage="lookup",
            )

        try:
            validated_arguments = (
                self.validator.validate(
                    tool=tool,
                    arguments=arguments,
                )
            )

        except ValueError as exc:
            error = ToolValidationError(
                str(exc)
            )

            logger.warning(
                "Tool argument validation failed | "
                "tool=%s | code=%s | error=%s",
                tool_name,
                error.code.value,
                error.message,
            )

            return self._build_failure_result(
                tool_name=tool_name,
                started_at=started_at,
                error=error.message,
                error_code=error.code,
                stage="validation",
            )

        logger.info(
            "Executing tool | tool=%s",
            tool_name,
        )

        try:
            result = await tool.execute(
                **validated_arguments
            )

        except Exception as exc:
            error = ToolExecutionError(
                str(exc)
            )

            logger.exception(
                "Tool execution failed | "
                "tool=%s | code=%s",
                tool_name,
                error.code.value,
            )

            return self._build_failure_result(
                tool_name=tool_name,
                started_at=started_at,
                error=error.message,
                error_code=error.code,
                stage="execution",
                extra_metadata={
                    "exception_type":
                        type(exc).__name__,
                },
            )

        if not isinstance(
            result,
            ToolResult,
        ):
            error = InvalidToolResultError(
                tool_name
            )

            logger.error(
                "Tool returned invalid result | "
                "tool=%s | type=%s",
                tool_name,
                type(result).__name__,
            )

            return self._build_failure_result(
                tool_name=tool_name,
                started_at=started_at,
                error=error.message,
                error_code=error.code,
                stage="result",
            )

        completed_at = datetime.now(
            UTC
        )

        duration_ms = (
            completed_at - started_at
        ).total_seconds() * 1000

        result.tool_name = tool_name
        result.started_at = started_at
        result.completed_at = completed_at
        result.duration_ms = duration_ms

        result.status = (
            ToolExecutionStatus.SUCCESS
            if result.success
            else ToolExecutionStatus.FAILED
        )

        if result.success:
            result.error_code = None

            result.metadata.setdefault(
                "stage",
                "completed",
            )

        else:
            if result.error_code is None:
                result.error_code = (
                    ToolErrorCode.TOOL_FAILED.value
                )

            result.metadata.setdefault(
                "stage",
                "tool_result",
            )

        result.metadata.setdefault(
            "tool",
            tool_name,
        )

        logger.info(
            "Tool execution completed | "
            "tool=%s | success=%s | "
            "duration_ms=%.3f",
            tool_name,
            result.success,
            duration_ms,
        )

        return result

    def _build_failure_result(
        self,
        tool_name: str,
        started_at: datetime,
        error: str,
        error_code: ToolErrorCode,
        stage: str,
        extra_metadata: dict | None = None,
    ) -> ToolResult:
        completed_at = datetime.now(
            UTC
        )

        duration_ms = (
            completed_at - started_at
        ).total_seconds() * 1000

        metadata = {
            "tool": tool_name,
            "stage": stage,
        }

        if extra_metadata:
            metadata.update(
                extra_metadata
            )

        return ToolResult(
            tool_name=tool_name,
            status=(
                ToolExecutionStatus.FAILED
            ),
            success=False,
            error=error,
            error_code=error_code.value,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            metadata=metadata,
        )