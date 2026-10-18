param(
  [Parameter(Mandatory = $true)]
  [string]$VaultRoot,
  [switch]$Check,
  [switch]$Apply
)

$ErrorActionPreference = "Stop"
if ($Check -and $Apply) { throw "Use -Check OR -Apply, not both." }
# Keep the original direct invocation compatible; sync-obsidian.bat uses -Apply.
if (-not $Check -and -not $Apply) { $Apply = $true }

$repoRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $repoRoot "manifest.json"
$VaultRoot = [IO.Path]::GetFullPath($VaultRoot)
$obsidianRoot = Join-Path $VaultRoot ".obsidian"
$targetRoot = Join-Path $obsidianRoot "snippets"
$stateFile = Join-Path $obsidianRoot "snippets-sync-state.json"
$backupRoot = Join-Path $obsidianRoot "snippets-sync-backups"

if (-not (Test-Path -LiteralPath $VaultRoot -PathType Container)) {
  throw "Vault root does not exist: $VaultRoot"
}
if (-not (Test-Path -LiteralPath $obsidianRoot -PathType Container)) {
  throw "Not an Obsidian Vault (missing .obsidian): $VaultRoot"
}

$targetRootItem = Get-Item -LiteralPath $targetRoot -Force -ErrorAction SilentlyContinue
if ($null -ne $targetRootItem) {
  if (-not $targetRootItem.PSIsContainer) { throw "Snippet destination is not a directory: $targetRoot" }
  if (($targetRootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw "Snippet destination is a junction/symlink. Migrate the Vault snippets directory first."
  }
}
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw "Missing manifest.json" }
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ([int]$manifest.schema_version -ne 1) { throw "Unsupported style manifest schema" }
if ($null -eq $manifest.core -or $null -eq $manifest.extensions) { throw "Incomplete style manifest" }
if ([string]::IsNullOrWhiteSpace([string]$manifest.repository)) { throw "Missing style repository identity" }

$state = $null
if (Test-Path -LiteralPath $stateFile -PathType Leaf) {
  $state = Get-Content -LiteralPath $stateFile -Raw -Encoding UTF8 | ConvertFrom-Json
  if ([int]$state.schema_version -ne 1 -or $null -eq $state.installed) {
    throw "Unsupported or invalid sync state: $stateFile"
  }
}

# Resolve the complete set before any writes. Local/personal snippets never enter this list.
$entries = @($manifest.core) + @($manifest.extensions)
$seen = @{}
$plan = @()
foreach ($entry in $entries) {
  $relative = [string]$entry.path
  if ($relative -cnotmatch '^snippets/[a-zA-Z0-9-]+[.]css$') {
    throw "Unsafe or invalid manifest CSS path: $relative"
  }
  $name = [IO.Path]::GetFileName($relative)
  if ($seen.ContainsKey($name)) { throw "Duplicate CSS path: $name" }
  if ($name -eq "vault-local.css") { throw "Private Vault CSS cannot be managed by the shared repository" }
  $seen[$name] = $true
  $source = Join-Path $repoRoot ($relative.Replace("/", "\"))
  if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing shared CSS: $source" }
  $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
  $target = Join-Path $targetRoot $name
  $targetItem = Get-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
  $installedHash = $null
  if ($null -ne $targetItem) {
    if ($targetItem.PSIsContainer -or ($targetItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
      throw "CSS target is a directory or junction/symlink: $target"
    }
    $installedHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
  }
  $trackedHash = $null
  if ($null -ne $state -and $null -ne $state.installed) {
    $tracked = $state.installed.PSObject.Properties[$name]
    if ($null -ne $tracked) { $trackedHash = [string]$tracked.Value }
  }
  $status = "conflict"
  if ($null -eq $installedHash) {
    $status = "install"
  } elseif ($installedHash -eq $sourceHash) {
    $status = "unchanged"
  } elseif ($null -ne $trackedHash -and $trackedHash -eq $installedHash) {
    $status = "update"
  }
  $plan += [pscustomobject]@{
    name = $name
    status = $status
    source = $source
    target = $target
    source_hash = $sourceHash
    installed_hash = $installedHash
    tracked_hash = $trackedHash
  }
}
$conflicts = @($plan | Where-Object { $_.status -eq "conflict" })
if ($conflicts.Count -gt 0) {
  $names = ($conflicts | ForEach-Object { $_.name }) -join ", "
  $plan | Select-Object name,status,source_hash,installed_hash,tracked_hash | ConvertTo-Json -Depth 5 | Write-Output
  throw "Refusing to overwrite untracked or personally modified CSS: $names. Review differences; do not force-sync."
}

$summary = [pscustomobject]@{
  mode = $(if ($Check) { "check" } else { "apply" })
  repository = [string]$manifest.repository
  vault = $VaultRoot
  snippets = @($plan | Select-Object name,status)
}
if ($Check) {
  $summary | ConvertTo-Json -Depth 5 | Write-Output
  return
}

if (-not (Test-Path -LiteralPath $targetRoot -PathType Container)) {
  New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
}
# Pre-backup every tracked update BEFORE modifying any CSS.
$updates = @($plan | Where-Object { $_.status -eq "update" })
if ($updates.Count -gt 0) {
  if (-not (Test-Path -LiteralPath $backupRoot -PathType Container)) {
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
  }
  foreach ($entry in $updates) {
    $backup = Join-Path $backupRoot ($entry.name + "." + $entry.installed_hash + ".bak")
    if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) {
      Copy-Item -LiteralPath $entry.target -Destination $backup
    }
    $backupHash = (Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($backupHash -ne $entry.installed_hash) { throw "Backup integrity failed: $backup" }
  }
}

foreach ($entry in $plan) {
  if ($entry.status -eq "unchanged") { continue }
  $temporary = Join-Path $targetRoot ($entry.name + ".sync-tmp")
  if (Test-Path -LiteralPath $temporary) { throw "Sync temp file already exists: $temporary" }
  try {
    Copy-Item -LiteralPath $entry.source -Destination $temporary
    $tmpHash = (Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($tmpHash -ne $entry.source_hash) { throw "Staged CSS hash mismatch: $temporary" }
    Move-Item -LiteralPath $temporary -Destination $entry.target -Force
  } finally {
    if (Test-Path -LiteralPath $temporary -PathType Leaf) { Remove-Item -LiteralPath $temporary -Force }
  }
}
foreach ($entry in $plan) {
  $actual = (Get-FileHash -LiteralPath $entry.target -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -ne $entry.source_hash) { throw "Installed CSS hash mismatch after sync: $($entry.name)" }
}

$hashes = [ordered]@{}
foreach ($entry in $plan) { $hashes[$entry.name] = $entry.source_hash }
$newState = [ordered]@{
  schema_version = 1
  repository = [string]$manifest.repository
  installed = $hashes
  updated_utc = (Get-Date).ToUniversalTime().ToString("o")
}
$tmpState = $stateFile + ".sync-tmp"
if (Test-Path -LiteralPath $tmpState) { throw "Sync state temporary file already exists" }
try {
  $newState | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $tmpState -Encoding UTF8
  Move-Item -LiteralPath $tmpState -Destination $stateFile -Force
} finally {
  if (Test-Path -LiteralPath $tmpState -PathType Leaf) { Remove-Item -LiteralPath $tmpState -Force }
}
$summary | ConvertTo-Json -Depth 5 | Write-Output
Write-Host "Shared snippets verified. Private Vault CSS and unknown snippets were not touched."
