//! SamurAI-Kern (Backlog B-115, Daniel 19.10.2026 22:33: "ja bau es in Rust"; B-145 Stufe S0, Daniel 20.10.2026 22:34:
//! "wir brauchen absolute Kontrolle in jedem Tick des Spiels").
//! Laeuft als 32-Bit-DLL im Spielprozess (geladen von logik.lua ueber core.openLibraryHandle, Aufruf cdecl) und liest die
//! Spielstrukturen direkt - ohne Datei-Kanal. Adressen und Felder: docs/research/Spielkarte.md Abschnitt 2 (OpenSHC-Strukturen,
//! gegen jede Lagebild-Spalte geprueft).
//! Stufe 1: Einheiten je Spieler zaehlen und alle 500 Takte eine Protokollzeile schreiben.
//! Stufe S0 (Plan_Kern.md): Taktwaechter (neuer Takt / Pause / Epochenwechsel / keine Partie), Messbasis (Dauer des Kerns
//! je Aufruf, echte Zeit je Spieltakt) und Fehlerfang - ein Fehler im Kern schaltet den Kern ab, nicht das Spiel.

mod waechter;

use std::fs::OpenOptions;
use std::io::Write;
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Instant;

use waechter::{Ereignis, Waechter};

pub const VERSION: u32 = 2;

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
/// samurai_test_fehler(TESTFEHLER) loest absichtlich einen Fehler aus (Gegenprobe zum Fehlerfang)
const TESTFEHLER: i32 = 0x5A4D;

/// Rueckgabe, wenn der Kern nach einem Fehler abgeschaltet ist
const AUS: i32 = -2;

static KAPUTT: AtomicBool = AtomicBool::new(false);

struct Zustand {
    waechter: Waechter,
    letzte_zeile: i32,
    /// Messbasis seit der letzten Protokollzeile
    aufrufe: u64,
    kern_ns_summe: u128,
    kern_ns_max: u128,
    takte: u64,
    takt_ns_summe: u128,
    letzter_takt: Option<Instant>,
}

static ZUSTAND: Mutex<Zustand> = Mutex::new(Zustand {
    waechter: Waechter::neu(),
    letzte_zeile: -1,
    aufrufe: 0,
    kern_ns_summe: 0,
    kern_ns_max: 0,
    takte: 0,
    takt_ns_summe: 0,
    letzter_takt: None,
});

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

fn schreibe(zeile: &str) {
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(PROTOKOLL) {
        let _ = writeln!(f, "{}", zeile);
    }
}

/// Fuehrt `f` aus; ein Fehler (panic) schaltet den Kern ab und wird protokolliert, das Spiel laeuft weiter.
fn geschuetzt(was: &str, f: impl FnOnce() -> i32) -> i32 {
    if KAPUTT.load(Ordering::Relaxed) {
        return AUS;
    }
    match catch_unwind(AssertUnwindSafe(f)) {
        Ok(n) => n,
        Err(e) => {
            KAPUTT.store(true, Ordering::Relaxed);
            let text = e
                .downcast_ref::<&str>()
                .map(|s| s.to_string())
                .or_else(|| e.downcast_ref::<String>().cloned())
                .unwrap_or_else(|| "unbekannt".to_string());
            schreibe(&format!("KERN AUS: Fehler in {} ({}) - Kern abgeschaltet, Spiel laeuft weiter", was, text));
            AUS
        }
    }
}

fn takt(tick: i32, spieler: i32) -> i32 {
    let start = Instant::now();
    let je = einheiten_je_spieler();
    let leer = je.iter().all(|&n| n == 0);
    let mut z = ZUSTAND.lock().unwrap_or_else(|e| e.into_inner());
    match z.waechter.sieh(tick, leer) {
        Ereignis::NeuerTakt => {
            if let Some(vorher) = z.letzter_takt {
                z.takt_ns_summe += start.duration_since(vorher).as_nanos();
                z.takte += 1;
            }
            z.letzter_takt = Some(start);
        }
        Ereignis::Epoche { von, nach } => {
            schreibe(&format!("epoche {} tick {} von {} (Sprung {})", z.waechter.epoche, nach,
                              von.map_or("-".to_string(), |v| v.to_string()),
                              von.map_or("-".to_string(), |v| (nach as i64 - v as i64).to_string())));
            z.letzter_takt = Some(start);
            z.letzte_zeile = -1;
        }
        Ereignis::Pause | Ereignis::KeinePartie => {}
    }
    let letzte = z.letzte_zeile;
    if letzte < 0 || tick < letzte || tick - letzte >= PROTOKOLL_ALLE {
        z.letzte_zeile = tick;
        schreibe(&format!("tick {} einheiten {:?}", tick, je));
        let w = &z.waechter;
        let mittel_us = if z.aufrufe > 0 { z.kern_ns_summe as f64 / z.aufrufe as f64 / 1000.0 } else { 0.0 };
        let takt_ms = if z.takte > 0 { z.takt_ns_summe as f64 / z.takte as f64 / 1e6 } else { 0.0 };
        schreibe(&format!(
            "waechter tick {} version {} epoche {} neu {} pause {} wechsel {} keine_partie {} | aufrufe {} kern_us_mittel {:.1} kern_us_max {:.1} | takte {} takt_ms_mittel {:.3}",
            tick, VERSION, w.epoche, w.neu, w.pause, w.wechsel, w.keine_partie, z.aufrufe, mittel_us,
            z.kern_ns_max as f64 / 1000.0, z.takte, takt_ms));
        z.aufrufe = 0;
        z.kern_ns_summe = 0;
        z.kern_ns_max = 0;
        z.takte = 0;
        z.takt_ns_summe = 0;
    }
    let dauer = start.elapsed().as_nanos();
    z.aufrufe += 1;
    z.kern_ns_summe += dauer;
    z.kern_ns_max = z.kern_ns_max.max(dauer);
    if (0..9).contains(&spieler) { je[spieler as usize] as i32 } else { -1 }
}

#[unsafe(no_mangle)]
pub extern "C" fn samurai_version() -> u32 {
    VERSION
}

/// Jeden Aufruf aus logik.lua (nach jedem Takt und in der Pause): gibt die Zahl lebender Einheiten von `spieler` zurueck,
/// -1 bei ungueltigem Spieler, -2 wenn der Kern nach einem Fehler abgeschaltet ist; alle 500 Takte zwei Protokollzeilen.
#[unsafe(no_mangle)]
pub extern "C" fn samurai_takt(tick: i32, spieler: i32) -> i32 {
    geschuetzt("samurai_takt", || takt(tick, spieler))
}

/// Zahl lebender Einheiten eines Spielers, ohne Protokoll (fuer Pruefungen).
#[unsafe(no_mangle)]
pub extern "C" fn samurai_einheiten(spieler: i32) -> i32 {
    geschuetzt("samurai_einheiten", || {
        let je = einheiten_je_spieler();
        if (0..9).contains(&spieler) { je[spieler as usize] as i32 } else { -1 }
    })
}

/// Gegenprobe zum Fehlerfang: mit TESTFEHLER loest der Kern absichtlich einen Fehler aus; danach liefert jeder Aufruf -2.
/// Jeder andere Wert kommt unveraendert zurueck.
#[unsafe(no_mangle)]
pub extern "C" fn samurai_test_fehler(code: i32) -> i32 {
    geschuetzt("samurai_test_fehler", || {
        if code == TESTFEHLER {
            panic!("absichtlicher Testfehler (Gegenprobe B-145)");
        }
        code
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    // (Nur Funktionen ohne Spielspeicher - einheiten_je_spieler/samurai_takt lesen feste Adressen und duerfen hier nicht laufen.)
    #[test]
    fn fehlerfang_schaltet_kern_ab_statt_abzustuerzen() {
        assert_eq!(samurai_test_fehler(7), 7);
        assert_eq!(samurai_test_fehler(TESTFEHLER), AUS);
        assert!(KAPUTT.load(Ordering::Relaxed));
        assert_eq!(samurai_test_fehler(7), AUS);
        assert_eq!(samurai_einheiten(1), AUS);
    }
}
