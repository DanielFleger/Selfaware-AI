//! Offline 32-bit Windows IPC peer; never installed as a Store module.
use samurai_kern::bridge_channel as channel;
use std::io::Write;
fn main() {
    assert_ne!(channel::bridge_open(),0);
    assert_eq!(channel::bridge_ready(),1);
    println!("{}",std::process::id());std::io::stdout().flush().unwrap();
    loop {
        let seq=channel::bridge_pending();
        if seq==0 { std::thread::sleep(std::time::Duration::from_millis(1));continue; }
        let input=channel::request_bytes();
        let stop=input.as_deref()==Some(b"stop");
        let (bytes,error)=input.map_or((b"invalid request length".to_vec(),1),|s|(s,0));
        assert_eq!(channel::response_bytes(&bytes,seq,error),1);
        if stop {break;}
    }
    std::thread::sleep(std::time::Duration::from_millis(20));
    channel::bridge_close();
}
