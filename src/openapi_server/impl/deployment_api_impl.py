# coding: utf-8
"""Deployment 接口的业务实现。

本文件由人工维护，openapi-generator **不会**生成或覆盖它：
模板只产出 `impl/__init__.py`，其余文件都是你自己的地盘。

工作机制：
    `apis/deployment_api.py` 在导入时会扫描 `impl` 包下所有模块，
    收集 `BaseDeploymentApi` 的子类，路由函数再调用 `subclasses[0]` 的方法。
    所以每个 Base 类在该包内只能有一个实现类，且状态要挂在类变量上
    （路由每次请求都会 `BaseDeploymentApi.subclasses[0]()` 新建一个实例）。

改造指引：把 `_store` 换成 kubernetes-client 的调用即可，方法签名保持不变。
"""

from datetime import datetime, timezone
from typing import ClassVar, Dict, Tuple

from fastapi import HTTPException

from openapi_server.apis.deployment_api_base import BaseDeploymentApi
from openapi_server.models.deployment import Deployment
from openapi_server.models.deployment_list import DeploymentList
from openapi_server.models.deployment_status import DeploymentStatus
from openapi_server.models.scale_request import ScaleRequest


class DeploymentApi(BaseDeploymentApi):
    """内存态示例实现（进程重启即丢失，仅用于联调与演示）。"""

    _store: ClassVar[Dict[Tuple[str, str], Deployment]] = {}

    async def list_namespaced_deployments(
        self,
        namespace: str,
        label_selector: str = None,
        limit: int = 50,
    ) -> DeploymentList:
        items = [item for (ns, _), item in self._store.items() if ns == namespace]

        if label_selector:
            key, _, value = label_selector.partition("=")
            key, value = key.strip(), value.strip()
            items = [d for d in items if (d.labels or {}).get(key) == value]

        items = items[: limit or 50]
        return DeploymentList(items=items, total=len(items))

    async def create_namespaced_deployment(self, namespace: str, deployment: Deployment) -> Deployment:
        key = (namespace, deployment.name)
        if key in self._store:
            raise HTTPException(
                status_code=409,
                detail=f"Deployment {namespace}/{deployment.name} 已存在",
            )

        replicas = deployment.spec.replicas or 0
        deployment.namespace = namespace
        deployment.created_at = datetime.now(timezone.utc)
        deployment.status = DeploymentStatus(
            available_replicas=0,
            ready_replicas=0,
            updated_replicas=replicas,
            phase="Pending",
        )
        self._store[key] = deployment
        return deployment

    async def read_namespaced_deployment(self, namespace: str, name: str) -> Deployment:
        deployment = self._store.get((namespace, name))
        if deployment is None:
            raise HTTPException(
                status_code=404,
                detail=f"Deployment {namespace}/{name} 不存在",
            )
        return deployment

    async def delete_namespaced_deployment(self, namespace: str, name: str) -> None:
        if self._store.pop((namespace, name), None) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Deployment {namespace}/{name} 不存在",
            )

    async def scale_namespaced_deployment(
        self,
        namespace: str,
        name: str,
        scale_request: ScaleRequest,
    ) -> Deployment:
        deployment = self._store.get((namespace, name))
        if deployment is None:
            raise HTTPException(
                status_code=404,
                detail=f"Deployment {namespace}/{name} 不存在",
            )

        deployment.spec.replicas = scale_request.replicas
        deployment.status.updated_replicas = scale_request.replicas
        return deployment
