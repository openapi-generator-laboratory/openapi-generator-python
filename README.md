# k8s-deployment

Kubernetes Deployment 管理 API，服务端代码由 **OpenAPI Generator 7.26.0（`python-fastapi`）** 从 `api/openapi.yaml` 生成。

> 规范先行：`api/openapi.yaml` 是唯一事实来源，接口代码由它生成，业务代码写在 `src/openapi_server/impl/`。
> 本 README 由人工维护，记录了模板本身不会告诉你的几个坑。

## 技术栈

| 项 | 值 |
| --- | --- |
| 生成器 | openapi-generator-cli 7.26.0，generator = `python-fastapi`（官方标注 beta） |
| 运行框架 | FastAPI 0.143.3 / Starlette 1.8.0 / Pydantic v2.14.1 |
| 服务容器 | Uvicorn 0.54.0 |
| 生成器前置 | Java 17（本机 17.0.12） |

## 目录结构

```
k8s-deployment/
├── api/openapi.yaml              # 【源头】接口定义，改接口先改这里
├── scripts/
│   ├── generate.sh               # 重新生成（Git Bash）
│   └── generate.ps1              # 重新生成（PowerShell）
├── src/openapi_server/
│   ├── main.py                   # 生成：FastAPI app 组装
│   ├── app.py                    # 手写：入口（补了统一错误响应）
│   ├── apis/*_api.py             # 生成：路由，含参数校验与响应模型
│   ├── apis/*_api_base.py        # 生成：业务基类（签名契约）
│   ├── models/*.py               # 生成：Pydantic v2 模型
│   ├── security_api.py           # 生成：鉴权依赖
│   └── impl/                     # 【手写】业务实现，生成器不会覆盖
│       ├── deployment_api_impl.py
│       └── health_api_impl.py
├── tests/                        # 生成：接口级测试
├── .openapi-generator-ignore     # 声明哪些文件不被生成器覆盖
├── requirements*.txt             # 手写：依赖（模板版已过时）
├── Dockerfile / docker-compose.yaml
└── .openapi-generator/           # 生成：产物清单，可提交
```

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows PowerShell 用 .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt    # 含运行依赖 + pytest/httpx/ruff

# 启动（PYTHONPATH 指向 src，因为模板采用 src 布局）
PYTHONPATH=src uvicorn openapi_server.app:app --reload
```

- Swagger UI：<http://localhost:8000/docs>
- 原始规范：<http://localhost:8000/openapi.json>

Docker：

```bash
docker compose up --build     # 监听 8080
```

## 接口清单

| 方法 | 路径 | operationId | 说明 |
| --- | --- | --- | --- |
| GET | `/namespaces/{namespace}/deployments` | listNamespacedDeployments | 列表，支持 `labelSelector`、`limit` |
| POST | `/namespaces/{namespace}/deployments` | createNamespacedDeployment | 创建 |
| GET | `/namespaces/{namespace}/deployments/{name}` | readNamespacedDeployment | 详情 |
| DELETE | `/namespaces/{namespace}/deployments/{name}` | deleteNamespacedDeployment | 删除 |
| PUT | `/namespaces/{namespace}/deployments/{name}/scale` | scaleNamespacedDeployment | 扩缩容 |
| GET | `/healthz` | getHealthz | 健康检查（免鉴权） |

除 `/healthz` 外，其余接口需要请求头 `Authorization: Bearer <token>`。

冒烟验证（已实测通过）：

```bash
curl -X POST http://localhost:8000/namespaces/default/deployments \
  -H "Authorization: Bearer test-token" -H "Content-Type: application/json" \
  -d '{"name":"nginx-web","labels":{"app":"nginx"},"spec":{"replicas":3,"image":"nginx:1.25-alpine"}}'

curl "http://localhost:8000/namespaces/default/deployments?labelSelector=app%3Dnginx" \
  -H "Authorization: Bearer test-token"
```

## 改接口的正确姿势

1. 修改 `api/openapi.yaml`（加路径、改字段、调校验规则）
2. 重新生成：
   ```bash
   ./scripts/generate.sh          # Git Bash
   .\scripts\generate.ps1         # PowerShell
   ```
3. 在 `src/openapi_server/impl/` 里补业务；若签名变了，Python 不会在运行时报错，请对着 `*_api_base.py` 的签名核一遍

`impl/` 下的文件不在模板产物清单里，**不会被覆盖**，可以放心写。

## 文件归属：哪些能改，哪些不能

| 文件 | 归属 | 改动方式 |
| --- | --- | --- |
| `src/openapi_server/apis/**`、`models/**`、`main.py`、`security_api.py` | 生成 | 不要手改，改 spec 后重新生成 |
| `src/openapi_server/impl/**`、`app.py` | 手写 | 随便改 |
| `requirements*.txt`、`Dockerfile`、`docker-compose.yaml`、`api/openapi.yaml` | 手写 | 已列入 `.openapi-generator-ignore`，不会被覆盖 |
| `tests/**`、`pyproject.toml`、`.flake8` | 生成 | 改动会被覆盖；`tests/test_deployment_api.py` 当前为修正版，重新生成后需按坑 7 再修一次 |
| `README.md` | 手写 | 已加入 ignore，不会被模板 README 覆盖 |

## 模板自带的坑（都已处理或规避）

1. **中文描述变乱码**：Java 17 默认按系统编码（中文 Windows 为 GBK）读取 spec，导致中文注释与描述写成乱码。生成脚本里已固定加 `-Dfile.encoding=UTF-8`。
2. **依赖清单过时**：模板输出的 `requirements.txt` 锁了 `uvicorn==0.13.4`、`click==7.1.2`、`graphene==2.1.8` 等 pydantic v1 时代的版本，在 Python 3.13 上装不上或冲突。已换成精简版并把该文件加入 ignore。
3. **错误响应与文档不一致**：模板对 `HTTPException` 返回 FastAPI 默认的 `{"detail": ...}`，而 openapi 里 404 声明的是 `Error` 模型。已在 `src/openapi_server/app.py` 注册统一 handler，现在返回 `{"code": 404000, "message": "..."}`。
4. **201/204 状态码不生效**：模板不给路由设置 `status_code`，创建/删除实际都返回 200。要让响应码与文档一致，需要自定义 mustache 模板或用 `responses` 之外的方式处理。
5. **`Path(regex=...)` 废弃告警**：模板仍生成 pydantic v1 的 `regex` 参数，FastAPI 会打印 `FastAPIDeprecationWarning`。功能不受影响，根治办法是自定义模板改成 `pattern`。
6. **servers.url 里的路径前缀不进路由**：spec 中 `servers.url = http://localhost:8080/api/v1`，但生成的路由是 `/healthz` 而非 `/api/v1/healthz`——模板不消费 server url 的 path 部分。前缀交给 Ingress/Nginx（K8s 场景推荐）；若必须让应用自带前缀，把 spec 里的 paths 直接写成 `/api/v1/...`。
7. **生成的测试文件直接跑会报错**：模板输出 `openapi_server.Deployment()` 这种写法，而 `openapi_server` 在测试模块里根本没定义，`pytest` 直接 NameError；且请求代码与断言全被注释，等于空测试。本项目的 `tests/test_deployment_api.py` 已改成可真实执行的用例（`PYTHONPATH=src pytest tests` 7 个用例全绿），重新生成后需要再修一次，或用自定义 `api_test.mustache` 根治。

## 常用命令

```bash
# 只校验规范（CI 里很有用）
java -Dfile.encoding=UTF-8 -jar "$OPENAPI_GENERATOR_JAR" validate -i api/openapi.yaml

# 查看 python 系列可用生成器
java -jar "$OPENAPI_GENERATOR_JAR" list | grep python

# 启动
PYTHONPATH=src uvicorn openapi_server.app:app --reload

# 测试
PYTHONPATH=src pytest tests
```

生成器 jar 默认放于 `~/.workbuddy/binaries/openapi-generator/openapi-generator-cli-7.26.0.jar`，
也可用环境变量 `OPENAPI_GENERATOR_JAR` 指定；脚本发现 jar 不存在时会自动从 Maven Central 下载。
