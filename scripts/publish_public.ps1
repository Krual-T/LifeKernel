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
    $hasUv = Get-Command "uv" -ErrorAction SilentlyContinue
    $hasFilterRepo = Get-Command "git-filter-repo" -ErrorAction SilentlyContinue
    if (-not $hasUv -and -not $hasFilterRepo) {
        throw "Neither 'uv' nor 'git-filter-repo' found. Install with 'uv add git-filter-repo'."
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

    if (Get-Command "uv" -ErrorAction SilentlyContinue) {
        uv run git-filter-repo --path workspace/records --invert-paths --force
    } else {
        git filter-repo --path workspace/records --invert-paths --force
    }
    git push $PublicRemote $Branch --force
} finally {
    Pop-Location
}
