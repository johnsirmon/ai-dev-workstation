# PR Checklist

Use this flow for every PR from checkout to merge.

## 1. Checkout and Sync

```powershell
git fetch --all --prune
git checkout -b review/<short-name> --track origin/<source-branch>
```

## 2. Review Scope

```powershell
git log --oneline --decorate --graph main..HEAD
git diff --stat main...HEAD
```

Review full file diffs for changed files:

```powershell
git diff main...HEAD -- <file1>
git diff main...HEAD -- <file2>
```

## 3. Approve PR

```powershell
gh auth status
gh pr review <PR_NUMBER> --approve --body "Reviewed locally: looks good and safe to merge."
```

## 4. Merge PR

If PR is draft:

```powershell
gh pr ready <PR_NUMBER>
```

Squash merge and delete remote branch:

```powershell
gh pr merge <PR_NUMBER> --squash --delete-branch
```

## 5. Post-Merge Cleanup

```powershell
git checkout main
git pull --ff-only
git branch -d review/<short-name>
```

## Optional: One-Command Helper

Use the helper script in this repo:

```powershell
# approve + ready + squash merge + optional branch delete
./scripts/review-pr.ps1 -PrNumber <PR_NUMBER> -Approve -Ready -Merge -MergeMethod squash -DeleteBranch
```

If you omit action switches, the script defaults to approve + ready + merge.
