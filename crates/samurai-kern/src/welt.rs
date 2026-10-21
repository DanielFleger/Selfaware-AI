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
    /// B-147: Mauerfeld, das die Einheit aufhacken soll (Unit +0x3A8 targetedBuildingTile, 0 = keins), und dessen x/y
    /// (+0x3E8/+0x3EA attackAtTile) - beim Mauerangriff bleibt zielart (targetingType) 0, abgelesen giveTribeAnInstruction
    pub mauerfeld: i32,
    pub mauerx: i16,
    pub mauery: i16,
    /// S3: wie logik.lua - fremde Einheit vom Startpunkt aus erreichbar 1/0, eigene -1; -9 = nicht berechnet
    pub erreichbar: i32,
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
    pub groesse: i32,
    /// S3: ein Feld am Rand des Grundrisses vom Startpunkt aus erreichbar 1/0; -9 = nicht berechnet
    pub erreichbar: i32,
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
    /// Kopie der ganzen Kartenschicht vom letzten Takt (Version 13: einziger Lesepfad der Grabenwache)
    roh: Vec<u32>,
    roh_neu: Vec<u32>,
}

impl Welt {
    pub const fn neu() -> Self {
        Welt { einheiten: Vec::new(), gebaeude: Vec::new(), einheiten_max: 0, graben: Vec::new(), roh: Vec::new(),
               roh_neu: Vec::new() }
    }

    /// Neue Epoche (Laden, neue Partie): die Grabenwache nimmt im naechsten Takt neu auf, ohne Alarm.
    pub fn epoche(&mut self) {
        self.graben.clear();
        self.roh.clear();
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
                    mauerfeld: i32_bei(u + 0x3A8),
                    mauerx: i16_bei(u + 0x3E8),
                    mauery: i16_bei(u + 0x3EA),
                    erreichbar: -9,
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
                        groesse: i32_bei(b + 0x10C),
                        erreichbar: -9,
                    });
                }
            }
        }
    }

    /// Grabenwache: die Kartenschicht (80.400 Felder) als ein Block kopieren, mit dem letzten Takt in Bloecken zu 64 Feldern
    /// vergleichen und nur geaenderte Bloecke auswerten; liefert, was seit dem letzten Takt neu geplant/ausgehoben/zugeschuettet
    /// wurde. (Version 12 lief parallel zum alten Weg Feld fuer Feld: 0 Abweichungen, ~35 statt ~140 us; Gegenprobe L166.)
    pub fn graben_lesen(&mut self) -> GrabenAenderung {
        self.roh_neu.resize(FELDER, 0);
        unsafe { std::ptr::copy_nonoverlapping(LOGIK as *const u32, self.roh_neu.as_mut_ptr(), FELDER) };
        let erste = self.roh.len() != FELDER;
        if erste {
            self.graben = self.roh_neu.iter().map(|&v| graben_bits(v)).collect();
            std::mem::swap(&mut self.roh, &mut self.roh_neu);
            return graben_vergleich(&[], &self.graben);
        }
        let mut a = GrabenAenderung::default();
        for (k, (alt, neu)) in self.roh.chunks(64).zip(self.roh_neu.chunks(64)).enumerate() {
            if alt == neu {
                continue;
            }
            for (j, (&va, &vn)) in alt.iter().zip(neu.iter()).enumerate() {
                let (v, n) = (graben_bits(va), graben_bits(vn));
                if v == n {
                    continue;
                }
                let i = k * 64 + j;
                if n & 1 != 0 && v & 1 == 0 {
                    a.neu_geplant.push(i);
                }
                if n & 2 != 0 && v & 2 == 0 {
                    a.neu_ausgehoben.push(i);
                }
                if v & 2 != 0 && n & 2 == 0 {
                    a.zugeschuettet.push(i);
                }
                if v & 1 != 0 && n & 1 == 0 && n & 2 == 0 {
                    a.plan_geloescht += 1;
                }
                if n == 0 && v != 0 {
                    a.weg += 1;
                }
                self.graben[i] = n;
            }
        }
        std::mem::swap(&mut self.roh, &mut self.roh_neu);
        a.geplant = self.graben.iter().filter(|&&b| b & 1 != 0).count();
        a.ausgehoben = self.graben.iter().filter(|&&b| b & 2 != 0).count();
        a
    }

    /// S3: die Spalte "erreichbar" genau wie das Lagebild von logik.lua (Startpunkt VON_LAGEBILD, Spieler "ich").
    pub fn erreichbar_berechnen(&mut self, ich: i32) {
        use crate::wege::{gebiet, kann_hin, VON_LAGEBILD};
        let von = gebiet(VON_LAGEBILD.0, VON_LAGEBILD.1);
        for e in &mut self.einheiten {
            e.erreichbar = -1;
            if e.besitzer as i32 != ich && e.besitzer > 0 && von > 0 {
                e.erreichbar = 0;
                let a = gebiet(e.x, e.y);
                if a > 0 && kann_hin(ich, von, a) {
                    e.erreichbar = 1;
                }
            }
        }
        for b in &mut self.gebaeude {
            b.erreichbar = 0;
            let (bx, by) = (b.x as i32, b.y as i32);
            let gr = if (1..=12).contains(&b.groesse) { b.groesse } else { 3 };
            if von > 0 && bx >= 1 && by >= 1 {
                'suche: for d in -1..=gr {
                    for (x, y) in [(bx + d, by - 1), (bx + d, by + gr), (bx - 1, by + d), (bx + gr, by + d)] {
                        if (0..400).contains(&x) && (0..400).contains(&y) {
                            let a = gebiet(x, y);
                            if a > 0 && kann_hin(ich, von, a) {
                                b.erreichbar = 1;
                                break 'suche;
                            }
                        }
                    }
                }
            }
        }
    }

    /// S3: liegt ein geplantes oder ausgehobenes Grabenfeld bis `r` Felder um (x, y)? (Stand der letzten Grabenwache)
    pub fn graben_nahe(&self, x: i32, y: i32, r: i32, zeilen: &[(i32, i32)]) -> bool {
        if self.graben.len() != FELDER {
            return false;
        }
        for yy in y - r..=y + r {
            for xx in x - r..=x + r {
                if let Some(f) = feld_aus(zeilen, xx, yy) {
                    if self.graben[f] != 0 {
                        return true;
                    }
                }
            }
        }
        false
    }

    /// Zeilentabelle (erstes x, erstes Feld) je Kartenzeile
    pub fn zeilen() -> Vec<(i32, i32)> {
        (0..KARTE_ZEILEN).map(|y| unsafe { (i32_bei(ZEILEN + y * 12), i32_bei(ZEILEN + y * 12 + 4)) }).collect()
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
            writeln!(f, "{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}",
                     e.nr, e.besitzer, e.typ, e.x, e.y, e.leben, e.zustand, e.zielart, e.zieleinheit, e.zieluid,
                     e.zielgebaeude, e.ziel, e.zielx, e.ziely, e.laufx, e.laufy, e.auswahlvon, e.auswahlmarke, e.gruppe,
                     e.gruppenuid, e.ladung, e.arbeitsplatz, e.erreichbar, e.nahziel, e.nahangreifer)?;
        }
        let mut g = BufWriter::new(File::create(pfad_gebaeude)?);
        writeln!(g, "nr besitzer typ x y leben uid erreichbar vorrat grenze verbund ware")?;
        for b in &self.gebaeude {
            writeln!(g, "{} {} {} {} {} {} {} {} {} {} {} {}", b.nr, b.besitzer, b.typ, b.x, b.y, b.leben, b.uid,
                     b.erreichbar, b.vorrat, b.grenze, b.verbund, b.ware)?;
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

/// (x, y) -> Feldnummer, nur innerhalb der Zeilenbreite (sonst None)
pub fn feld_aus(zeilen: &[(i32, i32)], x: i32, y: i32) -> Option<usize> {
    let (x0, start) = *zeilen.get(usize::try_from(y).ok()?)?;
    let ende = zeilen.get(y as usize + 1).map_or(FELDER as i32, |z| z.1);
    let f = start + x - x0;
    if x >= x0 && f < ende { Some(f as usize) } else { None }
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

    #[test]
    fn feld_aus_ist_die_umkehrung_und_kennt_die_zeilenbreite() {
        let zeilen = [(199, 0), (198, 2), (197, 6), (196, 12)];
        for f in 0..12 {
            let (x, y) = feld_xy_aus(&zeilen, f).unwrap();
            assert_eq!(feld_aus(&zeilen, x, y), Some(f));
        }
        assert_eq!(feld_aus(&zeilen, 198, 0), None);   // links vor der Zeile
        assert_eq!(feld_aus(&zeilen, 201, 0), None);   // rechts nach der Zeile (Zeile 0 hat 2 Felder)
        assert_eq!(feld_aus(&zeilen, 5, -1), None);
    }
}
