[Setup]
AppId={{A3F1B2C3-D4E5-4F6A-A7B8-9C0D1E2F3A4B}
AppName=Sitzordnungsersteller
AppVersion=1.0
DefaultDirName={autopf}\Sitzordnungsersteller
DefaultGroupName=Sitzordnungsersteller
OutputBaseFilename=Sitzordnungsersteller
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked


[Files]
Source: "dist\Sitzordnung\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]

Name: "{group}\Sitzordnungsersteller"; Filename: "{app}\Sitzordnung.exe"

Name: "{autodesktop}\Sitzordnungsersteller"; Filename: "{app}\Sitzordnung.exe"; Tasks: desktopicon

[Run]
; Startet die App direkt nach der Installation, wenn der Nutzer das Häkchen setzt
Filename: "{app}\Sitzordnung.exe"; Description: "{cm:LaunchProgram,Sitzordnungsersteller}"; Flags: nowait postinstall skipifsilent
