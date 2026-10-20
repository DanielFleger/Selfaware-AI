//! Wege (B-145 S3, docs/plans/Plan_Kern.md "Bauplan S3"): Erreichbarkeit ueber die Gebiete des Wegnetzes - die reine Abfrage
//! des Spiels, die das Lagebild fuer "erreichbar" und der Holzfaeller (findTree) nutzen; sie veraendert nichts im Spiel.
//! ring_suche ist reine Logik und offline geprueft.

const ZEILEN: usize = 0x0233_72F8;
/// PathConnectionLayer (TileMapState +0x363DD0): Gebiet je Feld, short
const WEGNETZ: usize = 0x01DF_6FD8;
/// calculateCanPlayerUnitsNavigateToAreaFromArea, thiscall auf PathFindingState
const KANN_HIN: usize = 0x004A_5320;
const PFS: usize = 0x012B_B8C8;
/// Startpunkt der Spalte "erreichbar" im Lagebild von logik.lua (lagebildVon wird nie gesetzt -> immer dieser Punkt)
pub const VON_LAGEBILD: (i32, i32) = (165, 111);

type KannHin = unsafe extern "thiscall" fn(this: usize, spieler: i32, von: i32, nach: i32, null: i32) -> i32;

/// Feldnummer genau wie logik.lua: addXgetTile(y) + x, ohne Pruefung der Zeilenbreite (fuer den 1:1-Vergleich).
pub fn feld_lua(x: i32, y: i32) -> i64 {
    let add = unsafe { std::ptr::read_volatile((ZEILEN + y.clamp(0, 399) as usize * 12 + 8) as *const i32) };
    add as i64 + x as i64
}

/// Gebiet des Wegnetzes an (x, y) wie logik.lua (readSmallInteger, ausserhalb der Karte 0).
pub fn gebiet(x: i32, y: i32) -> i32 {
    if !(0..400).contains(&x) || !(0..400).contains(&y) {
        return 0;
    }
    let a = (WEGNETZ as i64 + feld_lua(x, y) * 2) as usize;
    unsafe { std::ptr::read_volatile(a as *const i16) as i32 }
}

/// Kann Spieler `spieler` von Gebiet `von` nach Gebiet `nach` laufen? (Abfrage des Spiels, keine Nebenwirkung)
pub fn kann_hin(spieler: i32, von: i32, nach: i32) -> bool {
    if von <= 0 || nach <= 0 {
        return false;
    }
    unsafe {
        let f: KannHin = std::mem::transmute::<usize, KannHin>(KANN_HIN);
        f(PFS, spieler, von, nach, 0) != 0
    }
}

/// Alle Felder mit Schachbrett-Abstand genau r um z.
pub fn ring(z: (i32, i32), r: i32) -> Vec<(i32, i32)> {
    if r == 0 {
        return vec![z];
    }
    let mut v = Vec::with_capacity(8 * r as usize);
    for d in -r..=r {
        v.push((z.0 + d, z.1 - r));
        v.push((z.0 + d, z.1 + r));
    }
    for d in -r + 1..r {
        v.push((z.0 - r, z.1 + d));
        v.push((z.0 + r, z.1 + d));
    }
    v
}

/// Naechstes Feld auf den Ringen r_min..=r_max um `ziel`, fuer das `gut` gilt; im selben Ring das naechste an `von`
/// (Schachbrett-Abstand, bei Gleichstand der kuerzere gerade Weg).
pub fn ring_suche(ziel: (i32, i32), von: (i32, i32), r_min: i32, r_max: i32,
                  mut gut: impl FnMut(i32, i32) -> bool) -> Option<(i32, i32)> {
    for r in r_min..=r_max {
        let mut kand = ring(ziel, r);
        kand.sort_by_key(|&(x, y)| {
            let (dx, dy) = ((x - von.0).abs(), (y - von.1).abs());
            (dx.max(dy), dx + dy, x, y)
        });
        if let Some(p) = kand.into_iter().find(|&(x, y)| gut(x, y)) {
            return Some(p);
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ring_hat_8r_felder_im_richtigen_abstand() {
        for r in 1..5 {
            let v = ring((50, 50), r);
            assert_eq!(v.len(), 8 * r as usize);
            assert!(v.iter().all(|&(x, y)| (x - 50).abs().max((y - 50).abs()) == r));
        }
    }

    #[test]
    fn ring_suche_nimmt_den_naechsten_freien_an_der_einheit() {
        // Graben-Sperre: alles mit x >= 48 ist verboten; Einheit kommt von Westen (30, 50)
        let p = ring_suche((50, 50), (30, 50), 3, 10, |x, _| x < 48);
        assert_eq!(p, Some((47, 50)));
        // nichts frei -> None
        assert_eq!(ring_suche((50, 50), (30, 50), 3, 4, |_, _| false), None);
    }
}
