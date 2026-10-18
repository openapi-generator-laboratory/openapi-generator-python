# coding: utf-8
"""服务入口：在生成器产出的 app 之上补充统一错误响应。

为什么单独再包一层：
- `main.py` 由 openapi-generator 生成，手改会在下次生成时丢失；
- 本文件不在模板产物清单里，重新生成不会动它，中间件/CORS/异常处理都写在这里。

启动：
    PYTHONPATH=src uvicorn openapi_server.app:app
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from openapi_server.main import app as generated_app
from openapi_server.models.error import Error

app = generated_app


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """把 FastAPI 默认的 {"detail": ...} 统一成 openapi.yaml 声明的 Error 结构。

    不这样做的话，文档上写的是 404 -> Error，实际返回却是 {"detail": "..."}，
    Swagger UI 与真实响应会对不上。
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=Error(code=exc.status_code * 1000, message=str(exc.detail)).to_dict(),
    )
