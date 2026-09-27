[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$docker = Get-Command docker -ErrorAction SilentlyContinue
if ($null -eq $docker) {
    Write-Host "Docker CLI was not found on PATH." -ForegroundColor Red
    Write-Host "Install or repair Docker Desktop, then open a new PowerShell window."
    exit 1
}

try {
    $dockerVersion = & docker --version
    if ($LASTEXITCODE -ne 0) {
        throw "docker --version failed."
    }
    Write-Host "Docker CLI: $dockerVersion" -ForegroundColor Green

    $composeVersion = & docker compose version
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose v2 is unavailable. Update Docker Desktop."
    }
    Write-Host "Docker Compose: $composeVersion" -ForegroundColor Green

    $serverVersion = & docker info --format "{{.ServerVersion}}" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Engine is not reachable. Start Docker Desktop and wait for it to finish starting."
    }
    Write-Host "Docker Engine: $serverVersion" -ForegroundColor Green
}
catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

$wsl = Get-Command wsl -ErrorAction SilentlyContinue
if ($null -eq $wsl) {
    Write-Host "WSL command was not found. Docker may still work with another supported backend." -ForegroundColor Yellow
    exit 0
}

$wslVersion = & wsl --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "WSL version details:" -ForegroundColor Cyan
    $wslVersion | ForEach-Object { Write-Host "  $_" }
}
else {
    Write-Host "WSL version details were unavailable. Run 'wsl --update', then check Docker Desktop's WSL integration." -ForegroundColor Yellow
}

$distributions = & wsl --list --verbose 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "WSL distributions:" -ForegroundColor Cyan
    $distributions | ForEach-Object { Write-Host "  $_" }
}

Write-Host "Docker Desktop, Docker Compose, and the Docker Engine are available." -ForegroundColor Green