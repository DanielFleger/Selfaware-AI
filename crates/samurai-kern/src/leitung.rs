//! Leitung (B-145 S4a, docs/plans/Plan_Kern.md "Bauplan S4a"): der Kern legt sein Weltbild in jedem neuen Takt in einen
//! benannten gemeinsamen Speicher; Python liest ihn ohne Dateikanal (selfaware.game.kern_leitung).
//! Aufbau Fassung 2: Kopf 64 Byte, Einheiten zu 32 Byte (bis 2.500), Gebaeude zu 16 Byte (bis 2.000), dann der
//! Auftragsring (S4b): Ringkopf 16 Byte (+0 Schreibzaehler von Python, +4 Lesezaehler des Kerns), 256 Eintraege zu 20 Byte
//! (Art, Einheit, a, b, Ergebnis vom Kern). Little endian. Folgezaehler im Kopf: ungerade = Weltbild wird gerade geschrieben.

use std::ffi::c_void;
use std::sync::atomic::{AtomicU32, Ordering, fence};

use crate::welt::Welt;

pub const AUFBAU: u32 = 2;
pub const KENNUNG: u32 = u32::from_le_bytes(*b"SAMK");
pub const KOPF: usize = 64;
pub const EINHEIT: usize = 32;
pub const GEBAEUDE: usize = 16;
pub const MAX_EINHEITEN: usize = 2500;
pub const MAX_GEBAEUDE: usize = 2000;
pub const RING_START: usize = KOPF + MAX_EINHEITEN * EINHEIT + MAX_GEBAEUDE * GEBAEUDE;
pub const RING_KOPF: usize = 16;
pub const RING_N: usize = 256;
pub const RING_EINTRAG: usize = 20;
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

    /// S4b: alle neuen Auftraege aus dem Ring (Nr im Ring, Art, Einheit, a, b) - hoechstens RING_N.
    pub fn auftraege(&self) -> Vec<(u32, i32, i32, i32, i32)> {
        let w = self.zaehler(0).load(Ordering::Acquire);
        let r = self.zaehler(4).load(Ordering::Acquire);
        let n = w.wrapping_sub(r).min(RING_N as u32);
        (0..n).map(|k| {
            let i = r.wrapping_add(k);
            let o = RING_START + RING_KOPF + (i as usize % RING_N) * RING_EINTRAG;
            unsafe {
                let lies = |d: usize| std::ptr::read_unaligned(self.basis.add(o + d) as *const i32);
                (i, lies(0), lies(4), lies(8), lies(12))
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

    /// Schreibt das Weltbild dieses Takts (Folgezaehler ungerade waehrend des Schreibens).
    pub fn schreiben(&self, welt: &Welt, tick: i32, epoche: u32, ich: i32, geplant: u32, ausgehoben: u32, kern: u32) {
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
            for (i, e) in welt.einheiten.iter().take(ne).enumerate() {
                let o = KOPF + i * EINHEIT;
                self.setze::<i32>(o, e.nr);
                self.setze::<i32>(o + 4, e.leben);
                for (k, w) in [e.besitzer, e.typ, e.x as i16, e.y as i16, e.zustand, e.laufx, e.laufy, e.gruppe, e.zielart,
                               e.zieleinheit, e.zielgebaeude, e.nahziel].iter().enumerate() {
                    self.setze::<i16>(o + 8 + 2 * k, *w);
                }
            }
            let gb = KOPF + MAX_EINHEITEN * EINHEIT;
            for (i, b) in welt.gebaeude.iter().take(ng).enumerate() {
                let o = gb + i * GEBAEUDE;
                self.setze::<i32>(o, b.nr);
                for (k, w) in [b.typ, b.besitzer, b.x, b.y, b.leben, 0].iter().enumerate() {
                    self.setze::<i16>(o + 4 + 2 * k, *w);
                }
            }
        }
        fence(Ordering::Release);
        f.fetch_add(1, Ordering::AcqRel);
    }
}
