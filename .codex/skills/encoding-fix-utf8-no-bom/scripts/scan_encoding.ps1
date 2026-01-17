$root1 = 'D:\Projects\LifeKernel\workspace'
$root2 = 'D:\Projects\LifeKernel\.codex\skills'
$roots = @($root1, $root2)
$files = foreach ($r in $roots) { Get-ChildItem -File -Recurse -Force -Path $r }
$utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)
$results = @()
foreach ($f in $files) {
  $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
  if ($bytes.Length -eq 0) {
    $results += [pscustomobject]@{Path=$f.FullName; Type='empty'; Bom=''; InvalidUtf8=$false; HasReplacement=$false; HasNull=$false}
    continue
  }
  $hasNull = $bytes -contains 0
  $bom = ''
  if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { $bom = 'UTF8-BOM' }
  elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) { $bom = 'UTF16-LE' }
  elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) { $bom = 'UTF16-BE' }
  elseif ($bytes.Length -ge 4 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE -and $bytes[2] -eq 0x00 -and $bytes[3] -eq 0x00) { $bom = 'UTF32-LE' }
  elseif ($bytes.Length -ge 4 -and $bytes[0] -eq 0x00 -and $bytes[1] -eq 0x00 -and $bytes[2] -eq 0xFE -and $bytes[3] -eq 0xFF) { $bom = 'UTF32-BE' }

  $invalid = $false
  $hasReplacement = $false
  try {
    $text = $utf8Strict.GetString($bytes)
    if ($text -match "\uFFFD") { $hasReplacement = $true }
  } catch {
    $invalid = $true
  }

  $results += [pscustomobject]@{Path=$f.FullName; Type='file'; Bom=$bom; InvalidUtf8=$invalid; HasReplacement=$hasReplacement; HasNull=$hasNull}
}
$results | Sort-Object Path | Format-Table -AutoSize
