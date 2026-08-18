from enum import Enum


class ToolErrorCode(str, Enum):
    TOOL_NOT_FOUND = "tool_not_found"
    VALIDATION_ERROR = "validation_error"
    EXECUTION_ERROR = "execution_error"
    INVALID_RESULT = "invalid_result"
    TOOL_FAILED = "tool_failed"


class ToolError(Exception):
    def __init__(
        self,
        message: str,
        code: ToolErrorCode,
    ):
        super().__init__(message)

        self.message = message
        self.code = code


class ToolNotFoundError(ToolError):
    def __init__(
        self,
        tool_name: str,
    ):
        super().__init__(
            message=(
                f"Tool '{tool_name}' "
                "is not registered."
            ),
            code=ToolErrorCode.TOOL_NOT_FOUND,
        )


class ToolValidationError(ToolError):
    def __init__(
        self,
        message: str,
    ):
        super().__init__(
            message=message,
            code=ToolErrorCode.VALIDATION_ERROR,
        )


class ToolExecutionError(ToolError):
    def __init__(
        self,
        message: str,
    ):
        super().__init__(
            message=message,
            code=ToolErrorCode.EXECUTION_ERROR,
        )


class InvalidToolResultError(ToolError):
    def __init__(
        self,
        tool_name: str,
    ):
        super().__init__(
            message=(
                f"Tool '{tool_name}' "
                "returned an invalid result."
            ),
            code=ToolErrorCode.INVALID_RESULT,
        )