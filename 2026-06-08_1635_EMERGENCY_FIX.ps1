# EMERGENCY POWERSHELL FIX — Alex's PC (08.06.2026 16:35)
# Purpose: Stop окна ws_client + opencode от размножения. ONE instance каждого.

# ШАГ 1: ПОСМОТРЕТЬ что есть
Write-Host "=== ДО ОЧИСТКИ ===" -ForegroundColor Cyan
Write-Host "ws_client protsessy:"
Get-Process | Where-Object { $_.MainWindowTitle -like "*ws_client*" -or $_.ProcessName -eq "python" -and $_.CommandLine -like "*ws_client*" } | Select-Object Id, ProcessName, MainWindowTitle, StartTime | Format-Table
Write-Host "opencode protsessy:"
Get-Process opencode -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime | Format-Table

# ШАГ 2: УБИТЬ ВСЕ ws_client
Write-Host "=== UBIVAYU VSE ws_client (krome poslednego) ===" -ForegroundColor Yellow
$wsProcs = Get-CimInstance Win32_Process -Filter "Name = 'python.exe' AND CommandLine LIKE '%ws_client.py%'"
$keepOne = $wsProcs | Select-Object -Last 1
foreach ($p in $wsProcs) {
  if ($p.ProcessId -ne $keepOne.ProcessId) {
    Write-Host "  Kill PID $($p.ProcessId)"
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  } else {
    Write-Host "  OSTAVLYAYU PID $($p.ProcessId)"
  }
}

# ШАГ 3: УБИТЬ ВСЕ opencode (krome poslednego)
Write-Host "=== UBIVAYU VSE opencode (krome poslednego) ===" -ForegroundColor Yellow
$ocProcs = Get-Process opencode -ErrorAction SilentlyContinue | Sort-Object StartTime
$keepOc = $ocProcs | Select-Object -Last 1
foreach ($p in $ocProcs) {
  if ($p.Id -ne $keepOc.Id) {
    Write-Host "  Kill opencode PID $($p.Id)"
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
  } else {
    Write-Host "  OSTAVLYAYU opencode PID $($p.Id)"
  }
}

# ШАГ 4: ПЕРЕЗАПУСТИТЬ watchdog (esli on tozhe plodit processy)
Write-Host "=== PROVERKA WATCHDOG ===" -ForegroundColor Cyan
$wdProcs = Get-CimInstance Win32_Process -Filter "Name = 'python.exe' AND CommandLine LIKE '%watchdog%'"
if ($wdProcs) {
  Write-Host "  Watchdog naiden: $($wdProcs.Count) processov"
  # NE UBIVAT watchdog! On mozhet byt nuzhen. Tolko proverit logi.
  $wdLog = Get-Content "C:\matryoshka\logs\watchdog.log" -Tail 20 -ErrorAction SilentlyContinue
  if ($wdLog) {
    Write-Host "  Watchdog log (poslednie 20 strok):"
    $wdLog | ForEach-Object { Write-Host "    $_" }
  }
}

# ШАГ 5: ЖДUT 3 SEK
Write-Host "=== ZHDU 3 S ===" -ForegroundColor Cyan
Start-Sleep -Seconds 3

# ШАГ 6: PROVERKA
Write-Host "=== POSLE OCHISTKI ===" -ForegroundColor Green
$wsLeft = Get-CimInstance Win32_Process -Filter "Name = 'python.exe' AND CommandLine LIKE '%ws_client.py%'"
$ocLeft = Get-Process opencode -ErrorAction SilentlyContinue
Write-Host "ws_client OSTALOS: $($wsLeft.Count) (dolzhen byt 1)"
Write-Host "opencode OSTALOS: $($ocLeft.Count) (dolzhen byt 1)"

# ШАГ 7: ESLI nichego ne ostalos — zapustit zanovo
if ($wsLeft.Count -eq 0) {
  Write-Host "=== ZAPUSKAYU 1 ws_client ===" -ForegroundColor Yellow
  Start-Process -FilePath "C:\matryoshka\ws_client.bat" -WindowStyle Minimized
}
if ($ocLeft.Count -eq 0) {
  Write-Host "=== ZAPUSKAYU 1 opencode ===" -ForegroundColor Yellow
  Start-Process -FilePath "C:\Users\User\AppData\Roaming\npm\node_modules\opencode-ai\bin\opencode.exe" -ArgumentList "serve","--port","5001" -WindowStyle Minimized
}

# ШАГ 8: ISPravit ws_client.py — dobavit CREATE_NO_WINDOW i CLEANUP_ENABLED=True
Write-Host "=== PREDLOZHENIE ISPRAVLENIY ===" -ForegroundColor Cyan
Write-Host "1. V ws_client.py: subprocess.Popen(['python','ws_client.py'], creationflags=0x08000000)"
Write-Host "2. V ws_client.py: CLEANUP_ENABLED=True v konfig + finally: cleanup"
Write-Host "3. Watchdog: proverit chto on NE plodit processy (esli plodit — ubrat watchdog)"
Write-Host "4. Dobavit v C:\matryoshka\start_all.bat:"
Write-Host "   taskkill /F /IM python.exe /FI `"WINDOWTITLE eq ws_client*`""
Write-Host "   start /min ... opencode serve"
Write-Host "   start /min ... ws_client"

# DONE
Write-Host "=== GOTOVO. Sdelay screenshot, otprav HERMES v Telegram ===" -ForegroundColor Green
