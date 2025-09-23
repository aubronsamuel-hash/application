# Guards - Quick Troubleshooting

## Error: Missing 'Ref: docs/roadmap/step-02.md' in PR or last commit

**Fix locally:**

```powershell
./tools/ci/ensure_roadmap_ref.ps1 -RepoSlug "<owner>/<repo>" -Branch "<your-branch>"
```

This will:
- create an empty commit with the roadmap reference if missing,
- push (SSH, fallback to HTTPS if needed),
- update the PR body with the same reference when possible.

Also ensure your PR uses the template and keeps the `Ref:` line.

## Quick local validation

```powershell
$ref = 'Ref: docs/roadmap/step-02.md'
if (-not (git log -1 --pretty=%B | Select-String -SimpleMatch $ref)) {
  git commit --allow-empty -m $ref
}

$env:GITHUB_EVENT_NAME = 'pull_request'
$env:PR_BODY = git log -1 --pretty=%B

pwsh -File tools/guards/roadmap_guard.ps1
```

## PowerShell ParserError: Unexpected token '{'

Cause: PowerShell can fail to parse format strings such as `"\"{0}\"" -f $value`.

Fix: avoid `-f` and use simple interpolation instead, for example:

```
throw "Missing roadmap reference in LAST COMMIT. Expected line: '$requiredRef'"
```
