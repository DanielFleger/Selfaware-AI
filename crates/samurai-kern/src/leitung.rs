//! Leitung (B-145 S4a, docs/plans/Plan_Kern.md "Bauplan S4a"): der Kern legt sein Weltbild in jedem neuen Takt in einen
//! benannten gemeinsamen Speicher; Python liest ihn ohne Dateikanal (selfaware.game.kern_leitung).
//! Aufbau Fassung 5 (B-169): Kopf 64 Byte, Einheiten zu 108 Byte (bis 2.500), Gebaeude zu 20 Byte (bis 2.000), eigene Trupps zu 16 Byte (bis 1.250),
//! Geschosse zu 40 Byte (bis 3.000), Vorraete (9 Spieler x 25 Waren als i32, Ware wie im Spiel: 2 Holz ... 15 Gold ... 24 Ruestung), dann der Auftragsring
//! (S4b): Ringkopf 16 Byte (+0 Schreibzaehler von Python, +4 Lesezaehler des Kerns), 256 Eintraege zu 32 Byte (Art, Einheit, a, b, Ergebnis vom Kern, Vorrang,
//! Frist, Auftraggeber; P5, B-157). Little endian. Folgezaehler im Kopf: ungerade = Weltbild wird gerade geschrieben.

use std::ffi::c_void;
use std::sync::atomic::{AtomicU32, Ordering, fence};

use crate::welt::{Welt, fuer_fremde};

pub const AUFBAU: u32 = 5;
pub const KENNUNG: u32 = u32::from_le_bytes(*b"SAMK");
pub const KOPF: usize = 64;
pub const EINHEIT: usize = 108;
pub const GEBAEUDE: usize = 20;
pub const TRUPP: usize = 16;
pub const GESCHOSS: usize = 40;
pub const MAX_EINHEITEN: usize = 2500;
pub const MAX_GEBAEUDE: usize = 2000;
pub const MAX_TRUPPS: usize = 1250;
pub const MAX_GESCHOSSE: usize = 3000;
pub const GEBAEUDE_START: usize = KOPF + MAX_EINHEITEN * EINHEIT;
pub const TRUPP_START: usize = GEBAEUDE_START + MAX_GEBAEUDE * GEBAEUDE;
pub const GESCHOSS_START: usize = TRUPP_START + MAX_TRUPPS * TRUPP;
pub const VORRAT_START: usize = GESCHOSS_START + MAX_GESCHOSSE * GESCHOSS;
pub const SPIELER: usize = 9;
pub const WAREN: usize = 25;
pub const RING_START: usize = VORRAT_START + SPIELER * WAREN * 4;
// Was je Datensatz geschrieben wird, muss in den Datensatz passen (2 Byte Fuellung bei Einheit und Gebaeude)
const _: () = assert!(EINHEIT == 32 + 7 * 4 + 23 * 2 + 2 && GEBAEUDE == 4 + 7 * 2 + 2 && TRUPP == 2 * 4 + 4 * 2 && GESCHOSS == 4 + 10 * 2 + 2 * 4 + 2 * 4);
/// Spielerdaten 0x0115BDF8 + Spieler * 0x39F4, Waren ab +0x4D0 (wie logik.lua ware())
const SPIELERDATEN: usize = 0x0115_BDF8;
const SD_SCHRITT: usize = 0x39F4;
const SD_WAREN: usize = 0x4D0;
/// B-169: closestEnemyDistanceToTheLord (PlayerData.hpp)
const SD_LORD_FEIND: usize = 0x2B64;
pub const RING_KOPF: usize = 16;
pub const RING_N: usize = 256;
pub const RING_EINTRAG: usize = 32;
pub const GROESSE: usize = RING_START + RING_KOPF + RING_N * RING_EINTRAG;
// (vor dem Abarbeiten steht im Ergebnisfeld i32::MIN - das schreibt Python, siehe kern_leitung.OFFEN)
pub const NAME_DATEI: &str = "ucp/villagestudio/kern_leitung.txt";

const INVALID_HANDLE_VALUE: isize = -1;
const PAGE_READWRITE: u32 = 0x04;
const FILE_MAP_ALL_ACCESS: u32 = 0xF001F;

#[link(name = "kernel32")]
unsafe extern "system" {
    fn CreateFileMappingW(datei: isize, schutz_attr: *const c_void, schutz: u32, groesse_hoch: u32, groesse_tief: u32,
                          name: *const u16) -> isize;
    fn MapViewOfFile(abbild: isize, zugriff: u32, versatz_hoch: u32, versatz_tief: u32, bytes: usize) -> *mut c_void;
    fn GetCurrentProcessId() -> u32;
}

pub struct Leitung {
    basis: *mut u8,
    pub name: String,
}

// Der Kern laeuft im einen Spielfaden; der Zeiger wird nur dort benutzt.
unsafe impl Send for Leitung {}

impl Leitung {
    /// Legt den gemeinsamen Speicher an und schreibt seinen Namen nach NAME_DATEI. None bei einem Fehler.
    pub fn oeffnen() -> Option<Leitung> {
        // (Aufbau im Namen: eine aeltere Fassung im selben Prozess hat ihre Abbildung schon mit anderer Groesse angelegt)
        let name = format!("SamurAI_Kern_{}_A{}", unsafe { GetCurrentProcessId() }, AUFBAU);
        let breit: Vec<u16> = name.encode_utf16().chain(std::iter::once(0)).collect();
        unsafe {
            let h = CreateFileMappingW(INVALID_HANDLE_VALUE, std::ptr::null(), PAGE_READWRITE, 0, GROESSE as u32, breit.as_ptr());
            if h == 0 {
                return None;
            }
            let p = MapViewOfFile(h, FILE_MAP_ALL_ACCESS, 0, 0, GROESSE) as *mut u8;
            if p.is_null() {
                return None;
            }
            std::fs::write(NAME_DATEI, format!("{}\n{}\n", name, GROESSE)).ok()?;
            Some(Leitung { basis: p, name })
        }
    }

    fn folge(&self) -> &AtomicU32 {
        unsafe { &*(self.basis.add(8) as *const AtomicU32) }
    }

    unsafe fn setze<T: Copy>(&self, versatz: usize, wert: T) {
        unsafe { std::ptr::write_unaligned(self.basis.add(versatz) as *mut T, wert) }
    }

    fn zaehler(&self, versatz: usize) -> &AtomicU32 {
        unsafe { &*(self.basis.add(RING_START + versatz) as *const AtomicU32) }
    }

    /// S4b: alle neuen Auftraege aus dem Ring (Nr im Ring, Art, Einheit, a, b, Vorrang, Frist, Auftraggeber) - hoechstens RING_N.
    #[allow(clippy::type_complexity)]
    pub fn auftraege(&self) -> Vec<(u32, i32, i32, i32, i32, i32, i32, i32)> {
        let w = self.zaehler(0).load(Ordering::Acquire);
        let r = self.zaehler(4).load(Ordering::Acquire);
        let n = w.wrapping_sub(r).min(RING_N as u32);
        (0..n).map(|k| {
            let i = r.wrapping_add(k);
            let o = RING_START + RING_KOPF + (i as usize % RING_N) * RING_EINTRAG;
            unsafe {
                let lies = |d: usize| std::ptr::read_unaligned(self.basis.add(o + d) as *const i32);
                (i, lies(0), lies(4), lies(8), lies(12), lies(20), lies(24), lies(28))
            }
        }).collect()
    }

    /// S4b: Ergebnis in den Eintrag schreiben und den Lesezaehler dahinter setzen.
    pub fn quittieren(&self, i: u32, ergebnis: i32) {
        let o = RING_START + RING_KOPF + (i as usize % RING_N) * RING_EINTRAG;
        unsafe { self.setze::<i32>(o + 16, ergebnis) };
        fence(Ordering::Release);
        self.zaehler(4).store(i.wrapping_add(1), Ordering::Release);
    }

    /// P5: spaeteren Fortgang (abgesetzt, wirkt, verfallen ...) ins Ergebnisfeld schreiben - nur, solange Python den Platz
    /// im Ring nicht neu belegt hat.
    pub fn ergebnis_melden(&self, i: u32, ergebnis: i32) {
        let w = self.zaehler(0).load(Ordering::Acquire);
        if w.wrapping_sub(i) <= RING_N as u32 {
            let o = RING_START + RING_KOPF + (i as usize % RING_N) * RING_EINTRAG;
            unsafe { self.setze::<i32>(o + 16, ergebnis) };
        }
    }

    /// Schreibt das Weltbild dieses Takts (Folgezaehler ungerade waehrend des Schreibens).
    #[allow(clippy::too_many_arguments)]
    pub fn schreiben(&self, welt: &Welt, tick: i32, epoche: u32, ich: i32, geplant: u32, ausgehoben: u32, kern: u32,
                     beschuss: u32) {
        let f = self.folge();
        f.fetch_add(1, Ordering::AcqRel);
        fence(Ordering::Release);
        unsafe {
            self.setze::<u32>(0, KENNUNG);
            self.setze::<u32>(4, AUFBAU);
            self.setze::<i32>(12, tick);
            self.setze::<u32>(16, epoche);
            self.setze::<i32>(20, ich);
            let ne = welt.einheiten.len().min(MAX_EINHEITEN);
            let ng = welt.gebaeude.len().min(MAX_GEBAEUDE);
            self.setze::<u32>(24, ne as u32);
            self.setze::<u32>(28, ng as u32);
            self.setze::<u32>(32, geplant);
            self.setze::<u32>(36, ausgehoben);
            self.setze::<u32>(40, kern);
            self.setze::<u32>(44, beschuss);   // Zahl eigener Kaempfer unter Beschuss (Beschusswache)
            let lord = if (1..SPIELER as i32).contains(&ich) {
                std::ptr::read_volatile((SPIELERDATEN + ich as usize * SD_SCHRITT + SD_LORD_FEIND) as *const i32)
            } else {
                0
            };
            self.setze::<i32>(48, lord);       // nur der eigene Lord (Sichtschranke)
            for (i, roh) in welt.einheiten.iter().take(ne).enumerate() {
                let o = KOPF + i * EINHEIT;
                let sicht = if roh.besitzer as i32 == ich { *roh } else { fuer_fremde(roh) };
                let e = &sicht;
                self.setze::<i32>(o, e.nr);
                self.setze::<i32>(o + 4, e.leben);
                for (k, w) in [e.besitzer, e.typ, e.x as i16, e.y as i16, e.zustand, e.laufx, e.laufy, e.gruppe, e.zielart,
                               e.zieleinheit, e.zielgebaeude, e.nahziel].iter().enumerate() {
                    self.setze::<i16>(o + 8 + 2 * k, *w);
                }
                for (k, w) in [e.bild, e.bildzyklus, e.schussziel_uid, e.naechstesfeld, e.kletterstand, e.zieluid, e.mauerfeld].iter().enumerate() {
                    self.setze::<i32>(o + 32 + 4 * k, *w);
                }
                for (k, w) in [e.feinx, e.feiny, e.gelaendehoehe, e.gebaeudehoehe, e.schussx, e.schussy, e.schussz, e.wegindex, e.weglaenge,
                               e.feindabstand, e.planx, e.plany, e.ziel, e.zielx, e.ziely, e.schusseinheit, e.tempo, e.wegbedarf,
                               e.teilzustand, e.nahangreifer, e.mauerx, e.mauery, e.getoetet].iter().enumerate() {
                    self.setze::<i16>(o + 60 + 2 * k, *w);
                }
            }
            for sp in 0..SPIELER {
                for w in 0..WAREN {
                    let v = std::ptr::read_volatile((SPIELERDATEN + sp * SD_SCHRITT + SD_WAREN + w * 4) as *const i32);
                    self.setze::<i32>(VORRAT_START + (sp * WAREN + w) * 4, v);
                }
            }
            for (i, b) in welt.gebaeude.iter().take(ng).enumerate() {
                let o = GEBAEUDE_START + i * GEBAEUDE;
                self.setze::<i32>(o, b.nr);
                for (k, w) in [b.typ, b.besitzer, b.x, b.y, b.leben, b.feuer, b.tor].iter().enumerate() {   // (B-150: frei -> Feuerwert)
                    self.setze::<i16>(o + 4 + 2 * k, *w);
                }
            }
            let mut nt = 0;
            for t in welt.trupps.iter().filter(|t| t.besitzer == ich).take(MAX_TRUPPS) {   // fremde Trupps: FAIRNESS F10
                let o = TRUPP_START + nt * TRUPP;
                self.setze::<i32>(o, t.nr);
                self.setze::<i32>(o + 4, t.zielgebaeude_uid);
                for (k, w) in [t.zustand, t.zielx, t.ziely, t.zielgebaeude].iter().enumerate() {
                    self.setze::<i16>(o + 8 + 2 * k, *w);
                }
                nt += 1;
            }
            self.setze::<u32>(52, nt as u32);
            let nq = welt.geschosse.len().min(MAX_GESCHOSSE);
            self.setze::<u32>(56, nq as u32);
            for (i, q) in welt.geschosse.iter().take(nq).enumerate() {
                let o = GESCHOSS_START + i * GESCHOSS;
                self.setze::<i32>(o, q.nr);
                for (k, w) in [q.typ, q.zustand, q.besitzer, q.feinx, q.feiny, q.hoehe, q.x, q.y, q.weg, q.feuer].iter().enumerate() {
                    self.setze::<i16>(o + 4 + 2 * k, *w);
                }
                self.setze::<i32>(o + 24, q.feld);
                self.setze::<i32>(o + 28, q.richtung);
                self.setze::<f32>(o + 32, q.vcos);
                self.setze::<f32>(o + 36, q.vsin);
            }
        }
        fence(Ordering::Release);
        f.fetch_add(1, Ordering::AcqRel);
    }
}
