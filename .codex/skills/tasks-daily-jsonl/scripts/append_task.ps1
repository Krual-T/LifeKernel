param(
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$false)][string]$Id,
  [Parameter(Mandatory=$false)][string]$Details = $null,
  [Parameter(Mandatory=$false)][string]$Status = 'pending',
  [Parameter(Mandatory=$false)][string]$Priority = 'medium',
  [Parameter(Mandatory=$false)][string]$Module = 'work',
  [Parameter(Mandatory=$false)][string]$CreatedAt,
  [Parameter(Mandatory=$false)][string]$CompletedAt,
  [Parameter(Mandatory=$false)][string]$DueTime,
  [Parameter(Mandatory=$false)][string]$Source = 'conversation',
  [Parameter(Mandatory=$false)][string[]]$RelatedFiles = @()
)

$now = [DateTimeOffset]::Now
$created = if ($CreatedAt) { [DateTimeOffset]::Parse($CreatedAt) } else { $now }
$completed = if ($CompletedAt) { [DateTimeOffset]::Parse($CompletedAt) } else { $null }
$id = if ($Id) { $Id } else { $created.ToString('yyyy-MM-dd-HHmm') + '-task' }

$entry = [ordered]@{
  id = $id
  title = $Title
  details = $Details
  status = $Status
  priority = $Priority
  module = $Module
  created_at = $created.ToString('o')
  completed_at = if ($completed) { $completed.ToString('o') } else { $null }
  due_time = if ($DueTime) { [DateTimeOffset]::Parse($DueTime).ToString('o') } else { $null }
  source = $Source
  related_files = $RelatedFiles
}

$path = 'D:\Projects\LifeKernel\workspace\tasks\tasks.jsonl'
if (-not (Test-Path (Split-Path $path))) { New-Item -ItemType Directory -Path (Split-Path $path) -Force | Out-Null }
$line = ($entry | ConvertTo-Json -Compress) + "`n"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::AppendAllText($path, $line, $utf8NoBom)
