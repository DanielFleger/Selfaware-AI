//! Feuer-Auge (B-150, Daniel 21.10.2026 19:20 "ja bau das Feuer-Auge in den Kern"; Anlass 18:29: eigene Sklaven zuendeten eine
//! Mine an und das Heer lief durch das Feuer). Gemessen im Sandkasten (L177): fireDuration (Gebaeude +0x14+702) steigt ab dem
//! Anzuenden um ~1 je Takt und faellt erst auf 0, wenn das Gebaeude weg ist; eigene Einheiten 1-3 Felder daneben verlieren
//! ~7.500 Leben je 100 Takte. Ein Auge, kein Verhalten: gemeldet werden brennende Gebaeude (Beginn/Ende) und eigene Kaempfer,
//! die bis FEUER_R Felder neben einem brennenden Gebaeude stehen UND Leben verlieren (Beginn/Ende je Einheit).

use std::collections::{HashMap, HashSet};

/// Stellschraube (aus L177: Schaden in 1, 2 und 3 Feldern gemessen; 5 und 10 Felder ohne Gebaeudefeuer-Schaden)
pub const FEUER_R: i32 = 3;
/// Bodenfeuer schadet nur Einheiten AUF dem Feld (processFireDamageToUnitsAtTile 0x004015D0 nimmt die UnitLayer dieses
/// Feldes); 1 Feld Rand fuer die Takte zwischen zwei Proben
pub const BODEN_R: i32 = 1;
/// "haus" einer ImFeuer-Meldung, wenn es ein Bodenfeuer war
pub const BODEN: i32 = -1;

#[derive(Debug, PartialEq, Eq)]
pub enum Meldung {
    Brennt { nr: i32, wert: i16 },
    Aus { nr: i32 },
    /// eigene Einheit nr verliert Leben neben dem brennenden Gebaeude haus
    ImFeuer { nr: i32, haus: i32 },
    Raus { nr: i32 },
    /// Bodenfeuer: Zahl der brennenden Felder springt von 0 auf n (bei = eines davon) bzw. zurueck auf 0
    BodenAn { anzahl: usize, bei: (i32, i32) },
    BodenAus,
}

#[derive(Default)]
pub struct Wache {
    brennt: HashSet<i32>,
    leben: HashMap<i32, i32>,
    im_feuer: HashSet<i32>,
    boden: usize,
}

fn schach(a: (i32, i32), b: (i32, i32)) -> i32 {
    (a.0 - b.0).abs().max((a.1 - b.1).abs())
}

impl Wache {
    pub fn leeren(&mut self) {
        *self = Wache::default();
    }

    /// Ein Takt: haeuser = (nr, x, y, fireDuration) aller Gebaeude, eigene = (nr, leben, x, y) der eigenen Kaempfer.
    pub fn sieh(&mut self, haeuser: &[(i32, i32, i32, i16)], boden: &[(i32, i32)], eigene: &[(i32, i32, i32, i32)]) -> Vec<Meldung> {
        let mut aus = Vec::new();
        match (self.boden, boden.len()) {
            (0, n) if n > 0 => aus.push(Meldung::BodenAn { anzahl: n, bei: boden[0] }),
            (a, 0) if a > 0 => aus.push(Meldung::BodenAus),
            _ => {}
        }
        self.boden = boden.len();
        let jetzt: HashSet<i32> = haeuser.iter().filter(|h| h.3 > 0).map(|h| h.0).collect();
        for h in haeuser.iter().filter(|h| h.3 > 0 && !self.brennt.contains(&h.0)) {
            aus.push(Meldung::Brennt { nr: h.0, wert: h.3 });
        }
        let mut weg: Vec<i32> = self.brennt.difference(&jetzt).copied().collect();
        weg.sort_unstable();
        aus.extend(weg.into_iter().map(|nr| Meldung::Aus { nr }));
        self.brennt = jetzt;
        let feuer: Vec<(i32, (i32, i32))> = haeuser.iter().filter(|h| h.3 > 0).map(|h| (h.0, (h.1, h.2))).collect();
        let mut gesehen = HashMap::new();
        for &(nr, leben, x, y) in eigene {
            let verliert = self.leben.get(&nr).is_some_and(|&alt| leben < alt);
            let nah = feuer.iter().filter(|f| schach((x, y), f.1) <= FEUER_R).min_by_key(|f| schach((x, y), f.1)).map(|f| f.0)
                .or_else(|| boden.iter().any(|b| schach((x, y), *b) <= BODEN_R).then_some(BODEN));
            match (nah, self.im_feuer.contains(&nr)) {
                (Some(haus), false) if verliert => {
                    self.im_feuer.insert(nr);
                    aus.push(Meldung::ImFeuer { nr, haus });
                }
                (None, true) => {
                    self.im_feuer.remove(&nr);
                    aus.push(Meldung::Raus { nr });
                }
                _ => {}
            }
            gesehen.insert(nr, leben);
        }
        // tote/verschwundene Einheiten: Spur weg (Nummern werden neu vergeben, L177)
        self.im_feuer.retain(|nr| gesehen.contains_key(nr));
        self.leben = gesehen;
        aus
    }

    pub fn brennende(&self) -> usize {
        self.brennt.len()
    }

    pub fn im_feuer(&self) -> usize {
        self.im_feuer.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn brand_beginn_und_ende_je_gebaeude() {
        let mut w = Wache::default();
        assert!(w.sieh(&[(19, 201, 99, 0)], &[], &[]).is_empty());
        assert_eq!(w.sieh(&[(19, 201, 99, 46)], &[], &[]), vec![Meldung::Brennt { nr: 19, wert: 46 }]);
        assert!(w.sieh(&[(19, 201, 99, 102)], &[], &[]).is_empty());
        assert_eq!(w.sieh(&[(19, 201, 99, 0)], &[], &[]), vec![Meldung::Aus { nr: 19 }]);
    }

    #[test]
    fn im_feuer_nur_nah_und_mit_lebensverlust() {
        // wie Sandkasten L177: Plantage 19 bei (201,99) brennt; Streitkolben in 1 Feld (verliert), in 2 Feldern (verliert nicht),
        // in 10 Feldern (verliert - aus anderem Grund, darf NICHT "im Feuer" sein)
        let mut w = Wache::default();
        let h = [(19, 201, 99, 50)];
        w.sieh(&h, &[], &[(1, 25000, 202, 100), (2, 25000, 202, 101), (10, 25000, 202, 109)]);
        let m = w.sieh(&h, &[], &[(1, 18175, 202, 100), (2, 25000, 202, 101), (10, 20000, 202, 109)]);
        assert_eq!(m, vec![Meldung::ImFeuer { nr: 1, haus: 19 }]);
        assert_eq!(w.im_feuer(), 1);
        // er laeuft weg -> Raus
        let m = w.sieh(&h, &[], &[(1, 18000, 210, 100)]);
        assert_eq!(m, vec![Meldung::Raus { nr: 1 }]);
    }

    #[test]
    fn bodenfeuer_nur_auf_dem_feld_oder_daneben() {
        // Bodenfeuer bei (202,102) (L177: dort verlor der Streitkolben in 3 Feldern weiter Leben, als das Gebaeude aus war)
        let mut w = Wache::default();
        let boden = [(202, 102)];
        assert_eq!(w.sieh(&[], &boden, &[(3, 25000, 202, 102), (5, 25000, 202, 105)]),
                   vec![Meldung::BodenAn { anzahl: 1, bei: (202, 102) }]);
        let m = w.sieh(&[], &boden, &[(3, 22075, 202, 102), (5, 24000, 202, 105)]);
        assert_eq!(m, vec![Meldung::ImFeuer { nr: 3, haus: BODEN }]);
        assert_eq!(w.sieh(&[], &[], &[(3, 22000, 202, 102)]), vec![Meldung::BodenAus, Meldung::Raus { nr: 3 }]);
    }
}
