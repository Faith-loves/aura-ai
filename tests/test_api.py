from fastapi.testclient import TestClient

from apps.api.main import app
from aura.core.container import container
from aura.models.providers.mock import MockModelProvider


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == "AURA"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "AURA"
        assert data["kernel"]["ready"] is True
        assert data["kernel"]["model_provider"] is not None
        assert "memory_count" in data["kernel"]


def test_models_endpoint():
    with TestClient(app) as client:
        response = client.get("/models")

        assert response.status_code == 200

        data = response.json()

        assert "default_provider" in data
        assert "fallback_provider" in data
        assert "providers" in data

        provider_names = [
            provider["name"]
            for provider in data["providers"]
        ]

        assert "mock" in provider_names
        assert "ollama" in provider_names


def test_run_endpoint():
    original_provider = container.model_manager.default_provider

    container.model_manager.register_provider(
        MockModelProvider(),
        make_default=True,
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/run",
                json={
                    "message": "Hello AURA"
                },
            )

            assert response.status_code == 200

            data = response.json()

            assert data["success"] is True
            assert data["message"] == (
                "Task completed successfully."
            )

            assert data["result"].startswith(
                "Mock model response to:"
            )

            assert "Hello AURA" in data["result"]

            assert data["provider"] == "mock"
            assert data["model"] == "mock-model"
            assert data["used_fallback"] is False

    finally:
        if original_provider is not None:
            container.model_manager.set_default_provider(
                original_provider
            )


def test_run_endpoint_rejects_empty_message():
    with TestClient(app) as client:
        response = client.post(
            "/run",
            json={
                "message": ""
            },
        )

        assert response.status_code == 422

def test_create_memory_endpoint():
    with TestClient(app) as client:
        response = client.post(
            "/memory",
            json={
                "content": "AURA memory API test.",
                "memory_type": "fact",
                "importance": 0.8,
                "metadata": {
                    "source": "api-test"
                },
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["content"] == (
            "AURA memory API test."
        )

        assert data["memory_type"] == "fact"
        assert data["importance"] == 0.8
        assert data["metadata"]["source"] == (
            "api-test"
        )


def test_list_memory_endpoint():
    with TestClient(app) as client:
        client.post(
            "/memory",
            json={
                "content": "List memory test.",
                "memory_type": "fact",
            },
        )

        response = client.get(
            "/memory"
        )

        assert response.status_code == 200

        data = response.json()

        assert isinstance(data, list)

        assert any(
            memory["content"]
            == "List memory test."
            for memory in data
        )


def test_get_memory_endpoint():
    with TestClient(app) as client:
        create_response = client.post(
            "/memory",
            json={
                "content": "Get memory test.",
                "memory_type": "fact",
            },
        )

        memory_id = (
            create_response.json()["id"]
        )

        response = client.get(
            f"/memory/{memory_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == memory_id
        assert data["content"] == (
            "Get memory test."
        )


def test_get_unknown_memory_returns_404():
    with TestClient(app) as client:
        response = client.get(
            "/memory/unknown-memory-id"
        )

        assert response.status_code == 404


def test_search_memory_endpoint():
    with TestClient(app) as client:
        client.post(
            "/memory",
            json={
                "content":
                    "AURA uses FastAPI for its API.",
                "memory_type": "project",
                "importance": 0.9,
            },
        )

        client.post(
            "/memory",
            json={
                "content":
                    "Football is a popular sport.",
                "memory_type": "fact",
            },
        )

        response = client.post(
            "/memory/search",
            json={
                "query": "AURA FastAPI",
                "limit": 5,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) >= 1

        matching_results = [
            item
            for item in data
            if (
                item["memory"]["content"]
                == "AURA uses FastAPI for its API."
            )
        ]

        assert len(matching_results) >= 1

        assert (
            matching_results[0]["score"]
            > 0
        )
        
def test_search_memory_by_type():
    with TestClient(app) as client:
        client.post(
            "/memory",
            json={
                "content":
                    "AURA API project information.",
                "memory_type": "project",
            },
        )

        client.post(
            "/memory",
            json={
                "content":
                    "AURA general fact.",
                "memory_type": "fact",
            },
        )

        response = client.post(
            "/memory/search",
            json={
                "query": "AURA",
                "memory_type": "project",
                "limit": 5,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert all(
            item["memory"]["memory_type"]
            == "project"
            for item in data
        )


def test_delete_memory_endpoint():
    with TestClient(app) as client:
        create_response = client.post(
            "/memory",
            json={
                "content": "Delete via API.",
                "memory_type": "task",
            },
        )

        memory_id = (
            create_response.json()["id"]
        )

        delete_response = client.delete(
            f"/memory/{memory_id}"
        )

        assert delete_response.status_code == 200

        data = delete_response.json()

        assert data["success"] is True

        get_response = client.get(
            f"/memory/{memory_id}"
        )

        assert get_response.status_code == 404


def test_delete_unknown_memory_returns_404():
    with TestClient(app) as client:
        response = client.delete(
            "/memory/unknown-memory-id"
        )

        assert response.status_code == 404