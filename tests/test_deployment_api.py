# coding: utf-8
"""deployment 接口端到端测试。

注意：模板生成的版本有两个问题，本文件已修正——
1. 构造请求体时写的是 `openapi_server.Deployment()`，但 `openapi_server` 这个名字
   在测试模块里并不存在，直接跑会 NameError；
2. 所有请求与断言都被注释掉了，等于空测试。

代价：重新生成会覆盖回模板版本，届时要么再改一次，要么用自定义
`api_test.mustache` 模板根治（见 README「模板自带的坑」）。
"""

from uuid import uuid4

from fastapi.testclient import TestClient

NAMESPACE = "default"
BASE = f"/namespaces/{NAMESPACE}/deployments"
HEADERS = {"Authorization": "Bearer special-key"}


def _unique_name(prefix: str = "nginx") -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def _create(client: TestClient, name: str, replicas: int = 3) -> None:
    response = client.request(
        "POST",
        BASE,
        headers=HEADERS,
        json={
            "name": name,
            "labels": {"app": "nginx"},
            "spec": {"replicas": replicas, "image": "nginx:1.25-alpine"},
        },
    )
    assert response.status_code == 200, response.text


def test_create_namespaced_deployment(client: TestClient):
    name = _unique_name()
    response = client.request(
        "POST",
        BASE,
        headers=HEADERS,
        json={
            "name": name,
            "labels": {"app": "nginx", "tier": "frontend"},
            "spec": {"replicas": 3, "image": "nginx:1.25-alpine"},
        },
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["name"] == name
    assert body["namespace"] == NAMESPACE
    assert body["spec"]["replicas"] == 3
    assert body["spec"]["port"] == 80  # spec 里声明的默认值
    assert body["status"]["phase"] == "Pending"
    assert "createdAt" in body


def test_read_namespaced_deployment(client: TestClient):
    name = _unique_name()
    _create(client, name)

    response = client.request("GET", f"{BASE}/{name}", headers=HEADERS)
    assert response.status_code == 200, response.text
    assert response.json()["name"] == name


def test_read_namespaced_deployment_not_found(client: TestClient):
    response = client.request("GET", f"{BASE}/definitely-not-exist", headers=HEADERS)
    assert response.status_code == 404


def test_list_namespaced_deployments(client: TestClient):
    name = _unique_name()
    _create(client, name)

    response = client.request("GET", BASE, headers=HEADERS, params=[("limit", 50)])
    assert response.status_code == 200, response.text
    body = response.json()
    assert "items" in body
    assert any(item["name"] == name for item in body["items"])

    filtered = client.request(
        "GET",
        BASE,
        headers=HEADERS,
        params=[("labelSelector", "app=nginx"), ("limit", 10)],
    )
    assert filtered.status_code == 200, filtered.text
    assert all(item["labels"]["app"] == "nginx" for item in filtered.json()["items"])


def test_delete_namespaced_deployment(client: TestClient):
    name = _unique_name()
    _create(client, name)

    response = client.request("DELETE", f"{BASE}/{name}", headers=HEADERS)
    assert response.status_code == 200, response.text

    # 再删一次应报 404，确认资源真的被移除
    again = client.request("DELETE", f"{BASE}/{name}", headers=HEADERS)
    assert again.status_code == 404


def test_scale_namespaced_deployment(client: TestClient):
    name = _unique_name()
    _create(client, name, replicas=2)

    response = client.request(
        "PUT",
        f"{BASE}/{name}/scale",
        headers=HEADERS,
        json={"replicas": 5},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["spec"]["replicas"] == 5
    assert body["status"]["updatedReplicas"] == 5
