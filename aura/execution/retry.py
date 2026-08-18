from dataclasses import dataclass


@dataclass
class RetryPolicy:
    max_attempts: int = 3

    retryable_error_codes: tuple[str, ...] = (
        "execution_error",
        "tool_failed",
    )

    def __post_init__(
        self,
    ) -> None:
        if self.max_attempts < 1:
            raise ValueError(
                "max_attempts must be "
                "at least 1."
            )

    def should_retry(
        self,
        attempt: int,
        error_code: str | None,
    ) -> bool:
        if attempt >= self.max_attempts:
            return False

        if error_code is None:
            return False

        return (
            error_code
            in self.retryable_error_codes
        )