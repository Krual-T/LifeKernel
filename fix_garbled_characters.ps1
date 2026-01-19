# Setup-UTF8PowerShellProfile.ps1
# Windows only. For Linux, use fix_garbled_characters.sh
$utf8Config = @'
# 设置控制台使用 UTF-8 编码（无 BOM）
chcp 65001 | Out-Null
[Console]::InputEncoding  = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
# 设置默认文件操作编码为 UTF-8（无 BOM）
$PSDefaultParameterValues['Out-File:Encoding']    = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
'@
# 创建目录（如果不存在）
$profileDir = Split-Path -Parent $PROFILE
if (-not (Test-Path $profileDir)) {
New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}
# 读取现有内容
$existing = if (Test-Path $PROFILE) { Get-Content $PROFILE -Raw } else { "" }
# 检查是否已配置（避免重复）
$hasConfig = $existing -match 'Console::OutputEncoding' -and
$existing -match '\$OutputEncoding' -and
$existing -match "PSDefaultParameterValues.*Out-File:Encoding"
if (-not $hasConfig) {
$newContent = if ($existing) { "$existing`r`n$utf8Config" } else { $utf8Config }
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)  # $false = 无 BOM
[System.IO.File]::WriteAllText($PROFILE, $newContent, $utf8NoBom)
Write-Host "✅ UTF-8 配置已写入 Profile！路径: $PROFILE" -ForegroundColor Green
} else {
Write-Host "ℹ️ UTF-8 已配置，跳过。" -ForegroundColor Cyan
}
# 立即生效
. $PROFILE
