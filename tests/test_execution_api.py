from fastapi.testclient import TestClient

from apps.api.main import app
from aura.core.container import container


def clear_test_state():
    container.execution_store.clear()
    container.plan_store.clear()


def create_test_plan(
    client: TestClient,
):
    response = client.post(
        "/plans",
        json={
            "goal":
                "Get current time"
        },
    )

    assert response.status_code == 200

    return response.json()


def test_create_execution():
    with TestClient(app) as client:
        clear_test_state()

        plan = create_test_plan(
            client
        )

        response = client.post(
            "/executions",
            json={
                "plan_id":
                    plan["id"],
                "metadata": {
                    "source": "test",
                },
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["plan_id"]
            == plan["id"]
        )

        assert (
            data["status"]
            == "pending"
        )

        assert (
            data["metadata"][
                "source"
            ]
            == "test"
        )

        assert (
            len(
                data[
                    "step_executions"
                ]
            )
            > 0
        )


def test_create_execution_for_missing_plan():
    with TestClient(app) as client:
        clear_test_state()

        response = client.post(
            "/executions",
            json={
                "plan_id":
                    "missing-plan"
            },
        )

        assert (
            response.status_code
            == 404
        )

        assert (
            response.json()["detail"]
            == "Plan not found."
        )


def test_list_executions():
    with TestClient(app) as client:
        clear_test_state()

        plan = create_test_plan(
            client
        )

        client.post(
            "/executions",
            json={
                "plan_id":
                    plan["id"]
            },
        )

        response = client.get(
            "/executions"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1


def test_get_execution():
    with TestClient(app) as client:
        clear_test_state()

        plan = create_test_plan(
            client
        )

        created = client.post(
            "/executions",
            json={
                "plan_id":
                    plan["id"]
            },
        ).json()

        response = client.get(
            f"/executions/"
            f"{created['id']}"
        )

        assert response.status_code == 200

        assert (
            response.json()["id"]
            == created["id"]
        )


def test_get_missing_execution():
    with TestClient(app) as client:
        clear_test_state()

        response = client.get(
            "/executions/missing"
        )

        assert (
            response.status_code
            == 404
        )


def test_start_execution():
    with TestClient(app) as client:
        clear_test_state()

        plan = create_test_plan(
            client
        )

        execution = client.post(
            "/executions",
            json={
                "plan_id":
                    plan["id"]
            },
        ).json()

        response = client.post(
            f"/executions/"
            f"{execution['id']}"
            "/start"
        )

        assert response.status_code == 200

        assert (
            response.json()["status"]
            == "running"
        )


def test_pause_and_resume_execution():
    with TestClient(app) as client:
        clear_test_state()

        plan = create_test_plan(
            client
        )

        execution = client.post(
            "/executions",
            json={
                "plan_id":
                    plan["id"]
            },
        ).json()

        execution_id = (
            execution["id"]
        )

        start = client.post(
            f"/executions/"
            f"{execution_id}/start"
        )

        assert start.status_code == 200

        pause = client.post(
            f"/executions/"
            f"{execution_id}/pause"
        )

        assert pause.status_code == 200

        assert (
            pause.json()["status"]
            == "paused"
        )

        resume = client.post(
            f"/executions/"
            f"{execution_id}/resume"
        )

        assert resume.status_code == 200

        assert (
            resume.json()["status"]
            == "running"
        )


def test_cancel_execution():
    with TestClient(app) as client:
        clear_test_state()

        plan = create_test_plan(
            client
        )

        execution = client.post(
            "/executions",
            json={
                "plan_id":
                    plan["id"]
            },
        ).json()

        execution_id = (
            execution["id"]
        )

        client.post(
            f"/executions/"
            f"{execution_id}/start"
        )

        response = client.post(
            f"/executions/"
            f"{execution_id}/cancel"
        )

        assert response.status_code == 200

        assert (
            response.json()["status"]
            == "cancelled"
        )


def test_delete_execution():
    with TestClient(app) as client:
        clear_test_state()

        plan = create_test_plan(
            client
        )

        execution = client.post(
            "/executions",
            json={
                "plan_id":
                    plan["id"]
            },
        ).json()

        execution_id = (
            execution["id"]
        )

        response = client.delete(
            f"/executions/"
            f"{execution_id}"
        )

        assert response.status_code == 200

        assert (
            response.json()[
                "success"
            ]
            is True
        )

        get_response = client.get(
            f"/executions/"
            f"{execution_id}"
        )

        assert (
            get_response.status_code
            == 404
        )


def test_delete_missing_execution():
    with TestClient(app) as client:
        clear_test_state()

        response = client.delete(
            "/executions/missing"
        )

        assert (
            response.status_code
            == 404
        )