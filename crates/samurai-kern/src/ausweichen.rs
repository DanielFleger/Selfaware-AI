//! Zickzack (B-174, docs/plans/Plan_Gehirn.md 6.3 und 6.4): Ein Trupp laeuft auf sein Ziel zu und wechselt je Feld die Richtung.
//!
//! Gemessen am 08.11. (B-173, data/research/auge_plan/ausweichen_20261108/Ergebnis_Ausweichen.md): einzelner Sklave mit
//! Truppenbefehl gegen Bogenschuetzen, Wechsel je Feld auf den Schuetzen zu 25/2/1 % Treffer bei 8/12/16 Feldern, gerader Lauf
//! 92/86/78 %, Strecke 94 bis 97 %. Eine Python-Runde dauert im Median 63 Takte, ein Feld 12: darum der Kern.
//!
//! Warum ein Befehl je Feld fuer die ganze Gruppe reicht (gelesen in giveTribeMoveInstruction und
//! findNextTileInExistingSearchThatIsModuloDistanceAway): Das Spiel verteilt die Gruppe auf die Felder einer Suche um den
//! Zielpunkt, deren Abstand |dx|+|dy| gerade ist, in Suchreihenfolge; die erste Einheit bekommt den Zielpunkt selbst. Wandert
//! der Zielpunkt auf freiem Feld, wandert jeder Platz mit.
//!
//! Reine Logik, offline geprueft. Was das Spiel zeigt, kommt ueber `Stand` herein.

use std::collections::{BTreeMap, BTreeSet, HashSet};

use crate::haende::WIRK_TAKTE;

/// Auftragsring: Einheit `nr` gehoert zum Trupp mit der Nummer im Feld "vorrang" und laeuft im Zickzack nach (a, b)
pub const AUSWEICHEN: i32 = 30;
/// Waechter gegen Festlaufen, kein Messwert: Kommt der Trupp so lange nicht zum naechsten Wegpunkt, setzt er von seiner Mitte
/// neu an. Dieselbe Frist wie fuer die Wirkung eines Befehls, das sind drei Felder bei 12 Takten je Feld.
pub const FEST_TAKTE: i32 = WIRK_TAKTE;

type Punkt = (i32, i32);

/// Was der Zickzack von einer Einheit sieht: ihr Feld und ihr Platz aus dem letzten Befehl (plannedDestinationX/Y)
#[derive(Clone, Copy, Debug)]
pub struct Stand {
    pub x: i32,
    pub y: i32,
    pub planx: i32,
    pub plany: i32,
}

/// Der Gruppenbefehl, den ein Trupp in diesem Takt braucht
#[derive(Debug, PartialEq, Eq)]
pub struct Schritt {
    pub punkt: Punkt,
    pub einheiten: Vec<i32>,
    pub auftraggeber: i32,
}

struct Trupp {
    einheiten: BTreeSet<i32>,
    auftraggeber: i32,
    ziel: Punkt,
    /// Beginn der Linie zum Ziel; der Querschritt pendelt um diese Linie
    anker: Punkt,
    /// aktueller Wegpunkt; None = der Trupp setzt von seiner Mitte an
    punkt: Option<Punkt>,
    /// letzter Querschritt in Spielkoordinaten (+1, -1; 0 = noch keiner)
    seite: i32,
    /// Takt des letzten Wegpunkts
    takt: i32,
    /// Kein freies Feld fuer den Zickzack: Der Rest geht gerade, der Wegfinder des Spiels laeuft um das Hindernis
    direkt: bool,
}

/// Naechster Wegpunkt von `w` aus: ein Feld auf der laengeren Achse auf das Ziel zu, quer ein Feld im Wechsel um die Linie vom
/// Anker zum Ziel. Liegt das Ziel genau auf einer Achse, wechselt der Querschritt jedes Feld wie im Messlauf; liegt es schraeg,
/// wechselt er seltener, und auf der Diagonalen gar nicht, weil dort jedes andere Feld Strecke kostet (nicht gemessen).
/// Der Punkt geht immer auf: Nach max(|dx|, |dy|) Schritten steht der Trupp genau auf dem Ziel. None = kein freies Feld.
fn naechster_punkt(anker: Punkt, ziel: Punkt, w: Punkt, letzte_seite: i32, frei: &impl Fn(i32, i32) -> bool) -> Option<(Punkt, i32)> {
    let (ax, ay) = (ziel.0 - anker.0, ziel.1 - anker.1);
    let x_haupt = ax.abs() >= ay.abs();
    let (hg, qg, wh, wq) = if x_haupt {
        (ax, ay, w.0 - anker.0, w.1 - anker.1)
    } else {
        (ay, ax, w.1 - anker.1, w.0 - anker.0)
    };
    let (sh, sq) = (hg.signum(), if qg < 0 { -1 } else { 1 });
    let gesamt = hg.abs();
    let n = wh * sh + 1;
    if n > gesamt {
        return None;
    }
    let quer = wq * sq;
    let wunsch = if wh == 0 && wq == 0 && letzte_seite != 0 {
        // neues Ziel: Die Linie beginnt hier und wuerde immer dieselbe Seite waehlen, der Wechsel geht vor
        -letzte_seite * sq
    } else if quer * gesamt <= qg.abs() * n {
        1
    } else {
        -1
    };
    let rest = gesamt - n;
    [wunsch, -wunsch, 0].into_iter()
        .filter(|&s| (qg.abs() - (quer + s)).abs() <= rest)
        .map(|s| {
            let p = if x_haupt { (w.0 + sh, w.1 + s * sq) } else { (w.0 + s * sq, w.1 + sh) };
            (p, s * sq)
        })
        .find(|&(p, _)| frei(p.0, p.1))
}

fn mitte(stand: &[(i32, Stand)]) -> Punkt {
    let mitte_von = |mut v: Vec<i32>| {
        v.sort_unstable();
        v[v.len() / 2]
    };
    (mitte_von(stand.iter().map(|(_, s)| s.x).collect()), mitte_von(stand.iter().map(|(_, s)| s.y).collect()))
}

/// Alle Trupps im Zickzack
pub struct Schwarm {
    trupps: BTreeMap<i32, Trupp>,
    /// Zaehler fuers Protokoll: Wegpunkte, angekommene Trupps, Neuansaetze nach Festlaufen
    pub befehle: u64,
    pub fertig: u64,
    pub fest: u64,
}

impl Schwarm {
    pub const fn neu() -> Schwarm {
        Schwarm { trupps: BTreeMap::new(), befehle: 0, fertig: 0, fest: 0 }
    }

    pub fn leer(&self) -> bool {
        self.trupps.is_empty()
    }

    pub fn zahl(&self) -> usize {
        self.trupps.len()
    }

    pub fn leeren(&mut self) {
        self.trupps.clear();
    }

    /// Nimmt die Einheit in den Trupp. Ein neues Ziel laeuft von dort weiter, wo der Trupp gerade ist, ohne den Wechsel zu verlieren.
    pub fn annehmen(&mut self, trupp: i32, nr: i32, ziel: Punkt, auftraggeber: i32) {
        for (&n, t) in self.trupps.iter_mut() {
            if n != trupp {
                t.einheiten.remove(&nr);
            }
        }
        let t = self.trupps.entry(trupp).or_insert(Trupp {
            einheiten: BTreeSet::new(),
            auftraggeber,
            ziel,
            anker: ziel,
            punkt: None,
            seite: 0,
            takt: 0,
            direkt: false,
        });
        t.einheiten.insert(nr);
        if t.ziel != ziel {
            t.ziel = ziel;
            if t.direkt {
                t.direkt = false;
                t.punkt = None;
            } else if let Some(p) = t.punkt {
                t.anker = p;
            }
        }
    }

    /// Die Einheit verlaesst den Zickzack (anderer Befehl oder freigegeben).
    pub fn entfernen(&mut self, nr: i32) {
        for t in self.trupps.values_mut() {
            t.einheiten.remove(&nr);
        }
        self.trupps.retain(|_, t| !t.einheiten.is_empty());
    }

    /// Ist das der aktuelle Wegpunkt eines Trupps? (Solche Befehle kommen je Feld und stehen nicht einzeln im Protokoll.)
    pub fn ist_wegpunkt(&self, p: Punkt) -> bool {
        self.trupps.values().any(|t| t.punkt == Some(p))
    }

    /// Einmal je Takt: Welche Trupps brauchen jetzt ihren naechsten Wegpunkt? Weiter geht es, sobald die Einheit, die den Wegpunkt
    /// als Platz hat, sein Feld betritt (das Spiel liest ein neues Ziel erst in der Feldmitte) und keine andere mehr als ein Feld
    /// von ihrem Platz entfernt ist. So laeuft die Gruppe im Gleichschritt, und ein Befehl, der noch nicht angekommen ist, loest
    /// nichts aus: Dann hat noch keine Einheit den neuen Wegpunkt als Platz.
    pub fn takt(&mut self, tick: i32, sieh: impl Fn(i32) -> Option<Stand>, frei: impl Fn(i32, i32) -> bool) -> Vec<Schritt> {
        let mut aus = Vec::new();
        let mut weg = Vec::new();
        // Zwei Trupps mit demselben Wegpunkt im selben Takt verschmoelzen im Auftragsbuch zu einem Gruppenbefehl, und das Spiel
        // gibt dem zweiten einen anderen Platz: Sein Wegpunkt wird nie betreten, er steht bis zum Waechter (Lauf brand_g 09.11.).
        let mut vergeben: HashSet<Punkt> = HashSet::new();
        for (&nr, t) in self.trupps.iter_mut() {
            let stand: Vec<(i32, Stand)> = t.einheiten.iter().filter_map(|&e| sieh(e).map(|s| (e, s))).collect();
            if stand.is_empty() {
                weg.push(nr);
                continue;
            }
            t.einheiten = stand.iter().map(|&(e, _)| e).collect();
            if let Some(p) = t.punkt {
                let betreten = stand.iter().any(|(_, s)| (s.planx, s.plany) == p && (s.x, s.y) == p);
                let beisammen = stand.iter().all(|(_, s)| (s.x - s.planx).abs().max((s.y - s.plany).abs()) <= 1);
                let weiter = betreten && beisammen;
                if weiter && p == t.ziel {
                    self.fertig += 1;
                    weg.push(nr);
                    continue;
                }
                let fest = !t.direkt && tick - t.takt > FEST_TAKTE;
                if !weiter && !fest {
                    continue;
                }
                if !weiter {
                    self.fest += 1;
                    t.punkt = None;
                }
            }
            let von = match t.punkt {
                Some(p) => p,
                None => {
                    let m = mitte(&stand);
                    t.anker = m;
                    m
                }
            };
            if von == t.ziel {
                self.fertig += 1;
                weg.push(nr);
                continue;
            }
            match naechster_punkt(t.anker, t.ziel, von, t.seite, &|x, y| frei(x, y) && !vergeben.contains(&(x, y))) {
                Some((p, seite)) => {
                    vergeben.insert(p);
                    t.punkt = Some(p);
                    if seite != 0 {
                        t.seite = seite;
                    }
                }
                None => {
                    t.punkt = Some(t.ziel);
                    t.direkt = true;
                }
            }
            t.takt = tick;
            self.befehle += 1;
            aus.push(Schritt {
                punkt: t.punkt.unwrap_or(t.ziel),
                einheiten: t.einheiten.iter().copied().collect(),
                auftraggeber: t.auftraggeber,
            });
        }
        for nr in weg {
            self.trupps.remove(&nr);
        }
        aus
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;
    use std::collections::HashMap;

    fn alles_frei(_: i32, _: i32) -> bool {
        true
    }

    fn lauf(start: Punkt, ziel: Punkt) -> Vec<Punkt> {
        let (mut w, mut seite, mut weg) = (start, 0, vec![]);
        while w != ziel {
            let (p, s) = naechster_punkt(start, ziel, w, seite, &alles_frei).unwrap();
            w = p;
            if s != 0 {
                seite = s;
            }
            weg.push(p);
            assert!(weg.len() <= 1000, "kommt nie an");
        }
        weg
    }

    #[test]
    fn ziel_auf_der_achse_wechselt_jedes_feld_wie_im_messlauf() {
        let weg = lauf((100, 100), (110, 100));
        let erwartet: Vec<Punkt> = (1..=10).map(|i| (100 + i, 100 + if i % 2 == 1 && i < 10 { 1 } else { 0 })).collect();
        assert_eq!(weg, erwartet);
    }

    #[test]
    fn jede_richtung_kommt_genau_an_und_ohne_umweg() {
        for dx in -20..=20 {
            for dy in -20..=20 {
                if (dx, dy) == (0, 0) {
                    continue;
                }
                let weg = lauf((100, 100), (100 + dx, 100 + dy));
                assert_eq!(weg.len() as i32, dx.abs().max(dy.abs()), "{} {}", dx, dy);
                let mut vor = (100, 100);
                for &p in &weg {
                    assert_eq!((p.0 - vor.0).abs().max((p.1 - vor.1).abs()), 1, "{} {}: {:?}", dx, dy, weg);
                    vor = p;
                }
            }
        }
    }

    fn wechsel(weg: &[Punkt], start: Punkt) -> usize {
        let mut schritte = vec![];
        let mut vor = start;
        for &p in weg {
            schritte.push((p.0 - vor.0, p.1 - vor.1));
            vor = p;
        }
        schritte.windows(2).filter(|w| w[0] != w[1]).count()
    }

    #[test]
    fn schraeg_wechselt_seltener_und_auf_der_diagonalen_gar_nicht() {
        let (achse, flach, diagonal) = (lauf((0, 0), (32, 0)), lauf((0, 0), (32, 16)), lauf((0, 0), (32, 32)));
        assert_eq!(wechsel(&achse, (0, 0)), 31);
        assert!(wechsel(&flach, (0, 0)) < 31 && wechsel(&flach, (0, 0)) >= 16, "{}", wechsel(&flach, (0, 0)));
        assert_eq!(wechsel(&diagonal, (0, 0)), 0);
    }

    #[test]
    fn besetztes_feld_nimmt_die_andere_seite() {
        let zu = |x: i32, y: i32| (x, y) != (101, 101);
        assert_eq!(naechster_punkt((100, 100), (110, 100), (100, 100), 0, &zu), Some(((101, 99), -1)));
        let nur_gerade = |x: i32, y: i32| y == 100 || x > 101;
        assert_eq!(naechster_punkt((100, 100), (110, 100), (100, 100), 0, &nur_gerade), Some(((101, 100), 0)));
        assert_eq!(naechster_punkt((100, 100), (110, 100), (100, 100), 0, &|_, _| false), None);
    }

    #[test]
    fn neues_ziel_verliert_den_wechsel_nicht() {
        let w = (105, 101);
        let (p, s) = naechster_punkt(w, (130, 101), w, 1, &alles_frei).unwrap();
        assert_eq!((p, s), ((106, 100), -1));
    }

    /// Eine kleine Welt: Einheiten stehen auf Feldern, ein Befehl setzt die Plaetze (Zielpunkt + fester Versatz je Einheit)
    struct Welt {
        e: RefCell<HashMap<i32, Stand>>,
        versatz: HashMap<i32, Punkt>,
    }

    impl Welt {
        fn neu(einheiten: &[(i32, Punkt, Punkt)]) -> Welt {
            Welt {
                e: RefCell::new(einheiten.iter().map(|&(n, p, _)| (n, Stand { x: p.0, y: p.1, planx: p.0, plany: p.1 })).collect()),
                versatz: einheiten.iter().map(|&(n, _, v)| (n, v)).collect(),
            }
        }
        fn befehl(&self, s: &Schritt) {
            for n in &s.einheiten {
                let v = self.versatz[n];
                let mut e = self.e.borrow_mut();
                let u = e.get_mut(n).unwrap();
                (u.planx, u.plany) = (s.punkt.0 + v.0, s.punkt.1 + v.1);
            }
        }
        fn alle_am_platz(&self) {
            for u in self.e.borrow_mut().values_mut() {
                (u.x, u.y) = (u.planx, u.plany);
            }
        }
        fn sieh(&self) -> impl Fn(i32) -> Option<Stand> + '_ {
            |n| self.e.borrow().get(&n).copied()
        }
    }

    #[test]
    fn gruppe_laeuft_im_gleichschritt_mit_einem_befehl_je_feld() {
        let w = Welt::neu(&[(1, (50, 50), (0, 0)), (2, (49, 49), (-1, -1)), (3, (51, 49), (1, -1))]);
        let mut s = Schwarm::neu();
        for n in 1..=3 {
            s.annehmen(7, n, (60, 50), 2);
        }
        let mut t = 100;
        let a = s.takt(t, w.sieh(), alles_frei);
        assert_eq!(a, vec![Schritt { punkt: (51, 50), einheiten: vec![1, 2, 3], auftraggeber: 2 }]);
        assert!(s.takt(t + 1, w.sieh(), alles_frei).is_empty(), "der Befehl ist noch nicht angekommen");
        w.befehl(&a[0]);
        assert!(s.takt(t + 2, w.sieh(), alles_frei).is_empty(), "noch nicht auf dem Wegpunkt");
        w.alle_am_platz();
        t += 12;
        let b = s.takt(t, w.sieh(), alles_frei);
        assert_eq!(b.len(), 1);
        assert_ne!(b[0].punkt, a[0].punkt);
        assert_eq!(s.befehle, 2);
    }

    #[test]
    fn nachzuegler_haelt_die_gruppe_an_bis_der_waechter_kommt() {
        let w = Welt::neu(&[(1, (50, 50), (0, 0)), (2, (40, 50), (0, 2))]);
        let mut s = Schwarm::neu();
        s.annehmen(1, 1, (70, 50), 2);
        s.annehmen(1, 2, (70, 50), 2);
        let a = s.takt(100, w.sieh(), alles_frei);
        w.befehl(&a[0]);
        {
            let mut e = w.e.borrow_mut();
            let u = e.get_mut(&1).unwrap();
            (u.x, u.y) = (u.planx, u.plany);
        }
        assert!(s.takt(112, w.sieh(), alles_frei).is_empty());
        assert_eq!(s.takt(100 + FEST_TAKTE + 1, w.sieh(), alles_frei).len(), 1);
        assert_eq!(s.fest, 1);
    }

    #[test]
    fn am_ziel_ist_schluss_und_tote_fallen_heraus() {
        let w = Welt::neu(&[(1, (50, 50), (0, 0)), (2, (49, 50), (-1, 1))]);
        let mut s = Schwarm::neu();
        s.annehmen(1, 1, (51, 50), 2);
        s.annehmen(1, 2, (51, 50), 2);
        let a = s.takt(100, w.sieh(), alles_frei);
        assert_eq!(a[0].punkt, (51, 50));
        w.e.borrow_mut().remove(&2);
        w.befehl(&Schritt { punkt: a[0].punkt, einheiten: vec![1], auftraggeber: 2 });
        w.alle_am_platz();
        assert!(s.takt(112, w.sieh(), alles_frei).is_empty());
        assert!(s.leer());
        assert_eq!(s.fertig, 1);
    }

    #[test]
    fn zwei_trupps_bekommen_im_selben_takt_nie_denselben_wegpunkt() {
        let w = Welt::neu(&[(1, (50, 50), (0, 0)), (2, (50, 52), (0, 0))]);
        let mut s = Schwarm::neu();
        s.annehmen(1, 1, (60, 50), 2);
        s.annehmen(2, 2, (60, 47), 2);
        let a = s.takt(100, w.sieh(), alles_frei);
        assert_eq!(a.len(), 2);
        assert_eq!(a[0].punkt, (51, 51));
        assert_ne!(a[0].punkt, a[1].punkt, "sonst wird daraus ein gemeinsamer Gruppenbefehl");
        assert_eq!(a[1].punkt, (51, 53), "die andere Seite");
    }

    #[test]
    fn anderer_befehl_nimmt_die_einheit_heraus_und_trupps_tauschen_nicht_doppelt() {
        let mut s = Schwarm::neu();
        s.annehmen(1, 5, (60, 50), 2);
        s.annehmen(2, 5, (60, 50), 2);
        assert_eq!(s.zahl(), 2);
        let w = Welt::neu(&[(5, (50, 50), (0, 0))]);
        let a = s.takt(100, w.sieh(), alles_frei);
        assert_eq!(a.len(), 1, "die Einheit gehoert nur zum neuen Trupp");
        s.entfernen(5);
        assert!(s.leer());
    }

    #[test]
    fn neues_ziel_bleibt_auf_dem_wegpunkt_verankert() {
        let w = Welt::neu(&[(1, (50, 50), (0, 0))]);
        let mut s = Schwarm::neu();
        s.annehmen(1, 1, (60, 50), 2);
        let a = s.takt(100, w.sieh(), alles_frei);
        w.befehl(&a[0]);
        w.alle_am_platz();
        assert_eq!(a[0].punkt, (51, 51));
        s.annehmen(1, 1, (71, 51), 2);
        // Die neue Linie beginnt am Wegpunkt (51,51) und bleibt auf y = 51; vom alten Anfang (50,50) aus laege sie auf y = 50 bis 51
        let mut weg = vec![];
        for i in 1..=3 {
            let b = s.takt(100 + 12 * i, w.sieh(), alles_frei);
            w.befehl(&b[0]);
            w.alle_am_platz();
            weg.push(b[0].punkt);
        }
        assert_eq!(weg, vec![(52, 50), (53, 51), (54, 52)]);
    }
}
