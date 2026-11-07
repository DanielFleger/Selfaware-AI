//! Taktwaechter (B-145 S0). Der Kern wird nach jedem Spieltakt gerufen, aber auch in der Pause (Takt steht) und im Menue
//! (leere Welt) - ein Aufruf ist also nicht immer ein neuer Takt (Plan_Kern.md Befund 1, init.lua Z. 783-788).
//! Der Waechter ordnet jeden Aufruf ein; nur ein neuer Takt loest Arbeit aus, ein Epochenwechsel (Laden, neue Partie)
//! leert das Gedaechtnis. Reine Logik ohne Spielspeicher - darum offline pruefbar.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ereignis {
    /// Takt = letzter + 1
    NeuerTakt,
    /// Takt steht (Pause oder zweiter Aufruf im selben Takt)
    Pause,
    /// Jeder andere Sprung: Spielstand geladen, neue Partie - oder verpasste Takte. Welche Spruenge im echten Spiel
    /// vorkommen, ist noch nicht gemessen; deshalb zaehlt jeder Sprung als Epochenwechsel und wird mit Groesse protokolliert.
    Epoche { von: Option<i32>, nach: i32 },
    /// Keine einzige Einheit auf der Karte (Menue, Auswertung)
    KeinePartie,
}

pub struct Waechter {
    letzter: Option<i32>,
    pub epoche: u32,
    pub neu: u64,
    pub pause: u64,
    pub wechsel: u64,
    pub keine_partie: u64,
}

impl Waechter {
    pub const fn neu() -> Self {
        Waechter { letzter: None, epoche: 0, neu: 0, pause: 0, wechsel: 0, keine_partie: 0 }
    }

    pub fn sieh(&mut self, tick: i32, welt_leer: bool) -> Ereignis {
        if welt_leer {
            self.keine_partie += 1;
            self.letzter = None;
            return Ereignis::KeinePartie;
        }
        let e = match self.letzter {
            Some(l) if tick == l.wrapping_add(1) => {
                self.neu += 1;
                Ereignis::NeuerTakt
            }
            Some(l) if tick == l => {
                self.pause += 1;
                Ereignis::Pause
            }
            von => {
                self.epoche += 1;
                self.wechsel += 1;
                Ereignis::Epoche { von, nach: tick }
            }
        };
        self.letzter = Some(tick);
        e
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn erster_aufruf_ist_epoche_dann_takte() {
        let mut w = Waechter::neu();
        assert_eq!(w.sieh(100, false), Ereignis::Epoche { von: None, nach: 100 });
        assert_eq!(w.sieh(101, false), Ereignis::NeuerTakt);
        assert_eq!(w.sieh(102, false), Ereignis::NeuerTakt);
        assert_eq!((w.epoche, w.neu), (1, 2));
    }

    #[test]
    fn pause_ist_kein_takt() {
        let mut w = Waechter::neu();
        w.sieh(500, false);
        assert_eq!(w.sieh(500, false), Ereignis::Pause);
        assert_eq!(w.sieh(500, false), Ereignis::Pause);
        assert_eq!(w.sieh(501, false), Ereignis::NeuerTakt);
        assert_eq!((w.pause, w.neu), (2, 1));
    }

    #[test]
    fn laden_rueckwaerts_und_vorwaerts_ist_epoche() {
        let mut w = Waechter::neu();
        w.sieh(55_966, false);
        assert_eq!(w.sieh(40_470, false), Ereignis::Epoche { von: Some(55_966), nach: 40_470 });
        assert_eq!(w.sieh(40_480, false), Ereignis::Epoche { von: Some(40_470), nach: 40_480 });
        assert_eq!(w.epoche, 3);
    }

    #[test]
    fn menue_dazwischen_gibt_neue_epoche() {
        let mut w = Waechter::neu();
        w.sieh(197_222, false);
        w.sieh(197_223, false);
        assert_eq!(w.sieh(197_223, true), Ereignis::KeinePartie);
        assert_eq!(w.sieh(197_223, true), Ereignis::KeinePartie);
        // gleiche Spielzeit nach dem Menue ist trotzdem eine neue Partie
        assert_eq!(w.sieh(197_223, false), Ereignis::Epoche { von: None, nach: 197_223 });
        assert_eq!(w.keine_partie, 2);
    }
}
