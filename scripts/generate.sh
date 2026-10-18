#!/usr/bin/env bash
# 由 OpenAPI 规范重新生成 FastAPI 服务端代码。
#
# 用法（Git Bash）：
#   ./scripts/generate.sh                  # 使用默认规范 api/openapi.yaml
#   ./scripts/generate.sh path/to/api.yaml # 指定其它规范文件
#
# 生成器 jar 默认放在 ~/.workbuddy/binaries/openapi-generator/，
# 也可用 OPENAPI_GENERATOR_JAR 环境变量指向你自己的 jar。
set -euo pipefail

cd "$(dirname "$0")/.."

GENERATOR_VERSION="7.26.0"
DEFAULT_JAR="${USERPROFILE}/.workbuddy/binaries/openapi-generator/openapi-generator-cli-${GENERATOR_VERSION}.jar"
JAR="${OPENAPI_GENERATOR_JAR:-$DEFAULT_JAR}"
JAR_URL="https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/${GENERATOR_VERSION}/openapi-generator-cli-${GENERATOR_VERSION}.jar"
SPEC="${1:-api/openapi.yaml}"

if [ ! -f "$JAR" ]; then
    echo "==> 未找到 openapi-generator-cli，正在下载 ${GENERATOR_VERSION} ..."
    mkdir -p "$(dirname "$JAR")"
    curl -fsSL -o "$JAR" "$JAR_URL"
fi

echo "==> 校验规范：${SPEC}"
java -Dfile.encoding=UTF-8 -jar "$JAR" validate -i "$SPEC"

echo "==> 生成代码"
# -Dfile.encoding=UTF-8 是关键：Java 17 默认按系统编码（中文 Windows 为 GBK）读文件，
# 不加这个参数，规范里的中文描述会变成乱码写进生成代码。
java -Dfile.encoding=UTF-8 \
     -Dsun.stdout.encoding=UTF-8 \
     -Dsun.stderr.encoding=UTF-8 \
     -jar "$JAR" generate \
     -g python-fastapi \
     -i "$SPEC" \
     -o . \
     --additional-properties=packageName=openapi_server,projectName=k8s-deployment,hideGenerationTimestamp=true

echo "==> 完成。业务实现写在 src/openapi_server/impl/ 下，不会被生成器覆盖。"
echo "==> 启动：PYTHONPATH=src uvicorn openapi_server.app:app"
