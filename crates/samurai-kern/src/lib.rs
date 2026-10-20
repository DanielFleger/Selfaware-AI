//! SamurAI-Kern (Backlog B-115, Daniel 19.10.2026 22:33: "ja bau es in Rust"; B-145, Daniel 20.10.2026 22:34:
//! "wir brauchen absolute Kontrolle in jedem Tick des Spiels").
//! Laeuft als 32-Bit-DLL im Spielprozess (geladen von logik.lua ueber core.openLibraryHandle, Aufruf cdecl) und liest die
//! Spielstrukturen direkt - ohne Datei-Kanal. Adressen und Felder: docs/research/Spielkarte.md Abschnitt 2.
//! Stufe 1 (B-115): Einheiten je Spieler zaehlen, alle 500 Takte eine Protokollzeile.
//! S0 (docs/plans/Plan_Kern.md): Taktwaechter, Messbasis, Fehlerfang - ein Fehler schaltet den Kern ab, nicht das Spiel.
//! S1: Augen - Einheiten, Gebaeude und Grabenwache in jedem neuen Takt (welt.rs); Weltbild auf Befehl ausschreiben.

mod waechter;
mod welt;

use std::fs::OpenOptions;
use std::io::Write;
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Instant;

use waechter::{Ereignis, Waechter};
use welt::Welt;

pub const VERSION: u32 = 5;

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
const WELT_EINHEITEN: &str = "ucp/villagestudio/kern_lagebild.txt";
const WELT_GEBAEUDE: &str = "ucp/villagestudio/kern_gebaeude.txt";
const PROTOKOLL_ALLE: i32 = 500;
/// So viele neue Grabenfelder werden je Meldung mit Ort genannt
const GRABEN_ORTE: usize = 5;
/// samurai_test_fehler(TESTFEHLER) loest absichtlich einen Fehler aus (Gegenprobe zum Fehlerfang)
const TESTFEHLER: i32 = 0x5A4D;

/// Rueckgabe, wenn der Kern nach einem Fehler abgeschaltet ist
const AUS: i32 = -2;

static KAPUTT: AtomicBool = AtomicBool::new(false);

/// Summen und Hoechstwerte seit der letzten Protokollzeile
struct Messung {
    aufrufe: u64,
    kern_ns: u128,
    kern_ns_max: u128,
    takte: u64,
    takt_ns: u128,
    welt_ns: u128,
    karte_ns: u128,
}

impl Messung {
    const fn neu() -> Self {
        Messung { aufrufe: 0, kern_ns: 0, kern_ns_max: 0, takte: 0, takt_ns: 0, welt_ns: 0, karte_ns: 0 }
    }
}

struct Zustand {
    waechter: Waechter,
    welt: Welt,
    letzte_zeile: i32,
    letzter_takt: Option<Instant>,
    m: Messung,
}

static ZUSTAND: Mutex<Zustand> = Mutex::new(Zustand {
    waechter: Waechter::neu(),
    welt: Welt::neu(),
    letzte_zeile: -1,
    letzter_takt: None,
    m: Messung::neu(),
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

fn zustand() -> std::sync::MutexGuard<'static, Zustand> {
    ZUSTAND.lock().unwrap_or_else(|e| e.into_inner())
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

fn ort(feld: usize) -> String {
    Welt::feld_xy(feld).map_or(format!("Feld {}", feld), |(x, y)| format!("({},{})", x, y))
}

fn takt(tick: i32, spieler: i32) -> i32 {
    let start = Instant::now();
    let je = einheiten_je_spieler();
    let leer = je.iter().all(|&n| n == 0);
    let mut z = zustand();
    match z.waechter.sieh(tick, leer) {
        Ereignis::NeuerTakt => {
            if let Some(vorher) = z.letzter_takt {
                z.m.takt_ns += start.duration_since(vorher).as_nanos();
                z.m.takte += 1;
            }
            z.letzter_takt = Some(start);
            let t0 = Instant::now();
            z.welt.lesen();
            let t1 = Instant::now();
            let g = z.welt.graben_lesen();
            z.m.welt_ns += t1.duration_since(t0).as_nanos();
            z.m.karte_ns += t1.elapsed().as_nanos();
            if !g.neu_geplant.is_empty() || !g.neu_ausgehoben.is_empty() || !g.zugeschuettet.is_empty() || g.plan_geloescht > 0 {
                let orte = |v: &Vec<usize>| v.iter().take(GRABEN_ORTE).map(|&f| ort(f)).collect::<Vec<_>>().join(" ");
                schreibe(&format!(
                    "graben tick {}: neu geplant {} [{}] | neu ausgehoben {} [{}] | zugeschuettet {} [{}] | Planung geloescht {} | jetzt geplant {} ausgehoben {}",
                    tick, g.neu_geplant.len(), orte(&g.neu_geplant), g.neu_ausgehoben.len(), orte(&g.neu_ausgehoben),
                    g.zugeschuettet.len(), orte(&g.zugeschuettet), g.plan_geloescht, g.geplant, g.ausgehoben));
            }
        }
        Ereignis::Epoche { von, nach } => {
            schreibe(&format!("epoche {} tick {} von {} (Sprung {})", z.waechter.epoche, nach,
                              von.map_or("-".to_string(), |v| v.to_string()),
                              von.map_or("-".to_string(), |v| (nach as i64 - v as i64).to_string())));
            z.letzter_takt = Some(start);
            z.letzte_zeile = -1;
            z.welt.epoche();
            z.welt.lesen();
            let g = z.welt.graben_lesen();
            schreibe(&format!("graben tick {}: Aufnahme der Epoche - geplant {} ausgehoben {}", tick, g.geplant, g.ausgehoben));
        }
        Ereignis::Pause | Ereignis::KeinePartie => {}
    }
    let letzte = z.letzte_zeile;
    if letzte < 0 || tick < letzte || tick - letzte >= PROTOKOLL_ALLE {
        z.letzte_zeile = tick;
        schreibe(&format!("tick {} einheiten {:?}", tick, je));
        let m = &z.m;
        let je_aufruf = |ns: u128| if m.aufrufe > 0 { ns as f64 / m.aufrufe as f64 / 1000.0 } else { 0.0 };
        let je_takt = |ns: u128| if m.takte > 0 { ns as f64 / m.takte as f64 / 1000.0 } else { 0.0 };
        let w = &z.waechter;
        schreibe(&format!(
            "waechter tick {} version {} epoche {} neu {} pause {} wechsel {} keine_partie {} | aufrufe {} kern_us_mittel {:.1} \
             kern_us_max {:.1} | takte {} takt_ms_mittel {:.3} | welt_us {:.1} karte_us {:.1} einheiten {} gebaeude {} max {}",
            tick, VERSION, w.epoche, w.neu, w.pause, w.wechsel, w.keine_partie, m.aufrufe, je_aufruf(m.kern_ns),
            m.kern_ns_max as f64 / 1000.0, m.takte, je_takt(m.takt_ns) / 1000.0, je_takt(m.welt_ns), je_takt(m.karte_ns),
            z.welt.einheiten.len(), z.welt.gebaeude.len(), z.welt.einheiten_max));
        z.m = Messung::neu();
    }
    let dauer = start.elapsed().as_nanos();
    z.m.aufrufe += 1;
    z.m.kern_ns += dauer;
    z.m.kern_ns_max = z.m.kern_ns_max.max(dauer);
    if (0..9).contains(&spieler) { je[spieler as usize] as i32 } else { -1 }
}

#[unsafe(no_mangle)]
pub extern "C" fn samurai_version() -> u32 {
    VERSION
}

/// Jeden Aufruf aus logik.lua (nach jedem Takt und in der Pause): gibt die Zahl lebender Einheiten von `spieler` zurueck,
/// -1 bei ungueltigem Spieler, -2 wenn der Kern nach einem Fehler abgeschaltet ist.
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

/// S1: liest das Weltbild jetzt neu und schreibt es im Lagebild-Format nach ucp/villagestudio/kern_lagebild.txt und
/// kern_gebaeude.txt (Vergleich mit {"lagebild": true} im selben, angehaltenen Takt). Rueckgabe: Zahl der Einheiten, -3 bei
/// einem Schreibfehler.
#[unsafe(no_mangle)]
pub extern "C" fn samurai_welt_schreiben(tick: i32) -> i32 {
    geschuetzt("samurai_welt_schreiben", || {
        let mut z = zustand();
        z.welt.lesen();
        match z.welt.schreiben(tick, WELT_EINHEITEN, WELT_GEBAEUDE) {
            Ok(()) => z.welt.einheiten.len() as i32,
            Err(_) => -3,
        }
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

    // (Nur Funktionen ohne Spielspeicher - takt/welt lesen feste Adressen und duerfen hier nicht laufen.)
    #[test]
    fn fehlerfang_schaltet_kern_ab_statt_abzustuerzen() {
        assert_eq!(samurai_test_fehler(7), 7);
        assert_eq!(samurai_test_fehler(TESTFEHLER), AUS);
        assert!(KAPUTT.load(Ordering::Relaxed));
        assert_eq!(samurai_test_fehler(7), AUS);
        assert_eq!(samurai_einheiten(1), AUS);
    }
}
