//! Augen (B-145 S1, Plan_Kern.md): Einheiten, Gebaeude und Kartenschicht direkt aus dem Spielspeicher, in jedem Takt.
//! Felder und Filter genau wie das Lagebild von logik.lua ({"lagebild": true}, logik_stand_20261020.lua Z. ~2027), damit
//! beide im selben Takt verglichen werden koennen (python -m selfaware.tools.experiments.kern_vergleich). Die Spalte
//! "erreichbar" braucht den Wegfinder des Spiels - das ist S3; bis dahin steht dort -9 (nicht berechnet).

use std::fs::File;
use std::io::{BufWriter, Write};

/// DAT_UnitsState 0x01387F38: +0 maxUnitCount; Einheiten ab 0x0138854C, je 1.168 Byte, 2.500 Plaetze (Spielkarte 2)
const UNITS_STATE: usize = 0x0138_7F38;
const UNITS: usize = 0x0138_854C;
const UNIT_GROESSE: usize = 1168;
const UNIT_LETZTER: i32 = 2499;
/// DAT_BuildingsState 0x00F98520: +8 Zahl der Plaetze; Datensatz je 0x32C Byte, Felder wie logik.lua (mit 0x14-Versatz)
const GEBAEUDE: usize = 0x00F9_8520;
const G_SCHRITT: usize = 0x32C;
/// translationMatrix: je Kartenzeile 12 Byte - +0 erstes x, +4 Nummer des ersten Feldes, +8 addXgetTile (gemessen 20.10.:
/// Zeile y < 200 hat 2y+2 Felder, ab 200 entsprechend weniger; zusammen 80.400)
const ZEILEN: usize = 0x0233_72F8;
const KARTE_ZEILEN: usize = 400;
/// LogicLayer (TileMapState +0x165160): int je Feld, 80.400 Felder
const LOGIK: usize = 0x01BF_8368;
pub const FELDER: usize = 80_400;
/// Graben (L126): geplant = 0x4000 (L_MOAT_DUG_OR_PLANNED), ausgehoben = 0x40000000 (L_MOAT)
pub const GRABEN_GEPLANT: u32 = 0x4000;
pub const GRABEN: u32 = 0x4000_0000;

unsafe fn i16_bei(a: usize) -> i16 {
    unsafe { std::ptr::read_volatile(a as *const i16) }
}

unsafe fn i32_bei(a: usize) -> i32 {
    unsafe { std::ptr::read_volatile(a as *const i32) }
}

#[derive(Clone, Copy, Default)]
pub struct Einheit {
    pub nr: i32,
    pub besitzer: i16,
    pub typ: i16,
    pub x: i32,
    pub y: i32,
    pub leben: i32,
    pub zustand: i16,
    pub zielart: i16,
    pub zieleinheit: i16,
    pub zieluid: i32,
    pub zielgebaeude: i16,
    pub ziel: i16,
    pub zielx: i16,
    pub ziely: i16,
    pub laufx: i16,
    pub laufy: i16,
    pub auswahlvon: i16,
    pub auswahlmarke: i16,
    pub gruppe: i16,
    pub gruppenuid: i32,
    pub ladung: i16,
    pub arbeitsplatz: i16,
    pub nahziel: i16,
    pub nahangreifer: i16,
}

#[derive(Clone, Copy, Default)]
pub struct Gebaeude {
    pub nr: i32,
    pub besitzer: i16,
    pub typ: i16,
    pub x: i16,
    pub y: i16,
    pub leben: i16,
    pub uid: i32,
    pub vorrat: i32,
    pub grenze: i32,
    pub verbund: i16,
    pub ware: i32,
}

/// Was die Grabenwache in einem Takt gesehen hat
#[derive(Default, Debug, PartialEq, Eq)]
pub struct GrabenAenderung {
    pub neu_geplant: Vec<usize>,
    pub neu_ausgehoben: Vec<usize>,
    /// ausgehobener Graben ist weg (zugeschuettet) - dort oeffnet sich ein Weg
    pub zugeschuettet: Vec<usize>,
    /// Planung ohne Aushub verschwunden (geloescht)
    pub plan_geloescht: usize,
    pub weg: usize,
    pub geplant: usize,
    pub ausgehoben: usize,
}

pub struct Welt {
    pub einheiten: Vec<Einheit>,
    pub gebaeude: Vec<Gebaeude>,
    pub einheiten_max: i32,
    /// je Feld: Bit 0 geplant, Bit 1 ausgehoben (Stand des letzten Takts); leer = noch keine Aufnahme in dieser Epoche
    graben: Vec<u8>,
}

impl Welt {
    pub const fn neu() -> Self {
        Welt { einheiten: Vec::new(), gebaeude: Vec::new(), einheiten_max: 0, graben: Vec::new() }
    }

    /// Neue Epoche (Laden, neue Partie): die Grabenwache nimmt im naechsten Takt neu auf, ohne Alarm.
    pub fn epoche(&mut self) {
        self.graben.clear();
    }

    pub fn lesen(&mut self) {
        self.einheiten.clear();
        self.gebaeude.clear();
        unsafe {
            self.einheiten_max = i32_bei(UNITS_STATE);
            for i in 1..=self.einheiten_max.clamp(0, UNIT_LETZTER) {
                let u = UNITS + i as usize * UNIT_GROESSE;
                let typ = i16_bei(u + 0x8E);
                if typ <= 0 || i16_bei(u + 0x8C) == 0 || i16_bei(u + 672) != 0 {
                    continue;
                }
                self.einheiten.push(Einheit {
                    nr: i,
                    besitzer: i16_bei(u + 0x96),
                    typ,
                    x: (i16_bei(u + 0xB6) as i32).div_euclid(8),
                    y: (i16_bei(u + 0xB8) as i32).div_euclid(8),
                    leben: i32_bei(u + 968),
                    zustand: i16_bei(u + 704),
                    zielart: i16_bei(u + 924),
                    zieleinheit: i16_bei(u + 926),
                    zieluid: i32_bei(u + 928),
                    zielgebaeude: i16_bei(u + 822),
                    ziel: i16_bei(u + 782),
                    zielx: i16_bei(u + 784),
                    ziely: i16_bei(u + 786),
                    laufx: i16_bei(u + 0xC8),
                    laufy: i16_bei(u + 0xCA),
                    auswahlvon: i16_bei(u + 178),
                    auswahlmarke: i16_bei(u + 180),
                    gruppe: i16_bei(u + 728),
                    gruppenuid: i32_bei(u + 740),
                    ladung: i16_bei(u + 904),
                    arbeitsplatz: i16_bei(u + 824),
                    nahziel: i16_bei(u + 830),
                    nahangreifer: i16_bei(u + 942),
                });
            }
            let anz = i32_bei(GEBAEUDE + 8);
            if (2..=4000).contains(&anz) {
                for i in 1..anz {
                    let b = GEBAEUDE + i as usize * G_SCHRITT;
                    if i16_bei(b + 0xE4) == 0 {
                        continue;
                    }
                    self.gebaeude.push(Gebaeude {
                        nr: i,
                        besitzer: i16_bei(b + 0xEA),
                        typ: i16_bei(b + 0xE6),
                        x: i16_bei(b + 0x102),
                        y: i16_bei(b + 0x104),
                        leben: i16_bei(b + 0x120),
                        uid: i32_bei(b + 0xEC),
                        vorrat: i32_bei(b + 0x198),
                        grenze: i32_bei(b + 0x19C),
                        verbund: i16_bei(b + 0x1A6),
                        ware: i32_bei(b + 0x1A0),
                    });
                }
            }
        }
    }

    /// Grabenwache: alle 80.400 Felder; liefert, was seit dem letzten Takt neu geplant/ausgehoben wurde.
    pub fn graben_lesen(&mut self) -> GrabenAenderung {
        let jetzt: Vec<u8> = (0..FELDER)
            .map(|i| graben_bits(unsafe { i32_bei(LOGIK + 4 * i) } as u32))
            .collect();
        let a = graben_vergleich(&self.graben, &jetzt);
        self.graben = jetzt;
        a
    }

    /// Feldnummer -> (x, y) ueber die Zeilentabelle des Spiels
    pub fn feld_xy(feld: usize) -> Option<(i32, i32)> {
        let zeilen: Vec<(i32, i32)> = (0..KARTE_ZEILEN)
            .map(|y| unsafe { (i32_bei(ZEILEN + y * 12), i32_bei(ZEILEN + y * 12 + 4)) })
            .collect();
        feld_xy_aus(&zeilen, feld)
    }

    /// Schreibt Einheiten und Gebaeude im Format von abzug/lagebild.txt und abzug/gebaeude.txt.
    pub fn schreiben(&self, tick: i32, pfad_einheiten: &str, pfad_gebaeude: &str) -> std::io::Result<()> {
        let mut f = BufWriter::new(File::create(pfad_einheiten)?);
        writeln!(f, "tick {}", tick)?;
        writeln!(f, "nr besitzer typ x y leben zustand zielart zieleinheit zieluid zielgebaeude ziel zielx ziely laufx laufy \
                     auswahlvon auswahlmarke gruppe gruppenuid ladung arbeitsplatz erreichbar nahziel nahangreifer")?;
        for e in &self.einheiten {
            writeln!(f, "{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} -9 {} {}",
                     e.nr, e.besitzer, e.typ, e.x, e.y, e.leben, e.zustand, e.zielart, e.zieleinheit, e.zieluid,
                     e.zielgebaeude, e.ziel, e.zielx, e.ziely, e.laufx, e.laufy, e.auswahlvon, e.auswahlmarke, e.gruppe,
                     e.gruppenuid, e.ladung, e.arbeitsplatz, e.nahziel, e.nahangreifer)?;
        }
        let mut g = BufWriter::new(File::create(pfad_gebaeude)?);
        writeln!(g, "nr besitzer typ x y leben uid erreichbar vorrat grenze verbund ware")?;
        for b in &self.gebaeude {
            writeln!(g, "{} {} {} {} {} {} {} -9 {} {} {} {}", b.nr, b.besitzer, b.typ, b.x, b.y, b.leben, b.uid,
                     b.vorrat, b.grenze, b.verbund, b.ware)?;
        }
        Ok(())
    }
}

pub fn graben_bits(v: u32) -> u8 {
    (if v & GRABEN_GEPLANT != 0 { 1 } else { 0 }) | (if v & GRABEN != 0 { 2 } else { 0 })
}

/// Vergleich zweier Grabenaufnahmen. Ohne vorherige Aufnahme (neue Epoche) gibt es keinen Alarm, nur die Zaehlung.
pub fn graben_vergleich(vorher: &[u8], jetzt: &[u8]) -> GrabenAenderung {
    let mut a = GrabenAenderung {
        geplant: jetzt.iter().filter(|&&b| b & 1 != 0).count(),
        ausgehoben: jetzt.iter().filter(|&&b| b & 2 != 0).count(),
        ..Default::default()
    };
    if vorher.len() != jetzt.len() {
        return a;
    }
    for (i, (&v, &j)) in vorher.iter().zip(jetzt.iter()).enumerate() {
        if j & 1 != 0 && v & 1 == 0 {
            a.neu_geplant.push(i);
        }
        if j & 2 != 0 && v & 2 == 0 {
            a.neu_ausgehoben.push(i);
        }
        if v & 2 != 0 && j & 2 == 0 {
            a.zugeschuettet.push(i);
        }
        if v & 1 != 0 && j & 1 == 0 && j & 2 == 0 {
            a.plan_geloescht += 1;
        }
        if j == 0 && v != 0 {
            a.weg += 1;
        }
    }
    a
}

/// zeilen[y] = (erstes x, Nummer des ersten Feldes); die Zeile reicht bis zum ersten Feld der naechsten Zeile.
pub fn feld_xy_aus(zeilen: &[(i32, i32)], feld: usize) -> Option<(i32, i32)> {
    let feld = feld as i32;
    for (y, &(x0, start)) in zeilen.iter().enumerate() {
        let ende = zeilen.get(y + 1).map_or(FELDER as i32, |z| z.1);
        if feld >= start && feld < ende {
            return Some((x0 + feld - start, y as i32));
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn graben_bits_trennen_geplant_und_ausgehoben() {
        assert_eq!(graben_bits(0x8000), 0);
        assert_eq!(graben_bits(0x4000 | 0x8000), 1);
        assert_eq!(graben_bits(0x4000_8000), 2);
        assert_eq!(graben_bits(0x4000_4000), 3);
    }

    #[test]
    fn neue_epoche_gibt_keinen_alarm() {
        let jetzt = vec![0, 1, 2, 0];
        let a = graben_vergleich(&[], &jetzt);
        assert!(a.neu_geplant.is_empty() && a.neu_ausgehoben.is_empty());
        assert_eq!((a.geplant, a.ausgehoben), (1, 1));
    }

    #[test]
    fn neu_geplant_und_ausgehoben_werden_gemeldet() {
        let a = graben_vergleich(&[0, 1, 0, 2], &[1, 3, 0, 0]);
        assert_eq!(a.neu_geplant, vec![0]);
        assert_eq!(a.neu_ausgehoben, vec![1]);
        assert_eq!(a.weg, 1);
    }

    #[test]
    fn zuschuetten_und_planung_loeschen_werden_gemeldet() {
        // Feld 0: ausgehoben -> leer (zugeschuettet); Feld 1: geplant -> leer (geloescht); Feld 2: geplant -> ausgehoben
        let a = graben_vergleich(&[2, 1, 1], &[0, 0, 2]);
        assert_eq!(a.zugeschuettet, vec![0]);
        assert_eq!(a.plan_geloescht, 1);
        assert_eq!(a.neu_ausgehoben, vec![2]);
        assert_eq!(a.weg, 2);
    }

    #[test]
    fn feld_nach_xy_wie_gemessen() {
        // gemessene Zeilentabelle 20.10.: y 0 -> (199, 0), y 1 -> (198, 2), y 2 -> (197, 6)
        let zeilen = [(199, 0), (198, 2), (197, 6), (196, 12)];
        assert_eq!(feld_xy_aus(&zeilen, 0), Some((199, 0)));
        assert_eq!(feld_xy_aus(&zeilen, 1), Some((200, 0)));
        assert_eq!(feld_xy_aus(&zeilen, 2), Some((198, 1)));
        assert_eq!(feld_xy_aus(&zeilen, 7), Some((198, 2)));
    }
}
