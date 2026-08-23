param(
  [Parameter(Mandatory = $true)]
  [string]$VaultRoot
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $repoRoot "snippets"
$obsidianRoot = Join-Path $VaultRoot ".obsidian"
$targetRoot = Join-Path $obsidianRoot "snippets"
$backupBase = Join-Path $obsidianRoot "snippets-migration-backup"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = Join-Path $backupBase $timestamp
$backupCreated = $false

$sharedFiles = @(
  "learning-lab.css",
  "video-note.css",
  "github-note.css"
)

function Ensure-BackupRoot {
  if (-not $script:backupCreated) {
    New-Item -ItemType Directory -Force -Path $script:backupRoot | Out-Null
    $script:backupCreated = $true
  }
}

function Copy-ToBackup {
  param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath
  )

  Ensure-BackupRoot
  $destination = Join-Path $script:backupRoot (Split-Path -Leaf $SourcePath)
  Copy-Item -LiteralPath $SourcePath -Destination $destination -Force

  if ((Get-FileHash -LiteralPath $SourcePath -Algorithm SHA256).Hash -ne
      (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash) {
    throw "Backup verification failed: $SourcePath"
  }
}

if (-not (Test-Path -LiteralPath $VaultRoot -PathType Container)) {
  throw "Vault root does not exist: $VaultRoot"
}

if (-not (Test-Path -LiteralPath $obsidianRoot -PathType Container)) {
  throw "The target does not look like an Obsidian Vault because .obsidian is missing: $VaultRoot"
}

foreach ($file in $sharedFiles) {
  $source = Join-Path $sourceRoot $file
  if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
    throw "Shared snippet is missing: $source"
  }
}

$targetItem = Get-Item -LiteralPath $targetRoot -Force -ErrorAction SilentlyContinue
if ($null -ne $targetItem) {
  if (-not $targetItem.PSIsContainer) {
    throw "The snippets target exists but is not a directory: $targetRoot"
  }

  $isReparsePoint = (($targetItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
  if ($isReparsePoint) {
    $linkType = if ($targetItem.LinkType) { $targetItem.LinkType } else { "ReparsePoint" }
    $linkTarget = if ($targetItem.Target) { ($targetItem.Target -join ", ") } else { "(target unavailable)" }
    Write-Host "Detected ${linkType}: $targetRoot"
    Write-Host "Target: $linkTarget"

    $activeFiles = @(Get-ChildItem -LiteralPath $targetRoot -Force -File)
    foreach ($item in $activeFiles) {
      Copy-ToBackup -SourcePath $item.FullName
    }

    [System.IO.Directory]::Delete($targetRoot, $false)
    if (Get-Item -LiteralPath $targetRoot -Force -ErrorAction SilentlyContinue) {
      throw "Failed to remove the snippets junction/symlink itself: $targetRoot"
    }

    New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
    Write-Host "Replaced the junction/symlink with a normal directory."

    if ($backupCreated) {
      $preservedCss = @(Get-ChildItem -LiteralPath $backupRoot -Filter "*.css" -File | Where-Object {
        $sharedFiles -notcontains $_.Name
      })
      foreach ($item in $preservedCss) {
        Copy-Item -LiteralPath $item.FullName -Destination (Join-Path $targetRoot $item.Name) -Force
        Write-Host "Preserved personal snippet: $($item.Name)"
      }
    }
  }
}
else {
  New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
  Write-Host "Created normal snippets directory: $targetRoot"
}

foreach ($file in $sharedFiles) {
  $source = Join-Path $sourceRoot $file
  $destination = Join-Path $targetRoot $file
  $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash

  if (Test-Path -LiteralPath $destination -PathType Leaf) {
    $destinationHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    if ($sourceHash -eq $destinationHash) {
      Write-Host "Already current: $file"
      continue
    }

    if (-not $backupCreated -or -not (Test-Path -LiteralPath (Join-Path $backupRoot $file))) {
      Copy-ToBackup -SourcePath $destination
    }
  }

  Copy-Item -LiteralPath $source -Destination $destination -Force
  $finalHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
  if ($sourceHash -ne $finalHash) {
    throw "Sync verification failed: $file"
  }
  Write-Host "Synced: $file"
}

$unknownCss = @(Get-ChildItem -LiteralPath $targetRoot -Filter "*.css" -File | Where-Object {
  $sharedFiles -notcontains $_.Name
} | Sort-Object Name)

Write-Host ""
Write-Host "Migration complete."
Write-Host "Runtime snippets: $targetRoot"
if ($backupCreated) {
  Write-Host "Backup: $backupRoot"
}
else {
  Write-Host "Backup: not needed"
}

if ($unknownCss.Count -gt 0) {
  Write-Host "Preserved non-shared CSS:"
  foreach ($item in $unknownCss) {
    Write-Host "  - $($item.Name)"
  }
}
else {
  Write-Host "Preserved non-shared CSS: none"
}

Write-Host "Shared CSS verified: learning-lab.css, video-note.css, github-note.css"
Write-Host "Enable the snippets you need in Obsidian: Settings -> Appearance -> CSS snippets."
