from typing import Any

from aura.core.config import settings
from aura.core.logger import logger
from aura.memory.manager import MemoryManager
from aura.memory.models import MemoryType
from aura.models.manager import ModelManager
from aura.models.requests import AuraRequest
from aura.models.responses import AuraResponse
from aura.planning.models import Plan
from aura.planning.planner import Planner
from aura.tools.discovery import ToolDiscovery
from aura.tools.executor import ToolExecutor
from aura.tools.models import ToolResult


class AuraKernel:
    def __init__(
        self,
        model_manager: ModelManager,
        memory_manager: MemoryManager,
        planner: Planner,
        tool_discovery: ToolDiscovery,
        tool_executor: ToolExecutor,
    ):
        self.name = settings.app_name
        self.version = settings.app_version
        self.environment = settings.environment

        self.model_manager = model_manager
        self.memory_manager = memory_manager
        self.planner = planner
        self.tool_discovery = tool_discovery
        self.tool_executor = tool_executor

        self._initialized = False

    def initialize(self) -> None:
        logger.info(
            "Initializing AURA Kernel"
        )

        self._initialized = True

        logger.info(
            "AURA Kernel initialized successfully | "
            "version=%s | environment=%s",
            self.version,
            self.environment,
        )

    def shutdown(self) -> None:
        logger.info(
            "Shutting down AURA Kernel"
        )

        self._initialized = False

        logger.info(
            "AURA Kernel shutdown complete"
        )

    def is_ready(self) -> bool:
        return self._initialized

    async def get_status(self) -> dict:
        provider_name = (
            self.model_manager.default_provider
        )

        provider_healthy = False

        if provider_name is not None:
            provider_healthy = (
                await self.model_manager.health_check(
                    provider_name
                )
            )

        return {
            "name": self.name,
            "version": self.version,
            "environment": self.environment,
            "ready": self.is_ready(),
            "model_provider": provider_name,
            "model_provider_healthy":
                provider_healthy,
            "fallback_provider":
                self.model_manager.fallback_provider,
            "memory_count":
                self.memory_manager.count(),
            "planner_available":
                self.planner is not None,
            "tool_count":
                len(
                    self.tool_discovery
                    .registry
                    .list_tools()
                ),
            "tool_executor_available":
                self.tool_executor is not None,
        }

    def create_plan(
        self,
        goal: str,
        metadata: dict | None = None,
    ) -> Plan:
        if not self.is_ready():
            raise RuntimeError(
                "AURA Kernel is not ready."
            )

        logger.info(
            "Kernel creating plan | goal=%s",
            goal,
        )

        plan = self.planner.generate_plan(
            goal=goal,
            metadata=metadata,
        )

        logger.info(
            "Kernel created plan | "
            "plan_id=%s | steps=%s",
            plan.id,
            len(plan.steps),
        )

        return plan

    def validate_plan(
        self,
        plan: Plan,
    ) -> None:
        if not self.is_ready():
            raise RuntimeError(
                "AURA Kernel is not ready."
            )

        self.planner.validate_plan(
            plan
        )

    def start_plan(
        self,
        plan: Plan,
    ) -> Plan:
        if not self.is_ready():
            raise RuntimeError(
                "AURA Kernel is not ready."
            )

        return self.planner.start_plan(
            plan
        )

    def discover_tools(
        self,
        query: str,
    ) -> list[dict]:
        if not self.is_ready():
            raise RuntimeError(
                "AURA Kernel is not ready."
            )

        tools = self.tool_discovery.search(
            query
        )

        return [
            tool.get_schema()
            for tool in tools
        ]

    def list_tools(
        self,
    ) -> list[dict]:
        if not self.is_ready():
            raise RuntimeError(
                "AURA Kernel is not ready."
            )

        tools = (
            self.tool_discovery
            .registry
            .list_tools()
        )

        return [
            tool.get_schema()
            for tool in tools
        ]

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> ToolResult:
        if not self.is_ready():
            raise RuntimeError(
                "AURA Kernel is not ready."
            )

        logger.info(
            "Kernel executing tool | "
            "tool=%s",
            tool_name,
        )

        result = (
            await self.tool_executor.execute(
                tool_name=tool_name,
                arguments=arguments,
            )
        )

        logger.info(
            "Kernel tool execution finished | "
            "tool=%s | success=%s",
            tool_name,
            result.success,
        )

        return result

    async def process(
        self,
        request: AuraRequest,
    ) -> AuraResponse:
        logger.info(
            "Received AURA request: %s",
            request.message,
        )

        if not self.is_ready():
            return AuraResponse(
                success=False,
                message=(
                    "AURA Kernel is not ready."
                ),
                result=None,
                provider=None,
                model=None,
                used_fallback=False,
            )

        memory_context = (
            self.memory_manager.build_context(
                query=request.message,
                limit=5,
                mark_accessed=True,
            )
        )

        prompt = self._build_prompt(
            user_message=request.message,
            memory_context=memory_context,
        )

        generation = (
            await self.model_manager.generate(
                prompt
            )
        )

        clean_assistant_response = (
            self._clean_assistant_response(
                raw_response=generation.text,
                user_message=request.message,
                memory_context=memory_context,
                provider=generation.provider,
            )
        )

        self._persist_useful_conversation(
            user_message=request.message,
            assistant_response=(
                clean_assistant_response
            ),
            provider=generation.provider,
            model=generation.model,
        )

        return AuraResponse(
            success=True,
            message=(
                "Task completed successfully."
            ),
            result=clean_assistant_response,
            provider=generation.provider,
            model=generation.model,
            used_fallback=(
                generation.used_fallback
            ),
        )

    def _build_prompt(
        self,
        user_message: str,
        memory_context: str,
    ) -> str:
        if not memory_context:
            return user_message

        return (
            f"{memory_context}\n\n"
            "Current user request:\n"
            f"{user_message}\n\n"
            "Use the relevant memory context "
            "only when it helps answer the "
            "current request."
        )

    def _clean_assistant_response(
        self,
        raw_response: str,
        user_message: str,
        memory_context: str,
        provider: str,
    ) -> str:
        cleaned = raw_response.strip()

        if provider == "mock":
            prefix = (
                "Mock model response to:"
            )

            if cleaned.startswith(
                prefix
            ):
                echoed_content = cleaned[
                    len(prefix):
                ].strip()

                if memory_context:
                    marker = (
                        "Current user request:"
                    )

                    if marker in echoed_content:
                        after_marker = (
                            echoed_content.split(
                                marker,
                                1,
                            )[1].strip()
                        )

                        instruction_marker = (
                            "Use the relevant "
                            "memory context only "
                            "when it helps answer "
                            "the current request."
                        )

                        if (
                            instruction_marker
                            in after_marker
                        ):
                            after_marker = (
                                after_marker.split(
                                    instruction_marker,
                                    1,
                                )[0].strip()
                            )

                        echoed_content = (
                            after_marker
                        )

                if echoed_content:
                    return (
                        "Mock model response to: "
                        f"{echoed_content}"
                    )

        return cleaned

    def _persist_useful_conversation(
        self,
        user_message: str,
        assistant_response: str,
        provider: str,
        model: str,
    ) -> None:
        user_should_store = (
            self._should_store_memory(
                user_message
            )
        )

        assistant_should_store = (
            self._should_store_memory(
                assistant_response
            )
            and not self._is_contaminated_memory(
                assistant_response
            )
        )

        if user_should_store:
            user_memory_type = (
                self._classify_memory_type(
                    user_message
                )
            )

            self.memory_manager.remember(
                content=user_message,
                memory_type=user_memory_type,
                importance=(
                    self._estimate_importance(
                        user_message
                    )
                ),
                metadata={
                    "role": "user",
                    "source": "conversation",
                },
            )

        if assistant_should_store:
            self.memory_manager.remember(
                content=assistant_response,
                memory_type=(
                    MemoryType.CONVERSATION
                ),
                importance=(
                    self._estimate_importance(
                        assistant_response
                    )
                ),
                metadata={
                    "role": "assistant",
                    "source": "conversation",
                    "provider": provider,
                    "model": model,
                },
            )

        logger.info(
            "Conversation persistence "
            "completed | user_saved=%s | "
            "assistant_saved=%s",
            user_should_store,
            assistant_should_store,
        )

    def _is_contaminated_memory(
        self,
        content: str,
    ) -> bool:
        text = content.lower()

        contamination_markers = {
            "relevant memory context:",
            "current user request:",
            "memory 1\n",
            "memory 2\n",
            (
                "use the relevant memory "
                "context only when it helps"
            ),
        }

        return any(
            marker in text
            for marker in contamination_markers
        )

    def _should_store_memory(
        self,
        content: str,
    ) -> bool:
        cleaned = content.strip()

        if not cleaned:
            return False

        if len(cleaned) < 10:
            return False

        trivial_messages = {
            "hello aura",
            "hello",
            "hi",
            "hey",
            "thanks",
            "thank you",
            "okay",
            "ok",
            "bye",
            "goodbye",
        }

        if (
            cleaned.lower()
            in trivial_messages
        ):
            return False

        return True

    def _classify_memory_type(
        self,
        content: str,
    ) -> MemoryType:
        text = content.lower()

        preference_terms = {
            "i prefer",
            "i like",
            "i dislike",
            "i love",
            "i hate",
            "my preference",
            "i want",
        }

        project_terms = {
            "my project",
            "our project",
            "project uses",
            "project is",
            "building",
            "developing",
            "repository",
            "codebase",
        }

        task_terms = {
            "todo",
            "to do",
            "deadline",
            "need to",
            "must finish",
            "task",
            "remind me",
            "complete by",
        }

        fact_terms = {
            "my name is",
            "i am",
            "i work",
            "i study",
            "i live",
            "uses",
            "is called",
            "is located",
        }

        if any(
            term in text
            for term in preference_terms
        ):
            return MemoryType.PREFERENCE

        if any(
            term in text
            for term in project_terms
        ):
            return MemoryType.PROJECT

        if any(
            term in text
            for term in task_terms
        ):
            return MemoryType.TASK

        if any(
            term in text
            for term in fact_terms
        ):
            return MemoryType.FACT

        return MemoryType.CONVERSATION

    def _estimate_importance(
        self,
        content: str,
    ) -> float:
        text = content.lower()

        high_importance_terms = {
            "remember",
            "important",
            "project",
            "deadline",
            "preference",
            "prefer",
            "goal",
            "task",
            "requirement",
        }

        if any(
            term in text
            for term in high_importance_terms
        ):
            return 0.8

        if len(content) >= 200:
            return 0.7

        return 0.5