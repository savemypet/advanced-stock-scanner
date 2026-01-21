@echo off
echo ========================================
echo   Create Desktop Shortcut
echo   Advanced Stock Scanner
echo ========================================
echo.

REM Get the current directory
set "CURRENT_DIR=%~dp0"

REM Create shortcut using VBScript
echo Creating desktop shortcut...
cscript //nologo "%~dp0create-desktop-shortcut.vbs" "%CURRENT_DIR%"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create shortcut
    echo Trying PowerShell method...
    echo.
    
    REM Alternative: Use PowerShell
    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Advanced Stock Scanner.lnk'); $Shortcut.TargetPath = '%CURRENT_DIR%start-scanner.bat'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.Description = 'Advanced Stock Scanner - Real-time stock scanner'; $Shortcut.IconLocation = 'C:\Windows\System32\shell32.dll,137'; $Shortcut.Save()"
    
    if errorlevel 1 (
        echo ERROR: Both methods failed. Please create shortcut manually.
        echo.
        echo Manual steps:
        echo 1. Right-click on Desktop
        echo 2. New ^> Shortcut
        echo 3. Browse to: %CURRENT_DIR%start-scanner.bat
        echo 4. Name it: Advanced Stock Scanner
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Shortcut created successfully!
echo.
echo Look for "Advanced Stock Scanner" on your desktop.
echo Double-click it to start the app!
echo ========================================
echo.
pause
