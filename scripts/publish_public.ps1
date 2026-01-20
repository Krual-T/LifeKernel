param(
    [string]$PublicRemote = "public",
    [string]$PublicBranch = "public-main",
    [string]$SourceBranch = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Assert-Git {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "git not found in PATH."
    }
}

Assert-Git

try {
    git remote get-url $PublicRemote | Out-Null
} catch {
    throw "Remote '$PublicRemote' not found. Please add it first."
}

$tempRoot = Join-Path $env:TEMP ("lk_public_publish_" + [Guid]::NewGuid().ToString("N"))
git worktree add -f $tempRoot $SourceBranch | Out-Null

Push-Location $tempRoot
try {
    git checkout --orphan $PublicBranch | Out-Null
    try {
        git rm -r --cached . | Out-Null
    } catch {
        # Ignore if index is empty.
    }

    if (Test-Path "workspace/records") {
        Remove-Item -Recurse -Force "workspace/records"
    }

    git add -A
    git commit -m "Publish public template" | Out-Null
    git push $PublicRemote "$PublicBranch`:main" --force
} finally {
    Pop-Location
    git worktree remove $tempRoot --force | Out-Null
}
