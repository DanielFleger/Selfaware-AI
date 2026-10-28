//! B-287 R3 "Haken beim Schuss" (Daniel 28.10.2026 02:12; Plan_Takt_Kern.md, Abschnitt R3 nach Frage-Agent gelb 02:14).
//! Liest NUR, was ein Spieler sieht: fliegende Pfeile/Bolzen - wo sie erschienen sind, wo sie jetzt sind, wem sie gehoeren.
//! NICHT gelesen: der gespeicherte Zielpunkt des Geschosses (targetX/Y, Vorhalt) und die Zieleinheit (unitID) - FAIRNESS.md.
//! fairness_pruefen.py prueft, dass hier nur die Versaetze aus ERLAUBT_VERSATZ vorkommen.
//!
//! Geometrie in Mikroschritten (8 je Feld): Die Linie geht von der Startstelle durch die jetzige Stelle. Bedroht ist eine
//! Einheit, die vor dem Geschoss liegt und hoechstens STREIFEN neben der Linie steht (Treffer je ueberflogenem Feld, AU24).

/// Entity-Arten, die als Geschoss auf Einheiten fliegen: Pfeil, Bolzen, Pfeil-/Bolzen-Varianten (Kurve 6), Schleuder (auge.py)
pub const ARTEN: [i16; 5] = [1, 7, 24, 25, 33];
/// Halbe Streifenbreite: 1,5 Felder
pub const STREIFEN: f64 = 12.0;
/// So weit voraus wird geprueft (Pfeil-Reichweite 54 Felder, spielwerte geschoss.reichweite)
pub const VORAUS_MAX: f64 = 54.0 * 8.0;

const ES: usize = 0x0235_0300;            // DAT_EntityState; Eintrag i bei ES + i * 0xE8 (wie welt::bodenfeuer)
const GROESSE: usize = 0xE8;
const PLAETZE: usize = 3000;
/// Die einzigen Versaetze, die hier gelesen werden (auge.py ENTITY + 20): Zustand, Art, Besitzer, UID, jetzige Stelle,
/// Startstelle, am Boden.
pub const ERLAUBT_VERSATZ: [usize; 9] = [0x3C, 0x3E, 0x40, 0x44, 0x4C, 0x4E, 0x64, 0x66, 0x80];

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Geschoss {
    pub uid: i32,
    pub art: i16,
    pub besitzer: i16,
    /// Startstelle (Mikro), wo das Geschoss erschien
    pub start: (i32, i32),
    /// jetzige Stelle (Mikro)
    pub jetzt: (i32, i32),
}

unsafe fn i16_bei(a: usize) -> i16 {
    unsafe { std::ptr::read_volatile(a as *const i16) }
}

unsafe fn i32_bei(a: usize) -> i32 {
    unsafe { std::ptr::read_volatile(a as *const i32) }
}

/// Alle Geschosse, die gerade fliegen (Zustand 2, nicht am Boden) - nur im Spiel.
pub fn fliegende() -> Vec<Geschoss> {
    let mut aus = Vec::new();
    for i in 1..PLAETZE {
        let g = ES + i * GROESSE;
        unsafe {
            if i16_bei(g + 0x3C) != 2 || i16_bei(g + 0x80) != 0 {
                continue;
            }
            let art = i16_bei(g + 0x3E);
            if !ARTEN.contains(&art) {
                continue;
            }
            aus.push(Geschoss {
                uid: i32_bei(g + 0x44),
                art,
                besitzer: i16_bei(g + 0x40),
                start: (i16_bei(g + 0x64) as i32, i16_bei(g + 0x66) as i32),
                jetzt: (i16_bei(g + 0x4C) as i32, i16_bei(g + 0x4E) as i32),
            });
        }
    }
    aus
}

/// Lage eines Punkts p zur Fluglinie start -> jetzt: (quer, voraus) in Mikroschritten. quer mit Vorzeichen (links/rechts),
/// voraus = Abstand vor der jetzigen Stelle entlang der Flugrichtung. None, wenn das Geschoss noch nicht geflogen ist.
pub fn lage(start: (i32, i32), jetzt: (i32, i32), p: (i32, i32)) -> Option<(f64, f64)> {
    let (dx, dy) = ((jetzt.0 - start.0) as f64, (jetzt.1 - start.1) as f64);
    let l = (dx * dx + dy * dy).sqrt();
    if l < 1.0 {
        return None;
    }
    let (ux, uy) = (dx / l, dy / l);
    let (px, py) = ((p.0 - jetzt.0) as f64, (p.1 - jetzt.1) as f64);
    Some((px * -uy + py * ux, px * ux + py * uy))
}

/// Bedroht: vor dem Geschoss (bis VORAUS_MAX) und im Streifen.
pub fn bedroht(quer: f64, voraus: f64) -> bool {
    voraus > 0.0 && voraus <= VORAUS_MAX && quer.abs() <= STREIFEN
}

/// Ausweichrichtung in ganzen Feldern: quer zur Linie, zur Seite, auf der die Einheit schon steht (kuerzester Weg aus dem
/// Streifen); genau auf der Linie nach links. weg Felder.
pub fn ausweich(start: (i32, i32), jetzt: (i32, i32), quer: f64, weg: i32) -> (i32, i32) {
    let (dx, dy) = ((jetzt.0 - start.0) as f64, (jetzt.1 - start.1) as f64);
    let l = (dx * dx + dy * dy).sqrt().max(1.0);
    let s = if quer >= 0.0 { 1.0 } else { -1.0 };
    let (nx, ny) = (-dy / l * s, dx / l * s);
    ((nx * weg as f64).round() as i32, (ny * weg as f64).round() as i32)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lage_und_streifen() {
        // Pfeil fliegt nach Osten (x+), jetzt bei x=100
        let (s, j) = ((80, 50), (100, 50));
        let (q, v) = lage(s, j, (180, 50)).unwrap();          // 10 Felder voraus, genau auf der Linie
        assert!(q.abs() < 0.01 && (v - 80.0).abs() < 0.01);
        assert!(bedroht(q, v));
        let (q2, _) = lage(s, j, (180, 70)).unwrap();          // 2,5 Felder daneben -> nicht im Streifen
        assert!(!bedroht(q2, 80.0));
        let (_, v3) = lage(s, j, (60, 50)).unwrap();           // hinter dem Pfeil
        assert!(!bedroht(0.0, v3));
        assert_eq!(lage(s, s, (1, 1)), None);                  // noch nicht geflogen
    }

    #[test]
    fn ausweich_zur_eigenen_seite() {
        let (s, j) = ((80, 50), (100, 50));
        let (q, _) = lage(s, j, (180, 56)).unwrap();           // leicht suedlich (y+) der Linie
        let a = ausweich(s, j, q, 3);
        assert_eq!(a, (0, 3));                                 // weiter nach Sueden
        let (q, _) = lage(s, j, (180, 44)).unwrap();           // leicht noerdlich
        assert_eq!(ausweich(s, j, q, 3), (0, -3));
    }
}
