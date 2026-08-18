from dataclasses import dataclass
from enum import Enum


class ErrorCategory(str, Enum):
    VALIDATION = "validation"
    AUTHORIZATION = "authorization"
    APPROVAL = "approval"
    TOOL_TRANSIENT = "tool_transient"
    TOOL_PERMANENT = "tool_permanent"
    EXECUTION_LIMIT = "execution_limit"
    BINDING = "binding"
    UNKNOWN = "unknown"


class RecoveryAction(str, Enum):
    RETRY = "retry"
    REQUIRE_APPROVAL = "require_approval"
    STOP = "stop"
    FIX_INPUT = "fix_input"
    REBIND_TOOL = "rebind_tool"
    NONE = "none"


@dataclass
class ErrorClassification:
    category: ErrorCategory
    recovery_action: RecoveryAction
    retryable: bool = False
    recoverable: bool = False
    fatal: bool = False
    reason: str = ""