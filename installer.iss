[Setup]
AppName=RecordForge
AppVersion=2.1.0
AppPublisher=Michael Nocito
AppPublisherURL=https://github.com/michaelnocito/recordforge
AppSupportURL=https://github.com/michaelnocito/recordforge/issues
DefaultDirName={autopf}\RecordForge
DefaultGroupName=RecordForge
OutputBaseFilename=RecordForgeSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\RecordForge.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\RecordForge"; Filename: "{app}\RecordForge.exe"
Name: "{commondesktop}\RecordForge"; Filename: "{app}\RecordForge.exe"

[Run]
Filename: "{app}\RecordForge.exe"; Description: "Launch RecordForge"; Flags: nowait postinstall skipifsilent
