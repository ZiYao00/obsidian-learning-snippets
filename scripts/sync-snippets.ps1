param(
  [Parameter(Mandatory = $true)]
  [string]$VaultRoot
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $repoRoot "snippets"
$targetRoot = Join-Path $VaultRoot ".obsidian\snippets"

if (-not (Test-Path -LiteralPath $VaultRoot -PathType Container)) {
  throw "Vault root does not exist: $VaultRoot"
}

$obsidianRoot = Join-Path $VaultRoot ".obsidian"
if (-not (Test-Path -LiteralPath $obsidianRoot -PathType Container)) {
  throw "The target does not look like an Obsidian Vault because .obsidian is missing: $VaultRoot"
}

$targetItem = Get-Item -LiteralPath $targetRoot -Force -ErrorAction SilentlyContinue
if ($null -ne $targetItem) {
  if (-not $targetItem.PSIsContainer) {
    throw "The snippets target exists but is not a directory: $targetRoot"
  }
  if (($targetItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw "The snippets target is a junction/symlink. Run scripts\migrate-vault-snippets.ps1 first: $targetRoot"
  }
}
else {
  New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
}

$files = @(
  "learning-lab.css",
  "video-note.css",
  "github-note.css"
)

foreach ($file in $files) {
  $source = Join-Path $sourceRoot $file
  if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
    throw "Shared snippet is missing: $source"
  }

  Copy-Item -LiteralPath $source -Destination (Join-Path $targetRoot $file) -Force
  Write-Host "Synced $file"
}

Write-Host "Done: $targetRoot"
Write-Host "Enable the required snippets in Obsidian: Settings -> Appearance -> CSS snippets."
