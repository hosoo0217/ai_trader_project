param(
    [string]$Command = "python -m pytest -q"
)

$ErrorActionPreference = "Continue"

$OutputDir = ".\logs"
$OutputFile = "$OutputDir\last_output.txt"

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Write-Host ""
Write-Host "Running command:"
Write-Host $Command
Write-Host ""

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

"=== AI Trader Command Output ===" | Out-File $OutputFile -Encoding UTF8
"Time: $timestamp" | Out-File $OutputFile -Append -Encoding UTF8
"Command: $Command" | Out-File $OutputFile -Append -Encoding UTF8
"" | Out-File $OutputFile -Append -Encoding UTF8

Invoke-Expression $Command 2>&1 | Tee-Object -FilePath $OutputFile -Append

Get-Content $OutputFile | Set-Clipboard

Write-Host ""
Write-Host "Output saved to: $OutputFile"
Write-Host "Output copied to clipboard."
Write-Host "Now paste it into your AI Trader project chat."
