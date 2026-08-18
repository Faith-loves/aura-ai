from aura.safety.audit import (
    AuditEventType,
    AuditLogger,
)


def test_audit_logger_starts_empty():
    audit = AuditLogger()

    assert audit.count() == 0


def test_create_audit_record():
    audit = AuditLogger()

    record = audit.record(
        event_type=(
            AuditEventType
            .SAFETY_ALLOWED
        ),
        message="Action allowed.",
        execution_id="execution-1",
        plan_id="plan-1",
        step_id="step-1",
        tool_name="calculator",
        risk_level="low",
        success=True,
    )

    assert record.id

    assert (
        record.event_type
        == AuditEventType
        .SAFETY_ALLOWED
    )

    assert (
        record.execution_id
        == "execution-1"
    )

    assert (
        record.tool_name
        == "calculator"
    )

    assert record.success is True

    assert record.created_at

    assert audit.count() == 1


def test_list_audit_records():
    audit = AuditLogger()

    audit.record(
        event_type=(
            AuditEventType
            .SAFETY_ALLOWED
        ),
        message="First",
    )

    audit.record(
        event_type=(
            AuditEventType
            .SAFETY_DENIED
        ),
        message="Second",
    )

    records = audit.list_all()

    assert len(records) == 2


def test_get_audit_record():
    audit = AuditLogger()

    record = audit.record(
        event_type=(
            AuditEventType
            .SAFETY_ALLOWED
        ),
        message="Test",
    )

    result = audit.get(
        record.id
    )

    assert result is record


def test_get_unknown_record():
    audit = AuditLogger()

    assert (
        audit.get("missing")
        is None
    )


def test_list_by_event():
    audit = AuditLogger()

    audit.record(
        event_type=(
            AuditEventType
            .SAFETY_ALLOWED
        ),
        message="Allowed 1",
    )

    audit.record(
        event_type=(
            AuditEventType
            .SAFETY_DENIED
        ),
        message="Denied",
    )

    audit.record(
        event_type=(
            AuditEventType
            .SAFETY_ALLOWED
        ),
        message="Allowed 2",
    )

    records = audit.list_by_event(
        AuditEventType.SAFETY_ALLOWED
    )

    assert len(records) == 2


def test_list_by_execution():
    audit = AuditLogger()

    audit.record(
        event_type=(
            AuditEventType
            .TOOL_EXECUTION_STARTED
        ),
        message="Start",
        execution_id="execution-1",
    )

    audit.record(
        event_type=(
            AuditEventType
            .TOOL_EXECUTION_SUCCEEDED
        ),
        message="Success",
        execution_id="execution-1",
    )

    audit.record(
        event_type=(
            AuditEventType
            .TOOL_EXECUTION_FAILED
        ),
        message="Failure",
        execution_id="execution-2",
    )

    records = (
        audit.list_by_execution(
            "execution-1"
        )
    )

    assert len(records) == 2


def test_list_by_tool():
    audit = AuditLogger()

    audit.record(
        event_type=(
            AuditEventType
            .TOOL_EXECUTION_STARTED
        ),
        message="Calculator",
        tool_name="calculator",
    )

    audit.record(
        event_type=(
            AuditEventType
            .TOOL_EXECUTION_STARTED
        ),
        message="System",
        tool_name="system_info",
    )

    records = audit.list_by_tool(
        "calculator"
    )

    assert len(records) == 1

    assert (
        records[0].tool_name
        == "calculator"
    )


def test_clear_audit_log():
    audit = AuditLogger()

    audit.record(
        event_type=(
            AuditEventType
            .SAFETY_ALLOWED
        ),
        message="One",
    )

    audit.record(
        event_type=(
            AuditEventType
            .SAFETY_DENIED
        ),
        message="Two",
    )

    removed = audit.clear()

    assert removed == 2
    assert audit.count() == 0