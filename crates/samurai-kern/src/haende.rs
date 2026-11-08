//! Haende (B-145 S2, docs/plans/Plan_Kern.md "Bauplan S2"): der Kern befiehlt Einheiten ueber den Befehlsweg des Spiels -
//! derselbe Weg wie logik.lua (befehlAbsetzen + angriff), nur in Rust und in dem Takt, in dem der Kern es entscheidet.
//! Das Auftragsbuch (Buch) ist reine Logik und offline geprueft; laufen()/befehl_absetzen() schreiben in den Spielspeicher
//! und rufen queueCommand - nur im Spiel.

use std::collections::{BTreeMap, HashMap};

pub const LAUF: i32 = 17;
pub const ANGRIFF_EINHEIT: i32 = 4;
pub const ANGRIFF_GEBAEUDE: i32 = 9;
/// So lange wartet der naechste Gruppenbefehl hoechstens, bis die Einheiten des letzten in ihrer Gruppe stehen
pub const WARTEN_TAKTE: i32 = 20;

// P5 (B-157, docs/plans/Plan_Befehlsweg.md): je Takt ein Gruppenbefehl, also entscheidet der Vorrang, wer ihn bekommt.
pub const VORRANG_REFLEX: i32 = 1;
pub const VORRANG_FLUCHT: i32 = 2;
pub const VORRANG_ANGRIFF: i32 = 3;
pub const VORRANG_LAUFEN: i32 = 4;
pub const VORRANG_ROUTINE: i32 = 5;
/// So lange leiht sich ein Reflex ohne Frist eine Einheit, dann geht sie an ihren alten Auftrag zurueck
pub const LEIHE_TAKTE: i32 = 30;
/// So lange darf ein abgesetzter Befehl brauchen, bis er an der Einheit sichtbar ist
pub const WIRK_TAKTE: i32 = 40;

// Ergebnisse im Auftragsring (Python liest sie mit kern_leitung.Leitung.ergebnis): erst die Annahme, spaeter der Fortgang
pub const ERG_DOPPELT: i32 = 0;
pub const ERG_ANGENOMMEN: i32 = 1;
pub const ERG_ABGESETZT: i32 = 2;
pub const ERG_WIRKT: i32 = 3;
pub const ERG_GEPARKT: i32 = 4;
pub const ERG_NICHT_UEBERNOMMEN: i32 = -4;
pub const ERG_UNBEKANNT: i32 = -5;
pub const ERG_FREMD: i32 = -6;
pub const ERG_VERFALLEN: i32 = -8;
pub const ERG_FEHLER: i32 = -9;
pub const ERG_EINHEIT_WEG: i32 = -10;
pub const ERG_WIRKT_NICHT: i32 = -11;

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
    /// die Einheit gehoert einem anderen Auftraggeber
    Fremd,
    /// die Einheit ist an einen Reflex verliehen - der Auftrag gilt, sobald sie zurueck ist
    Geparkt,
    /// die Frist war schon beim Eintreffen vorbei
    Verfallen,
}

impl Annahme {
    /// Der Wert fuer das Ergebnisfeld im Auftragsring
    pub fn ergebnis(&self) -> i32 {
        match self {
            Annahme::Angenommen => ERG_ANGENOMMEN,
            Annahme::Doppelt => ERG_DOPPELT,
            Annahme::NichtUebernommen => ERG_NICHT_UEBERNOMMEN,
            Annahme::UnbekannteArt => ERG_UNBEKANNT,
            Annahme::Fremd => ERG_FREMD,
            Annahme::Geparkt => ERG_GEPARKT,
            Annahme::Verfallen => ERG_VERFALLEN,
        }
    }
}

/// Wie dringend ein Auftrag ist und von wem er kommt. vorrang 0 = nach Art (Angriff oder Laufen), frist 0 = ohne Frist,
/// auftraggeber 0 = die alte Schnittstelle ohne Besitzer.
#[derive(Clone, Copy, PartialEq, Eq, Debug, Default)]
pub struct Anspruch {
    pub vorrang: i32,
    pub frist: i32,
    pub auftraggeber: i32,
    pub ring: Option<u32>,
}

fn vorrang_von(a: Auftrag, an: Anspruch) -> i32 {
    match (an.vorrang, a.art) {
        (0, LAUF) => VORRANG_LAUFEN,
        (0, _) => VORRANG_ANGRIFF,
        (v, _) => v,
    }
}

#[derive(Default)]
struct Offen {
    /// Einheit -> (Frist, Nummer im Auftragsring)
    einheiten: BTreeMap<i32, (i32, Option<u32>)>,
    /// laufende Nummer des aeltesten Eintrags: bei gleicher Dringlichkeit geht der aeltere vor
    eingang: u64,
}

impl Offen {
    fn frist(&self) -> i32 {
        self.einheiten.values().map(|e| e.0).filter(|f| *f != 0).min().unwrap_or(i32::MAX)
    }
}

/// Ein Reflex hat die Einheit bis zum Takt `bis`; danach kommt `zurueck` wieder an die Reihe.
struct Leihe {
    bis: i32,
    zurueck: Option<(Auftrag, Anspruch)>,
}

/// Der Gruppenbefehl dieses Takts
#[derive(Debug, PartialEq, Eq)]
pub struct Abgabe {
    pub vorrang: i32,
    pub auftrag: Auftrag,
    pub einheiten: Vec<i32>,
    /// (Einheit, Nummer im Auftragsring) der Auftraege, die aus dem Ring kamen
    pub ringe: Vec<(i32, u32)>,
}

/// Was der Kern von einer Einheit sieht, um die Wirkung eines Befehls zu pruefen
#[derive(Clone, Copy)]
pub struct Blick {
    pub gruppe: i32,
    pub zieleinheit: i32,
    pub zielgebaeude: i32,
}

struct Wirkung {
    ring: u32,
    nr: i32,
    auftrag: Auftrag,
    gruppe: i32,
    takt: i32,
}

#[derive(Default)]
pub struct Buch {
    /// uebergebene Einheiten -> Auftraggeber (0 = keiner benannt)
    pub eigene: BTreeMap<i32, i32>,
    letzter: HashMap<i32, Auftrag>,
    offen: BTreeMap<(i32, Auftrag), Offen>,
    leihe: HashMap<i32, Leihe>,
    wirkung: Vec<Wirkung>,
    zaehler: u64,
    /// Ring-Nummern von Auftraegen, die verfallen oder ersetzt sind - der Aufrufer meldet sie und leert die Liste
    pub verfallen: Vec<u32>,
    /// (Gruppe, Einheiten, Takt) des zuletzt abgesetzten Gruppenbefehls
    pub warten: Option<(i32, Vec<i32>, i32)>,
}

impl Buch {
    pub fn uebernehmen(&mut self, nr: i32) {
        self.eigene.entry(nr).or_insert(0);
    }

    /// Uebergibt die Einheit an einen benannten Auftraggeber. false, wenn sie schon einem anderen gehoert.
    pub fn uebernehmen_fuer(&mut self, nr: i32, wer: i32) -> bool {
        let b = self.eigene.entry(nr).or_insert(wer);
        if *b == 0 {
            *b = wer;
        }
        wer == 0 || *b == wer
    }

    pub fn freigeben(&mut self, nr: i32) {
        self.eigene.remove(&nr);
        self.letzter.remove(&nr);
        self.wirkung.retain(|w| w.nr != nr);
        if let Some((_, an)) = self.aus_offen_nehmen(nr) {
            self.verfallen.extend(an.ring);
        }
        if let Some(l) = self.leihe.remove(&nr) {
            self.verfallen.extend(l.zurueck.and_then(|(_, an)| an.ring));
        }
    }

    /// Nimmt den offenen Auftrag der Einheit heraus (eine Einheit hat hoechstens einen).
    fn aus_offen_nehmen(&mut self, nr: i32) -> Option<(Auftrag, Anspruch)> {
        let mut raus = None;
        for ((vorrang, a), o) in self.offen.iter_mut() {
            if let Some((frist, ring)) = o.einheiten.remove(&nr) {
                raus = Some((*a, Anspruch { vorrang: *vorrang, frist, auftraggeber: 0, ring }));
                break;
            }
        }
        self.offen.retain(|_, o| !o.einheiten.is_empty());
        raus
    }

    fn einreihen(&mut self, nr: i32, a: Auftrag, an: Anspruch) {
        let schluessel = (vorrang_von(a, an), a);
        self.zaehler += 1;
        let zaehler = self.zaehler;
        let o = self.offen.entry(schluessel).or_insert_with(|| Offen { eingang: zaehler, ..Offen::default() });
        o.einheiten.insert(nr, (an.frist, an.ring));
    }

    pub fn auftrag(&mut self, nr: i32, a: Auftrag, untaetig: bool) -> Annahme {
        self.auftrag_mit(nr, a, untaetig, Anspruch::default(), i32::MIN)
    }

    /// Nimmt einen Auftrag an. Ein neuer Auftrag ersetzt den offenen derselben Einheit; ein Reflex leiht sich die Einheit,
    /// waehrend der Leihe wartet jeder andere Auftrag und kommt danach an die Reihe.
    pub fn auftrag_mit(&mut self, nr: i32, a: Auftrag, untaetig: bool, an: Anspruch, tick: i32) -> Annahme {
        if ![LAUF, ANGRIFF_EINHEIT, ANGRIFF_GEBAEUDE].contains(&a.art) {
            return Annahme::UnbekannteArt;
        }
        let Some(&besitzer) = self.eigene.get(&nr) else {
            return Annahme::NichtUebernommen;
        };
        let reflex = vorrang_von(a, an) == VORRANG_REFLEX;
        if !reflex && besitzer != 0 && an.auftraggeber != 0 && an.auftraggeber != besitzer {
            return Annahme::Fremd;
        }
        if an.frist != 0 && an.frist < tick {
            return Annahme::Verfallen;
        }
        if self.letzter.get(&nr) == Some(&a) && !untaetig {
            return Annahme::Doppelt;
        }
        if reflex {
            let bisher = self.aus_offen_nehmen(nr);
            let alt = bisher.or_else(|| self.letzter.get(&nr).map(|x| (*x, Anspruch::default())));
            let bis = if an.frist != 0 { an.frist } else { tick.saturating_add(LEIHE_TAKTE) };
            let l = self.leihe.entry(nr).or_insert(Leihe { bis, zurueck: alt });
            l.bis = l.bis.max(bis);
        } else {
            if let Some(l) = self.leihe.get_mut(&nr) {
                let alt = l.zurueck.replace((a, an));
                self.verfallen.extend(alt.and_then(|(_, x)| x.ring));
                return Annahme::Geparkt;
            }
            if let Some((_, alt)) = self.aus_offen_nehmen(nr) {
                self.verfallen.extend(alt.ring);
            }
        }
        self.einreihen(nr, a, an);
        Annahme::Angenommen
    }

    /// Leihen, deren Zeit um ist, geben ihre Einheit zurueck; abgelaufene Auftraege verfallen.
    fn aufraeumen(&mut self, tick: i32) {
        let mut fertig: Vec<i32> = self.leihe.iter().filter(|(_, l)| l.bis <= tick).map(|(nr, _)| *nr).collect();
        fertig.sort_unstable();
        for nr in fertig {
            let reflex_offen = self.offen.iter().any(|((v, _), o)| *v == VORRANG_REFLEX && o.einheiten.contains_key(&nr));
            if reflex_offen {
                continue;
            }
            if let Some((a, an)) = self.leihe.remove(&nr).and_then(|l| l.zurueck) {
                self.einreihen(nr, a, an);
            }
        }
        let verfallen = &mut self.verfallen;
        for o in self.offen.values_mut() {
            o.einheiten.retain(|_, (frist, ring)| {
                let lebt = *frist == 0 || *frist >= tick;
                if !lebt {
                    verfallen.extend(*ring);
                }
                lebt
            });
        }
        self.offen.retain(|_, o| !o.einheiten.is_empty());
    }

    /// Der Gruppenbefehl dieses Takts: zuerst der hoechste Vorrang, dann die frueheste Frist, dann der aelteste Auftrag.
    pub fn naechster_mit(&mut self, tick: i32) -> Option<Abgabe> {
        self.aufraeumen(tick);
        let schluessel = *self.offen.iter().min_by_key(|((v, _), o)| (*v, o.frist(), o.eingang))?.0;
        let o = self.offen.remove(&schluessel)?;
        Some(Abgabe {
            vorrang: schluessel.0,
            auftrag: schluessel.1,
            einheiten: o.einheiten.keys().copied().collect(),
            ringe: o.einheiten.iter().filter_map(|(nr, (_, r))| r.map(|r| (*nr, r))).collect(),
        })
    }

    /// Wie naechster_mit, fuer Aufrufer ohne Takt und ohne Ring
    pub fn naechster(&mut self) -> Option<(Auftrag, Vec<i32>)> {
        self.naechster_mit(i32::MIN).map(|x| (x.auftrag, x.einheiten))
    }

    pub fn abgesetzt(&mut self, a: Auftrag, einheiten: &[i32], gruppe: i32, tick: i32) {
        for &nr in einheiten {
            self.letzter.insert(nr, a);
        }
        self.warten = Some((gruppe, einheiten.to_vec(), tick));
    }

    /// Merkt sich, an welchen Einheiten die Wirkung des abgesetzten Befehls zu pruefen ist.
    pub fn wirkung_beobachten(&mut self, abgabe: &Abgabe, gewaehlt: &[i32], gruppe: i32, tick: i32) {
        for &(nr, ring) in &abgabe.ringe {
            if gewaehlt.contains(&nr) {
                self.wirkung.push(Wirkung { ring, nr, auftrag: abgabe.auftrag, gruppe, takt: tick });
            }
        }
    }

    /// (Ring-Nummer, Ergebnis) aller Befehle, deren Wirkung jetzt feststeht: Die Einheit steht in der neuen Gruppe und hat
    /// beim Angriff ihr Ziel eingetragen, sie lebt nicht mehr, oder nach WIRK_TAKTE ist nichts zu sehen.
    pub fn wirkung_pruefen(&mut self, tick: i32, sieh: impl Fn(i32) -> Option<Blick>) -> Vec<(u32, i32)> {
        let mut fertig = Vec::new();
        self.wirkung.retain(|w| {
            let urteil = match sieh(w.nr) {
                None => Some(ERG_EINHEIT_WEG),
                Some(b) => {
                    let ziel = match w.auftrag.art {
                        ANGRIFF_EINHEIT => b.zieleinheit == w.auftrag.a,
                        ANGRIFF_GEBAEUDE => b.zielgebaeude == w.auftrag.a,
                        _ => true,
                    };
                    if b.gruppe == w.gruppe && ziel {
                        Some(ERG_WIRKT)
                    } else if tick - w.takt > WIRK_TAKTE {
                        Some(ERG_WIRKT_NICHT)
                    } else {
                        None
                    }
                }
            };
            if let Some(e) = urteil {
                fertig.push((w.ring, e));
            }
            urteil.is_none()
        });
        fertig
    }

    /// S3: (Einheit, Laufziel) aller zuletzt abgesetzten Laufauftraege von Einheiten, die der Kern noch fuehrt
    pub fn lauf_ziele(&self) -> Vec<(i32, (i32, i32))> {
        let mut v: Vec<_> = self.letzter.iter()
            .filter(|(nr, a)| a.art == LAUF && self.eigene.contains_key(*nr))
            .map(|(nr, a)| (*nr, (a.a, a.b)))
            .collect();
        v.sort();
        v
    }

    pub fn offen_zahl(&self) -> usize {
        self.offen.values().map(|o| o.einheiten.len()).sum()
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

// thiscall gibt es nur auf 32 Bit (das Spiel); auf dem Testrechner wird nie gerufen, nur uebersetzt (B-157)
#[cfg(target_arch = "x86")]
type QueueCommand = unsafe extern "thiscall" fn(this: usize, nr: i32) -> i32;
#[cfg(not(target_arch = "x86"))]
type QueueCommand = unsafe extern "C" fn(this: usize, nr: i32) -> i32;

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

    fn an(vorrang: i32, frist: i32, auftraggeber: i32, ring: u32) -> Anspruch {
        Anspruch { vorrang, frist, auftraggeber, ring: Some(ring) }
    }

    fn buch(einheiten: &[i32]) -> Buch {
        let mut b = Buch::default();
        for &nr in einheiten {
            b.uebernehmen(nr);
        }
        b
    }

    #[test]
    fn vorrang_entscheidet_nicht_die_reihenfolge_des_eingangs() {
        let mut b = buch(&[1, 2, 3, 4]);
        b.auftrag_mit(1, L1, false, an(VORRANG_ROUTINE, 0, 0, 1), 100);
        b.auftrag_mit(2, L2, false, an(VORRANG_ANGRIFF, 0, 0, 2), 100);
        b.auftrag_mit(3, Auftrag { art: LAUF, a: 7, b: 7 }, false, an(VORRANG_FLUCHT, 0, 0, 3), 100);
        b.auftrag_mit(4, Auftrag { art: LAUF, a: 8, b: 8 }, false, an(VORRANG_REFLEX, 150, 0, 4), 100);
        let reihe: Vec<i32> = std::iter::from_fn(|| b.naechster_mit(100)).map(|x| x.vorrang).collect();
        assert_eq!(reihe, [VORRANG_REFLEX, VORRANG_FLUCHT, VORRANG_ANGRIFF, VORRANG_ROUTINE]);
    }

    #[test]
    fn in_einer_klasse_erst_die_fruehste_frist_dann_der_aelteste() {
        let mut b = buch(&[1, 2, 3]);
        let z = |x| Auftrag { art: LAUF, a: x, b: 0 };
        b.auftrag_mit(1, z(1), false, an(VORRANG_FLUCHT, 0, 0, 1), 100);
        b.auftrag_mit(2, z(2), false, an(VORRANG_FLUCHT, 300, 0, 2), 100);
        b.auftrag_mit(3, z(3), false, an(VORRANG_FLUCHT, 200, 0, 3), 100);
        let reihe: Vec<i32> = std::iter::from_fn(|| b.naechster_mit(100)).map(|x| x.auftrag.a).collect();
        assert_eq!(reihe, [3, 2, 1]);
    }

    #[test]
    fn abgelaufene_auftraege_verfallen_und_werden_gemeldet() {
        let mut b = buch(&[1, 2]);
        b.auftrag_mit(1, L1, false, an(VORRANG_FLUCHT, 110, 0, 7), 100);
        b.auftrag_mit(2, L1, false, an(VORRANG_FLUCHT, 0, 0, 8), 100);
        let x = b.naechster_mit(111).unwrap();
        assert_eq!(x.einheiten, [2]);
        assert_eq!(b.verfallen, [7]);
        assert_eq!(b.auftrag_mit(1, L2, false, an(VORRANG_FLUCHT, 105, 0, 9), 111), Annahme::Verfallen);
    }

    #[test]
    fn gebuendelt_wird_nur_innerhalb_einer_klasse() {
        let mut b = buch(&[1, 2, 3]);
        b.auftrag_mit(1, L1, false, an(VORRANG_LAUFEN, 0, 0, 1), 100);
        b.auftrag_mit(2, L1, false, an(VORRANG_LAUFEN, 0, 0, 2), 100);
        b.auftrag_mit(3, L1, false, an(VORRANG_FLUCHT, 0, 0, 3), 100);
        let x = b.naechster_mit(100).unwrap();
        assert_eq!((x.vorrang, x.einheiten), (VORRANG_FLUCHT, vec![3]));
        let x = b.naechster_mit(100).unwrap();
        assert_eq!((x.vorrang, x.einheiten, x.ringe), (VORRANG_LAUFEN, vec![1, 2], vec![(1, 1), (2, 2)]));
    }

    #[test]
    fn fremde_einheit_wird_abgewiesen_der_reflex_darf() {
        let mut b = Buch::default();
        assert!(b.uebernehmen_fuer(1, 10));
        assert!(!b.uebernehmen_fuer(1, 20));
        assert_eq!(b.auftrag_mit(1, L1, false, an(VORRANG_LAUFEN, 0, 20, 1), 100), Annahme::Fremd);
        assert_eq!(b.auftrag_mit(1, L1, false, an(VORRANG_LAUFEN, 0, 10, 2), 100), Annahme::Angenommen);
        assert_eq!(b.auftrag_mit(1, L2, false, an(VORRANG_REFLEX, 150, 20, 3), 100), Annahme::Angenommen);
    }

    #[test]
    fn leihe_gibt_die_einheit_mit_dem_alten_auftrag_zurueck() {
        let mut b = buch(&[1]);
        b.auftrag_mit(1, L1, false, an(VORRANG_LAUFEN, 0, 0, 1), 100);
        let x = b.naechster_mit(100).unwrap();
        b.abgesetzt(x.auftrag, &x.einheiten, 5, 100);
        let weg = Auftrag { art: LAUF, a: 50, b: 50 };
        assert_eq!(b.auftrag_mit(1, weg, false, an(VORRANG_REFLEX, 130, 0, 2), 110), Annahme::Angenommen);
        let x = b.naechster_mit(110).unwrap();
        assert_eq!((x.auftrag, x.vorrang), (weg, VORRANG_REFLEX));
        b.abgesetzt(x.auftrag, &x.einheiten, 6, 110);
        assert_eq!(b.naechster_mit(129), None);
        let x = b.naechster_mit(130).unwrap();
        assert_eq!((x.auftrag, x.einheiten), (L1, vec![1]));
    }

    #[test]
    fn waehrend_der_leihe_wartet_der_neueste_auftrag() {
        let mut b = buch(&[1]);
        let weg = Auftrag { art: LAUF, a: 50, b: 50 };
        b.auftrag_mit(1, weg, false, an(VORRANG_REFLEX, 130, 0, 1), 100);
        assert_eq!(b.auftrag_mit(1, L1, false, an(VORRANG_ANGRIFF, 0, 0, 2), 101), Annahme::Geparkt);
        assert_eq!(b.auftrag_mit(1, L2, false, an(VORRANG_ANGRIFF, 0, 0, 3), 102), Annahme::Geparkt);
        assert_eq!(b.verfallen, [2]);                           // der aeltere geparkte Auftrag ist erledigt
        let x = b.naechster_mit(103).unwrap();
        assert_eq!(x.auftrag, weg);
        b.abgesetzt(x.auftrag, &x.einheiten, 6, 103);
        let x = b.naechster_mit(130).unwrap();
        assert_eq!((x.auftrag, x.ringe), (L2, vec![(1, 3)]));
    }

    #[test]
    fn ein_neuer_auftrag_ersetzt_den_offenen_und_meldet_ihn() {
        let mut b = buch(&[1]);
        b.auftrag_mit(1, L1, false, an(VORRANG_LAUFEN, 0, 0, 1), 100);
        b.auftrag_mit(1, L2, false, an(VORRANG_LAUFEN, 0, 0, 2), 100);
        assert_eq!(b.verfallen, [1]);
        assert_eq!(b.offen_zahl(), 1);
    }

    #[test]
    fn freigeben_beendet_offene_und_geparkte_auftraege() {
        let mut b = buch(&[1, 2]);
        b.auftrag_mit(1, L1, false, an(VORRANG_LAUFEN, 0, 0, 1), 100);
        b.auftrag_mit(2, L2, false, an(VORRANG_REFLEX, 130, 0, 2), 100);
        b.auftrag_mit(2, L1, false, an(VORRANG_LAUFEN, 0, 0, 3), 100);
        b.freigeben(1);
        b.freigeben(2);
        assert_eq!(b.offen_zahl(), 0);
        let mut v = b.verfallen.clone();
        v.sort_unstable();
        assert_eq!(v, [1, 2, 3]);
        assert_eq!(b.naechster_mit(200), None);
    }

    fn abgabe(ringe: Vec<(i32, u32)>, a: Auftrag) -> Abgabe {
        Abgabe { vorrang: VORRANG_ANGRIFF, auftrag: a, einheiten: ringe.iter().map(|r| r.0).collect(), ringe }
    }

    #[test]
    fn wirkung_erst_wenn_gruppe_und_ziel_stimmen() {
        let mut b = Buch::default();
        let a = Auftrag { art: ANGRIFF_EINHEIT, a: 77, b: 0 };
        b.wirkung_beobachten(&abgabe(vec![(1, 11), (2, 12), (3, 13)], a), &[1, 2, 3], 9, 100);
        let sieh = |nr| match nr {
            1 => Some(Blick { gruppe: 9, zieleinheit: 77, zielgebaeude: 0 }),
            2 => Some(Blick { gruppe: 9, zieleinheit: 5, zielgebaeude: 0 }),
            _ => None,
        };
        assert_eq!(b.wirkung_pruefen(101, sieh), [(11, ERG_WIRKT), (13, ERG_EINHEIT_WEG)]);
        assert_eq!(b.wirkung_pruefen(120, sieh), []);
        assert_eq!(b.wirkung_pruefen(141, sieh), [(12, ERG_WIRKT_NICHT)]);
    }

    #[test]
    fn wirkung_nur_fuer_ausgewaehlte_einheiten() {
        let mut b = Buch::default();
        b.wirkung_beobachten(&abgabe(vec![(1, 11), (2, 12)], L1), &[2], 9, 100);
        let sieh = |_| Some(Blick { gruppe: 9, zieleinheit: 0, zielgebaeude: 0 });
        assert_eq!(b.wirkung_pruefen(101, sieh), [(12, ERG_WIRKT)]);
    }

    #[test]
    fn unbekannte_art_wird_abgelehnt() {
        let mut b = Buch::default();
        b.uebernehmen(5);
        assert_eq!(b.auftrag(5, Auftrag { art: 99, a: 0, b: 0 }, false), Annahme::UnbekannteArt);
    }
}
