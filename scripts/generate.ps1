# 由 OpenAPI 规范重新生成 FastAPI 服务端代码（PowerShell 版）。
#
# 用法：
#   .\scripts\generate.ps1
#   .\scripts\generate.ps1 path\to\api.yaml
#
# 生成器 jar 默认放在 ~/.workbuddy/binaries/openapi-generator/，
# 也可用 $env:OPENAPI_GENERATOR_JAR 指向你自己的 jar。
$ErrorActionPreference = 'Stop'

$GeneratorVersion = '7.26.0'
$DefaultJar = Join-Path $env:USERPROFILE ".workbuddy/binaries/openapi-generator/openapi-generator-cli-$GeneratorVersion.jar"
$Jar = if ($env:OPENAPI_GENERATOR_JAR) { $env:OPENAPI_GENERATOR_JAR } else { $DefaultJar }
$Spec = if ($args.Count -gt 0) { $args[0] } else { 'api/openapi.yaml' }

Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path $Jar)) {
    Write-Host "==> 未找到 openapi-generator-cli，正在下载 $GeneratorVersion ..."
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Jar) | Out-Null
    $url = "https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/$GeneratorVersion/openapi-generator-cli-$GeneratorVersion.jar"
    Invoke-WebRequest -Uri $url -OutFile $Jar
}

Write-Host "==> 校验规范：$Spec"
& java "-Dfile.encoding=UTF-8" -jar $Jar validate -i $Spec
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host '==> 生成代码'
# -Dfile.encoding=UTF-8 是关键：Java 17 默认按系统编码（中文 Windows 为 GBK）读文件，
# 不加这个参数，规范里的中文描述会变成乱码写进生成代码。
& java "-Dfile.encoding=UTF-8" "-Dsun.stdout.encoding=UTF-8" "-Dsun.stderr.encoding=UTF-8" -jar $Jar generate `
    -g python-fastapi `
    -i $Spec `
    -o . `
    --additional-properties=packageName=openapi_server,projectName=k8s-deployment,hideGenerationTimestamp=true
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host '==> 完成。业务实现写在 src/openapi_server/impl/ 下，不会被生成器覆盖。'
Write-Host '==> 启动：$env:PYTHONPATH = "src"; uvicorn openapi_server.app:app'
