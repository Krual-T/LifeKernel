param(
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$true)][string]$Body
)

try {
  if (-not (Get-Module -ListAvailable -Name BurntToast)) {
    if (-not (Get-PackageProvider -ListAvailable -Name NuGet)) {
      Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Scope CurrentUser | Out-Null
    }
    Install-Module -Name BurntToast -Scope CurrentUser -Force -AllowClobber | Out-Null
  }
  Import-Module BurntToast -ErrorAction Stop
  New-BurntToastNotification -Text $Title, $Body | Out-Null
} catch {
  # Fallback: try msg in interactive session
  try { msg * "$Title`n$Body" | Out-Null } catch {}
}

