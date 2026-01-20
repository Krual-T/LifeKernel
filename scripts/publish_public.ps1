param(
    [string]$PublicPath = $(Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) "LifeKernel-Public"),
    [string]$SourceRemote = "origin",
    [string]$PublicRemote = "public",
    [string]$Branch = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Assert-Git {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "git not found in PATH."
    }
}

function Assert-FilterRepo {
    if (-not (Get-Command "git-filter-repo" -ErrorAction SilentlyContinue)) {
        throw "git-filter-repo not found in PATH. Install it first (e.g., 'uv add git-filter-repo')."
    }
}

Assert-Git
Assert-FilterRepo

if (-not (Test-Path $PublicPath)) {
    throw "Public repo not found at: $PublicPath"
}

Push-Location $PublicPath
try {
    git remote get-url $SourceRemote | Out-Null
    git remote get-url $PublicRemote | Out-Null

    git fetch $SourceRemote | Out-Null
    git checkout $Branch | Out-Null
    git pull $SourceRemote $Branch | Out-Null

    git filter-repo --path workspace/records --invert-paths --force
    git push $PublicRemote $Branch --force
} finally {
    Pop-Location
}
