param([switch]$UseVSCodeConfig, [int]$Port = 8769)
$ErrorActionPreference = 'Stop'
$trackerPreviousToken = $env:DATABRICKS_TOKEN
$trackerPrompted = $false
Push-Location $PSScriptRoot
try {
    uv sync --locked
    if ($LASTEXITCODE -ne 0) { throw '依赖同步失败。' }
    if ($UseVSCodeConfig) {
        uv run --locked python app.py --vscode-config --port $Port
    } else {
        if (-not $env:DATABRICKS_TOKEN) {
            $trackerSecureToken = Read-Host '输入 Databricks Token（隐藏输入，仅本进程使用）' -AsSecureString
            $trackerCredential = [System.Net.NetworkCredential]::new('', $trackerSecureToken)
            $env:DATABRICKS_TOKEN = $trackerCredential.Password
            $trackerPrompted = $true
        }
        uv run --locked python app.py --port $Port
    }
    if ($LASTEXITCODE -ne 0) { throw '应用已退出，请查看上述错误。' }
} finally {
    if ($trackerPrompted) {
        $env:DATABRICKS_TOKEN = $trackerPreviousToken
        $trackerCredential = $null
        if ($trackerSecureToken) { $trackerSecureToken.Dispose() }
    }
    Pop-Location
}
