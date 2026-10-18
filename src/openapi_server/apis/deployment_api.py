# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.deployment_api_base import BaseDeploymentApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from pydantic import Field, field_validator
from typing import Any, Optional
from typing_extensions import Annotated
from openapi_server.models.deployment import Deployment
from openapi_server.models.deployment_list import DeploymentList
from openapi_server.models.error import Error
from openapi_server.models.scale_request import ScaleRequest
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/namespaces/{namespace}/deployments",
    responses={
        200: {"model": DeploymentList, "description": "查询成功"},
        401: {"model": Error, "description": "未授权或凭证无效"},
        500: {"model": Error, "description": "服务端内部错误"},
    },
    tags=["deployment"],
    summary="列出命名空间下的 Deployment",
    response_model_by_alias=True,
)
async def list_namespaced_deployments(
    namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")] = Path(..., description="Kubernetes 命名空间", regex=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", min_length=1, max_length=63),
    label_selector: Annotated[Optional[str], Field(description="标签选择器，形如 app=nginx")] = Query(None, description="标签选择器，形如 app&#x3D;nginx", alias="labelSelector"),
    limit: Annotated[Optional[Annotated[int, Field(le=500, ge=1)]], Field(description="单次返回的最大条数")] = Query(50, description="单次返回的最大条数", alias="limit", ge=1, le=500),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> DeploymentList:
    if not BaseDeploymentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeploymentApi.subclasses[0]().list_namespaced_deployments(namespace, label_selector, limit)


@router.post(
    "/namespaces/{namespace}/deployments",
    responses={
        201: {"model": Deployment, "description": "创建成功"},
        400: {"model": Error, "description": "请求参数不合法"},
        401: {"model": Error, "description": "未授权或凭证无效"},
        409: {"model": Error, "description": "同名 Deployment 已存在"},
        500: {"model": Error, "description": "服务端内部错误"},
    },
    tags=["deployment"],
    summary="创建 Deployment",
    response_model_by_alias=True,
)
async def create_namespaced_deployment(
    namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")] = Path(..., description="Kubernetes 命名空间", regex=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", min_length=1, max_length=63),
    deployment: Deployment = Body(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Deployment:
    if not BaseDeploymentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeploymentApi.subclasses[0]().create_namespaced_deployment(namespace, deployment)


@router.get(
    "/namespaces/{namespace}/deployments/{name}",
    responses={
        200: {"model": Deployment, "description": "查询成功"},
        401: {"model": Error, "description": "未授权或凭证无效"},
        404: {"model": Error, "description": "Deployment 不存在"},
        500: {"model": Error, "description": "服务端内部错误"},
    },
    tags=["deployment"],
    summary="获取单个 Deployment",
    response_model_by_alias=True,
)
async def read_namespaced_deployment(
    namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")] = Path(..., description="Kubernetes 命名空间", regex=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", min_length=1, max_length=63),
    name: Annotated[str, Field(min_length=1, max_length=253, description="Deployment 名称")] = Path(..., description="Deployment 名称", regex=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", min_length=1, max_length=253),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Deployment:
    if not BaseDeploymentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeploymentApi.subclasses[0]().read_namespaced_deployment(namespace, name)


@router.delete(
    "/namespaces/{namespace}/deployments/{name}",
    responses={
        204: {"description": "删除成功"},
        401: {"model": Error, "description": "未授权或凭证无效"},
        404: {"model": Error, "description": "Deployment 不存在"},
        500: {"model": Error, "description": "服务端内部错误"},
    },
    tags=["deployment"],
    summary="删除 Deployment",
    response_model_by_alias=True,
)
async def delete_namespaced_deployment(
    namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")] = Path(..., description="Kubernetes 命名空间", regex=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", min_length=1, max_length=63),
    name: Annotated[str, Field(min_length=1, max_length=253, description="Deployment 名称")] = Path(..., description="Deployment 名称", regex=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", min_length=1, max_length=253),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    if not BaseDeploymentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeploymentApi.subclasses[0]().delete_namespaced_deployment(namespace, name)


@router.put(
    "/namespaces/{namespace}/deployments/{name}/scale",
    responses={
        200: {"model": Deployment, "description": "扩缩容成功"},
        400: {"model": Error, "description": "请求参数不合法"},
        401: {"model": Error, "description": "未授权或凭证无效"},
        404: {"model": Error, "description": "Deployment 不存在"},
        500: {"model": Error, "description": "服务端内部错误"},
    },
    tags=["deployment"],
    summary="调整 Deployment 副本数",
    response_model_by_alias=True,
)
async def scale_namespaced_deployment(
    namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")] = Path(..., description="Kubernetes 命名空间", regex=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", min_length=1, max_length=63),
    name: Annotated[str, Field(min_length=1, max_length=253, description="Deployment 名称")] = Path(..., description="Deployment 名称", regex=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", min_length=1, max_length=253),
    scale_request: ScaleRequest = Body(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Deployment:
    if not BaseDeploymentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeploymentApi.subclasses[0]().scale_namespaced_deployment(namespace, name, scale_request)
