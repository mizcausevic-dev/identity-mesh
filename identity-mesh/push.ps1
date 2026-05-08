# identity-mesh push script
# Run from the EXTRACTED identity-mesh folder
$ErrorActionPreference = 'Stop'

$repo = 'identity-mesh'
$org  = 'mizcausevic-dev'

Write-Host "`n🔐 Pushing $org/$repo ..." -ForegroundColor Cyan

git init -b main | Out-Null
git add -A
git commit -m "feat: identity-mesh v0.1.0 - SPIFFE-style JWT-SVID broker for AI agents" | Out-Null

Write-Host "📦 Creating GitHub repo and pushing..." -ForegroundColor Yellow

gh repo create "$org/$repo" `
    --public `
    --source=. `
    --remote=origin `
    --push `
    --description "SPIFFE-style workload identity broker for AI agents. Short-lived JWT-SVIDs, audience binding, zero long-lived API keys. Zero-trust identity layer for agent fleets."

# Apply topics
gh repo edit "$org/$repo" --add-topic workload-identity,spiffe,zero-trust,jwt-svid,agent-security,ciso,ai-agents,oidc,credential-rotation,python

Write-Host "`n✅ identity-mesh LIVE." -ForegroundColor Green
Write-Host "🌐 https://github.com/$org/$repo" -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "https://github.com/$org/$repo"
Start-Process "https://github.com/$org/$repo/actions"
