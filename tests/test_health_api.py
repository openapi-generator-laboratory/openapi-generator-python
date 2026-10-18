# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models.health_status import HealthStatus  # noqa: F401


def test_get_healthz(client: TestClient):
    """Test case for get_healthz

    健康检查
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/healthz",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

