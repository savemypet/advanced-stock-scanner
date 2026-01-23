# Test All Platforms - Stock Scanner
Write-Host "=== Testing Stock Scanner on All Platforms ===" -ForegroundColor Cyan
Write-Host ""

# 1. Test Backend
Write-Host "1. Testing Backend (Port 5000)..." -ForegroundColor Yellow
try {
    $backendTest = Invoke-WebRequest -Uri "http://localhost:5000/api/scan" -Method POST -ContentType "application/json" -Body '{"minPrice":1,"maxPrice":20,"maxFloat":10000000,"minGainPercent":1,"volumeMultiplier":1.5,"chartTimeframe":"5m","displayCount":1}' -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "   ✅ Backend is responding" -ForegroundColor Green
    $backendData = $backendTest.Content | ConvertFrom-Json
    Write-Host "   📊 IBKR Connected: $($backendData.apiStatus.ibkrConnected)" -ForegroundColor $(if ($backendData.apiStatus.ibkrConnected) { "Green" } else { "Red" })
    Write-Host "   📈 Stocks found: $($backendData.stocks.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Backend Error: $_" -ForegroundColor Red
    Write-Host "   💡 Try: cd backend && python app.py" -ForegroundColor Yellow
}

Write-Host ""

# 2. Test Web Frontend
Write-Host "2. Testing Web Frontend..." -ForegroundColor Yellow
$frontendPorts = @(3000, 3001, 5173)
$frontendFound = $false
foreach ($port in $frontendPorts) {
    try {
        $frontendTest = Invoke-WebRequest -Uri "http://localhost:$port" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        Write-Host "   ✅ Frontend is running on port $port" -ForegroundColor Green
        Write-Host "   🌐 Open: http://localhost:$port" -ForegroundColor Cyan
        $frontendFound = $true
        break
    } catch {
        # Port not active, continue
    }
}
if (-not $frontendFound) {
    Write-Host "   ❌ Frontend not found on ports 3000, 3001, or 5173" -ForegroundColor Red
    Write-Host "   💡 Try: cd frontend && npm run dev" -ForegroundColor Yellow
}

Write-Host ""

# 3. Test IB Gateway
Write-Host "3. Testing IB Gateway Connection..." -ForegroundColor Yellow
$ibPorts = @(4001, 7497, 7496)
$ibFound = $false
foreach ($port in $ibPorts) {
    $ibCheck = netstat -ano | findstr ":$port"
    if ($ibCheck) {
        Write-Host "   ✅ IB Gateway listening on port $port" -ForegroundColor Green
        $ibFound = $true
        break
    }
}
if (-not $ibFound) {
    Write-Host "   ❌ IB Gateway not found" -ForegroundColor Red
    Write-Host "   💡 Start IB Gateway and enable API access" -ForegroundColor Yellow
}

Write-Host ""

# 4. Test Mobile App API Endpoint
Write-Host "4. Testing Mobile App API Endpoint..." -ForegroundColor Yellow
$mobileApiUrl = "http://192.168.1.157:5000/api/scan"
try {
    $mobileTest = Invoke-WebRequest -Uri $mobileApiUrl -Method POST -ContentType "application/json" -Body '{"minPrice":1,"maxPrice":20,"maxFloat":10000000,"minGainPercent":1,"volumeMultiplier":1.5,"chartTimeframe":"5m","displayCount":1}' -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "   ✅ Mobile API endpoint accessible" -ForegroundColor Green
    Write-Host "   📱 URL: $mobileApiUrl" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Mobile API Error: $_" -ForegroundColor Red
    Write-Host "   💡 Check firewall allows port 5000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Web: Open http://localhost:3001 (or check other ports)" -ForegroundColor White
Write-Host "2. iOS: Run npm start in mobile app folder, press i" -ForegroundColor White
Write-Host "3. Android: Run npm start in mobile app folder, press a" -ForegroundColor White
