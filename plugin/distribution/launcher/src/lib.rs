//! Start our bundled worker; no mouse, keyboard, focus or window control.
use std::os::windows::process::CommandExt;
use std::panic::catch_unwind;
use std::process::{Command, Stdio};

fn game() -> Option<std::path::PathBuf> {
    std::env::current_exe().ok()?.parent().map(|p| p.to_path_buf())
}

#[unsafe(no_mangle)]
pub extern "C" fn sai_prepare() -> i32 {
    catch_unwind(|| {
        let Some(root) = game() else { return 0 };
        std::fs::create_dir_all(root.join("ucp/villagestudio")).is_ok() as i32
    }).unwrap_or(0)
}

#[unsafe(no_mangle)]
pub extern "C" fn sai_start() -> i32 {
    catch_unwind(|| {
        let Some(root) = game() else { return 0 };
        let Ok(system) = std::env::var("SystemRoot") else { return 0 };
        let powershell = std::path::Path::new(&system).join("System32/WindowsPowerShell/v1.0/powershell.exe");
        Command::new(powershell)
            .args(["-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File"])
            .arg(root.join("ucp/villagestudio/bootstrap.ps1"))
            .arg("-Game").arg(&root).arg("-GamePid").arg(std::process::id().to_string())
            .current_dir(&root).creation_flags(0x08000000)
            .stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null())
            .spawn().is_ok() as i32
    }).unwrap_or(0)
}
