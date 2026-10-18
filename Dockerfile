FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 只带运行期需要的目录，src 下包含生成物与 impl/ 下的业务实现
COPY src ./src
COPY api ./api

EXPOSE 8080

# 入口用 app.py：它在生成器产出的 main.py 之上补充了统一错误响应
CMD ["uvicorn", "openapi_server.app:app", "--host", "0.0.0.0", "--port", "8080"]
