from typing import Any

from aura.tools.base import Tool
from aura.tools.models import (
    ToolParameter,
    ToolParameterType,
)


class ToolArgumentValidator:
    def validate(
        self,
        tool: Tool,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        parameters = {
            parameter.name: parameter
            for parameter in tool.parameters
        }

        self._validate_unexpected_arguments(
            parameters=parameters,
            arguments=arguments,
        )

        validated_arguments = {}

        for parameter in tool.parameters:
            value_exists = (
                parameter.name
                in arguments
            )

            if not value_exists:
                if parameter.required:
                    raise ValueError(
                        f"Missing required argument "
                        f"'{parameter.name}'."
                    )

                if parameter.default is not None:
                    validated_arguments[
                        parameter.name
                    ] = parameter.default

                continue

            value = arguments[
                parameter.name
            ]

            self._validate_type(
                parameter=parameter,
                value=value,
            )

            self._validate_choices(
                parameter=parameter,
                value=value,
            )

            validated_arguments[
                parameter.name
            ] = value

        return validated_arguments

    def _validate_unexpected_arguments(
        self,
        parameters: dict[str, ToolParameter],
        arguments: dict[str, Any],
    ) -> None:
        valid_names = set(
            parameters.keys()
        )

        received_names = set(
            arguments.keys()
        )

        unexpected = (
            received_names
            - valid_names
        )

        if unexpected:
            unexpected_name = sorted(
                unexpected
            )[0]

            raise ValueError(
                f"Unexpected argument "
                f"'{unexpected_name}'."
            )

    def _validate_type(
        self,
        parameter: ToolParameter,
        value: Any,
    ) -> None:
        expected_type = (
            parameter.parameter_type
        )

        is_valid = self._matches_type(
            expected_type=expected_type,
            value=value,
        )

        if not is_valid:
            raise ValueError(
                f"Argument '{parameter.name}' "
                f"must be of type "
                f"'{expected_type.value}'."
            )

    def _matches_type(
        self,
        expected_type: ToolParameterType,
        value: Any,
    ) -> bool:
        if (
            expected_type
            == ToolParameterType.STRING
        ):
            return isinstance(
                value,
                str,
            )

        if (
            expected_type
            == ToolParameterType.INTEGER
        ):
            return (
                isinstance(
                    value,
                    int,
                )
                and not isinstance(
                    value,
                    bool,
                )
            )

        if (
            expected_type
            == ToolParameterType.FLOAT
        ):
            return (
                isinstance(
                    value,
                    float,
                )
                and not isinstance(
                    value,
                    bool,
                )
            )

        if (
            expected_type
            == ToolParameterType.BOOLEAN
        ):
            return isinstance(
                value,
                bool,
            )

        if (
            expected_type
            == ToolParameterType.LIST
        ):
            return isinstance(
                value,
                list,
            )

        if (
            expected_type
            == ToolParameterType.OBJECT
        ):
            return isinstance(
                value,
                dict,
            )

        return False

    def _validate_choices(
        self,
        parameter: ToolParameter,
        value: Any,
    ) -> None:
        if parameter.choices is None:
            return

        if value not in parameter.choices:
            raise ValueError(
                f"Argument '{parameter.name}' "
                f"must be one of "
                f"{parameter.choices}."
            )