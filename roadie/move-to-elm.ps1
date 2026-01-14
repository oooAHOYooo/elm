# PowerShell script to move Roadie into elm project
# Usage: .\move-to-elm.ps1 "C:\path\to\elm\project"

param(
    [Parameter(Mandatory=$true)]
    [string]$ElmPath
)

$RoadieDest = Join-Path $ElmPath "roadie"

# Check if elm directory exists
if (-not (Test-Path $ElmPath)) {
    Write-Host "Error: $ElmPath does not exist" -ForegroundColor Red
    exit 1
}

# Create roadie directory
Write-Host "Creating roadie folder in $ElmPath..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path $RoadieDest | Out-Null

# Copy all files except .git, node_modules, venv, etc.
Write-Host "Copying Roadie files..." -ForegroundColor Green
$exclude = @('.git', 'node_modules', 'venv', '__pycache__', '.next')
Get-ChildItem -Path . -Recurse | Where-Object {
    $item = $_
    $shouldExclude = $false
    foreach ($ex in $exclude) {
        if ($item.FullName -like "*\$ex\*" -or $item.Name -eq $ex) {
            $shouldExclude = $true
            break
        }
    }
    return -not $shouldExclude
} | Copy-Item -Destination {
    $_.FullName.Replace((Get-Location).Path, $RoadieDest)
} -Force

Write-Host "✅ Done! Roadie is now in $RoadieDest" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. cd $ElmPath"
Write-Host "2. Update netlify.toml base directory to 'roadie/frontend'"
Write-Host "3. Deploy to Netlify!"

