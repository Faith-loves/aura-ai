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


def test_container_has_safety_policy():
    container = Container()

    assert isinstance(
        container.safety_policy,
        SafetyPolicy,
    )


def test_container_has_permission_manager():
    container = Container()

    assert isinstance(
        container.permission_manager,
        PermissionManager,
    )


def test_permission_manager_uses_policy():
    container = Container()

    assert (
        container.permission_manager.policy
        is container.safety_policy
    )


def test_container_has_risk_classifier():
    container = Container()

    assert isinstance(
        container.risk_classifier,
        RiskClassifier,
    )


def test_risk_classifier_uses_registry():
    container = Container()

    assert (
        container.risk_classifier.registry
        is container.tool_registry
    )


def test_container_has_audit_logger():
    container = Container()

    assert isinstance(
        container.audit_logger,
        AuditLogger,
    )


def test_container_has_approval_manager():
    container = Container()

    assert isinstance(
        container.approval_manager,
        ApprovalManager,
    )


def test_approval_manager_uses_audit_logger():
    container = Container()

    assert (
        container.approval_manager
        .audit_logger
        is container.audit_logger
    )


def test_container_has_authorizer():
    container = Container()

    assert isinstance(
        container.execution_authorizer,
        ExecutionAuthorizer,
    )


def test_authorizer_uses_classifier():
    container = Container()

    assert (
        container.execution_authorizer
        .classifier
        is container.risk_classifier
    )


def test_authorizer_uses_permissions():
    container = Container()

    assert (
        container.execution_authorizer
        .permission_manager
        is container.permission_manager
    )


def test_authorizer_uses_approvals():
    container = Container()

    assert (
        container.execution_authorizer
        .approval_manager
        is container.approval_manager
    )


def test_container_has_safety_enforcer():
    container = Container()

    assert isinstance(
        container.safety_enforcer,
        SafetyEnforcer,
    )


def test_enforcer_uses_authorizer():
    container = Container()

    assert (
        container.safety_enforcer
        .authorizer
        is container.execution_authorizer
    )


def test_enforcer_uses_approval_manager():
    container = Container()

    assert (
        container.safety_enforcer
        .approval_manager
        is container.approval_manager
    )


def test_enforcer_uses_audit_logger():
    container = Container()

    assert (
        container.safety_enforcer
        .audit_logger
        is container.audit_logger
    )


def test_container_has_error_classifier():
    container = Container()

    assert isinstance(
        container.error_classifier,
        ErrorClassifier,
    )


def test_container_has_recovery_manager():
    container = Container()

    assert isinstance(
        container.recovery_manager,
        RecoveryManager,
    )


def test_recovery_manager_uses_classifier():
    container = Container()

    assert (
        container.recovery_manager
        .classifier
        is container.error_classifier
    )


def test_container_has_reliability_policy():
    container = Container()

    assert isinstance(
        container.reliability_policy,
        ReliabilityPolicy,
    )


def test_container_has_reliability_manager():
    container = Container()

    assert isinstance(
        container.reliability_manager,
        ReliabilityManager,
    )


def test_reliability_manager_uses_policy():
    container = Container()

    assert (
        container.reliability_manager
        .policy
        is container.reliability_policy
    )


def test_runner_uses_authorizer():
    container = Container()

    assert (
        container.execution_runner
        .execution_authorizer
        is container.execution_authorizer
    )


def test_runner_uses_reliability_manager():
    container = Container()

    assert (
        container.execution_runner
        .reliability_manager
        is container.reliability_manager
    )