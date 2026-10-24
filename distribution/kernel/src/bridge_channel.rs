//! Pagefile-backed volatile IPC only. No filesystem, extraction or process launch.
//! Layout shared with werkzeug/speicherkanal.py; all lengths bounded before use.
use std::collections::VecDeque;
use std::ffi::{c_void, CString};
use std::sync::{Mutex, atomic::{AtomicU32, Ordering}};

pub const MAGIC: u32 = 0x5341_4942;
pub const VERSION: u32 = 1;
pub const HEADER: usize = 4096;
pub const REQUEST_CAP: usize = 1024 * 1024;
pub const RESPONSE_CAP: usize = 32 * 1024 * 1024;
pub const RESPONSE: usize = HEADER + REQUEST_CAP;
pub const SIZE: usize = RESPONSE + RESPONSE_CAP;
pub const STATUS: usize = 64;
pub const STATUS_CAP: usize = HEADER - STATUS;

#[link(name = "kernel32")]
unsafe extern "system" {
    fn CreateFileMappingW(file: isize, attr: *const c_void, protect: u32, high: u32, low: u32, name: *const u16) -> isize;
    fn MapViewOfFile(handle: isize, access: u32, high: u32, low: u32, size: usize) -> *mut c_void;
    fn UnmapViewOfFile(base: *const c_void) -> i32;
    fn CloseHandle(handle: isize) -> i32;
    fn GetCurrentProcessId() -> u32;
    fn GetLastError() -> u32;
}

struct Channel { base: usize, handle: isize }
impl Channel {
    fn atom(&self, offset: usize) -> &AtomicU32 { unsafe { &*((self.base+offset) as *const AtomicU32) } }
}
impl Drop for Channel {
    fn drop(&mut self) { unsafe { self.atom(40).store(0,Ordering::Release); UnmapViewOfFile(self.base as *const c_void); CloseHandle(self.handle); } }
}
static CHANNEL: Mutex<Option<Channel>> = Mutex::new(None);
static TRACE: Mutex<VecDeque<String>> = Mutex::new(VecDeque::new());
static LAST_TRACE: Mutex<Option<CString>> = Mutex::new(None);
fn channel() -> std::sync::MutexGuard<'static,Option<Channel>> { CHANNEL.lock().unwrap_or_else(|e| e.into_inner()) }

pub fn trace(text: &str) {
    let mut logs=TRACE.lock().unwrap_or_else(|e| e.into_inner());
    if logs.len()>=128 { logs.pop_front(); }
    logs.push_back(text.chars().take(4096).collect());
}

#[unsafe(no_mangle)]
pub extern "C" fn bridge_open() -> usize {
    let mut state=channel();
    if let Some(c)=&*state { return c.base; }
    unsafe {
        let pid=GetCurrentProcessId();
        let name: Vec<u16>=format!("Local\\SelfawareBridge_{}_V{}",pid,VERSION).encode_utf16().chain(Some(0)).collect();
        let handle=CreateFileMappingW(-1,std::ptr::null(),4,0,SIZE as u32,name.as_ptr());
        if handle==0 { return 0; }
        // Never adopt a stale mapping held by a client of a recycled process ID.
        if GetLastError()==183 { CloseHandle(handle); return 0; }
        let base=MapViewOfFile(handle,0xF001F,0,0,SIZE) as usize;
        if base==0 { CloseHandle(handle); return 0; }
        let c=Channel{base,handle};
        c.atom(4).store(VERSION,Ordering::Relaxed);
        c.atom(8).store(SIZE as u32,Ordering::Relaxed);
        c.atom(12).store(pid,Ordering::Relaxed);
        c.atom(0).store(MAGIC,Ordering::Release);
        *state=Some(c);base
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn bridge_ready() -> i32 {
    if let Some(c)=&*channel() { c.atom(40).store(1,Ordering::Release);1 } else { 0 }
}

#[unsafe(no_mangle)]
pub extern "C" fn bridge_pending() -> u32 {
    if let Some(c)=&*channel() {
        if c.atom(48).load(Ordering::Acquire)!=c.atom(20).load(Ordering::Acquire) {return 0;}
        let request=c.atom(16).load(Ordering::Acquire);
        if request!=c.atom(20).load(Ordering::Acquire) { return request; }
    } 0
}

#[unsafe(no_mangle)]
pub extern "C" fn bridge_reply(length: u32, sequence: u32, error: u32) -> i32 {
    if length as usize>=RESPONSE_CAP { return -1; }
    if let Some(c)=&*channel() {
        if sequence==0 || sequence!=c.atom(16).load(Ordering::Acquire) || sequence==c.atom(20).load(Ordering::Acquire) { return -2; }
        c.atom(28).store(length,Ordering::Relaxed);
        c.atom(44).store(error,Ordering::Relaxed);
        c.atom(20).store(sequence,Ordering::Release);return 1;
    } -3
}

#[unsafe(no_mangle)]
pub extern "C" fn bridge_status_begin() -> usize {
    if let Some(c)=&*channel() { c.atom(32).fetch_add(1,Ordering::AcqRel);c.base+STATUS } else { 0 }
}

#[unsafe(no_mangle)]
pub extern "C" fn bridge_status_end(length: u32) -> i32 {
    if let Some(c)=&*channel() {
        let valid=(length as usize)<STATUS_CAP;
        c.atom(36).store(if valid {length} else {0},Ordering::Relaxed);
        c.atom(32).fetch_add(1,Ordering::Release);return if valid {1} else {-1};
    } 0
}

#[unsafe(no_mangle)]
pub extern "C" fn bridge_log_next() -> usize {
    let line=TRACE.lock().unwrap_or_else(|e| e.into_inner()).pop_front();
    let mut last=LAST_TRACE.lock().unwrap_or_else(|e| e.into_inner());
    *last=line.and_then(|s| CString::new(s.replace('\0',"?")).ok());
    last.as_ref().map_or(0,|s| s.as_ptr() as usize)
}

#[unsafe(no_mangle)]
pub extern "C" fn bridge_close() { *channel()=None; }

/// Synthetic server only; validates the same bounds used by the Lua bridge.
pub fn request_bytes() -> Option<Vec<u8>> {
    let state=channel();let c=state.as_ref()?;
    let n=c.atom(24).load(Ordering::Acquire) as usize;
    if n==0 || n>=REQUEST_CAP { return None; }
    Some(unsafe { std::slice::from_raw_parts((c.base+HEADER) as *const u8,n) }.to_vec())
}

pub fn response_bytes(bytes: &[u8],sequence: u32,error: u32) -> i32 {
    if bytes.len()>=RESPONSE_CAP { return -1; }
    { let state=channel();let Some(c)=state.as_ref() else {return -3};
      unsafe { std::ptr::copy_nonoverlapping(bytes.as_ptr(),(c.base+RESPONSE) as *mut u8,bytes.len()) }; }
    bridge_reply(bytes.len() as u32,sequence,error)
}
