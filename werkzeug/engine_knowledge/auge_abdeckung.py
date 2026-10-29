# -*- coding: utf-8 -*-

"""B-267 Auge-Abdeckung (Daniel 27.10. 17:51: "im Endeffekt darf im Code keine Zeile unerklaert sein").


Misst - statt aus dem Gedaechtnis - fuer ALLE Funktionen der Wissensdatenbank (knowledge.sqlite, Ghidra-Referenz) und

ALLE Felder der Strukturen Einheit, Gebaeude, Geschoss, Trupp, Spieler, KI-Vorgaben (AICSpecification), Karte/Zeit

(MapAndTimeState) und Weltkarte (TileMapState):

  - registerbelegt: ja, wenn eine Belegzeile sie im versionierten Wissensregister.md nennt (Zeilen AU/P/L/W/B/G/S/A).

    Der unversionierte VillageStudio-Wissensstand zaehlt nur mit dem ausdruecklichen Pruefschalter.

    Funktion genannt = exakte Adresse (8 Hex-Ziffern oder dieselbe Zahl ohne fuehrende Nullen), niemals nur Name.

    Feld erwaehnt = Namens-/Offsettreffer; registerbelegt nur mit explizitem Struktur-/Offset-/Groessenschluessel in auge_feldbelege.csv.

  - liest das Auge: Feldname steht in einem Datentyp oder im Quelltext von werkzeug/auge.py.

  - Name unklar: Ghidra-Platzhalter (fieldNNN_0x.., ...Unk, unknown..., _OR_-Doppelnamen, FUN_...).

Das ist nur "im Register adresslich erwaehnt", nicht "vollstaendig verstanden". Eine semantische Abnahme wird

getrennt ausgewiesen und niemals aus einer blossen Adressnennung abgeleitet. Sie verlangt vollstaendige Angaben, Gegenprobe und unveraenderte Export-/Registerhashes.


Aufruf: python werkzeug/engine_knowledge/auge_abdeckung.py   -> daten/auge_abdeckung_{funktionen,felder}.csv + .json

"""

import argparse

import csv

import io

import json

import os

import re

import sqlite3

import sys


HIER = os.path.dirname(os.path.abspath(__file__))

REPO = os.path.dirname(os.path.dirname(HIER))

EK = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge"

WS = os.path.join(os.path.dirname(REPO), "VillageStudio", "doku", "Wissensstand.md")

STRUKTUREN = {

    "Einheit": "/_HoldStrong/Map/Units/Unit",

    "Gebaeude": "/_HoldStrong/Map/Buildings/Building",

    "Geschoss": "/_HoldStrong/Map/Entities/Entity",

    "Trupp": "/_HoldStrong/Map/Units/Tribe",

    "Spieler": "/_HoldStrong/Game/Player/PlayerData",

    "KI-Vorgaben": "/_HoldStrong/AI/AIC/AICSpecification",

    "Karte/Zeit": "/_HoldStrong/Game/State/MapAndTimeState",

    "Weltkarte": "/_HoldStrong/Map/TileMapState",

}

# Technik ohne Spielwirkung (Oberflaeche, C-Laufzeit, Start, Text, Ton, Dateien, Grafik, Eingabe, Kartenversion)

TECHNIK = ("_HoldStrong::UI", "HoldStrong_lib", "_HoldStrong::Global::Init", "_HoldStrong::Meta", "_HoldStrong::Text",

           "_HoldStrong::Audio", "_HoldStrong::IO", "_HoldStrong::Rendering", "_HoldStrong::OS", "_HoldStrong::Input",

           "_HoldStrong::Map::Version")

UNKLAR = re.compile(r"^(field\d+_0x[0-9a-f]+|FUN_|DAT_|_?unknown|.*Unk\d*$|.*_OR_|.*Unknown|.*unk\d)", re.I)

STATUSWORTE = re.compile(r"\b(abgelesen|gemessen|belegt|getestet|vermutet|offen|luecke|widerlegt)\b", re.I)

INHALTSBELEG = re.compile(r"\b(abgelesen|gemessen|belegt|getestet)\b", re.I)


def register_status(spalten):
    """Statusspalte von rechts lesen; Stichwoerter im Erklaertext sind kein Status."""
    for spalte in reversed(spalten[2:]):
        if re.match(r"^\s*(?:\*\*)?(abgelesen|gemessen|belegt|getestet|vermutet|offen|luecke|widerlegt|gebaut)\b", spalte, re.I):
            return spalte
    return ""


def adressmuster(a):

    """Exakte achtstellige Adresse oder dieselbe Zahl ohne fuehrende Nullen."""

    return [re.compile(r"(?<![0-9a-f])(0x)?" + a + r"\b"),

            re.compile(r"(?<![0-9a-f])(0x)?" + a.lstrip("0") + r"\b")]


def belegzeilen(ohne_beleg=None, mit_externem_wissensstand=False):

    """[(beleg, marke_text, text_klein)] aus Register und Wissensstand."""

    aus = []

    reg = io.open(os.path.join(REPO, "Wissensregister.md"), encoding="utf-8").read().splitlines()

    for z in reg:

        m = re.match(r"^\| ([A-Z]+\d+) \|", z)

        if m:

            if m.group(1) == ohne_beleg:

                continue

            spalten = [s.strip() for s in re.split(r" \| ", z.strip(" |"))]

            marke = register_status(spalten)

            aus.append((m.group(1), marke, z.lower()))

    if mit_externem_wissensstand and os.path.exists(WS):

        abschnitt = "0"

        for z in io.open(WS, encoding="utf-8").read().splitlines():

            m = re.match(r"^##+ (\d+(\.\d+)*)", z)

            if m:

                abschnitt = m.group(1)

            if z.startswith("| ") and "---" not in z:

                spalten = [s.strip() for s in z.split("|")]

                marke = next((s for s in spalten if s.startswith("**") and s.endswith("**")), "")

                aus.append(("WS " + abschnitt, marke.strip("*"), z.lower()))

    return [(b, m, t) for b, m, t in aus if "widerlegt" not in m.lower()]


def auge_namen():

    sys.path.insert(0, os.path.join(REPO, "werkzeug"))

    import auge

    namen = set()

    for dt in (auge.UNIT, auge.ENTITY, auge.BUILDING, auge.TRIBE, auge.AIC):

        namen |= set(dt.names)

    for n in dir(auge):

        v = getattr(auge, n)

        if hasattr(v, "names") and getattr(v, "names", None):

            try:

                namen |= set(v.names)

            except TypeError:

                pass

    alias_originale = {alt for alt, neu in auge.FELD_ALIASE.items() if neu in namen}

    return namen | alias_originale, auge.INDIREKT_GELESENE_FELDER


def semantikdaten():

    """Explizite semantische Abnahmen; leere oder andere Statuswerte zaehlen nicht."""

    pfad = os.path.join(REPO, "daten", "auge_semantik.csv")

    if not os.path.exists(pfad):

        return {}

    with io.open(pfad, encoding="utf-8-sig", newline="") as f:

        zeilen = list(csv.DictReader(f, delimiter=";"))

    aus = {}

    for zeile in zeilen:

        adresse = zeile.get("adresse", "").lower().replace("0x", "").rjust(8, "0")

        if adresse in aus:

            raise ValueError("Doppelte Semantikadresse: " + adresse)

        aus[adresse] = zeile

    return aus


def funktionsklasse(name):
    """Unbenannte Funktionen bleiben unklassifiziert statt pauschal Technik."""
    if "::" not in name:
        return "unklar"
    return "nein" if name.startswith(TECHNIK) else "ja"


def semantische_abnahme(adresse, eintrag, belege, exportpfad, registertexte):
    """Explizite Abnahme gilt nur fuer genau diese Quelle und Registerfassung."""
    if eintrag.get("status") != "abgenommen":
        return False
    pflicht = ("kurzaussage", "eingaben", "rueckgabe", "schreibfelder",
               "voraussetzungen", "grenzwerte", "sonderfaelle", "abhaengigkeiten",
               "quelle", "gegenprobe", "registermarke", "registerhash", "pruefdatum")
    if any(not eintrag.get(k, "").strip() for k in pflicht):
        return False
    if eintrag.get("offene_fragen", "").strip().lower() != "keine":
        return False
    marke = eintrag["registermarke"]
    if marke not in {b for b, _ in belege} or marke not in registertexte:
        return False
    import hashlib
    try:
        with open(exportpfad, "rb") as f:
            quellhash = hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return False
    registerhash = hashlib.sha256(registertexte[marke].encode("utf-8")).hexdigest()
    return (eintrag.get("funktionshash") == quellhash
            and eintrag["registerhash"] == registerhash
            and eintrag.get("adresse", "").lower().replace("0x", "").rjust(8, "0") == adresse)


def feldzuordnungen():
    """Nur explizite Struktur-/Offset-/Groessenbindungen, keine Namensvermutung."""
    pfad = os.path.join(REPO, "daten", "auge_feldbelege.csv")
    if not os.path.exists(pfad):
        return []
    with io.open(pfad, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def feldbeleg_passt(eintrag, struktur, offset, groesse, feld, aktive_belege):
    import hashlib
    text = aktive_belege.get(eintrag.get("beleg"), "")
    return (bool(text)
            and eintrag.get("registerhash") == hashlib.sha256(text.encode("utf-8")).hexdigest()
            and eintrag.get("struktur") == struktur
            and eintrag.get("offset") == str(offset)
            and eintrag.get("groesse") == str(groesse)
            and eintrag.get("feld") == feld
            and eintrag.get("beleg") in aktive_belege)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--ohne-beleg", help="Negativlauf: diese Registerzeile bei der Messung ausblenden")

    parser.add_argument("--ausgabe", default=os.path.join(REPO, "daten"), help="Ausgabeordner (Standard: daten)")

    parser.add_argument("--mit-externem-wissensstand", action="store_true",

                        help="Unversionierten VillageStudio-Wissensstand zusaetzlich einbeziehen")

    args = parser.parse_args()

    zeilen = belegzeilen(args.ohne_beleg, args.mit_externem_wissensstand)

    semantik = semantikdaten()
    feldbindungen = feldzuordnungen()
    registertexte = {b: t for b, m, t in zeilen}

    namen, indirekt = auge_namen()

    # Funktionen

    con = sqlite3.connect(os.path.join(EK, "knowledge.sqlite"))

    fn = con.execute("select address, name from functions").fetchall()

    f_aus = []

    for adr, name in fn:

        a = adr.lower().lstrip("0x")[-8:].rjust(8, "0")

        kurz = name.split("::")[-1]

        # Nur die eindeutige Adresse belegt eine Funktion. Ein Name in einer Registerzeile kann bloss

        # ein aufgerufener Nachbar sein; das erklaert dessen eigenen Funktionskoerper noch nicht.

        muster = adressmuster(a)

        belege = [(b, m) for b, m, t in zeilen
                  if (a in t or a.lstrip("0") in t) and any(p.search(t) for p in muster)]

        inhaltsbelege = [(b, m) for b, m in belege if INHALTSBELEG.search(m or "")]

        abgenommen = semantische_abnahme(a, semantik.get(a, {}), inhaltsbelege,
                                          os.path.join(EK, "exports", "reference", "functions", a + ".json"),
                                          registertexte)

        f_aus.append({"adresse": "0x" + a.upper(), "name": name,

                      "registerbelegt": "ja" if belege else "nein",

                      "beschreibungsstand": "teilbeschreibung" if inhaltsbelege else "offen",

                      "semantisch_abgenommen": "ja" if abgenommen else "nein",

                      "beleg": " ".join(sorted(set(b for b, _ in belege)))[:200],

                      "marke": " / ".join(sorted(set(m for _, m in belege if m)))[:80],

                      "name_unklar": "ja" if UNKLAR.match(kurz) else "nein",

                      "spiellogik": funktionsklasse(name)})

    # Felder

    t = json.load(io.open(os.path.join(EK, "exports", "reference", "types.json"), encoding="utf-8"))

    nach_pfad = {x.get("path"): x for x in t}

    fe_aus = []

    for struktur, pfad in STRUKTUREN.items():

        d = nach_pfad.get(pfad)

        if d is None:

            continue

        for z in d["definition"].split("\n"):

            m = re.match(r"\s+(\d+)\s+(.+?)\s+(\d+)\s+([A-Za-z_][A-Za-z0-9_]*)\s", z + " ")

            if not m:

                continue

            off, typ, gr, feld = int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)

            muster = [re.compile(r"\b" + re.escape(feld.lower()) + r"\b")]

            if struktur == "Einheit":

                muster.append(re.compile(r"\+" + str(off) + r"\b"))

            belege = [(b, mk) for b, mk, tx in zeilen
                       if (feld.lower() in tx or (struktur == "Einheit" and "+" + str(off) in tx))
                       and any(p.search(tx) for p in muster)]

            erwaehnungen = belege
            aktiv = {b: tx for b, _, tx in zeilen}
            belege = [(e["beleg"], next((mk for b, mk, tx in zeilen if b == e["beleg"]), ""))
                       for e in feldbindungen
                       if feldbeleg_passt(e, struktur, off, gr, feld, aktiv)]
            liest = feld in namen or feld in indirekt.get(struktur, set())

            fe_aus.append({"struktur": struktur, "offset": off, "typ": typ, "groesse": gr, "feld": feld,

                           "register_erwaehnt": "ja" if erwaehnungen else "nein",
                           "registerbelegt": "ja" if belege else "nein",

                           "beleg": " ".join(sorted(set(b for b, _ in belege)))[:200],

                           "marke": " / ".join(sorted(set(mk for _, mk in belege if mk)))[:80],

                           "liest_auge": "ja" if liest else "nein",

                           "name_unklar": "ja" if UNKLAR.match(feld) else "nein"})

    daten = os.path.abspath(args.ausgabe)

    os.makedirs(daten, exist_ok=True)

    for datei, liste in (("auge_abdeckung_funktionen.csv", f_aus), ("auge_abdeckung_felder.csv", fe_aus)):

        with io.open(os.path.join(daten, datei), "w", encoding="utf-8-sig", newline="") as f:

            w = csv.DictWriter(f, fieldnames=list(liste[0].keys()), delimiter=";")

            w.writeheader()

            w.writerows(liste)


    def zahl(liste, **bed):

        return sum(1 for r in liste if all(r[k] == v for k, v in bed.items()))

    je = {}

    for s in STRUKTUREN:

        teil = [r for r in fe_aus if r["struktur"] == s]

        je[s] = {"felder": len(teil), "registerbelegt": zahl(teil, registerbelegt="ja"),

                 "liest_auge": zahl(teil, liest_auge="ja"), "name_unklar": zahl(teil, name_unklar="ja"),

                 "liest_aber_unbelegt": zahl(teil, liest_auge="ja", registerbelegt="nein")}

    erg = {"stand": __import__("time").strftime("%d.%m.%Y %H:%M"),

           "funktionen": {"gesamt": len(f_aus), "registerbelegt": zahl(f_aus, registerbelegt="ja"),

                          "teilbeschrieben": zahl(f_aus, beschreibungsstand="teilbeschreibung"),

                          "semantisch_abgenommen": zahl(f_aus, semantisch_abgenommen="ja"),

                          "name_unklar": zahl(f_aus, name_unklar="ja"), "spiellogik": zahl(f_aus, spiellogik="ja"),

                          "klassifikation_unklar": zahl(f_aus, spiellogik="unklar"),
                          "spiellogik_nenner_vorlaeufig": True,
                          "spiellogik_registerbelegt": zahl(f_aus, spiellogik="ja", registerbelegt="ja"),

                          "spiellogik_teilbeschrieben": zahl(f_aus, spiellogik="ja", beschreibungsstand="teilbeschreibung"),

                          "spiellogik_semantisch_abgenommen": zahl(f_aus, spiellogik="ja", semantisch_abgenommen="ja")},

           "felder": {"gesamt": len(fe_aus), "register_erwaehnt": zahl(fe_aus, register_erwaehnt="ja"),
                      "registerbelegt": zahl(fe_aus, registerbelegt="ja"),

                      "liest_auge": zahl(fe_aus, liest_auge="ja"),

                      "liest_aber_unbelegt": zahl(fe_aus, liest_auge="ja", registerbelegt="nein")},

           "je_struktur": je, "belegzeilen": len(zeilen),

           "regel": __doc__.split("Aufruf:")[0].strip()}

    json.dump(erg, io.open(os.path.join(daten, "auge_abdeckung.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(json.dumps({k: v for k, v in erg.items() if k != "regel"}, ensure_ascii=False, indent=1))

    return 0


if __name__ == "__main__":

    sys.exit(main())
