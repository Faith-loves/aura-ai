from fastapi.testclient import TestClient

from apps.api.main import app
from aura.core.container import container


def clear_plans():
    container.plan_store.clear()


def test_create_plan_endpoint():
    clear_plans()

    with TestClient(app) as client:
        response = client.post(
            "/plans",
            json={
                "goal":
                    "Build a REST API.",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["goal"] == (
            "Build a REST API."
        )

        assert data["status"] == "pending"

        assert len(
            data["steps"]
        ) == 6


def test_list_plans_endpoint():
    clear_plans()

    with TestClient(app) as client:
        client.post(
            "/plans",
            json={
                "goal":
                    "Build a frontend dashboard.",
            },
        )

        response = client.get(
            "/plans"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1


def test_get_plan_endpoint():
    clear_plans()

    with TestClient(app) as client:
        created = client.post(
            "/plans",
            json={
                "goal":
                    "Build a REST API.",
            },
        ).json()

        response = client.get(
            f"/plans/{created['id']}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == created["id"]


def test_unknown_plan_returns_404():
    clear_plans()

    with TestClient(app) as client:
        response = client.get(
            "/plans/missing-plan"
        )

        assert response.status_code == 404


def test_start_plan_endpoint():
    clear_plans()

    with TestClient(app) as client:
        created = client.post(
            "/plans",
            json={
                "goal":
                    "Build a REST API.",
            },
        ).json()

        response = client.post(
            f"/plans/{created['id']}/start"
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["status"]
            == "in_progress"
        )

        assert (
            data["steps"][0]["status"]
            == "ready"
        )


def test_start_and_complete_step():
    clear_plans()

    with TestClient(app) as client:
        created = client.post(
            "/plans",
            json={
                "goal":
                    "Build a REST API.",
            },
        ).json()

        plan_id = created["id"]

        started = client.post(
            f"/plans/{plan_id}/start"
        ).json()

        step_id = (
            started["steps"][0]["id"]
        )

        response = client.post(
            f"/plans/{plan_id}"
            f"/steps/{step_id}/start"
        )

        assert response.status_code == 200

        assert (
            response.json()["steps"][0]["status"]
            == "in_progress"
        )

        response = client.post(
            f"/plans/{plan_id}"
            f"/steps/{step_id}/complete"
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["steps"][0]["status"]
            == "completed"
        )

        assert (
            data["steps"][1]["status"]
            == "ready"
        )


def test_update_step_priority():
    clear_plans()

    with TestClient(app) as client:
        created = client.post(
            "/plans",
            json={
                "goal":
                    "Build a frontend dashboard.",
            },
        ).json()

        step_id = (
            created["steps"][0]["id"]
        )

        response = client.patch(
            f"/plans/{created['id']}"
            f"/steps/{step_id}/priority",
            json={
                "priority": 2,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["steps"][0]["priority"]
            == 2
        )


def test_complete_plan_requires_finished_steps():
    clear_plans()

    with TestClient(app) as client:
        created = client.post(
            "/plans",
            json={
                "goal":
                    "Build a REST API.",
            },
        ).json()

        client.post(
            f"/plans/{created['id']}/start"
        )

        response = client.post(
            f"/plans/{created['id']}/complete"
        )

        assert response.status_code == 400


def test_delete_plan_endpoint():
    clear_plans()

    with TestClient(app) as client:
        created = client.post(
            "/plans",
            json={
                "goal":
                    "Build a REST API.",
            },
        ).json()

        response = client.delete(
            f"/plans/{created['id']}"
        )

        assert response.status_code == 200

        response = client.get(
            f"/plans/{created['id']}"
        )

        assert response.status_code == 404


def test_empty_goal_is_rejected():
    clear_plans()

    with TestClient(app) as client:
        response = client.post(
            "/plans",
            json={
                "goal": "",
            },
        )

        assert response.status_code == 422