//! Beschusswache (B-145, Daniel 20.10.: "du magst es wirklich, dass die Einheiten einfach nur dastehen und sich abschiessen
//! lassen" / "es waere schoen, wenn so ein Bullshit direkt auffaellt"): ein Auge, kein Verhalten. Gemeldet wird, wenn eine
//! eigene Einheit Leben verliert und seit STILL_TAKTE auf demselben Feld steht - Beginn und Ende je Einheit. Was darauf
//! geschieht, entscheidet das Gehirn (Python/Daniel). Zustand und Zielart der Einheit stehen in der Meldung, damit spaeter
//! aus den Daten gelernt werden kann, welche Faelle "steht und kaempft" und welche "steht und wird nur beschossen" sind.

use std::collections::HashMap;

/// Stellschrauben (noch nicht gemessen, deshalb in jeder Meldung mitgeschrieben)
pub const SCHADEN_FENSTER: i32 = 100;
pub const STILL_TAKTE: i32 = 100;

#[derive(Clone, Copy)]
struct Spur {
    leben: i32,
    ort: (i32, i32),
    still_seit: i32,
    schaden_zuletzt: i32,
    gemeldet: bool,
}

#[derive(Debug, PartialEq, Eq)]
pub enum Meldung {
    /// (Einheit, Takte still, Leben vorher -> jetzt seit Beginn der Spur)
    Beginn { nr: i32, still: i32 },
    Ende { nr: i32 },
}

#[derive(Default)]
pub struct Wache {
    spuren: HashMap<i32, Spur>,
}

impl Wache {
    pub fn leeren(&mut self) {
        self.spuren.clear();
    }

    /// Eine Runde: `eigene` = (nr, leben, x, y) aller eigenen Kaempfer dieses Takts. Gibt Beginn/Ende-Meldungen zurueck.
    pub fn sieh(&mut self, tick: i32, eigene: impl Iterator<Item = (i32, i32, i32, i32)>) -> Vec<Meldung> {
        let mut aus = Vec::new();
        let mut gesehen = Vec::new();
        for (nr, leben, x, y) in eigene {
            gesehen.push(nr);
            let s = self.spuren.entry(nr).or_insert(Spur {
                leben,
                ort: (x, y),
                still_seit: tick,
                schaden_zuletzt: i32::MIN / 2,
                gemeldet: false,
            });
            if leben < s.leben {
                s.schaden_zuletzt = tick;
            }
            if (x, y) != s.ort {
                s.ort = (x, y);
                s.still_seit = tick;
            }
            s.leben = leben;
            let jetzt = tick - s.schaden_zuletzt <= SCHADEN_FENSTER && tick - s.still_seit >= STILL_TAKTE;
            if jetzt && !s.gemeldet {
                s.gemeldet = true;
                aus.push(Meldung::Beginn { nr, still: tick - s.still_seit });
            } else if !jetzt && s.gemeldet {
                s.gemeldet = false;
                aus.push(Meldung::Ende { nr });
            }
        }
        // Tote/verschwundene Einheiten: Spur weg (eine laufende Meldung endet mit ihr)
        self.spuren.retain(|nr, _| gesehen.contains(nr));
        aus
    }

    pub fn betroffen(&self) -> usize {
        self.spuren.values().filter(|s| s.gemeldet).count()
    }
}

/// Art einer Meldung. B-147 (21.10., L175): wer eine Mauer aufhackt, hat zielart 0 und kein Nahziel - er zaehlt als "HAT ZIEL",
/// wenn ein Mauerfeld eingetragen ist UND er hoechstens 2 Felder neben dieser Mauer steht (ein veralteter Eintrag nach einem
/// spaeteren Laufbefehl zaehlt so nicht).
pub fn art(nahziel: i16, zielart: i16, mauerfeld: i32, ort: (i32, i32), mauer: (i16, i16)) -> &'static str {
    let an_der_mauer = mauerfeld != 0
        && (ort.0 - mauer.0 as i32).abs().max((ort.1 - mauer.1 as i32).abs()) <= 2;
    if nahziel > 0 {
        "KAEMPFT"
    } else if zielart != 0 || an_der_mauer {
        "HAT ZIEL"
    } else {
        "STEHT NUR"
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn mauerhacker_an_der_mauer_hat_ziel_weit_weg_steht_nur() {
        assert_eq!(super::art(0, 0, 14378, (178, 120), (178, 119)), "HAT ZIEL");
        assert_eq!(super::art(0, 0, 14378, (150, 200), (178, 119)), "STEHT NUR");
        assert_eq!(super::art(0, 0, 0, (178, 120), (178, 119)), "STEHT NUR");
        assert_eq!(super::art(0, 3, 0, (1, 1), (0, 0)), "HAT ZIEL");
        assert_eq!(super::art(681, 0, 0, (1, 1), (0, 0)), "KAEMPFT");
    }

    use super::*;

    #[test]
    fn stehen_und_leben_verlieren_wird_gemeldet_und_endet() {
        let mut w = Wache::default();
        let mut leben = 1000;
        let mut beginn = None;
        for t in 0..=STILL_TAKTE + 10 {
            if t % 20 == 0 {
                leben -= 50;
            }
            let m = w.sieh(t, [(7, leben, 10, 10)].into_iter());
            if m.contains(&Meldung::Beginn { nr: 7, still: t }) {
                beginn = Some(t);
            }
        }
        assert_eq!(beginn, Some(STILL_TAKTE));
        assert_eq!(w.betroffen(), 1);
        // er laeuft los -> Ende
        let m = w.sieh(STILL_TAKTE + 11, [(7, leben, 11, 10)].into_iter());
        assert_eq!(m, vec![Meldung::Ende { nr: 7 }]);
    }

    #[test]
    fn stehen_ohne_schaden_und_laufen_mit_schaden_werden_nicht_gemeldet() {
        let mut w = Wache::default();
        for t in 0..=3 * STILL_TAKTE {
            // Einheit 1 steht, verliert nichts; Einheit 2 verliert Leben, laeuft aber jeden Takt
            let m = w.sieh(t, [(1, 500, 5, 5), (2, 1000 - t, t, 0)].into_iter());
            assert!(m.is_empty(), "Takt {}: {:?}", t, m);
        }
        assert_eq!(w.betroffen(), 0);
    }
}
