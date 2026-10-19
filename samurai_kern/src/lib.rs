//! SamurAI-Kern (Backlog B-115, Daniel 19.10.2026 22:33: "ja bau es in Rust").
//! Laeuft als 32-Bit-DLL im Spielprozess (geladen von logik.lua ueber core.openLibraryHandle, Aufruf cdecl) und liest die
//! Spielstrukturen direkt - ohne Datei-Kanal. Adressen und Felder: Selfaware-AI/Spielkarte.md Abschnitt 2 (OpenSHC-Strukturen,
//! gegen jede Lagebild-Spalte geprueft).
//! Stufe 1: Einheiten je Spieler zaehlen und alle 500 Takte eine Protokollzeile schreiben.

use std::fs::OpenOptions;
use std::io::Write;

/// DAT_UnitsState 0x01387F38: +0 maxUnitCount; Einheiten-Array ab +0x614 = 0x0138854C, je Einheit 1.168 Byte, 2.500 Plaetze
const UNITS_STATE: usize = 0x0138_7F38;
const UNITS: usize = 0x0138_854C;
const UNIT_GROESSE: usize = 1168;
const UNIT_PLAETZE: usize = 2500;
/// Felder einer Einheit (Spielkarte 2): logicalState +0x8C, unitType +0x8E, owner +0x96, dying +0x2A0
const F_ZUSTAND: usize = 0x8C;
const F_TYP: usize = 0x8E;
const F_BESITZER: usize = 0x96;
const F_STIRBT: usize = 0x2A0;
const PROTOKOLL: &str = "ucp/villagestudio/samurai_kern.log";
const PROTOKOLL_ALLE: i32 = 500;

static mut LETZTE_ZEILE: i32 = -1;

unsafe fn i16_bei(adresse: usize) -> i16 {
    unsafe { std::ptr::read_volatile(adresse as *const i16) }
}

unsafe fn i32_bei(adresse: usize) -> i32 {
    unsafe { std::ptr::read_volatile(adresse as *const i32) }
}

/// Lebende Einheiten je Spieler 0..8 (Zustand != 0, Typ > 0, stirbt nicht) - wie der Filter im Lagebild von logik.lua.
pub fn einheiten_je_spieler() -> [u32; 9] {
    let mut je = [0u32; 9];
    let max = unsafe { i32_bei(UNITS_STATE) }.clamp(0, UNIT_PLAETZE as i32) as usize;
    for i in 1..max {
        let u = UNITS + i * UNIT_GROESSE;
        unsafe {
            if i16_bei(u + F_TYP) > 0 && i16_bei(u + F_ZUSTAND) != 0 && i16_bei(u + F_STIRBT) == 0 {
                let b = i16_bei(u + F_BESITZER);
                if (0..9).contains(&b) {
                    je[b as usize] += 1;
                }
            }
        }
    }
    je
}

#[unsafe(no_mangle)]
pub extern "C" fn samurai_version() -> u32 {
    1
}

/// Jeden Takt aus logik.lua: gibt die Zahl lebender Einheiten von `spieler` zurueck; alle 500 Takte eine Zeile ins Protokoll.
#[unsafe(no_mangle)]
pub extern "C" fn samurai_takt(tick: i32, spieler: i32) -> i32 {
    let je = einheiten_je_spieler();
    unsafe {
        let letzte = LETZTE_ZEILE;
        if letzte < 0 || tick < letzte || tick - letzte >= PROTOKOLL_ALLE {
            LETZTE_ZEILE = tick;
            if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(PROTOKOLL) {
                let _ = writeln!(f, "tick {} einheiten {:?}", tick, je);
            }
        }
    }
    if (0..9).contains(&spieler) { je[spieler as usize] as i32 } else { -1 }
}

/// Zahl lebender Einheiten eines Spielers, ohne Protokoll (fuer Pruefungen).
#[unsafe(no_mangle)]
pub extern "C" fn samurai_einheiten(spieler: i32) -> i32 {
    let je = einheiten_je_spieler();
    if (0..9).contains(&spieler) { je[spieler as usize] as i32 } else { -1 }
}
