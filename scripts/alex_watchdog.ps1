# ALEX Watchdog — PowerShell Script
# Запускать: .\alex_watchdog.ps1
# Работает в фоне, пингует ws_server каждые 60 сек

$wsServer = "85.137.166.209"
$wsPort = 8446
$logFile = "C:\matryoshka\alex_watchdog.log"
$restartThreshold = 3
$fails = 0

function Write-Log {
    param($msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts $msg" | Tee-Object -FilePath $logFile -Append
}

Write-Log "=== ALEX WATCHDOG STARTED ==="
Write-Log "ws_server: $wsServer`:$wsPort"

while ($true) {
    try {
        # Проверка HTTP API
        $response = Invoke-WebRequest -Uri "http://$wsServer`:$wsPort/api/status" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        $json = $response.Content | ConvertFrom-Json
        
        if ($json.alex_connected -eq $true) {
            if ($fails -gt 0) {
                Write-Log "ALEX RECOVERED (was $fails fails)"
                $fails = 0
            }
        } else {
            Write-Log "ALEX DISCONNECTED"
            $fails++
        }
    }
    catch {
        Write-Log "WARN: No response from ws_server (attempt $($fails + 1))"
        $fails++
    }
    
    if ($fails -ge $restartThreshold) {
        Write-Log "FAIL COUNT = $restartThreshold — restarting ws_client"
        
        # Kill existing ws_client
        Get-Process | Where-Object { $_.Name -like "*python*" -and $_.CommandLine -like "*ws_client*" } | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        
        # Restart ws_client
        $wsClientPath = "C:\matryoshka\bots\alex\ws_client.py"
        if (Test-Path $wsClientPath) {
            Start-Process python -ArgumentList $wsClientPath -WindowStyle Hidden -PassThru
            Write-Log "ws_client.py RESTARTED"
        } else {
            Write-Log "ERROR: ws_client.py not found at $wsClientPath"
        }
        
        $fails = 0
    }
    
    Start-Sleep -Seconds 60
}