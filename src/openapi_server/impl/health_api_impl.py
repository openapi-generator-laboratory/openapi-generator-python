# coding: utf-8
"""健康检查接口的业务实现（人工维护）。"""

from openapi_server.apis.health_api_base import BaseHealthApi
from openapi_server.models.health_status import HealthStatus


class HealthApi(BaseHealthApi):
    async def get_healthz(self) -> HealthStatus:
        # TODO: 这里按需加上对 k8s apiserver / 数据库等下游依赖的探活
        return HealthStatus(status="up", version="1.0.0")
