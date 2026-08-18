import pytest

from aura.tools.base import Tool
from aura.tools.models import (
    ToolParameter,
    ToolParameterType,
    ToolResult,
)
from aura.tools.validator import ToolArgumentValidator


class ValidationTool(Tool):
    @property
    def name(self) -> str:
        return "validation_test"

    @property
    def description(self) -> str:
        return (
            "Tool used for argument "
            "validation tests."
        )

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="name",
                description="User name.",
                parameter_type=(
                    ToolParameterType.STRING
                ),
                required=True,
            ),
            ToolParameter(
                name="age",
                description="User age.",
                parameter_type=(
                    ToolParameterType.INTEGER
                ),
                required=False,
                default=18,
            ),
            ToolParameter(
                name="score",
                description="Score value.",
                parameter_type=(
                    ToolParameterType.FLOAT
                ),
                required=False,
            ),
            ToolParameter(
                name="active",
                description="Active status.",
                parameter_type=(
                    ToolParameterType.BOOLEAN
                ),
                required=False,
            ),
            ToolParameter(
                name="tags",
                description="List of tags.",
                parameter_type=(
                    ToolParameterType.LIST
                ),
                required=False,
            ),
            ToolParameter(
                name="settings",
                description="Settings object.",
                parameter_type=(
                    ToolParameterType.OBJECT
                ),
                required=False,
            ),
            ToolParameter(
                name="format",
                description="Output format.",
                parameter_type=(
                    ToolParameterType.STRING
                ),
                required=False,
                default="text",
                choices=[
                    "text",
                    "json",
                ],
            ),
        ]

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            output=kwargs,
        )


def create_validator():
    return ToolArgumentValidator()


def create_tool():
    return ValidationTool()


def test_valid_required_argument():
    validator = create_validator()
    tool = create_tool()

    validated = validator.validate(
        tool=tool,
        arguments={
            "name": "Faith",
        },
    )

    assert (
        validated["name"]
        == "Faith"
    )


def test_missing_required_argument_fails():
    validator = create_validator()
    tool = create_tool()

    with pytest.raises(
        ValueError,
        match="Missing required argument",
    ):
        validator.validate(
            tool=tool,
            arguments={},
        )


def test_default_values_are_added():
    validator = create_validator()
    tool = create_tool()

    validated = validator.validate(
        tool=tool,
        arguments={
            "name": "Faith",
        },
    )

    assert validated["age"] == 18

    assert (
        validated["format"]
        == "text"
    )


def test_unexpected_argument_fails():
    validator = create_validator()
    tool = create_tool()

    with pytest.raises(
        ValueError,
        match="Unexpected argument",
    ):
        validator.validate(
            tool=tool,
            arguments={
                "name": "Faith",
                "unknown": "value",
            },
        )


def test_string_type_validation():
    validator = create_validator()
    tool = create_tool()

    with pytest.raises(
        ValueError,
        match="must be of type 'string'",
    ):
        validator.validate(
            tool=tool,
            arguments={
                "name": 123,
            },
        )


def test_integer_type_validation():
    validator = create_validator()
    tool = create_tool()

    with pytest.raises(
        ValueError,
        match="must be of type 'integer'",
    ):
        validator.validate(
            tool=tool,
            arguments={
                "name": "Faith",
                "age": "18",
            },
        )


def test_boolean_is_not_valid_integer():
    validator = create_validator()
    tool = create_tool()

    with pytest.raises(
        ValueError,
        match="must be of type 'integer'",
    ):
        validator.validate(
            tool=tool,
            arguments={
                "name": "Faith",
                "age": True,
            },
        )


def test_float_type_validation():
    validator = create_validator()
    tool = create_tool()

    validated = validator.validate(
        tool=tool,
        arguments={
            "name": "Faith",
            "score": 95.5,
        },
    )

    assert (
        validated["score"]
        == 95.5
    )


def test_boolean_type_validation():
    validator = create_validator()
    tool = create_tool()

    validated = validator.validate(
        tool=tool,
        arguments={
            "name": "Faith",
            "active": True,
        },
    )

    assert (
        validated["active"]
        is True
    )


def test_list_type_validation():
    validator = create_validator()
    tool = create_tool()

    validated = validator.validate(
        tool=tool,
        arguments={
            "name": "Faith",
            "tags": [
                "python",
                "aura",
            ],
        },
    )

    assert validated["tags"] == [
        "python",
        "aura",
    ]


def test_object_type_validation():
    validator = create_validator()
    tool = create_tool()

    validated = validator.validate(
        tool=tool,
        arguments={
            "name": "Faith",
            "settings": {
                "theme": "dark",
            },
        },
    )

    assert validated["settings"] == {
        "theme": "dark",
    }


def test_valid_choice():
    validator = create_validator()
    tool = create_tool()

    validated = validator.validate(
        tool=tool,
        arguments={
            "name": "Faith",
            "format": "json",
        },
    )

    assert (
        validated["format"]
        == "json"
    )


def test_invalid_choice_fails():
    validator = create_validator()
    tool = create_tool()

    with pytest.raises(
        ValueError,
        match="must be one of",
    ):
        validator.validate(
            tool=tool,
            arguments={
                "name": "Faith",
                "format": "xml",
            },
        )