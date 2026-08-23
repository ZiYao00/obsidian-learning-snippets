param(
    [Parameter(Mandatory = $true)]
    [string]$VaultRoot
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $repoRoot "snippets"
$target = Join-Path $VaultRoot ".obsidian\snippets"

if (-not (Test-Path $source -PathType Container)) {
    throw "Snippet source directory not found: $source"
}

if (-not (Test-Path (Join-Path $VaultRoot ".obsidian") -PathType Container)) {
    throw "The supplied VaultRoot does not contain .obsidian: $VaultRoot"
}

if (-not (Test-Path $target -PathType Container)) {
    New-Item -ItemType Directory -Path $target | Out-Null
}

$files = @(
    "learning-lab.css",
    "video-note.css",
    "github-note.css"
)

foreach ($file in $files) {
    Copy-Item -LiteralPath (Join-Path $source $file) -Destination (Join-Path $target $file) -Force
    Write-Host "Synced $file"
}

Write-Host "Done. Enable the required snippets in Obsidian Settings -> Appearance -> CSS snippets."
