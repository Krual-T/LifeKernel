param(
  [Parameter(Mandatory=$true)][string]$Description,
  [Parameter(Mandatory=$false)][string]$Timestamp,
  [Parameter(Mandatory=$false)][string]$Id,
  [Parameter(Mandatory=$false)][string]$Module = 'work',
  [Parameter(Mandatory=$false)][string]$SkillName = $null,
  [Parameter(Mandatory=$false)][string]$Source = 'conversation',
  [Parameter(Mandatory=$false)][string]$Status = 'completed',
  [Parameter(Mandatory=$false)][string[]]$RelatedFiles = @()
)

$now = if ($Timestamp) { [DateTimeOffset]::Parse($Timestamp) } else { [DateTimeOffset]::Now }
$id = if ($Id) { $Id } else { $now.ToString('yyyy-MM-dd-HHmm') + '-log' }

$entry = [ordered]@{
  id = $id
  timestamp = $now.ToString('o')
  module = $Module
  skill_name = $SkillName
  source = $Source
  description = $Description
  status = $Status
  related_files = $RelatedFiles
}

$path = Join-Path 'D:\Projects\LifeKernel\workspace\lifelog' ($now.ToString('yyyy\\MM\\dd') + '.jsonl')
$dir = Split-Path $path
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

$line = ($entry | ConvertTo-Json -Compress) + "`n"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::AppendAllText($path, $line, $utf8NoBom)
