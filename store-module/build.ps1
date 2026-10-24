param([string]$BuildType='Release',[string]$UCP3Path='')
$ErrorActionPreference='Stop'
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$vs=& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(-not $vs){throw 'Visual C++ x86 build tools required'}
$setup=Join-Path $vs 'VC/Auxiliary/Build/vcvars32.bat'
$info=[Diagnostics.ProcessStartInfo]::new()
$info.FileName=$env:ComSpec
$info.Arguments='/d /s /c ""'+$setup+'" >nul && set"'
$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardOutput=$true
$process=[Diagnostics.Process]::Start($info);$environment=$process.StandardOutput.ReadToEnd();$process.WaitForExit()
if($process.ExitCode -ne 0){throw 'Visual C++ environment setup failed'}
foreach($line in $environment -split "`r?`n") {
    $separator=$line.IndexOf('=')
    if($separator -gt 0){[Environment]::SetEnvironmentVariable($line.Substring(0,$separator),$line.Substring($separator+1),'Process')}
}
& rustup target add i686-pc-windows-msvc
if($LASTEXITCODE -ne 0){throw 'Rust x86 target installation failed'}
& cargo build --locked --release --target i686-pc-windows-msvc --features store-bridge --lib --manifest-path "$PSScriptRoot/Cargo.toml" --target-dir "$PSScriptRoot/build/native-target"
if($LASTEXITCODE -ne 0){throw 'Store bridge source build failed'}
Copy-Item -LiteralPath "$PSScriptRoot/build/native-target/i686-pc-windows-msvc/release/samurai_kern.dll" -Destination "$PSScriptRoot/build/samurai_kern.dll" -Force
