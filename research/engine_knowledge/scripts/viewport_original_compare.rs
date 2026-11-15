//! Executes only the inspected 54-byte leaf predicate in this isolated 32-bit process.
//! Never injects code into the game. Input is the fresh game's captured renderer mask.
mod viewport_rule;
use std::{ffi::c_void, fs, env};
#[link(name="kernel32")]
extern "system" {
    fn VirtualAlloc(a:*mut c_void,n:usize,t:u32,p:u32)->*mut c_void;
    fn VirtualProtect(a:*mut c_void,n:usize,p:u32,old:*mut u32)->i32;
    fn VirtualFree(a:*mut c_void,n:usize,t:u32)->i32;
    fn FlushInstructionCache(p:*mut c_void,a:*const c_void,n:usize)->i32;
    fn GetCurrentProcess()->*mut c_void;
}
type Original=unsafe extern "thiscall" fn(*const u8,u32,u32)->u32;
fn main(){
    let args:Vec<String>=env::args().collect();
    let dir=&args[1];
    let code=fs::read(format!("{dir}/xy-original.bin")).unwrap();
    // Guard against code changes, calls, relocations or unreviewed target versions.
    let expected:[u8;54]=[0x8b,0x54,0x24,0x04,0x81,0xfa,0x8f,0x01,0,0,0x77,0x25,0x8b,0x44,0x24,0x08,0x3d,0x8f,0x01,0,0,0x77,0x1a,0x69,0xc0,0x90,0x01,0,0,0x03,0xc2,0x80,0xbc,0x08,0xc0,0,0,0,0,0x74,0x08,0xb8,0x01,0,0,0,0xc2,0x08,0,0x33,0xc0,0xc2,0x08,0];
    assert_eq!(code,expected,"unreviewed machine code; do not execute");
    let capture=fs::read(format!("{dir}/viewport-mask.bin")).unwrap();
    let mask:&[u8;160000]=capture.as_slice().try_into().unwrap();
    let mut object=vec![0u8;0xc0+160000]; object[0xc0..].copy_from_slice(mask);
    unsafe {
        let mem=VirtualAlloc(std::ptr::null_mut(),code.len(),0x3000,0x04);
        assert!(!mem.is_null());std::ptr::copy_nonoverlapping(code.as_ptr(),mem as *mut u8,code.len());
        let mut old=0;assert_ne!(VirtualProtect(mem,code.len(),0x20,&mut old),0);
        assert_ne!(FlushInstructionCache(GetCurrentProcess(),mem,code.len()),0);
        let original:Original=std::mem::transmute(mem);
        let mut checked=0; let mut mutation_killed=false;
        for y in 0..400u32 {for x in 0..400u32 {
            let got=original(object.as_ptr(),x,y)!=0;
            assert_eq!(got,viewport_rule::xy_are_valid(mask,x,y),"x={x} y={y}");
            // Deliberately wrong claim: any square coordinate is a valid map cell.
            if !got {mutation_killed=true;}
            checked+=1;
        }}
        assert!(mutation_killed,"capture has no counterexample to naive rectangle rule");
        let edge=[0,1,398,399,400,401,u32::MAX,0x80000000];
        for x in edge {for y in edge {
            assert_eq!(original(object.as_ptr(),x,y)!=0,viewport_rule::xy_are_valid(mask,x,y));checked+=1;
        }}
        let mut synthetic=[0u8;160000];
        synthetic[1*400+3]=255;synthetic[399*400+399]=128;
        object[0xc0..].copy_from_slice(&synthetic);
        for (x,y) in [(3,1),(1,3),(399,399),(400,399),(399,400),(u32::MAX,0)] {
            assert_eq!(original(object.as_ptr(),x,y)!=0,viewport_rule::xy_are_valid(&synthetic,x,y));checked+=1;
        }
        assert_ne!(original(object.as_ptr(),3,1),original(object.as_ptr(),1,3),"axis-swap mutation not detected");
        assert_ne!(VirtualFree(mem,0,0x8000),0);
        println!("{{\"comparisons\":{checked},\"mismatches\":0,\"rectangle_mutation_killed\":true,\"axis_swap_mutation_killed\":true,\"scope\":\"isolated original leaf code with captured live input, not pathfinding or gameplay\"}}");
    }
}
