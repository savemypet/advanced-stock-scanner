Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\Advanced Stock Scanner.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = WScript.Arguments(0) & "\start-scanner.bat"
oLink.WorkingDirectory = WScript.Arguments(0)
oLink.Description = "Advanced Stock Scanner - Real-time stock scanner with candlestick charts"
oLink.IconLocation = "C:\Windows\System32\shell32.dll,137"
oLink.Save
WScript.Echo "Desktop shortcut created successfully!"
