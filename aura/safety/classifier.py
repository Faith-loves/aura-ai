from typing import Any

from aura.core.logger import logger
from aura.safety.models import (
    RiskLevel,
    SafetyContext,
)
from aura.tools.base import Tool
from aura.tools.registry import ToolRegistry


class RiskClassifier:
    def __init__(
        self,
        registry: ToolRegistry | None = None,
    ):
        self.registry = registry

        self._tool_overrides: dict[
            str,
            RiskLevel,
        ] = {}

        self._action_overrides: dict[
            str,
            RiskLevel,
        ] = {}

    def classify_tool(
        self,
        tool_name: str,
    ) -> RiskLevel:
        normalized = (
            tool_name.strip().lower()
        )

        if normalized in self._tool_overrides:
            return self._tool_overrides[
                normalized
            ]

        if self.registry is not None:
            tool = self.registry.find(
                tool_name
            )

            if tool is not None:
                return self._classify_tool_object(
                    tool
                )

        return self._classify_tool_name(
            normalized
        )

    def classify_action(
        self,
        action: str,
    ) -> RiskLevel:
        normalized = (
            action.strip().lower()
        )

        if normalized in self._action_overrides:
            return self._action_overrides[
                normalized
            ]

        critical_actions = {
            "delete_system",
            "format_disk",
            "wipe_disk",
            "disable_security",
            "delete_all",
            "destroy",
            "shutdown_system",
        }

        high_actions = {
            "delete",
            "write_file",
            "modify_file",
            "execute_shell",
            "run_command",
            "install_package",
            "change_permissions",
            "send_email",
            "make_payment",
            "deploy",
        }

        medium_actions = {
            "read_file",
            "list_files",
            "network_request",
            "fetch_url",
            "system_info",
            "inspect_environment",
        }

        if normalized in critical_actions:
            return RiskLevel.CRITICAL

        if normalized in high_actions:
            return RiskLevel.HIGH

        if normalized in medium_actions:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def classify_context(
        self,
        context: SafetyContext,
    ) -> RiskLevel:
        risks: list[RiskLevel] = []

        if context.tool_name:
            risks.append(
                self.classify_tool(
                    context.tool_name
                )
            )

        if context.action:
            risks.append(
                self.classify_action(
                    context.action
                )
            )

        argument_risk = (
            self._classify_arguments(
                context.arguments
            )
        )

        risks.append(
            argument_risk
        )

        return self._highest_risk(
            risks
        )

    def set_tool_risk(
        self,
        tool_name: str,
        risk_level: RiskLevel,
    ) -> None:
        normalized = (
            tool_name.strip().lower()
        )

        if not normalized:
            raise ValueError(
                "tool_name cannot be empty."
            )

        self._tool_overrides[
            normalized
        ] = risk_level

        logger.info(
            "Tool risk override set | "
            "tool=%s | risk=%s",
            normalized,
            risk_level.value,
        )

    def set_action_risk(
        self,
        action: str,
        risk_level: RiskLevel,
    ) -> None:
        normalized = (
            action.strip().lower()
        )

        if not normalized:
            raise ValueError(
                "action cannot be empty."
            )

        self._action_overrides[
            normalized
        ] = risk_level

        logger.info(
            "Action risk override set | "
            "action=%s | risk=%s",
            normalized,
            risk_level.value,
        )

    def clear_tool_override(
        self,
        tool_name: str,
    ) -> bool:
        normalized = (
            tool_name.strip().lower()
        )

        if normalized not in (
            self._tool_overrides
        ):
            return False

        del self._tool_overrides[
            normalized
        ]

        return True

    def clear_action_override(
        self,
        action: str,
    ) -> bool:
        normalized = (
            action.strip().lower()
        )

        if normalized not in (
            self._action_overrides
        ):
            return False

        del self._action_overrides[
            normalized
        ]

        return True

    def _classify_tool_object(
        self,
        tool: Tool,
    ) -> RiskLevel:
        if tool.dangerous:
            return RiskLevel.HIGH

        if tool.requires_confirmation:
            return RiskLevel.HIGH

        category = (
            tool.category
            .strip()
            .lower()
        )

        if category in {
            "system",
            "filesystem",
            "network",
            "external",
        }:
            return RiskLevel.MEDIUM

        if category in {
            "destructive",
            "privileged",
            "security",
        }:
            return RiskLevel.HIGH

        if category in {
            "critical",
        }:
            return RiskLevel.CRITICAL

        return self._classify_tool_name(
            tool.name.lower()
        )

    def _classify_tool_name(
        self,
        tool_name: str,
    ) -> RiskLevel:
        low_risk_tools = {
            "echo",
            "calculator",
            "current_time",
            "text_stats",
        }

        medium_risk_tools = {
            "system_info",
            "web_fetch",
            "http_request",
            "read_file",
            "list_files",
        }

        high_risk_tools = {
            "write_file",
            "delete_file",
            "shell",
            "terminal",
            "email",
            "deploy",
            "package_manager",
        }

        critical_risk_tools = {
            "format_disk",
            "wipe_disk",
            "credential_manager",
            "security_control",
        }

        if tool_name in low_risk_tools:
            return RiskLevel.LOW

        if tool_name in medium_risk_tools:
            return RiskLevel.MEDIUM

        if tool_name in high_risk_tools:
            return RiskLevel.HIGH

        if tool_name in critical_risk_tools:
            return RiskLevel.CRITICAL

        return RiskLevel.MEDIUM

    def _classify_arguments(
        self,
        arguments: dict[str, Any],
    ) -> RiskLevel:
        if not arguments:
            return RiskLevel.LOW

        dangerous_keys = {
            "password",
            "token",
            "secret",
            "api_key",
            "credential",
            "private_key",
        }

        destructive_keys = {
            "delete",
            "overwrite",
            "force",
            "recursive",
            "format",
            "wipe",
        }

        normalized_keys = {
            str(key).lower()
            for key in arguments
        }

        if (
            normalized_keys
            & dangerous_keys
        ):
            return RiskLevel.HIGH

        if (
            normalized_keys
            & destructive_keys
        ):
            return RiskLevel.HIGH

        return RiskLevel.LOW

    def _highest_risk(
        self,
        risks: list[RiskLevel],
    ) -> RiskLevel:
        ranking = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }

        if not risks:
            return RiskLevel.LOW

        return max(
            risks,
            key=lambda risk: ranking[
                risk
            ],
        )