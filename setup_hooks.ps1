# Setup Git Hooks for Windows PowerShell
# Run this script to install pre-push testing hooks

Write-Host "🔧 Setting up Git hooks..." -ForegroundColor Cyan
Write-Host ""

# Get the repository root
$RepoRoot = git rev-parse --show-toplevel
$HooksDir = Join-Path $RepoRoot ".git\hooks"

# Create hooks directory if it doesn't exist
if (-not (Test-Path $HooksDir)) {
    New-Item -ItemType Directory -Path $HooksDir -Force | Out-Null
}

# Copy the PowerShell pre-push hook
$SourceHook = Join-Path $RepoRoot ".git\hooks\pre-push.ps1"
$TargetHook = Join-Path $HooksDir "pre-push"

if (Test-Path $SourceHook) {
    Copy-Item $SourceHook $TargetHook -Force
    Write-Host "✅ Installed pre-push hook (PowerShell)" -ForegroundColor Green
} else {
    Write-Host "❌ Source hook not found: $SourceHook" -ForegroundColor Red
    exit 1
}

# Create a wrapper script that calls the PowerShell hook
$WrapperContent = @"
#!/bin/sh
# Git hook wrapper for Windows - calls PowerShell script
powershell.exe -ExecutionPolicy Bypass -File ".git/hooks/pre-push.ps1"
"@

Set-Content -Path $TargetHook -Value $WrapperContent -NoNewline

Write-Host "✅ Pre-push hook configured successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "What happens now:" -ForegroundColor Yellow
Write-Host "  • Every time you run 'git push', tests will run automatically" -ForegroundColor White
Write-Host "  • If tests fail, the push will be blocked" -ForegroundColor White
Write-Host "  • If tests pass, the push proceeds to GitHub" -ForegroundColor White
Write-Host ""
Write-Host "To test it, try pushing to GitHub - tests will run first!" -ForegroundColor Cyan
Write-Host ""
Write-Host "To bypass the hook (emergency only):" -ForegroundColor Gray
Write-Host "  git push --no-verify" -ForegroundColor Gray
Write-Host ""
