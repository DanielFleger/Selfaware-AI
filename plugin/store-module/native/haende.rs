//! Haende (B-145 S2, docs/plans/Plan_Kern.md "Bauplan S2"): der Kern befiehlt Einheiten ueber den Befehlsweg des Spiels -
//! derselbe Weg wie logik.lua (befehlAbsetzen + angriff), nur in Rust und in dem Takt, in dem der Kern es entscheidet.
//! Das Auftragsbuch (Buch) ist reine Logik und offline geprueft; laufen()/befehl_absetzen() schreiben in den Spielspeicher
//! und rufen queueCommand - nur im Spiel.

use std::collections::{BTreeMap, BTreeSet, HashMap};

pub const LAUF: i32 = 17;
pub const ANGRIFF_EINHEIT: i32 = 4;
pub const ANGRIFF_GEBAEUDE: i32 = 9;
/// So lange wartet der naechste Gruppenbefehl hoechstens, bis die Einheiten des letzten in ihrer Gruppe stehen
pub const WARTEN_TAKTE: i32 = 20;

/// Ein Auftrag: Laufen nach (a, b) oder Angriff auf Einheit/Gebaeude a
#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug, PartialOrd, Ord)]
pub struct Auftrag {
    pub art: i32,
    pub a: i32,
    pub b: i32,
}

#[derive(Debug, PartialEq, Eq)]
pub enum Annahme {
    Angenommen,
    /// derselbe Auftrag laeuft schon und die Einheit ist nicht untaetig - kein Dauer-Neubefehl
    Doppelt,
    /// die Einheit ist dem Kern nicht uebergeben - ein Schreiber je Einheit
    NichtUebernommen,
    UnbekannteArt,
}

#[derive(Default)]
pub struct Buch {
    pub eigene: BTreeSet<i32>,
    letzter: HashMap<i32, Auftrag>,
    offen: BTreeMap<Auftrag, BTreeSet<i32>>,
    /// (Gruppe, Einheiten, Takt) des zuletzt abgesetzten Gruppenbefehls
    pub warten: Option<(i32, Vec<i32>, i32)>,
}

impl Buch {
    pub fn uebernehmen(&mut self, nr: i32) {
        self.eigene.insert(nr);
    }

    pub fn freigeben(&mut self, nr: i32) {
        self.eigene.remove(&nr);
        self.letzter.remove(&nr);
        for s in self.offen.values_mut() {
            s.remove(&nr);
        }
        self.offen.retain(|_, s| !s.is_empty());
    }

    pub fn auftrag(&mut self, nr: i32, a: Auftrag, untaetig: bool) -> Annahme {
        if ![LAUF, ANGRIFF_EINHEIT, ANGRIFF_GEBAEUDE].contains(&a.art) {
            return Annahme::UnbekannteArt;
        }
        if !self.eigene.contains(&nr) {
            return Annahme::NichtUebernommen;
        }
        if self.letzter.get(&nr) == Some(&a) && !untaetig {
            return Annahme::Doppelt;
        }
        for s in self.offen.values_mut() {
            s.remove(&nr);
        }
        self.offen.retain(|_, s| !s.is_empty());
        self.offen.entry(a).or_default().insert(nr);
        Annahme::Angenommen
    }

    /// Der naechste abzusetzende Auftrag mit seinen Einheiten (aeltester Schluessel zuerst), oder None.
    pub fn naechster(&mut self) -> Option<(Auftrag, Vec<i32>)> {
        let a = *self.offen.keys().next()?;
        let einheiten = self.offen.remove(&a)?.into_iter().collect();
        Some((a, einheiten))
    }

    pub fn abgesetzt(&mut self, a: Auftrag, einheiten: &[i32], gruppe: i32, tick: i32) {
        for &nr in einheiten {
            self.letzter.insert(nr, a);
        }
        self.warten = Some((gruppe, einheiten.to_vec(), tick));
    }

    /// S3: (Einheit, Laufziel) aller zuletzt abgesetzten Laufauftraege von Einheiten, die der Kern noch fuehrt
    pub fn lauf_ziele(&self) -> Vec<(i32, (i32, i32))> {
        let mut v: Vec<_> = self.letzter.iter()
            .filter(|(nr, a)| a.art == LAUF && self.eigene.contains(*nr))
            .map(|(nr, a)| (*nr, (a.a, a.b)))
            .collect();
        v.sort();
        v
    }

    pub fn offen_zahl(&self) -> usize {
        self.offen.values().map(|s| s.len()).sum()
    }
}

// ---------------------------------------------------------------------------------------------------------------------
// Spielspeicher und Befehlsweg (nur im Spiel)

const GSS: usize = 0x0191_D768;
const PARAM: usize = GSS + 0x7A850;
const QUEUE_COMMAND: usize = 0x0048_9100;
const EINTRAG_NR: usize = GSS + 0x2D824;
const EINTRAEGE: usize = GSS + 0x3C67C;
const EINTRAG_GROESSE: usize = 0x4F8;
const ABSENDER_STELLE: usize = 0x0048_9387;
const ABSENDER_KENNUNG: u32 = 0x5341_4D00;
const SLOT_ICH: usize = 0x01A2_75DC;
const UNITS_STATE: usize = 0x0138_7F38;
const UNITS: usize = 0x0138_854C;
const UNIT_GROESSE: usize = 1168;
const AUSWAHL: usize = UNITS_STATE + 116;
const AUSWAHL_WORTE: usize = 100;
const GRUPPEN: usize = 0x0166_7F78 + 40;
const GRUPPE_GROESSE: usize = 0x334;
const GRUPPE_LETZTE: i32 = 1249;
const GEBAEUDE: usize = 0x00F9_8520;
const G_SCHRITT: usize = 0x32C;

type QueueCommand = unsafe extern "thiscall" fn(this: usize, nr: i32) -> i32;

unsafe fn lies<T: Copy>(a: usize) -> T {
    unsafe { std::ptr::read_volatile(a as *const T) }
}

unsafe fn schreib<T: Copy>(a: usize, v: T) {
    unsafe { std::ptr::write_volatile(a as *mut T, v) }
}

/// Ist der Absender-Umbau von logik.lua (B-94) eingebaut? Ohne ihn gingen Befehle an den Menschen.
pub fn absender_aktiv() -> bool {
    unsafe { lies::<u8>(ABSENDER_STELLE) == 0xE8 }
}

unsafe fn befehl_absetzen(nr: i32, werte: [i32; 6], platz: i32) -> Result<(), String> {
    unsafe {
        for (i, w) in werte.iter().enumerate() {
            schreib::<i32>(PARAM + 4 * i, *w);
        }
        let f: QueueCommand = std::mem::transmute::<usize, QueueCommand>(QUEUE_COMMAND);
        f(GSS, nr);
        let idx = lies::<i32>(EINTRAG_NR);
        if !(0..200).contains(&idx) {
            return Err(format!("Befehl {}: Eintragsnummer {} ausserhalb", nr, idx));
        }
        let e = EINTRAEGE + idx as usize * EINTRAG_GROESSE;
        let (art, zustand) = (lies::<u8>(e + 8), lies::<u8>(e + 9));
        if art != (nr & 0xFF) as u8 || zustand != 1 {
            return Err(format!("Befehl {}: Eintrag {} passt nicht (Art {}, Zustand {}) - nicht gestempelt", nr, idx, art, zustand));
        }
        schreib::<u32>(e + 4, ABSENDER_KENNUNG + platz as u32);
        Ok(())
    }
}

fn gruppe_frei() -> Option<i32> {
    // von 1 aufwaerts - logik.lua sucht von 1249 abwaerts; so greifen beide im selben Takt nie dieselbe Gruppe
    (1..=GRUPPE_LETZTE).find(|&g| unsafe { lies::<i16>(GRUPPEN + g as usize * GRUPPE_GROESSE + 24) } == 0)
}

/// Stehen alle noch lebenden Einheiten des letzten Gruppenbefehls in ihrer Gruppe (Einheit +728 tribeID)?
pub fn in_gruppe(gruppe: i32, einheiten: &[i32]) -> bool {
    einheiten.iter().all(|&nr| unsafe {
        let u = UNITS + nr as usize * UNIT_GROESSE;
        lies::<i16>(u + 0x8C) == 0 || lies::<i16>(u + 672) != 0 || lies::<i16>(u + 728) as i32 == gruppe
    })
}

/// Setzt einen Gruppenbefehl fuer `einheiten` (alle von Spieler `platz`) ab - wie angriff in logik.lua. Gibt die Gruppe zurueck.
pub fn absetzen(a: Auftrag, einheiten: &[i32], platz: i32) -> Result<(i32, Vec<i32>), String> {
    unsafe {
        let alt_ich = lies::<i32>(SLOT_ICH);
        schreib::<i32>(SLOT_ICH, platz);
        let mut alte_auswahl = [0i32; AUSWAHL_WORTE];
        for (k, w) in alte_auswahl.iter_mut().enumerate() {
            *w = lies::<i32>(AUSWAHL + 4 * k);
        }
        let ergebnis = absetzen_innen(a, einheiten, platz, &alte_auswahl);
        for (k, w) in alte_auswahl.iter().enumerate() {
            schreib::<i32>(AUSWAHL + 4 * k, *w);
        }
        schreib::<i32>(SLOT_ICH, alt_ich);
        ergebnis
    }
}

unsafe fn absetzen_innen(a: Auftrag, einheiten: &[i32], platz: i32, alte_auswahl: &[i32; AUSWAHL_WORTE])
                         -> Result<(i32, Vec<i32>), String> {
    unsafe {
        // Auswahlmarken aller eigenen Einheiten loeschen (logik.lua, gemessen 04.10.: sonst rutschen alte Einheiten in jede Gruppe)
        let max = lies::<i32>(UNITS_STATE).clamp(0, 2499);
        for i in 1..=max {
            let u = UNITS + i as usize * UNIT_GROESSE;
            if lies::<i16>(u + 0x96) as i32 == platz && lies::<i16>(u + 178) != 0 {
                schreib::<i16>(u + 178, 0);
                schreib::<i16>(u + 180, 0);
            }
        }
        for k in 0..AUSWAHL_WORTE {
            schreib::<i32>(AUSWAHL + 4 * k, 0);
        }
        let mut gewaehlt = Vec::new();
        for &nr in einheiten {
            let u = UNITS + nr as usize * UNIT_GROESSE;
            if nr > 0 && lies::<i16>(u + 0x96) as i32 == platz && lies::<i16>(u + 672) == 0 {
                let b = AUSWAHL + (nr as usize / 8);
                schreib::<u8>(b, lies::<u8>(b) | (1 << (nr % 8)));
                gewaehlt.push(nr);
            }
        }
        if gewaehlt.is_empty() {
            return Err("keine lebende Einheit des Spielers dabei".into());
        }
        let gruppe = gruppe_frei().ok_or("keine freie Gruppe")?;
        befehl_absetzen(16, [gruppe, 0, 0, 0, 0, 0], platz)?;
        // die Auswahl steckt jetzt im Eintrag (B-94) - dem Menschen seine sofort zurueck
        for (k, w) in alte_auswahl.iter().enumerate() {
            schreib::<i32>(AUSWAHL + 4 * k, *w);
        }
        match a.art {
            LAUF => befehl_absetzen(17, [gruppe, a.a, a.b, 0, 0, 0], platz)?,
            ANGRIFF_EINHEIT => {
                let uid = lies::<i32>(UNITS + a.a as usize * UNIT_GROESSE + 0x98);
                befehl_absetzen(36, [gruppe, 4, a.a, uid, 0, 0], platz)?
            }
            ANGRIFF_GEBAEUDE => {
                let uid = lies::<i32>(GEBAEUDE + a.a as usize * G_SCHRITT + 0xEC);
                befehl_absetzen(36, [gruppe, 9, a.a, uid, 0, 0], platz)?
            }
            _ => return Err(format!("unbekannte Art {}", a.art)),
        }
        Ok((gruppe, gewaehlt))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const L1: Auftrag = Auftrag { art: LAUF, a: 100, b: 200 };
    const L2: Auftrag = Auftrag { art: LAUF, a: 110, b: 200 };

    #[test]
    fn nur_uebergebene_einheiten() {
        let mut b = Buch::default();
        assert_eq!(b.auftrag(5, L1, false), Annahme::NichtUebernommen);
        b.uebernehmen(5);
        assert_eq!(b.auftrag(5, L1, false), Annahme::Angenommen);
        b.freigeben(5);
        assert_eq!(b.offen_zahl(), 0);
        assert_eq!(b.auftrag(5, L1, false), Annahme::NichtUebernommen);
    }

    #[test]
    fn kein_dauer_neubefehl_ausser_untaetig() {
        let mut b = Buch::default();
        b.uebernehmen(5);
        b.auftrag(5, L1, false);
        let (a, e) = b.naechster().unwrap();
        b.abgesetzt(a, &e, 7, 1000);
        assert_eq!(b.auftrag(5, L1, false), Annahme::Doppelt);
        assert_eq!(b.auftrag(5, L1, true), Annahme::Angenommen);   // steht untaetig -> neu befehlen ist richtig
        assert_eq!(b.auftrag(5, L2, false), Annahme::Angenommen);  // neues Ziel
    }

    #[test]
    fn gleiche_auftraege_werden_eine_gruppe() {
        let mut b = Buch::default();
        for nr in [3, 4, 5] {
            b.uebernehmen(nr);
        }
        b.auftrag(3, L1, false);
        b.auftrag(4, L1, false);
        b.auftrag(5, L2, false);
        b.auftrag(4, L2, false);   // 4 wechselt das Ziel -> nur noch in L2
        assert_eq!(b.naechster(), Some((L1, vec![3])));
        assert_eq!(b.naechster(), Some((L2, vec![4, 5])));
        assert_eq!(b.naechster(), None);
    }

    #[test]
    fn unbekannte_art_wird_abgelehnt() {
        let mut b = Buch::default();
        b.uebernehmen(5);
        assert_eq!(b.auftrag(5, Auftrag { art: 99, a: 0, b: 0 }, false), Annahme::UnbekannteArt);
    }
}
