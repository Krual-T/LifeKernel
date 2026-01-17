$root1 = 'D:\Projects\LifeKernel\workspace'
$root2 = 'D:\Projects\LifeKernel\.codex\skills'
$roots = @($root1, $root2)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)
$gbk = [System.Text.Encoding]::GetEncoding(936)
$files = foreach ($r in $roots) { Get-ChildItem -File -Recurse -Force -Path $r }
foreach ($f in $files) {
  $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
  if ($bytes.Length -eq 0) { $text = '' }
  else {
    if ($bytes -contains 0) { continue }
    $encoding = $null
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { $encoding = [System.Text.Encoding]::UTF8 }
    elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) { $encoding = [System.Text.Encoding]::Unicode }
    elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) { $encoding = [System.Text.Encoding]::BigEndianUnicode }
    elseif ($bytes.Length -ge 4 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE -and $bytes[2] -eq 0x00 -and $bytes[3] -eq 0x00) { $encoding = [System.Text.Encoding]::UTF32 }
    elseif ($bytes.Length -ge 4 -and $bytes[0] -eq 0x00 -and $bytes[1] -eq 0x00 -and $bytes[2] -eq 0xFE -and $bytes[3] -eq 0xFF) { $encoding = [System.Text.Encoding]::GetEncoding('utf-32BE') }
    if ($encoding -ne $null) {
      $text = $encoding.GetString($bytes)
    } else {
      try { $text = $utf8Strict.GetString($bytes) } catch { $text = $gbk.GetString($bytes) }
    }
  }
  if ($text.Length -gt 0 -and $text[0] -eq [char]0xFEFF) { $text = $text.Substring(1) }
  [System.IO.File]::WriteAllText($f.FullName, $text, $utf8NoBom)
}
