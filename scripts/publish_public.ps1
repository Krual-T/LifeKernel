param(
    [string]$PublicRemote = "public",
    [string]$SourceRemote = "origin",
    [string]$SourceBranch = "main",
    [string]$PublicBranch = "main"
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

try {
    $sourceUrl = (git remote get-url $SourceRemote).Trim()
} catch {
    throw "Remote '$SourceRemote' not found. Please add it first."
}

try {
    $publicUrl = (git remote get-url $PublicRemote).Trim()
} catch {
    throw "Remote '$PublicRemote' not found. Please add it first."
}

$tempRoot = Join-Path $env:TEMP ("lk_public_publish_" + [Guid]::NewGuid().ToString("N"))
git clone --no-hardlinks $sourceUrl $tempRoot | Out-Null

Push-Location $tempRoot
try {
    git checkout $SourceBranch | Out-Null
    git filter-repo --path workspace/records --invert-paths --force

    git remote add $PublicRemote $publicUrl | Out-Null
    git push $PublicRemote "$SourceBranch`:$PublicBranch" --force
} finally {
    Pop-Location
    Remove-Item -Recurse -Force $tempRoot
}
