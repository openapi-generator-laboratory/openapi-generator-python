# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, field_validator
from typing import Any, Optional
from typing_extensions import Annotated
from openapi_server.models.deployment import Deployment
from openapi_server.models.deployment_list import DeploymentList
from openapi_server.models.error import Error
from openapi_server.models.scale_request import ScaleRequest
from openapi_server.security_api import get_token_bearerAuth

class BaseDeploymentApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDeploymentApi.subclasses = BaseDeploymentApi.subclasses + (cls,)
    async def list_namespaced_deployments(
        self,
        namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")],
        label_selector: Annotated[Optional[str], Field(description="标签选择器，形如 app=nginx")],
        limit: Annotated[Optional[Annotated[int, Field(le=500, ge=1)]], Field(description="单次返回的最大条数")],
    ) -> DeploymentList:
        ...


    async def create_namespaced_deployment(
        self,
        namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")],
        deployment: Deployment,
    ) -> Deployment:
        ...


    async def read_namespaced_deployment(
        self,
        namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")],
        name: Annotated[str, Field(min_length=1, max_length=253, description="Deployment 名称")],
    ) -> Deployment:
        ...


    async def delete_namespaced_deployment(
        self,
        namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")],
        name: Annotated[str, Field(min_length=1, max_length=253, description="Deployment 名称")],
    ) -> None:
        ...


    async def scale_namespaced_deployment(
        self,
        namespace: Annotated[str, Field(min_length=1, max_length=63, description="Kubernetes 命名空间")],
        name: Annotated[str, Field(min_length=1, max_length=253, description="Deployment 名称")],
        scale_request: ScaleRequest,
    ) -> Deployment:
        ...
