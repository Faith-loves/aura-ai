from aura.safety.classifier import (
    RiskClassifier,
)
from aura.safety.models import (
    RiskLevel,
    SafetyContext,
)
from aura.tools.loader import ToolLoader
from aura.tools.registry import (
    ToolRegistry,
)


def create_classifier():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    return RiskClassifier(
        registry=registry
    )


def test_echo_is_low_risk():
    classifier = create_classifier()

    assert (
        classifier.classify_tool(
            "echo"
        )
        == RiskLevel.LOW
    )


def test_calculator_is_low_risk():
    classifier = create_classifier()

    assert (
        classifier.classify_tool(
            "calculator"
        )
        == RiskLevel.LOW
    )


def test_current_time_is_low_risk():
    classifier = create_classifier()

    assert (
        classifier.classify_tool(
            "current_time"
        )
        == RiskLevel.LOW
    )


def test_text_stats_is_low_risk():
    classifier = create_classifier()

    assert (
        classifier.classify_tool(
            "text_stats"
        )
        == RiskLevel.LOW
    )


def test_system_info_is_medium_risk():
    classifier = create_classifier()

    assert (
        classifier.classify_tool(
            "system_info"
        )
        == RiskLevel.MEDIUM
    )


def test_unknown_tool_defaults_to_medium():
    classifier = RiskClassifier()

    assert (
        classifier.classify_tool(
            "unknown_tool"
        )
        == RiskLevel.MEDIUM
    )


def test_delete_action_is_high_risk():
    classifier = RiskClassifier()

    assert (
        classifier.classify_action(
            "delete"
        )
        == RiskLevel.HIGH
    )


def test_shell_action_is_high_risk():
    classifier = RiskClassifier()

    assert (
        classifier.classify_action(
            "execute_shell"
        )
        == RiskLevel.HIGH
    )


def test_read_file_is_medium_risk():
    classifier = RiskClassifier()

    assert (
        classifier.classify_action(
            "read_file"
        )
        == RiskLevel.MEDIUM
    )


def test_format_disk_is_critical():
    classifier = RiskClassifier()

    assert (
        classifier.classify_action(
            "format_disk"
        )
        == RiskLevel.CRITICAL
    )


def test_unknown_action_defaults_low():
    classifier = RiskClassifier()

    assert (
        classifier.classify_action(
            "calculate_value"
        )
        == RiskLevel.LOW
    )


def test_context_uses_highest_risk():
    classifier = create_classifier()

    context = SafetyContext(
        tool_name="calculator",
        action="delete",
    )

    result = (
        classifier.classify_context(
            context
        )
    )

    assert result == RiskLevel.HIGH


def test_sensitive_arguments_increase_risk():
    classifier = create_classifier()

    context = SafetyContext(
        tool_name="calculator",
        action="execute",
        arguments={
            "api_key": "secret-value"
        },
    )

    result = (
        classifier.classify_context(
            context
        )
    )

    assert result == RiskLevel.HIGH


def test_tool_override():
    classifier = create_classifier()

    classifier.set_tool_risk(
        "calculator",
        RiskLevel.HIGH,
    )

    assert (
        classifier.classify_tool(
            "calculator"
        )
        == RiskLevel.HIGH
    )


def test_action_override():
    classifier = RiskClassifier()

    classifier.set_action_risk(
        "calculate_value",
        RiskLevel.CRITICAL,
    )

    assert (
        classifier.classify_action(
            "calculate_value"
        )
        == RiskLevel.CRITICAL
    )


def test_clear_tool_override():
    classifier = create_classifier()

    classifier.set_tool_risk(
        "calculator",
        RiskLevel.HIGH,
    )

    removed = (
        classifier.clear_tool_override(
            "calculator"
        )
    )

    assert removed is True

    assert (
        classifier.classify_tool(
            "calculator"
        )
        == RiskLevel.LOW
    )


def test_clear_missing_tool_override():
    classifier = create_classifier()

    assert (
        classifier.clear_tool_override(
            "missing"
        )
        is False
    )


def test_clear_action_override():
    classifier = RiskClassifier()

    classifier.set_action_risk(
        "custom",
        RiskLevel.HIGH,
    )

    removed = (
        classifier.clear_action_override(
            "custom"
        )
    )

    assert removed is True

    assert (
        classifier.classify_action(
            "custom"
        )
        == RiskLevel.LOW
    )