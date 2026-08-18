from typing import Any

from aura.core.logger import logger
from aura.execution.models import (
    StepExecution,
)
from aura.planning.models import PlanStep
from aura.tools.discovery import ToolDiscovery
from aura.tools.registry import ToolRegistry


class ToolBindingManager:
    def __init__(
        self,
        registry: ToolRegistry,
        discovery: ToolDiscovery,
    ):
        self.registry = registry
        self.discovery = discovery

    def bind(
        self,
        plan_step: PlanStep,
        step_execution: StepExecution,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> StepExecution:
        tool = self.registry.find(
            tool_name
        )

        if tool is None:
            raise ValueError(
                f"Tool '{tool_name}' "
                "is not registered."
            )

        if (
            step_execution.plan_step_id
            != plan_step.id
        ):
            raise ValueError(
                "Step execution does not belong "
                "to the provided plan step."
            )

        step_execution.tool_name = (
            tool_name
        )

        step_execution.arguments = (
            arguments or {}
        )

        step_execution.metadata[
            "tool_bound"
        ] = True

        step_execution.metadata[
            "tool_category"
        ] = tool.category

        logger.info(
            "Bound tool to execution step | "
            "plan_step_id=%s | tool=%s",
            plan_step.id,
            tool_name,
        )

        return step_execution

    def unbind(
        self,
        step_execution: StepExecution,
    ) -> StepExecution:
        previous_tool = (
            step_execution.tool_name
        )

        step_execution.tool_name = None
        step_execution.arguments = {}

        step_execution.metadata[
            "tool_bound"
        ] = False

        step_execution.metadata.pop(
            "tool_category",
            None,
        )

        logger.info(
            "Unbound tool from execution step | "
            "plan_step_id=%s | previous_tool=%s",
            step_execution.plan_step_id,
            previous_tool,
        )

        return step_execution

    def suggest_tools(
        self,
        plan_step: PlanStep,
    ) -> list[str]:
        queries = self._build_queries(
            plan_step
        )

        matches = []

        for query in queries:
            tools = self.discovery.search(
                query
            )

            for tool in tools:
                if tool.name not in matches:
                    matches.append(
                        tool.name
                    )

        return matches

    def auto_bind(
        self,
        plan_step: PlanStep,
        step_execution: StepExecution,
        arguments: dict[str, Any] | None = None,
    ) -> StepExecution:
        suggestions = self.suggest_tools(
            plan_step
        )

        if not suggestions:
            raise ValueError(
                f"No suitable tool found for "
                f"plan step '{plan_step.title}'."
            )

        return self.bind(
            plan_step=plan_step,
            step_execution=step_execution,
            tool_name=suggestions[0],
            arguments=arguments,
        )

    def _build_queries(
        self,
        plan_step: PlanStep,
    ) -> list[str]:
        queries = []

        title = (
            plan_step.title
            .strip()
            .lower()
        )

        if title:
            queries.append(
                title
            )

        metadata = (
            plan_step.metadata or {}
        )

        category = metadata.get(
            "category"
        )

        if isinstance(
            category,
            str,
        ):
            queries.append(
                category
            )

        specialization = (
            metadata.get(
                "specialization"
            )
        )

        if isinstance(
            specialization,
            str,
        ):
            queries.append(
                specialization
            )

        keyword_map = {
            "calculate": "calculator",
            "calculation": "calculator",
            "math": "calculator",
            "arithmetic": "calculator",
            "time": "current_time",
            "date": "current_time",
            "clock": "current_time",
            "text": "text_stats",
            "word": "text_stats",
            "words": "text_stats",
            "character": "text_stats",
            "characters": "text_stats",
            "echo": "echo",
            "repeat": "echo",
            "system": "system_info",
            "environment": "system_info",
            "machine": "system_info",
        }

        combined = " ".join(
            queries
        )

        for keyword, query in (
            keyword_map.items()
        ):
            if keyword in combined:
                queries.append(
                    query
                )

        return queries