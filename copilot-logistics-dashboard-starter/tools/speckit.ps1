param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$SpecifyArgs
)
$ErrorActionPreference = 'Stop'
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'Install uv before running Spec Kit.' }
if (-not $SpecifyArgs -or $SpecifyArgs.Count -eq 0) { $SpecifyArgs = @('version') }
$projectRoot = Split-Path -Parent $PSScriptRoot
$exitCode = 1
Push-Location -LiteralPath $projectRoot
try {
    & uv tool run --from 'specify-cli==1.3.2' specify @SpecifyArgs
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $exitCode
