//! SamurAI-Kern (Backlog B-115, Daniel 19.10.2026 22:33: "ja bau es in Rust"; B-145, Daniel 20.10.2026 22:34:
//! "wir brauchen absolute Kontrolle in jedem Tick des Spiels").
//! Laeuft als 32-Bit-DLL im Spielprozess (geladen von logik.lua ueber core.openLibraryHandle, Aufruf cdecl) und liest die
//! Spielstrukturen direkt - ohne Datei-Kanal. Adressen und Felder: docs/research/Spielkarte.md Abschnitt 2.
//! Stufe 1 (B-115): Einheiten je Spieler zaehlen, alle 500 Takte eine Protokollzeile.
//! S0 (docs/plans/Plan_Kern.md): Taktwaechter, Messbasis, Fehlerfang - ein Fehler schaltet den Kern ab, nicht das Spiel.
//! S1: Augen - Einheiten, Gebaeude und Grabenwache in jedem neuen Takt (welt.rs); Weltbild auf Befehl ausschreiben.
//! S2: Haende - Auftraege an uebergebene Einheiten ueber den Befehlsweg des Spiels, ein Gruppenbefehl je Takt (haende.rs).
//! S3: Wege - Erreichbarkeit ueber das Wegnetz (wege.rs); Grabenreflex: Graben am Ziel einer Kern-Einheit -> sofort neues Ziel.
//! S4a: Leitung - Weltbild jeden neuen Takt in einen benannten gemeinsamen Speicher fuer Python (leitung.rs).
//! S4b: Auftragsring - Python schreibt Auftraege in denselben Speicher, der Kern arbeitet sie im naechsten Takt ab.
//! Beschusswache: eigene Kaempfer, die stehen und Leben verlieren, werden im Takt gemeldet (beschuss.rs) - Auge, kein Verhalten.

mod beschuss;
mod feuer;
mod haende;
mod haken;
mod leitung;
mod waechter;
mod wege;
mod welt;
#[cfg(feature = "store-bridge")]
pub mod bridge_channel;

#[cfg(not(feature = "store-bridge"))]
use std::fs::OpenOptions;
#[cfg(not(feature = "store-bridge"))]
use std::io::Write;
use std::collections::HashMap;
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, AtomicI32, Ordering};
use std::time::Instant;

use haende::{Annahme, Auftrag, Buch};
use waechter::{Ereignis, Waechter};
use welt::Welt;

pub const VERSION: u32 = 26;   // B-287 R1 nur Sichtbares (Zielen + Blickrichtung), Ankunft gemessen, Schalter; 23: Kennung (nie Fremde steuern); 24: R3 Haken beim Schuss; 25: R3 Warteschlange, ein Gruppenbefehl je Takt; 26: R3 jeden Takt neu, VERLUST-Zuordnung

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
/// S3 Grabenreflex: Graben bis so viele Felder am Laufziel -> neues Ziel auf den Ringen GRABEN_RING_MIN..=MAX
const GRABEN_R: i32 = 2;
const GRABEN_RING_MIN: i32 = 3;
const GRABEN_RING_MAX: i32 = 10;
const SLOT_ICH: usize = 0x01A2_75DC;
/// Kaempfer fuer die Beschusswache: Bogen, Armbrust, Speer, Pike, Streitkolben, Schwert, Ritter, Lord, arabische Truppen
const KAEMPFER: [i16; 15] = [22, 23, 24, 25, 26, 27, 28, 55, 70, 71, 72, 73, 74, 75, 76];
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
    buch: Option<Buch>,
    /// S4a: None = noch nicht versucht; Some(None) = Anlegen fehlgeschlagen
    leitung: Option<Option<leitung::Leitung>>,
    graben_zahl: (u32, u32),
    beschuss: Option<beschuss::Wache>,
    feuer: Option<feuer::Wache>,
    letzte_zeile: i32,
    letzter_takt: Option<Instant>,
    m: Messung,
}

static ZUSTAND: Mutex<Zustand> = Mutex::new(Zustand {
    waechter: Waechter::neu(),
    welt: Welt::neu(),
    buch: None,
    leitung: None,
    graben_zahl: (0, 0),
    beschuss: None,
    feuer: None,
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

#[cfg(not(feature = "store-bridge"))]
fn schreibe(zeile: &str) {
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(PROTOKOLL) {
        let _ = writeln!(f, "{}", zeile);
    }
}

#[cfg(feature = "store-bridge")]
fn schreibe(zeile: &str) { bridge_channel::trace(zeile); }

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

/// S2: ein Gruppenbefehl je neuem Takt - erst wenn der letzte in seiner Gruppe steht (oder WARTEN_TAKTE vorbei sind).
fn haende_takt(z: &mut Zustand, tick: i32) {
    let buch = z.buch.get_or_insert_with(Buch::default);
    if let Some((g, e, t)) = &buch.warten {
        if !haende::in_gruppe(*g, e) && tick - *t < haende::WARTEN_TAKTE {
            return;
        }
        buch.warten = None;
    }
    let Some((a, einheiten)) = buch.naechster() else { return };
    if !haende::absender_aktiv() {
        schreibe(&format!("haende tick {}: VERWEIGERT - Absender-Umbau von logik.lua fehlt, Befehle gingen an den Menschen \
                           ({} Einheiten, Auftrag {:?})", tick, einheiten.len(), a));
        return;
    }
    let platz = einheiten.iter().find_map(|nr| z.welt.einheiten.iter().find(|e| e.nr == *nr).map(|e| e.besitzer as i32));
    let Some(platz) = platz else {
        schreibe(&format!("haende tick {}: keine der {} Einheiten lebt - Auftrag {:?} verworfen", tick, einheiten.len(), a));
        return;
    };
    match haende::absetzen(a, &einheiten, platz) {
        Ok((gruppe, gewaehlt)) => {
            schreibe(&format!("haende tick {}: Gruppe {}, {} von {} Einheiten von Spieler {}, Auftrag {:?} - abgesetzt",
                              tick, gruppe, gewaehlt.len(), einheiten.len(), platz, a));
            buch.abgesetzt(a, &gewaehlt, gruppe, tick);
        }
        Err(e) => schreibe(&format!("haende tick {}: Auftrag {:?} fuer {} Einheiten - FEHLER {}", tick, a, einheiten.len(), e)),
    }
}

/// S3 Grabenreflex (Daniel 22:27: "sofort erkennen, wenn jemand einen Burggraben setzt - dann soll darauf nicht gegangen
/// werden, sondern einen anderen Weg"): liegt ein neues Grabenfeld bis GRABEN_R am Laufziel einer Kern-Einheit, sucht der Kern
/// das naechste Feld ohne Graben im Umkreis GRABEN_R, das die Einheit erreichen kann, und gibt den neuen Laufauftrag.
fn grabenreflex(z: &mut Zustand, tick: i32, neu: &[(i32, i32)]) {
    let Some(buch) = z.buch.as_mut() else { return };
    let welt = &z.welt;
    let zeilen = Welt::zeilen();
    let mut neue: Vec<(i32, (i32, i32))> = Vec::new();
    for (nr, ziel) in buch.lauf_ziele() {
        let Some(&(gx, gy)) = neu.iter().find(|&&(x, y)| (x - ziel.0).abs().max((y - ziel.1).abs()) <= GRABEN_R) else {
            continue;
        };
        let Some(e) = welt.einheiten.iter().find(|e| e.nr == nr) else { continue };
        let platz = e.besitzer as i32;
        // (gemessen 23:46: eine Einheit kann auf einem Feld mit Gebiet 0 stehen - dann zaehlt das naechste begehbare daneben)
        let von = match wege::gebiet(e.x, e.y) {
            g if g > 0 => g,
            _ => wege::ring_suche((e.x, e.y), (e.x, e.y), 1, 3, |x, y| wege::gebiet(x, y) > 0)
                .map_or(0, |(x, y)| wege::gebiet(x, y)),
        };
        let ersatz = wege::ring_suche(ziel, (e.x, e.y), GRABEN_RING_MIN, GRABEN_RING_MAX, |x, y| {
            !welt.graben_nahe(x, y, GRABEN_R, &zeilen) && wege::kann_hin(platz, von, wege::gebiet(x, y))
        });
        schreibe(&format!("grabenreflex tick {}: Graben bei ({},{}) am Ziel ({},{}) von Einheit {} -> {}", tick, gx, gy,
                          ziel.0, ziel.1, nr, ersatz.map_or("KEIN freies erreichbares Feld bis 10".to_string(),
                                                            |p| format!("neues Ziel ({},{})", p.0, p.1))));
        if let Some(p) = ersatz {
            neue.push((nr, p));
        }
    }
    for (nr, p) in neue {
        buch.auftrag(nr, Auftrag { art: haende::LAUF, a: p.0, b: p.1 }, true);
    }
}

/// B-287 R1 "Schuetze zielt -> raus aus der Schusslinie" (Daniel 28.10.2026 01:28 "sie soll literally jeden Takt
/// entscheiden"). NUR SICHTBARES (FAIRNESS.md): ein feindlicher Schuetze ZIELT oder SCHIESST (Zustand 5/6 = sichtbare
/// Taetigkeit, Auge 25.10.: 4 nachladen, 5 zielen, 6 schiessen), seine BLICKRICHTUNG (+692, sichtbar am Bild; Schuetzen
/// drehen beim Zielen je Takt ein Achtel zum Ziel, AU25) zeigt auf unsere Einheit (Richtungsregel des Spiels aus Feldern,
/// AU25 calculatePreferredRelativeOrientation) und sie steht in seiner Reichweite (sicht.REICHWEITE). Dann laeuft sie SOFORT
/// R1_WEG Felder quer zur Schusslinie (die Seite, die erreichbar ist; sonst weg vom Schuetzen). Das gespeicherte Ziel des
/// Schuetzen (+836 shootTargetedUnit, +926) wird NICHT gelesen - verboten, und es haette auch Unbeteiligte in der Schusslinie
/// nicht erfasst (28.10. 01:50 gemessen: vier Armbrueste zielten auf den Lord, getroffen wurden Speertraeger in der Linie).
/// Je Einheit hoechstens alle R1_PAUSE Takte neu. Protokoll: Takt, seit dem die Lage sichtbar ist, gegen den Takt des Befehls,
/// und (r1_ankunft) der Takt, in dem das Spiel das neue Laufziel zeigt. Gibt true, wenn ein Reflex-Befehl abgesetzt wurde
/// (dann keine weitere Gruppe in diesem Takt).
const R1_WEG: i32 = 8;
const R1_PAUSE: i32 = 30;
/// Schalter zur Laufzeit (Gegenprobe ohne Neustart): Auftrag Art 17 fuer Einheit R1_SCHALTER_NR, x = 1 an / 0 aus -
/// {"kern": {"lauf": {"x": 0, "y": 0, "einheiten": [-1]}}}. Aus: der Kern meldet die Lage, reagiert aber nicht.
static R1_AN: AtomicBool = AtomicBool::new(true);
const R1_SCHALTER_NR: i32 = -1;
/// So lange wird nach dem Befehl geprueft, ob das Spiel das Laufziel der Einheit gesetzt hat.
const R1_ANKUNFT_MAX: i32 = 60;
/// Sichtbares Zielen und Schiessen (Auge 25.10., Lauf 153627).
const ZIELT: [i16; 2] = [5, 6];
/// Fernkaempfer und Reichweite in Feldern (sicht.REICHWEITE): Bogen, Armbrust, arab. Bogen, Pferdebogen 44, Schleuder 17,
/// Feuerwerfer 11.
const SCHUETZEN: [(i16, i32); 6] = [(22, 44), (23, 44), (70, 44), (74, 44), (72, 17), (76, 11)];

/// Richtung von (x, y) nach (tx, ty) wie das Spiel (AU25 calculatePreferredRelativeOrientation 0x0046C9E0, aus Feldern;
/// 0 = N (y-1) ... im Uhrzeigersinn, wie facingDirection). None = dasselbe Feld. Gleich simulator._zielrichtung.
fn zielrichtung(x: i32, y: i32, tx: i32, ty: i32) -> Option<i16> {
    let (dx, dy) = ((tx - x).abs(), (ty - y).abs());
    if dx == 0 && dy == 0 {
        return None;
    }
    Some(if 2 * dy < dx {
        if tx < x { 6 } else { 2 }
    } else if 2 * dx < dy {
        if ty < y { 0 } else { 4 }
    } else if ty < y {
        if x <= tx { 1 } else { 7 }
    } else if tx < x {
        5
    } else {
        3
    })
}

/// Abgesetzte Reflex-Befehle: Einheit -> (Laufziel, Takt des Befehls, Toleranz in Feldern - 1 einzeln, R3_GRUPPE_TOL fuer
/// Gruppen, die das Spiel um das Ziel herum aufstellt). Je Takt geprueft, bis das Spiel das Laufziel zeigt.
fn r1_offen() -> std::sync::MutexGuard<'static, HashMap<i32, ((i32, i32), i32, i32)>> {
    static O: std::sync::OnceLock<Mutex<HashMap<i32, ((i32, i32), i32, i32)>>> = std::sync::OnceLock::new();
    O.get_or_init(|| Mutex::new(HashMap::new())).lock().unwrap_or_else(|e| e.into_inner())
}

/// B-287 Beleg: Hat das Spiel den Befehl ausgefuehrt? Laufziel der EIGENEN Einheit (laufx/laufy) = Befehlsziel (+-1 Feld,
/// das Spiel setzt Einheiten bis 1 Feld daneben) - unabhaengig vom Absenden gemessen, aus dem Speicher des Spiels.
fn r1_ankunft(z: &Zustand, tick: i32) {
    let mut offen = r1_offen();
    let mut fertig = Vec::new();
    for (&nr, &(p, t0, tol)) in offen.iter() {
        match z.welt.einheiten.iter().find(|e| e.nr == nr) {
            Some(e) if (e.laufx as i32 - p.0).abs() <= tol && (e.laufy as i32 - p.1).abs() <= tol => {
                schreibe(&format!("reflex tick {}: R1 ANGEKOMMEN Einheit {} - Laufziel ({},{}) im Spiel, Befehl Takt {}, im Spiel ab \
                                   Takt {} (+{} Takte), steht bei ({},{}) Zustand {}",
                                  tick, nr, e.laufx, e.laufy, t0, tick, tick - t0, e.x, e.y, e.zustand));
                fertig.push(nr);
            }
            None => {
                schreibe(&format!("reflex tick {}: R1 Einheit {} nicht mehr da (Befehl Takt {})", tick, nr, t0));
                fertig.push(nr);
            }
            Some(e) if tick - t0 > R1_ANKUNFT_MAX => {
                schreibe(&format!("reflex tick {}: R1 NICHT ANGEKOMMEN Einheit {} - Befehl ({},{}) Takt {}, Laufziel im Spiel ({},{}) \
                                   Zustand {}", tick, nr, p.0, p.1, t0, e.laufx, e.laufy, e.zustand));
                fertig.push(nr);
            }
            _ => {}
        }
    }
    for nr in fertig {
        offen.remove(&nr);
    }
}

/// Einheit -> (Takt, seit dem die Lage sichtbar ist, Takt des letzten Befehls).
fn r1_zustand() -> std::sync::MutexGuard<'static, HashMap<i32, (i32, i32)>> {
    static R1: std::sync::OnceLock<Mutex<HashMap<i32, (i32, i32)>>> = std::sync::OnceLock::new();
    R1.get_or_init(|| Mutex::new(HashMap::new())).lock().unwrap_or_else(|e| e.into_inner())
}

fn anvisiert_reflex(z: &mut Zustand, tick: i32) -> bool {
    r1_ankunft(z, tick);
    let an = R1_AN.load(Ordering::Relaxed);
    let Some(buch) = z.buch.as_mut() else { return false };
    if buch.eigene.is_empty() {
        return false;
    }
    let welt = &z.welt;
    let mut st = r1_zustand();
    for &nr in buch.eigene.iter() {
        let Some(e) = welt.einheiten.iter().find(|e| e.nr == nr) else { continue };
        // naechster feindlicher Schuetze, der sichtbar zielt/schiesst, in Reichweite steht und in ihre Richtung blickt
        let schuetze = welt.einheiten.iter()
            .filter(|s| s.besitzer != e.besitzer && s.besitzer > 0 && ZIELT.contains(&s.zustand))
            .filter_map(|s| SCHUETZEN.iter().find(|(t, _)| *t == s.typ).map(|&(_, r)| (s, r)))
            .filter(|(s, r)| (e.x - s.x).abs().max((e.y - s.y).abs()) <= *r && zielrichtung(s.x, s.y, e.x, e.y) == Some(s.blick))
            .map(|(s, _)| s)
            .min_by_key(|s| (e.x - s.x).abs().max((e.y - s.y).abs()));
        let Some(s) = schuetze else {
            st.remove(&nr);
            continue;
        };
        let (seit, zuletzt) = *st.entry(nr).or_insert((tick, i32::MIN / 2));
        if tick - zuletzt < R1_PAUSE {
            continue;
        }
        let abstand = (e.x - s.x).abs().max((e.y - s.y).abs());
        if !an {
            schreibe(&format!("reflex tick {}: R1 AUS - Einheit {} in der Schusslinie von {} (Typ {}, Zustand {}, Blick {}, {} Felder) \
                               seit Takt {} - keine Reaktion", tick, nr, s.nr, s.typ, s.zustand, s.blick, abstand, seit));
            st.insert(nr, (seit, tick));
            continue;
        }
        // quer zur Schusslinie (beide Seiten), sonst weg vom Schuetzen
        let (dx, dy) = (e.x - s.x, e.y - s.y);
        let n = dx.abs().max(dy.abs()).max(1);
        let quer = [(-dy, dx), (dy, -dx), (dx, dy)];
        let platz = e.besitzer as i32;
        let von = match wege::gebiet(e.x, e.y) {
            g if g > 0 => g,
            _ => wege::ring_suche((e.x, e.y), (e.x, e.y), 1, 3, |x, y| wege::gebiet(x, y) > 0)
                .map_or(0, |(x, y)| wege::gebiet(x, y)),
        };
        let p = quer.iter().find_map(|&(qx, qy)| {
            let soll = (e.x + R1_WEG * qx / n, e.y + R1_WEG * qy / n);
            wege::ring_suche(soll, (e.x, e.y), 0, 3, |x, y| wege::kann_hin(platz, von, wege::gebiet(x, y)))
        });
        let Some(p) = p else {
            schreibe(&format!("reflex tick {}: R1 Einheit {} in der Schusslinie von {} - KEIN erreichbares Feld quer oder weg",
                              tick, nr, s.nr));
            st.insert(nr, (seit, tick));
            continue;
        };
        let a = Auftrag { art: haende::LAUF, a: p.0, b: p.1 };
        match haende::absetzen(a, &[nr], platz) {
            Ok((gruppe, gewaehlt)) => {
                schreibe(&format!("reflex tick {}: R1 Einheit {} bei ({},{}) in der Schusslinie von {} (Typ {}, Zustand {}, Blick {}, \
                                   {} Felder) seit Takt {} - Reaktion {} Takte - LAUF ({},{}) quer, Gruppe {}",
                                  tick, nr, e.x, e.y, s.nr, s.typ, s.zustand, s.blick, abstand, seit, tick - seit, p.0, p.1, gruppe));
                buch.abgesetzt(a, &gewaehlt, gruppe, tick);
                st.insert(nr, (seit, tick));
                r1_offen().insert(nr, (p, tick, 1));
                return true;                     // ein Befehl je Takt (die Gruppe muss stehen, bevor die naechste kommt)
            }
            Err(f) => schreibe(&format!("reflex tick {}: R1 Einheit {} - Befehl FEHLER {}", tick, nr, f)),
        }
        st.insert(nr, (seit, tick));
    }
    false
}

/// B-287 R3 Haken beim Schuss (haken.rs; Plan_Takt_Kern.md R3 nach Frage-Agent gelb). Modus zur Laufzeit ueber Auftrag Art 17
/// fuer Einheit R3_SCHALTER_NR, x = 0 nur zaehlen / 1 an / 2 Versuch (je Pfeil per UID gerade = Haken, ungerade = nur zaehlen):
/// {"kern": {"lauf": {"x": 2, "y": 0, "einheiten": [-2]}}}.
static R3_MODUS: AtomicI32 = AtomicI32::new(1);
const R3_SCHALTER_NR: i32 = -2;
const R3_WEG: i32 = 3;
/// Das Spiel fuehrt je Takt nur EINEN Gruppenbefehl aus (gemessen 02:30: 231 von 231 verlorenen Haken stammten aus Takten mit
/// mehreren Befehlen, bis 12 je Salve). Darum: Warteschlange, je Takt der dringendste Haken - zusammen mit allen Einheiten,
/// die in dieselbe Richtung ausweichen und hoechstens R3_GRUPPE_R Felder neben ihm stehen (ein Gruppenbefehl).
const R3_GRUPPE_R: i32 = 4;
const R3_GRUPPE_TOL: i32 = 3;

/// Ein ausstehender Haken: Einheit, Ausweich-Versatz (Felder), Frist (Takt, an dem der Pfeil bei ihr ist), Geschoss, Takt des
/// ersten Sehens.
#[derive(Clone, Copy)]
struct Wunsch {
    nr: i32,
    versatz: (i32, i32),
    frist: i32,
    uid: i32,
    gesehen: i32,
}

/// Ein beobachtetes Geschoss: Takt des ersten Sehens, letzte Stelle, ob schon entschieden, bedrohte Einheiten
/// (Nummer, Haken ja/nein, Resttakte bis zu ihr).
struct Flug {
    erster: i32,
    start: (i32, i32),
    letzt: (i32, i32),
    entschieden: bool,
    bedroht: Vec<(i32, bool, i32)>,
}

struct R3 {
    fluege: HashMap<i32, Flug>,
    warte: Vec<Wunsch>,
    /// im letzten Takt verschwundene Geschosse (UID, Start, letzte Stelle, als Bedrohung erkannte Einheiten mit Haken ja/nein)
    weg_letzt: Vec<(i32, (i32, i32), (i32, i32), Vec<(i32, bool)>)>,
    /// Kern-Einheit -> (Leben im letzten Takt, Takt des letzten Lebensverlusts)
    leben: HashMap<i32, (i32, i32)>,
}

fn r3_zustand() -> std::sync::MutexGuard<'static, R3> {
    static Z: std::sync::OnceLock<Mutex<R3>> = std::sync::OnceLock::new();
    Z.get_or_init(|| Mutex::new(R3 { fluege: HashMap::new(), warte: Vec::new(), weg_letzt: Vec::new(), leben: HashMap::new() })).lock().unwrap_or_else(|e| e.into_inner())
}

/// Je Takt: neue Geschosse merken; einen Takt nach dem Abschuss (Linie sichtbar) bedrohte Kern-Einheiten bestimmen und - je
/// Modus - einen Haken befehlen; verschwundene Geschosse auswerten (getroffen = die Einheit verlor in diesem Takt +-1 Leben).
/// Gibt true, wenn ein Befehl abgesetzt wurde.
fn haken_takt(z: &mut Zustand, tick: i32) -> bool {
    let Some(buch) = z.buch.as_mut() else { return false };
    if buch.eigene.is_empty() {
        return false;
    }
    let modus = R3_MODUS.load(Ordering::Relaxed);
    let welt = &z.welt;
    let mut r = r3_zustand();
    // Lebensverlust je Kern-Einheit (Kern 26: jeder Verlust wird einem Geschoss zugeordnet oder als "keins" protokolliert)
    let mut verluste: Vec<(i32, i32)> = Vec::new();
    for &nr in buch.eigene.iter() {
        if let Some(e) = welt.einheiten.iter().find(|e| e.nr == nr) {
            let alt = r.leben.get(&nr).copied();
            if let Some((l, _)) = alt {
                if e.leben < l {
                    verluste.push((nr, l - e.leben));
                }
            }
            let verlust = alt.map_or(i32::MIN / 2, |(l, t)| if e.leben < l { tick } else { t });
            r.leben.insert(nr, (e.leben, verlust));
        }
    }
    let fliegend = haken::fliegende();
    // verschwundene auswerten
    let weg: Vec<i32> = r.fluege.keys().copied().filter(|u| !fliegend.iter().any(|g| g.uid == *u)).collect();
    let mut weg_jetzt = Vec::new();
    for uid in weg {
        let f = r.fluege.remove(&uid).unwrap();
        weg_jetzt.push((uid, f.start, f.letzt, f.bedroht.iter().map(|b| (b.0, b.1)).collect::<Vec<_>>()));
        for (nr, haken, rest) in f.bedroht {
            let getroffen = r.leben.get(&nr).is_some_and(|&(_, t)| (tick - t).abs() <= 1);
            schreibe(&format!("haken tick {}: R3 ERGEBNIS Geschoss {} Einheit {} - {} (Haken {}, Resttakte {}, Flug {} Takte)",
                              tick, uid, nr, if getroffen { "GETROFFEN" } else { "verfehlt" }, if haken { "ja" } else { "nein" },
                              rest, tick - f.erster));
        }
    }
    // Messung (Frage 02:38): woher kommt jeder Verlust? Naechstes Geschoss, das in diesem oder dem letzten Takt verschwand
    for (nr, d) in verluste {
        let Some(e) = welt.einheiten.iter().find(|e| e.nr == nr) else { continue };
        let beste = weg_jetzt.iter().chain(r.weg_letzt.iter())
            .filter_map(|(uid, st, le, bed)| haken::lage(*st, *le, (e.mx, e.my)).map(|(q, v)| (*uid, q, v, bed)))
            .min_by(|a, b| a.1.abs().total_cmp(&b.1.abs()));
        match beste {
            Some((uid, q, v, bed)) => {
                let erkannt = bed.iter().find(|b| b.0 == nr);
                schreibe(&format!("haken tick {}: R3 VERLUST Einheit {} -{} bei ({},{}): Geschoss {} {:.2} Felder neben seiner Linie, {:.2} voraus beim letzten Sehen, als Bedrohung erkannt {}", tick, nr, d, e.x, e.y, uid, q / 8.0, v / 8.0,
                                  match erkannt { Some((_, true)) => "ja (Haken)", Some((_, false)) => "ja (nur gezaehlt)", None => "NEIN" }));
            }
            None => schreibe(&format!("haken tick {}: R3 VERLUST Einheit {} -{} bei ({},{}): kein Geschoss verschwunden (Nahkampf/anderes)",
                                      tick, nr, d, e.x, e.y)),
        }
    }
    r.weg_letzt = weg_jetzt;
    let mut befohlen = false;
    let mut neue: Vec<Wunsch> = Vec::new();
    for g in &fliegend {
        let f = r.fluege.entry(g.uid).or_insert(Flug { erster: tick, start: g.start, letzt: g.jetzt, entschieden: false, bedroht: Vec::new() });
        let schritt = (((g.jetzt.0 - f.letzt.0).pow(2) + (g.jetzt.1 - f.letzt.1).pow(2)) as f64).sqrt();
        f.letzt = g.jetzt;
        if g.jetzt == g.start {
            continue;
        }
        f.entschieden = true;       // Kern 26: jeden Takt neu pruefen - Einheiten koennen nach dem Abschuss in die Linie laufen
        let je_takt = if schritt > 0.0 { schritt } else { ((g.jetzt.0 - g.start.0).pow(2) as f64 + (g.jetzt.1 - g.start.1).pow(2) as f64).sqrt() };
        let eigene: Vec<i32> = buch.eigene.iter().copied().collect();
        for nr in eigene {
            let Some(e) = welt.einheiten.iter().find(|e| e.nr == nr) else { continue };
            if e.besitzer == g.besitzer || f.bedroht.iter().any(|b| b.0 == nr) {
                continue;
            }
            let Some((quer, voraus)) = haken::lage(g.start, g.jetzt, (e.mx, e.my)) else { continue };
            if !haken::bedroht(quer, voraus) {
                continue;
            }
            let rest = (voraus / je_takt.max(1.0)).round() as i32;
            let haken = modus == 1 || (modus == 2 && g.uid % 2 == 0);
            f.bedroht.push((nr, haken, rest));
            let wie = format!("Geschoss {} (Art {}, Spieler {}) Einheit {} bei ({},{}) {:.1} Felder neben der Linie, {:.1} Felder voraus, \
                               Resttakte {}", g.uid, g.art, g.besitzer, nr, e.x, e.y, quer / 8.0, voraus / 8.0, rest);
            if !haken {
                schreibe(&format!("haken tick {}: R3 {} - nur gezaehlt (Modus {})", tick, wie, modus));
                continue;
            }
            let versatz = haken::ausweich(g.start, g.jetzt, quer, R3_WEG);
            schreibe(&format!("haken tick {}: R3 {} - Haken in die Warteschlange (Versatz {:?})", tick, wie, versatz));
            let w = Wunsch { nr, versatz, frist: tick + rest, uid: g.uid, gesehen: f.erster };
            neue.push(w);
        }
    }
    for w in neue {
        match r.warte.iter_mut().find(|x| x.nr == w.nr) {
            Some(x) if x.frist <= w.frist => {}
            Some(x) => *x = w,
            None => r.warte.push(w),
        }
    }
    // je Takt EIN Befehl: der dringendste Haken, mit allen Nachbarn derselben Richtung als Gruppe
    r.warte.retain(|w| w.frist > tick && welt.einheiten.iter().any(|e| e.nr == w.nr));
    let Some(erst) = r.warte.iter().min_by_key(|w| w.frist).copied() else { return befohlen };
    let Some(e0) = welt.einheiten.iter().find(|e| e.nr == erst.nr) else { return befohlen };
    let platz = e0.besitzer as i32;
    let gruppe_nr: Vec<i32> = r.warte.iter()
        .filter(|w| w.versatz == erst.versatz)
        .filter_map(|w| welt.einheiten.iter().find(|e| e.nr == w.nr))
        .filter(|e| e.besitzer as i32 == platz && (e.x - e0.x).abs().max((e.y - e0.y).abs()) <= R3_GRUPPE_R)
        .map(|e| e.nr).collect();
    let (sx, sy) = gruppe_nr.iter().filter_map(|n| welt.einheiten.iter().find(|e| e.nr == *n))
        .fold((0, 0), |(a, b), e| (a + e.x, b + e.y));
    let k = gruppe_nr.len().max(1) as i32;
    let mitte = (sx / k, sy / k);
    let von = match wege::gebiet(e0.x, e0.y) {
        v if v > 0 => v,
        _ => wege::ring_suche((e0.x, e0.y), (e0.x, e0.y), 1, 3, |x, y| wege::gebiet(x, y) > 0)
            .map_or(0, |(x, y)| wege::gebiet(x, y)),
    };
    let ziel = (mitte.0 + erst.versatz.0, mitte.1 + erst.versatz.1);
    r.warte.retain(|w| !gruppe_nr.contains(&w.nr));
    let Some(p) = wege::ring_suche(ziel, mitte, 0, 1, |x, y| wege::kann_hin(platz, von, wege::gebiet(x, y))) else {
        schreibe(&format!("haken tick {}: R3 Gruppe {:?} - KEIN erreichbares Feld bei ({},{})", tick, gruppe_nr, ziel.0, ziel.1));
        return befohlen;
    };
    let a = Auftrag { art: haende::LAUF, a: p.0, b: p.1 };
    match haende::absetzen(a, &gruppe_nr, platz) {
        Ok((gruppe, gewaehlt)) => {
            schreibe(&format!("haken tick {}: R3 HAKEN Gruppe {:?} nach ({},{}) - dringendster Pfeil {} bei Einheit {} in {} Takten, Reaktion {} Takte nach dem ersten Sehen, noch {} in der Warteschlange, Spielgruppe {}",
                              tick, gewaehlt, p.0, p.1, erst.uid, erst.nr, erst.frist - tick, tick - erst.gesehen, r.warte.len(), gruppe));
            buch.abgesetzt(a, &gewaehlt, gruppe, tick);
            let tol = if gewaehlt.len() > 1 { R3_GRUPPE_TOL } else { 1 };
            for n in &gewaehlt {
                r1_offen().insert(*n, (p, tick, tol));
            }
            befohlen = true;
        }
        Err(x) => schreibe(&format!("haken tick {}: R3 Gruppe {:?} - Befehl FEHLER {}", tick, gruppe_nr, x)),
    }
    befohlen
}

#[cfg(test)]
mod r1_tests {
    use super::zielrichtung;

    /// Gleich simulator._zielrichtung (Python) an den Grenzfaellen; Armbrust (181,263) -> Lord (143,266) = W (6).
    #[test]
    fn richtung_wie_das_spiel() {
        assert_eq!(zielrichtung(181, 263, 143, 266), Some(6));
        assert_eq!(zielrichtung(10, 10, 10, 10), None);
        assert_eq!(zielrichtung(10, 10, 10, 0), Some(0));
        assert_eq!(zielrichtung(10, 10, 20, 0), Some(1));
        assert_eq!(zielrichtung(10, 10, 20, 20), Some(3));
        assert_eq!(zielrichtung(10, 10, 0, 20), Some(5));
        assert_eq!(zielrichtung(10, 10, 0, 0), Some(7));
        assert_eq!(zielrichtung(10, 10, 21, 15), Some(2));   // 2*5 < 11 -> waagrecht
        assert_eq!(zielrichtung(10, 10, 20, 15), Some(3));   // 2*5 == 10 -> schraeg
    }
}

/// Beschusswache: eigene Kaempfer ("ich"), die stehen und Leben verlieren - Beginn und Ende je Einheit ins Protokoll.
fn beschuss_takt(z: &mut Zustand, tick: i32) {
    let ich = unsafe { i32_bei(SLOT_ICH) };
    let welt = &z.welt;
    let w = z.beschuss.get_or_insert_with(beschuss::Wache::default);
    let eigene = welt.einheiten.iter()
        .filter(|e| e.besitzer as i32 == ich && KAEMPFER.contains(&e.typ))
        .map(|e| (e.nr, e.leben, e.x, e.y));
    for m in w.sieh(tick, eigene) {
        match m {
            beschuss::Meldung::Beginn { nr, still } => {
                if let Some(e) = welt.einheiten.iter().find(|e| e.nr == nr) {
                    // (gemessen 00:07: die meisten Faelle sind Nahkaempfe - Nahziel = der Gegner; der Aergerfall ist "steht nur")
                    let art = beschuss::art(e.nahziel, e.zielart, e.mauerfeld, (e.x, e.y), (e.mauerx, e.mauery));
                    schreibe(&format!(
                        "beschuss tick {}: {} - Einheit {} (Typ {}, Zustand {}, Zielart {}, Nahziel {}) bei ({},{}) steht seit {} Takten und verliert Leben ({}) [Fenster {} / still {}]",
                        tick, art, nr, e.typ, e.zustand, e.zielart, e.nahziel, e.x, e.y, still, e.leben,
                        beschuss::SCHADEN_FENSTER, beschuss::STILL_TAKTE));
                }
            }
            beschuss::Meldung::Ende { nr } => schreibe(&format!("beschuss tick {}: Einheit {} - Ende", tick, nr)),
        }
    }
}

/// B-150 Feuer-Auge: brennende Gebaeude (Beginn/Ende) und eigene Kaempfer im Feuer ins Protokoll (feuer.rs, L177).
fn feuer_takt(z: &mut Zustand, tick: i32) {
    let ich = unsafe { i32_bei(SLOT_ICH) };
    let welt = &z.welt;
    let w = z.feuer.get_or_insert_with(feuer::Wache::default);
    let haeuser: Vec<(i32, i32, i32, i16)> =
        welt.gebaeude.iter().map(|g| (g.nr, g.x as i32, g.y as i32, g.feuer)).collect();
    let eigene: Vec<(i32, i32, i32, i32)> = welt.einheiten.iter()
        .filter(|e| e.besitzer as i32 == ich && KAEMPFER.contains(&e.typ))
        .map(|e| (e.nr, e.leben, e.x, e.y)).collect();
    let boden = welt::Welt::bodenfeuer(&welt::Welt::zeilen());
    for m in w.sieh(&haeuser, &boden, &eigene) {
        let text = match m {
            feuer::Meldung::Brennt { nr, wert } => {
                let g = welt.gebaeude.iter().find(|g| g.nr == nr);
                g.map_or(String::new(), |g| format!("Gebaeude {} (Typ {}, Spieler {}) bei ({},{}) brennt (Wert {})",
                                                      nr, g.typ, g.besitzer, g.x, g.y, wert))
            }
            feuer::Meldung::Aus { nr } => format!("Gebaeude {} brennt nicht mehr", nr),
            feuer::Meldung::ImFeuer { nr, haus } => {
                let e = welt.einheiten.iter().find(|e| e.nr == nr);
                let wo = if haus == feuer::BODEN { "auf/neben Bodenfeuer".to_string() } else { format!("neben brennendem Gebaeude {}", haus) };
                e.map_or(String::new(), |e| format!("IM FEUER - Einheit {} (Typ {}) bei ({},{}) {}, Leben {} [r {}/{}]",
                                                      nr, e.typ, e.x, e.y, wo, e.leben, feuer::FEUER_R, feuer::BODEN_R))
            }
            feuer::Meldung::Raus { nr } => format!("Einheit {} raus aus dem Feuer", nr),
            feuer::Meldung::BodenAn { anzahl, bei } => format!("Bodenfeuer: {} Felder brennen, z. B. ({},{})", anzahl, bei.0, bei.1),
            feuer::Meldung::BodenAus => "Bodenfeuer aus".to_string(),
        };
        if !text.is_empty() {
            schreibe(&format!("feuer tick {}: {}", tick, text));
        }
    }
}

/// S4b: Auftraege aus dem Ring - Art 1 uebernehmen, 2 freigeben, 17/4/9 Auftrag (wie samurai_auftrag). Ergebnis je Eintrag.
/// B-287: UID und Besitzer einer Einheit jetzt, aus dem Speicher (ungueltige Nummer -> uid 0, Besitzer -1).
fn kennung_jetzt(nr: i32) -> haende::Kennung {
    if !(1..UNIT_PLAETZE as i32).contains(&nr) {
        return haende::Kennung { uid: 0, besitzer: -1 };
    }
    let u = UNITS + nr as usize * UNIT_GROESSE;
    unsafe { haende::Kennung { uid: i32_bei(u + 0x98), besitzer: i16_bei(u + 0x96) } }
}

/// B-287: vor jedem Befehl - Einheiten, deren Nummer das Spiel neu vergeben hat, fallen aus dem Buch (nie Fremde steuern).
fn kennung_takt(z: &mut Zustand, tick: i32) {
    let Some(buch) = z.buch.as_mut() else { return };
    for (nr, vorher, jetzt) in buch.kennung_pruefen(kennung_jetzt) {
        schreibe(&format!("kennung tick {}: Einheit {} ist nicht mehr dieselbe (UID {} -> {}, Besitzer {} -> {}) - aus dem Buch",
                          tick, nr, vorher.uid, jetzt.uid, vorher.besitzer, jetzt.besitzer));
    }
}

fn ring_abarbeiten(z: &mut Zustand, tick: i32) {
    let Some(Some(l)) = &z.leitung else { return };
    let liste = l.auftraege();
    if liste.is_empty() {
        return;
    }
    let buch = z.buch.get_or_insert_with(Buch::default);
    let mut zahl = [0usize; 4];
    for &(i, art, nr, a, b) in &liste {
        let ergebnis = match art {
            1 => {
                buch.uebernehmen(nr, kennung_jetzt(nr));
                1
            }
            2 => {
                buch.freigeben(nr);
                1
            }
            _ => {
                let untaetig = z.welt.einheiten.iter().find(|e| e.nr == nr).is_none_or(|e| matches!(e.zustand, 0 | 1));
                match buch.auftrag(nr, Auftrag { art, a, b }, untaetig) {
                    Annahme::Angenommen => 1,
                    Annahme::Doppelt => 0,
                    Annahme::NichtUebernommen => -4,
                    Annahme::UnbekannteArt => -5,
                }
            }
        };
        zahl[match ergebnis { 1 => 0, 0 => 1, -4 => 2, _ => 3 }] += 1;
        l.quittieren(i, ergebnis);
    }
    schreibe(&format!("ring tick {}: {} Eintraege - angenommen {}, doppelt {}, nicht uebergeben {}, abgelehnt {}", tick,
                      liste.len(), zahl[0], zahl[1], zahl[2], zahl[3]));
}

/// S4a: Weltbild dieses Takts in den gemeinsamen Speicher (beim ersten Mal anlegen und den Namen protokollieren).
fn leitung_schreiben(z: &mut Zustand, tick: i32) {
    if z.leitung.is_none() {
        let l = leitung::Leitung::oeffnen();
        schreibe(&format!("leitung tick {}: {}", tick, l.as_ref().map_or("FEHLER - gemeinsamer Speicher nicht angelegt".to_string(),
            |l| format!("gemeinsamer Speicher {} ({} Byte), Name in {}", l.name, leitung::GROESSE, leitung::NAME_DATEI))));
        z.leitung = Some(l);
    }
    if let Some(Some(l)) = &z.leitung {
        let ich = unsafe { i32_bei(SLOT_ICH) };
        let beschuss = z.beschuss.as_ref().map_or(0, |w| w.betroffen() as u32);
        l.schreiben(&z.welt, tick, z.waechter.epoche, ich, z.graben_zahl.0, z.graben_zahl.1, VERSION, beschuss);
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
            z.graben_zahl = (g.geplant as u32, g.ausgehoben as u32);
            z.m.welt_ns += t1.duration_since(t0).as_nanos();
            z.m.karte_ns += t1.elapsed().as_nanos();
            if !g.neu_geplant.is_empty() || !g.neu_ausgehoben.is_empty() || !g.zugeschuettet.is_empty() || g.plan_geloescht > 0 {
                let orte = |v: &Vec<usize>| v.iter().take(GRABEN_ORTE).map(|&f| ort(f)).collect::<Vec<_>>().join(" ");
                schreibe(&format!(
                    "graben tick {}: neu geplant {} [{}] | neu ausgehoben {} [{}] | zugeschuettet {} [{}] | Planung geloescht {} | jetzt geplant {} ausgehoben {}",
                    tick, g.neu_geplant.len(), orte(&g.neu_geplant), g.neu_ausgehoben.len(), orte(&g.neu_ausgehoben),
                    g.zugeschuettet.len(), orte(&g.zugeschuettet), g.plan_geloescht, g.geplant, g.ausgehoben));
            }
            if !g.neu_geplant.is_empty() || !g.neu_ausgehoben.is_empty() {
                let neu: Vec<(i32, i32)> = g.neu_geplant.iter().chain(g.neu_ausgehoben.iter())
                    .filter_map(|&f| Welt::feld_xy(f)).collect();
                grabenreflex(&mut z, tick, &neu);
            }
            beschuss_takt(&mut z, tick);
            feuer_takt(&mut z, tick);
            ring_abarbeiten(&mut z, tick);
            kennung_takt(&mut z, tick);
            if !haken_takt(&mut z, tick) && !anvisiert_reflex(&mut z, tick) {
                haende_takt(&mut z, tick);
            }
            leitung_schreiben(&mut z, tick);
        }
        Ereignis::Epoche { von, nach } => {
            schreibe(&format!("epoche {} tick {} von {} (Sprung {})", z.waechter.epoche, nach,
                              von.map_or("-".to_string(), |v| v.to_string()),
                              von.map_or("-".to_string(), |v| (nach as i64 - v as i64).to_string())));
            z.letzter_takt = Some(start);
            z.letzte_zeile = -1;
            z.welt.epoche();
            if let Some(w) = z.beschuss.as_mut() {
                w.leeren();
            }
            if let Some(w) = z.feuer.as_mut() {
                w.leeren();
            }
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
             kern_us_max {:.1} | takte {} takt_ms_mittel {:.3} | welt_us {:.1} karte_us {:.1} einheiten {} gebaeude {} max {} | kern_einheiten {} \
             auftraege_offen {}",
            tick, VERSION, w.epoche, w.neu, w.pause, w.wechsel, w.keine_partie, m.aufrufe, je_aufruf(m.kern_ns),
            m.kern_ns_max as f64 / 1000.0, m.takte, je_takt(m.takt_ns) / 1000.0, je_takt(m.welt_ns), je_takt(m.karte_ns),
            z.welt.einheiten.len(), z.welt.gebaeude.len(), z.welt.einheiten_max,
            z.buch.as_ref().map_or(0, |b| b.eigene.len()), z.buch.as_ref().map_or(0, |b| b.offen_zahl())));
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
#[cfg(not(feature = "store-bridge"))]
pub extern "C" fn samurai_welt_schreiben(tick: i32) -> i32 {
    geschuetzt("samurai_welt_schreiben", || {
        let mut z = zustand();
        z.welt.lesen();
        let ich = unsafe { i32_bei(SLOT_ICH) };
        z.welt.erreichbar_berechnen(ich);
        match z.welt.schreiben(tick, WELT_EINHEITEN, WELT_GEBAEUDE) {
            Ok(()) => z.welt.einheiten.len() as i32,
            Err(_) => -3,
        }
    })
}

#[unsafe(no_mangle)]
#[cfg(feature = "store-bridge")]
pub extern "C" fn samurai_welt_schreiben(_tick: i32) -> i32 { -4 }

/// S2: Einheit `nr` dem Kern uebergeben (ein Schreiber je Einheit). Rueckgabe 1.
#[unsafe(no_mangle)]
pub extern "C" fn samurai_uebernehmen(nr: i32) -> i32 {
    geschuetzt("samurai_uebernehmen", || {
        zustand().buch.get_or_insert_with(Buch::default).uebernehmen(nr, kennung_jetzt(nr));
        1
    })
}

/// S2: Einheit `nr` zurueckgeben - offene Auftraege fuer sie verfallen. Rueckgabe 1.
#[unsafe(no_mangle)]
pub extern "C" fn samurai_freigeben(nr: i32) -> i32 {
    geschuetzt("samurai_freigeben", || {
        zustand().buch.get_or_insert_with(Buch::default).freigeben(nr);
        1
    })
}

/// S2: Auftrag fuer eine uebergebene Einheit - art 17 Laufen nach (a, b), 4 Angriff auf Einheit a, 9 auf Gebaeude a.
/// Abgesetzt wird im naechsten neuen Takt. Rueckgabe: 1 angenommen, 0 doppelt (laeuft schon), -4 nicht uebergeben,
/// -5 unbekannte Art.
#[unsafe(no_mangle)]
pub extern "C" fn samurai_auftrag(art: i32, nr: i32, a: i32, b: i32) -> i32 {
    geschuetzt("samurai_auftrag", || {
        if art == haende::LAUF && nr == R3_SCHALTER_NR {
            R3_MODUS.store(a.clamp(0, 2), Ordering::Relaxed);
            schreibe(&format!("haken: R3 Modus {} ({})", a.clamp(0, 2), ["nur zaehlen", "an", "Versuch je Pfeil"][a.clamp(0, 2) as usize]));
            return 1;
        }
        if art == haende::LAUF && nr == R1_SCHALTER_NR {
            R1_AN.store(a != 0, Ordering::Relaxed);
            schreibe(&format!("reflex: R1 Schalter {}", if a != 0 { "AN" } else { "AUS" }));
            return 1;
        }
        let mut z = zustand();
        let untaetig = z.welt.einheiten.iter().find(|e| e.nr == nr).is_none_or(|e| matches!(e.zustand, 0 | 1));
        match z.buch.get_or_insert_with(Buch::default).auftrag(nr, Auftrag { art, a, b }, untaetig) {
            Annahme::Angenommen => 1,
            Annahme::Doppelt => 0,
            Annahme::NichtUebernommen => -4,
            Annahme::UnbekannteArt => -5,
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
