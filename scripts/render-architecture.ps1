param(
    [string]$InputFile = "docs/architecture.puml",
    [string]$OutputFile = "docs/architecture.svg"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Path $PSScriptRoot -Parent
$inputPath = Join-Path $projectRoot $InputFile
$outputPath = Join-Path $projectRoot $OutputFile

if (-not (Test-Path $inputPath)) {
    throw "Input PlantUML file not found: $inputPath"
}

$body = Get-Content $inputPath -Raw
Invoke-WebRequest -Uri "https://kroki.io/plantuml/svg" -Method Post -ContentType "text/plain" -Body $body -OutFile $outputPath

Write-Host "Rendered architecture diagram: $outputPath" -ForegroundColor Green
