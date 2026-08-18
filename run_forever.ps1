while ($true) {
    Write-Host "Starting AlgoSniper Bot..." -ForegroundColor Green
    .\venv\Scripts\python.exe bot.py
    $exitCode = $LASTEXITCODE
    
    Write-Host "Bot exited with code $exitCode. Restarting in 10 seconds..." -ForegroundColor Red
    Start-Sleep -Seconds 10
}
