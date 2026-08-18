from aura.core.kernel import AuraKernel
from aura.core.logger import logger
from aura.execution.binding import (
    ToolBindingManager,
)
from aura.execution.guards import (
    ExecutionGuard,
    ExecutionLimits,
)
from aura.execution.manager import (
    ExecutionManager,
)
from aura.execution.retry import (
    RetryPolicy,
)
from aura.execution.runner import (
    ExecutionRunner,
)
from aura.execution.store import (
    ExecutionStore,
)
from aura.memory.formatter import (
    MemoryFormatter,
)
from aura.memory.manager import (
    MemoryManager,
)
from aura.memory.repository import (
    MemoryRepository,
)
from aura.memory.scorer import (
    MemoryScorer,
)
from aura.models.manager import (
    ModelManager,
)
from aura.models.providers.mock import (
    MockModelProvider,
)
from aura.models.providers.ollama import (
    OllamaProvider,
)
from aura.planning.planner import (
    Planner,
)
from aura.planning.store import (
    PlanStore,
)
from aura.safety.approvals import (
    ApprovalManager,
)
from aura.safety.audit import (
    AuditLogger,
)
from aura.safety.authorizer import (
    ExecutionAuthorizer,
)
from aura.safety.classifier import (
    RiskClassifier,
)
from aura.safety.enforcer import (
    SafetyEnforcer,
)
from aura.safety.models import (
    SafetyPolicy,
)
from aura.safety.permissions import (
    PermissionManager,
)
from aura.safety.recovery import (
    ErrorClassifier,
    RecoveryManager,
)
from aura.safety.reliability import (
    ReliabilityManager,
    ReliabilityPolicy,
)
from aura.tools.discovery import (
    ToolDiscovery,
)
from aura.tools.executor import (
    ToolExecutor,
)
from aura.tools.loader import (
    ToolLoader,
)
from aura.tools.registry import (
    ToolRegistry,
)
from aura.tools.validator import (
    ToolArgumentValidator,
)


class Container:
    def __init__(self):
        self._initialized = False

        self.model_manager = (
            ModelManager()
        )

        self._configure_models()

        self.memory_repository = (
            MemoryRepository(
                database_path=(
                    "data/aura_memory.db"
                )
            )
        )

        self.memory_scorer = (
            MemoryScorer()
        )

        self.memory_formatter = (
            MemoryFormatter()
        )

        self.memory_manager = (
            MemoryManager(
                repository=(
                    self.memory_repository
                ),
                scorer=(
                    self.memory_scorer
                ),
                formatter=(
                    self.memory_formatter
                ),
            )
        )

        self.planner = Planner()

        self.plan_store = PlanStore()

        self.execution_store = (
            ExecutionStore()
        )

        self.execution_manager = (
            ExecutionManager(
                store=(
                    self.execution_store
                ),
                planner=(
                    self.planner
                ),
            )
        )

        self.tool_registry = (
            ToolRegistry()
        )

        self.tool_loader = (
            ToolLoader(
                registry=(
                    self.tool_registry
                )
            )
        )

        self.tool_loader.load_builtin_tools()

        self.tool_discovery = (
            ToolDiscovery(
                registry=(
                    self.tool_registry
                )
            )
        )

        self.tool_validator = (
            ToolArgumentValidator()
        )

        self.tool_executor = (
            ToolExecutor(
                registry=(
                    self.tool_registry
                ),
                validator=(
                    self.tool_validator
                ),
            )
        )

        self.tool_binding_manager = (
            ToolBindingManager(
                registry=(
                    self.tool_registry
                ),
                discovery=(
                    self.tool_discovery
                ),
            )
        )

        self.retry_policy = (
            RetryPolicy(
                max_attempts=3
            )
        )

        self.execution_limits = (
            ExecutionLimits(
                max_steps=50,
                max_failures=3,
                max_iterations=100,
            )
        )

        self.execution_guard = (
            ExecutionGuard(
                limits=(
                    self.execution_limits
                )
            )
        )

        self.audit_logger = (
            AuditLogger()
        )

        self.safety_policy = (
            SafetyPolicy()
        )

        self.permission_manager = (
            PermissionManager(
                policy=(
                    self.safety_policy
                )
            )
        )

        self.risk_classifier = (
            RiskClassifier(
                registry=(
                    self.tool_registry
                )
            )
        )

        self.approval_manager = (
            ApprovalManager(
                audit_logger=(
                    self.audit_logger
                )
            )
        )

        self.execution_authorizer = (
            ExecutionAuthorizer(
                classifier=(
                    self.risk_classifier
                ),
                permission_manager=(
                    self.permission_manager
                ),
                approval_manager=(
                    self.approval_manager
                ),
            )
        )

        self.safety_enforcer = (
            SafetyEnforcer(
                authorizer=(
                    self.execution_authorizer
                ),
                approval_manager=(
                    self.approval_manager
                ),
                audit_logger=(
                    self.audit_logger
                ),
            )
        )

        self.error_classifier = (
            ErrorClassifier()
        )

        self.recovery_manager = (
            RecoveryManager(
                classifier=(
                    self.error_classifier
                )
            )
        )

        self.reliability_policy = (
            ReliabilityPolicy(
                failure_threshold=3,
                recovery_timeout_seconds=60,
            )
        )

        self.reliability_manager = (
            ReliabilityManager(
                policy=(
                    self.reliability_policy
                )
            )
        )

        self.execution_runner = (
            ExecutionRunner(
                execution_manager=(
                    self.execution_manager
                ),
                tool_executor=(
                    self.tool_executor
                ),
                tool_binding_manager=(
                    self.tool_binding_manager
                ),
                retry_policy=(
                    self.retry_policy
                ),
                execution_guard=(
                    self.execution_guard
                ),
                execution_authorizer=(
                    self.execution_authorizer
                ),
                reliability_manager=(
                    self.reliability_manager
                ),
            )
        )

        self.kernel = AuraKernel(
            model_manager=(
                self.model_manager
            ),
            memory_manager=(
                self.memory_manager
            ),
            planner=(
                self.planner
            ),
            tool_discovery=(
                self.tool_discovery
            ),
            tool_executor=(
                self.tool_executor
            ),
        )

    def _configure_models(
        self,
    ) -> None:
        mock_provider = (
            MockModelProvider()
        )

        self.model_manager.register_provider(
            mock_provider,
            make_default=True,
        )

        try:
            ollama_provider = (
                OllamaProvider()
            )

            self.model_manager.register_provider(
                ollama_provider
            )

            self.model_manager.set_default_provider(
                ollama_provider.name
            )

            self.model_manager.set_fallback_provider(
                mock_provider.name
            )

        except Exception as exc:
            logger.warning(
                "Could not configure "
                "Ollama provider: %s",
                exc,
            )

    def initialize(
        self,
    ) -> None:
        if self._initialized:
            return

        self.kernel.initialize()

        self._initialized = True

    def shutdown(
        self,
    ) -> None:
        if not self._initialized:
            return

        self.kernel.shutdown()

        self._initialized = False

    def is_ready(
        self,
    ) -> bool:
        return (
            self._initialized
            and self.kernel.is_ready()
        )


container = Container()