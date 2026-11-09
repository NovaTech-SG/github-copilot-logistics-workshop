param(
    [switch]$UseVSCodeConfig,
    [int]$Port = 8766
)
$ErrorActionPreference = 'Stop'
$dashboardPreviousToken = $env:DATABRICKS_TOKEN
$dashboardPrompted = $false
Push-Location $PSScriptRoot
try {
    uv sync --locked
    if ($LASTEXITCODE -ne 0) { throw '依赖同步失败。' }
    if ($UseVSCodeConfig) {
        uv run --locked python app.py --vscode-config --port $Port
    } else {
        if (-not $env:DATABRICKS_TOKEN) {
            $dashboardSecureToken = Read-Host '输入 Databricks Token（隐藏输入，仅本进程使用）' -AsSecureString
            $dashboardCredential = [System.Net.NetworkCredential]::new('', $dashboardSecureToken)
            $env:DATABRICKS_TOKEN = $dashboardCredential.Password
            $dashboardPrompted = $true
        }
        uv run --locked python app.py --port $Port
    }
    if ($LASTEXITCODE -ne 0) { throw '应用已退出，请检查上述错误。' }
} finally {
    if ($dashboardPrompted) {
        $env:DATABRICKS_TOKEN = $dashboardPreviousToken
        $dashboardCredential = $null
        if ($dashboardSecureToken) { $dashboardSecureToken.Dispose() }
    }
    Pop-Location
}
