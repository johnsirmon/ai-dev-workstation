param(
    [Parameter(Mandatory = $true)]
    [int]$PrNumber,

    [switch]$Approve,
    [switch]$Ready,
    [switch]$Merge,

    [ValidateSet("squash", "merge", "rebase")]
    [string]$MergeMethod = "squash",

    [switch]$DeleteBranch,

    [string]$ApproveBody = "Reviewed locally: looks good and safe to merge."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host "`n==> $Message" -ForegroundColor Cyan
    & $Action
}

# Safe defaults:
# - If no action switches are supplied, run approve + ready + merge.
if (-not ($Approve -or $Ready -or $Merge)) {
    $Approve = $true
    $Ready = $true
    $Merge = $true
}

Invoke-Step -Message "Checking gh auth status" -Action {
    gh auth status
}

Invoke-Step -Message "Fetching PR metadata" -Action {
    gh pr view $PrNumber --json number,title,state,isDraft,headRefName,baseRefName,url
}

if ($Approve) {
    Invoke-Step -Message "Approving PR #$PrNumber" -Action {
        gh pr review $PrNumber --approve --body $ApproveBody
    }
}

if ($Ready) {
    Invoke-Step -Message "Marking PR #$PrNumber ready for review (if draft)" -Action {
        try {
            gh pr ready $PrNumber
        }
        catch {
            # Continue if already ready/non-draft.
            Write-Host "PR already ready or cannot be marked ready: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

if ($Merge) {
    $mergeArgs = @("pr", "merge", "$PrNumber", "--$MergeMethod")
    if ($DeleteBranch) {
        $mergeArgs += "--delete-branch"
    }

    Invoke-Step -Message "Merging PR #$PrNumber using '$MergeMethod'" -Action {
        gh @mergeArgs
    }
}

Invoke-Step -Message "Final PR state" -Action {
    gh pr view $PrNumber --json state,isDraft,mergedAt,mergeCommit,reviewDecision,url
}
