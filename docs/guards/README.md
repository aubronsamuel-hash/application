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
