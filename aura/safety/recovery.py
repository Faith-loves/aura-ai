from aura.core.logger import logger
from aura.safety.errors import (
    ErrorCategory,
    ErrorClassification,
    RecoveryAction,
)


class ErrorClassifier:
    def classify(
        self,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> ErrorClassification:
        code = (
            error_code
            or ""
        ).strip().lower()

        message = (
            error_message
            or ""
        ).strip().lower()

        if code in {
            "validation_error",
            "invalid_arguments",
            "invalid_input",
        }:
            return ErrorClassification(
                category=(
                    ErrorCategory.VALIDATION
                ),
                recovery_action=(
                    RecoveryAction.FIX_INPUT
                ),
                retryable=False,
                recoverable=True,
                fatal=False,
                reason=(
                    "Input validation failed."
                ),
            )

        if code in {
            "execution_authorization_failed",
            "authorization_failed",
            "safety_denied",
        }:
            return ErrorClassification(
                category=(
                    ErrorCategory.AUTHORIZATION
                ),
                recovery_action=(
                    RecoveryAction.STOP
                ),
                retryable=False,
                recoverable=False,
                fatal=True,
                reason=(
                    "Execution was denied by "
                    "authorization policy."
                ),
            )

        if code in {
            "approval_required",
        }:
            return ErrorClassification(
                category=(
                    ErrorCategory.APPROVAL
                ),
                recovery_action=(
                    RecoveryAction
                    .REQUIRE_APPROVAL
                ),
                retryable=False,
                recoverable=True,
                fatal=False,
                reason=(
                    "Execution is waiting for "
                    "approval."
                ),
            )

        if code in {
            "automatic_binding_failed",
            "binding_failed",
        }:
            return ErrorClassification(
                category=(
                    ErrorCategory.BINDING
                ),
                recovery_action=(
                    RecoveryAction.REBIND_TOOL
                ),
                retryable=False,
                recoverable=True,
                fatal=False,
                reason=(
                    "Tool binding failed."
                ),
            )

        if code in {
            "execution_limit_exceeded",
        }:
            return ErrorClassification(
                category=(
                    ErrorCategory.EXECUTION_LIMIT
                ),
                recovery_action=(
                    RecoveryAction.STOP
                ),
                retryable=False,
                recoverable=False,
                fatal=True,
                reason=(
                    "Execution safety limit "
                    "was exceeded."
                ),
            )

        if code in {
            "execution_error",
            "timeout",
            "temporary_failure",
            "service_unavailable",
        }:
            return ErrorClassification(
                category=(
                    ErrorCategory.TOOL_TRANSIENT
                ),
                recovery_action=(
                    RecoveryAction.RETRY
                ),
                retryable=True,
                recoverable=True,
                fatal=False,
                reason=(
                    "Transient tool failure."
                ),
            )

        if code in {
            "tool_failed",
            "tool_error",
        }:
            if any(
                marker in message
                for marker in {
                    "temporary",
                    "timeout",
                    "unavailable",
                    "try again",
                }
            ):
                return ErrorClassification(
                    category=(
                        ErrorCategory
                        .TOOL_TRANSIENT
                    ),
                    recovery_action=(
                        RecoveryAction.RETRY
                    ),
                    retryable=True,
                    recoverable=True,
                    fatal=False,
                    reason=(
                        "Tool failure appears "
                        "transient."
                    ),
                )

            return ErrorClassification(
                category=(
                    ErrorCategory.TOOL_PERMANENT
                ),
                recovery_action=(
                    RecoveryAction.STOP
                ),
                retryable=False,
                recoverable=False,
                fatal=True,
                reason=(
                    "Tool execution failed "
                    "permanently."
                ),
            )

        if (
            "approval"
            in message
        ):
            return ErrorClassification(
                category=(
                    ErrorCategory.APPROVAL
                ),
                recovery_action=(
                    RecoveryAction
                    .REQUIRE_APPROVAL
                ),
                retryable=False,
                recoverable=True,
                fatal=False,
                reason=(
                    "Approval is required."
                ),
            )

        if (
            "no suitable tool"
            in message
            or "no bound tool"
            in message
        ):
            return ErrorClassification(
                category=(
                    ErrorCategory.BINDING
                ),
                recovery_action=(
                    RecoveryAction.REBIND_TOOL
                ),
                retryable=False,
                recoverable=True,
                fatal=False,
                reason=(
                    "Tool binding could not "
                    "be completed."
                ),
            )

        return ErrorClassification(
            category=ErrorCategory.UNKNOWN,
            recovery_action=(
                RecoveryAction.NONE
            ),
            retryable=False,
            recoverable=False,
            fatal=True,
            reason="Unknown failure.",
        )


class RecoveryManager:
    def __init__(
        self,
        classifier: ErrorClassifier | None = None,
    ):
        self.classifier = (
            classifier
            or ErrorClassifier()
        )

    def analyze(
        self,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> ErrorClassification:
        classification = (
            self.classifier.classify(
                error_code=error_code,
                error_message=error_message,
            )
        )

        logger.info(
            "Error classified | "
            "category=%s | "
            "recovery=%s | "
            "retryable=%s | "
            "fatal=%s",
            classification.category.value,
            classification.recovery_action.value,
            classification.retryable,
            classification.fatal,
        )

        return classification

    def should_retry(
        self,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> bool:
        classification = self.analyze(
            error_code=error_code,
            error_message=error_message,
        )

        return classification.retryable

    def can_recover(
        self,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> bool:
        classification = self.analyze(
            error_code=error_code,
            error_message=error_message,
        )

        return classification.recoverable