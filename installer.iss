; FocusFlow Inno Setup Installer Script
; -----------------------------------------
; To build: Run 'python build_installer.py' or open this file in Inno Setup.

#define MyAppName "FocusFlow"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Zakir"
#define MyAppExeName "FocusFlow.exe"
#define MyAppURL "https://zakir-focusflow.com"

[Setup]
; Unique App ID (generated for persistent tracking)
AppId={{DA686654-706E-4CB2-A8D1-460B05F4BAEA}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation path
DefaultDirName={localappdata}\{#MyAppName}
DisableDirPage=yes
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Packaging options
OutputDir=installer_output
OutputBaseFilename=FocusFlow_Setup
SetupIconFile=Logo.png
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; Uninstallation
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Privileges (lowest ensures users can install without admin rights)
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Launch FocusFlow on Windows startup"; GroupDescription: "Preferences:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "Logo.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Standard Windows Autostart
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
