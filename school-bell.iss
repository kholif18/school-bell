[Setup]
AppName=School Bell Automation
AppVersion=1.0
DefaultDirName={pf}\SchoolBell
DefaultGroupName=School Bell
OutputBaseFilename=school-bell-installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon\schoolbell.ico"; DestDir: "{app}"

[Icons]
Name: "{group}\School Bell"; Filename: "{app}\main.exe"; IconFilename: "{app}\schoolbell.ico"
Name: "{commondesktop}\School Bell"; Filename: "{app}\main.exe"; IconFilename: "{app}\schoolbell.ico"

[Run]
Filename: "{app}\main.exe"; Description: "Launch School Bell"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
ValueType: string; ValueName: "SchoolBell"; ValueData: "{app}\main.exe"

Name: "{userstartup}\School Bell"; Filename: "{app}\main.exe"