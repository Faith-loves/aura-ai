from fastapi.testclient import TestClient

from apps.api.main import app


def test_list_tools_endpoint():
    with TestClient(app) as client:
        response = client.get(
            "/tools"
        )

        assert response.status_code == 200

        data = response.json()

        names = {
            tool["name"]
            for tool in data
        }

        assert names == {
            "echo",
            "system_info",
            "calculator",
            "current_time",
            "text_stats",
        }


def test_tool_schema_contains_metadata():
    with TestClient(app) as client:
        response = client.get(
            "/tools"
        )

        data = response.json()

        calculator = next(
            tool
            for tool in data
            if (
                tool["name"]
                == "calculator"
            )
        )

        assert (
            calculator["category"]
            == "utility"
        )

        assert (
            calculator["dangerous"]
            is False
        )

        assert len(
            calculator["parameters"]
        ) == 3


def test_search_tools_endpoint():
    with TestClient(app) as client:
        response = client.get(
            "/tools/search",
            params={
                "query": "math",
            },
        )

        assert response.status_code == 200

        data = response.json()

        names = {
            tool["name"]
            for tool in data
        }

        assert (
            "calculator"
            in names
        )


def test_search_tools_by_text_tag():
    with TestClient(app) as client:
        response = client.get(
            "/tools/search",
            params={
                "query": "statistics",
            },
        )

        assert response.status_code == 200

        names = {
            tool["name"]
            for tool in response.json()
        }

        assert (
            "text_stats"
            in names
        )


def test_empty_search_query_is_rejected():
    with TestClient(app) as client:
        response = client.get(
            "/tools/search",
            params={
                "query": "",
            },
        )

        assert (
            response.status_code
            == 422
        )


def test_execute_echo_tool():
    with TestClient(app) as client:
        response = client.post(
            "/tools/echo/execute",
            json={
                "arguments": {
                    "message":
                        "Hello AURA",
                }
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is True

        assert (
            data["tool_name"]
            == "echo"
        )

        assert (
            data["output"]
            == "Hello AURA"
        )

        assert (
            data["status"]
            == "success"
        )

        assert (
            data["error_code"]
            is None
        )


def test_execute_calculator_tool():
    with TestClient(app) as client:
        response = client.post(
            "/tools/calculator/execute",
            json={
                "arguments": {
                    "operation": "add",
                    "a": 10.0,
                    "b": 5.0,
                }
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is True

        assert data["output"] == 15.0

        assert (
            data["tool_name"]
            == "calculator"
        )


def test_execute_current_time_tool():
    with TestClient(app) as client:
        response = client.post(
            "/tools/current_time/execute",
            json={
                "arguments": {}
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is True

        assert (
            data["output"]["timezone"]
            == "UTC"
        )


def test_execute_unknown_tool():
    with TestClient(app) as client:
        response = client.post(
            "/tools/missing/execute",
            json={
                "arguments": {}
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is False

        assert (
            data["error_code"]
            == "tool_not_found"
        )

        assert (
            data["status"]
            == "failed"
        )


def test_execute_tool_validation_failure():
    with TestClient(app) as client:
        response = client.post(
            "/tools/echo/execute",
            json={
                "arguments": {}
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is False

        assert (
            data["error_code"]
            == "validation_error"
        )


def test_execution_response_has_tracking():
    with TestClient(app) as client:
        response = client.post(
            "/tools/echo/execute",
            json={
                "arguments": {
                    "message": "AURA",
                }
            },
        )

        data = response.json()

        assert data["execution_id"]

        assert data["started_at"]

        assert data["completed_at"]

        assert (
            data["duration_ms"]
            is not None
        )


def test_calculator_division_by_zero():
    with TestClient(app) as client:
        response = client.post(
            "/tools/calculator/execute",
            json={
                "arguments": {
                    "operation": "divide",
                    "a": 10.0,
                    "b": 0.0,
                }
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is False

        assert (
            data["error_code"]
            == "tool_failed"
        )

        assert (
            data["error"]
            == (
                "Division by zero "
                "is not allowed."
            )
        )