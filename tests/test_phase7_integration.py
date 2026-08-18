from aura.core.container import (
    Container,
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
from aura.safety.permissions import (
    PermissionManager,
)
from aura.safety.recovery import (
    RecoveryManager,
)
from aura.safety.reliability import (
    ReliabilityManager,
)


def test_phase7_components_are_wired():
    container = Container()

    assert isinstance(
        container.permission_manager,
        PermissionManager,
    )

    assert isinstance(
        container.risk_classifier,
        RiskClassifier,
    )

    assert isinstance(
        container.approval_manager,
        ApprovalManager,
    )

    assert isinstance(
        container.execution_authorizer,
        ExecutionAuthorizer,
    )

    assert isinstance(
        container.safety_enforcer,
        SafetyEnforcer,
    )

    assert isinstance(
        container.audit_logger,
        AuditLogger,
    )

    assert isinstance(
        container.recovery_manager,
        RecoveryManager,
    )

    assert isinstance(
        container.reliability_manager,
        ReliabilityManager,
    )


def test_shared_safety_dependencies():
    container = Container()

    assert (
        container.permission_manager.policy
        is container.safety_policy
    )

    assert (
        container.risk_classifier.registry
        is container.tool_registry
    )

    assert (
        container.execution_authorizer
        .approval_manager
        is container.approval_manager
    )

    assert (
        container.safety_enforcer
        .audit_logger
        is container.audit_logger
    )

    assert (
        container.execution_runner
        .reliability_manager
        is container.reliability_manager
    )


def test_default_phase7_policy_is_safe():
    container = Container()

    assert (
        container.safety_policy
        .allow_low_risk
        is True
    )

    assert (
        container.safety_policy
        .allow_medium_risk
        is True
    )

    assert (
        container.safety_policy
        .require_approval_for_high_risk
        is True
    )

    assert (
        container.safety_policy
        .block_critical_risk
        is True
    )


def test_phase7_stores_start_empty():
    container = Container()

    assert (
        container.approval_manager.count()
        == 0
    )

    assert (
        container.audit_logger.count()
        == 0
    )

    assert (
        container.reliability_manager.count()
        == 0
    )