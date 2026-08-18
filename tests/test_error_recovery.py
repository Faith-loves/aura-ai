from aura.safety.errors import (
    ErrorCategory,
    RecoveryAction,
)
from aura.safety.recovery import (
    ErrorClassifier,
    RecoveryManager,
)


def test_validation_error_classification():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_code="validation_error"
    )

    assert (
        result.category
        == ErrorCategory.VALIDATION
    )

    assert (
        result.recovery_action
        == RecoveryAction.FIX_INPUT
    )

    assert result.retryable is False
    assert result.recoverable is True
    assert result.fatal is False


def test_authorization_error_classification():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_code=(
            "execution_authorization_failed"
        )
    )

    assert (
        result.category
        == ErrorCategory.AUTHORIZATION
    )

    assert (
        result.recovery_action
        == RecoveryAction.STOP
    )

    assert result.fatal is True


def test_approval_required_classification():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_code="approval_required"
    )

    assert (
        result.category
        == ErrorCategory.APPROVAL
    )

    assert (
        result.recovery_action
        == RecoveryAction
        .REQUIRE_APPROVAL
    )

    assert result.recoverable is True


def test_binding_error_classification():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_code="automatic_binding_failed"
    )

    assert (
        result.category
        == ErrorCategory.BINDING
    )

    assert (
        result.recovery_action
        == RecoveryAction.REBIND_TOOL
    )

    assert result.recoverable is True


def test_execution_limit_is_fatal():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_code=(
            "execution_limit_exceeded"
        )
    )

    assert (
        result.category
        == ErrorCategory.EXECUTION_LIMIT
    )

    assert result.fatal is True
    assert result.retryable is False


def test_transient_execution_error():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_code="execution_error"
    )

    assert (
        result.category
        == ErrorCategory.TOOL_TRANSIENT
    )

    assert (
        result.recovery_action
        == RecoveryAction.RETRY
    )

    assert result.retryable is True
    assert result.recoverable is True


def test_temporary_tool_failure_is_transient():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_code="tool_failed",
        error_message=(
            "Temporary service unavailable."
        ),
    )

    assert (
        result.category
        == ErrorCategory.TOOL_TRANSIENT
    )

    assert result.retryable is True


def test_permanent_tool_failure():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_code="tool_failed",
        error_message=(
            "Division by zero is not allowed."
        ),
    )

    assert (
        result.category
        == ErrorCategory.TOOL_PERMANENT
    )

    assert result.retryable is False
    assert result.fatal is True


def test_binding_detected_from_message():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_message=(
            "No suitable tool found "
            "for this plan step."
        )
    )

    assert (
        result.category
        == ErrorCategory.BINDING
    )


def test_approval_detected_from_message():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_message=(
            "Tool execution requires approval."
        )
    )

    assert (
        result.category
        == ErrorCategory.APPROVAL
    )


def test_unknown_error():
    classifier = ErrorClassifier()

    result = classifier.classify(
        error_code="something_new"
    )

    assert (
        result.category
        == ErrorCategory.UNKNOWN
    )

    assert (
        result.recovery_action
        == RecoveryAction.NONE
    )

    assert result.fatal is True


def test_recovery_manager_should_retry():
    manager = RecoveryManager()

    assert (
        manager.should_retry(
            error_code="execution_error"
        )
        is True
    )


def test_recovery_manager_does_not_retry_validation():
    manager = RecoveryManager()

    assert (
        manager.should_retry(
            error_code="validation_error"
        )
        is False
    )


def test_recovery_manager_can_recover_approval():
    manager = RecoveryManager()

    assert (
        manager.can_recover(
            error_code="approval_required"
        )
        is True
    )


def test_recovery_manager_cannot_recover_limit():
    manager = RecoveryManager()

    assert (
        manager.can_recover(
            error_code=(
                "execution_limit_exceeded"
            )
        )
        is False
    )