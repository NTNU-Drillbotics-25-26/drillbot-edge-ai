# Deploy drillbot to Raspberry Pi
# Usage: .\deploy.ps1 [-Restart]

param(
    [switch]$Restart
)

$PI_USER = "drillbotics"
# Static IP on rig Ethernet network
$PI_HOST = "10.10.10.20"
$PI_PATH = "~/drillbot"
$PI_TARGET = "${PI_USER}@${PI_HOST}:${PI_PATH}"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Deploying to $PI_TARGET..." -ForegroundColor Cyan

# Use scp to copy files (rsync not available on Windows by default)
$folders = @("app", "scripts", "docs")

foreach ($folder in $folders) {
    $source = Join-Path $ScriptDir $folder
    if (Test-Path $source) {
        Write-Host "Copying $folder..."
        scp -r $source "${PI_USER}@${PI_HOST}:${PI_PATH}/"
    }
}

Write-Host ""
Write-Host "Files synced." -ForegroundColor Green

if ($Restart) {
    Write-Host "Restarting drillbot service..." -ForegroundColor Yellow
    ssh "${PI_USER}@${PI_HOST}" "cd ${PI_PATH} && pkill -f 'uvicorn.*api:app' 2>/dev/null; nohup uvicorn app.api:app --host 0.0.0.0 --port 8000 > drillbot.log 2>&1 &"
    Write-Host "Service restarted." -ForegroundColor Green
}

Write-Host ""
Write-Host "Done! Test with:" -ForegroundColor Cyan
Write-Host "  Invoke-RestMethod http://${PI_HOST}:8000/health"
Write-Host ""
Write-Host "To pull the new model on the Pi:" -ForegroundColor Yellow
Write-Host "  ssh ${PI_USER}@${PI_HOST} 'ollama pull qwen2:0.5b'"
