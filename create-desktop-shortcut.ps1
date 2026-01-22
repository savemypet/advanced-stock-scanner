# Create Desktop Shortcut for Stock Scanner
# Run this script to create a desktop shortcut

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Start Stock Scanner.lnk"
$targetPath = Join-Path $PSScriptRoot "start-scanner.bat"
$workingDir = $PSScriptRoot

Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow
Write-Host "Desktop: $desktop" -ForegroundColor Cyan
Write-Host "Shortcut: $shortcutPath" -ForegroundColor Cyan
Write-Host "Target: $targetPath" -ForegroundColor Cyan

try {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $targetPath
    $shortcut.WorkingDirectory = $workingDir
    $shortcut.Description = "Start Advanced Stock Scanner with IB Gateway"
    $shortcut.IconLocation = "C:\Windows\System32\shell32.dll,137"  # Chart/Graph icon
    $shortcut.Save()
    
    Write-Host ""
    Write-Host "✅ Desktop shortcut created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Shortcut Details:" -ForegroundColor Yellow
    Write-Host "  Name: Start Stock Scanner" -ForegroundColor White
    Write-Host "  Location: Desktop" -ForegroundColor White
    Write-Host "  Target: start-scanner.bat" -ForegroundColor White
    Write-Host "  Description: Start Advanced Stock Scanner with IB Gateway" -ForegroundColor White
    Write-Host ""
    Write-Host "Double-click the shortcut on your desktop to start the app!" -ForegroundColor Cyan
} catch {
    Write-Host ""
    Write-Host "❌ Error creating shortcut: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Right-click start-scanner.bat and select 'Create shortcut'" -ForegroundColor Yellow
    Write-Host "Then drag the shortcut to your desktop" -ForegroundColor Yellow
}
