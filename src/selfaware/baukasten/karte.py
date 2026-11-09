"""Die Modulkarte (B-176, docs/plans/Plan_Baukasten.md): Welcher Spielteil hat welche Module, und wo steht jedes im Code.

Die Beziehung gilt in beiden Richtungen: module_von(teil) und teil_von(modul). Der Stand jedes Moduls wird aus dem Quelltext gelesen, nicht
von Hand gepflegt, und tests/test_baukasten.py sperrt, dass etwas fehlt oder etwas genannt wird, das es nicht gibt.
Ansehen: docs/plans/Modulkarte.md, neu schreiben mit python -m selfaware.baukasten.karte --schreiben
"""

import ast
import collections
import dataclasses
import functools
import pathlib
import re
import sys

PAKET = pathlib.Path(__file__).resolve().parents[1]
KERN = PAKET.parents[1] / "crates" / "samurai-kern" / "src"
ZIEL = PAKET.parents[1] / "docs" / "plans" / "Modulkarte.md"
LENKER = "runtime/live/erstes_spiel.py"
ORDNER = (
    "macro",
    "micro",
    "micro/tasks",
    "strategy",
    "services",
    "execution",
    "learning",
    "runtime/live",
    "baukasten",
    "game/ucp",
)

SPIELTEILE = {
    "apfel": "Apfelwirtschaft",
    "brot": "Brotwirtschaft",
    "bier": "Bierwirtschaft",
    "nahrung": "Nahrung gesamt",
    "waffen": "Waffenwirtschaft",
    "grund": "Grundwirtschaft",
    "bestellung_raid": "Bestellung Raid",
    "bestellung_angriff": "Bestellung Angriff",
    "bestellung_verteidigung": "Bestellung Verteidigung",
    "einsatz_raid": "Einsatz Raid",
    "einsatz_angriff": "Einsatz Angriff",
    "einsatz_verteidigung": "Einsatz Verteidigung",
    "werkzeug": "Werkzeugkasten",
    "scaling": "Scaling",
    "acceleration": "Acceleration",
    "haende": "Haende",
    "augen": "Augen",
    "lernen": "Lernen",
    "rahmen": "Rahmen",
}


@dataclasses.dataclass(frozen=True)
class Modul:
    name: str
    stellen: tuple  # "macro/brotbau.py:BrotBau", "macro/standort.py" oder "kern/welt.rs"; die erste Stelle bestimmt den Stand
    schalter: tuple


def _m(name, stellen, schalter=""):
    return Modul(name, tuple(stellen.split()), tuple(schalter.split()))


def _l(namen):
    """Stellen im Lenker, durch Leerzeichen getrennt."""
    return " ".join(f"{LENKER}:{n}" for n in namen.split())


KARTE = {
    "apfel": (
        _m("Apfelplaetze", "macro/nahrungswahl.py:apfel_plaetze macro/nahrungswahl.py:apfel_rate"),
        _m("Apfelgruppen", "macro/wirtschaft.py:apfel_gruppen", "b_versatz"),
        _m("Erste Plantagen", "macro/eroeffnung.py:plane_essen"),
    ),
    "brot": (_m("Brotbau", "macro/brotbau.py:BrotBau"),),
    "bier": (_m("Bierkette", "macro/bierkette.py:Bierkette", "bier"),),
    "nahrung": (
        _m("Nahrungswahl", "macro/nahrungswahl.py", "nahrung_ausbau"),
        _m("Hoefe mischen", "macro/farmen_mischen.py"),
        _m("Hoefe packen", "macro/farmen_packen.py"),
        _m("Nahrungsmodell", "macro/nahrungsmodell.py"),
        _m("Jagd", "macro/brotbau.py:JagdBau"),
        _m("Vorrat kaufen", _l("nahrung_puffer nahrung_notkauf nahrung_auf_kante"), "rationen"),
    ),
    "waffen": (
        _m(
            "Produktion",
            _l(
                "Produktion produktions_hofplaetze hofplaetze_live plaetze_live hofvorrat_erschoepft"
            ),
            "produktion produktion_fenster",
        ),
        _m("Lederkette", _l("LederKette")),
        _m("Waffenlager", _l("waffenlager_ueberhang waffenlager_ausgleich")),
    ),
    "grund": (
        _m(
            "Wirtschaft",
            "macro/wirtschaft.py:Wirtschaft",
            "je_arbeiter vollbeschaeftigung lager_max",
        ),
        _m("Alter Ausbau", "macro/wirtschaft.py:Ausbau"),
        _m("Ertragsplaner", "macro/ertragsplaner.py:Ertragsplaner"),
        _m("Aufbauplan", "macro/aufbau_planer.py", "v14"),
        _m(
            "Haushalt",
            "macro/haushalt.py",
            "haushalt_rand steuer_runter steuer_ende stufe2_beliebt gute_dinge",
        ),
        _m("Lagerplatz", "macro/standort.py", "umzug"),
        _m(
            "Bauen und Platz",
            _l(
                "freier_platz haus_noetig kosten_spiel preis platz_sauber speicher_nachbauen baue_schnell baue_haus "
                "lager_knapp baue_lager kosten_aller wohnraum_fehlt v14_sperrflaechen"
            ),
            "abriss huetten_voraus neubau_sicher",
        ),
        _m(
            "Holz und Stein",
            _l("v16_holzfaeller haufen_hat_stein stein_joche v14_steinpflicht stein_pflicht"),
            "holzfaeller_max holzfaeller_je_baum holzfaeller_vorab holz_kaufen holz_spam stein_max stein_parallel "
            "steinbruch_zuerst steinbrueche_frueh joch_nach_stein",
        ),
        _m("Markt", _l("verkaufen")),
    ),
    "bestellung_raid": (
        _m(
            "Raid-Werbung",
            "baukasten/raid.py:RaidBestellung micro/tasks/raids.py:werbung baukasten/bestellung.py",
            "bestellung raids raid_reihenfolge",
        ),
        _m("Assassinen werben", _l("phase1 phase2 loewen_am_posten")),
    ),
    "bestellung_angriff": (
        _m(
            "Streitkolben",
            _l(
                "ruestung_kaufen anwerbewelle anwerbe_menge werbung_freigegeben werbung_gemerkt abwanderer_zuerst kaserne_am_feuer"
            ),
            "streitkolben schub einzelkauf aufloesen",
        ),
        _m("Bilanz", _l("bilanz_schritt bestzeit_split") + " strategy/bilanz.py"),
        _m("Heer", _l("phase2"), "heer_anteil"),
        _m("Endspurt", "strategy/endspurt.py", "endspurt"),
    ),
    "bestellung_verteidigung": (_m("Notwerbung", _l("phase2"), "notwerbung"),),
    "einsatz_raid": (
        _m("Raid-Einsatz", "baukasten/raid.py:RaidEinsatz", "ohne_angriff"),
        _m("Brandtrupp", "micro/tasks/raids.py:Brandtrupp"),
        _m("Reiterjagd", "micro/tasks/raids.py:Reiterjagd"),
        _m("Deckung", "micro/tasks/raids.py:Deckung"),
        _m("Vorstoss", "micro/tasks/vorstoss.py:Vorstoss", "vorstoss vorstoss_bis"),
        _m("Assassinen einzeln", "micro/tasks/assassinen.py:Einzeln", "assassinen"),
    ),
    "einsatz_angriff": (
        _m("Feldzug", "micro/tasks/feldzug.py:Feldzug", "weg angriff_ab"),
        _m("Alter Angriffstrupp", "micro/tasks/assassinen.py:Angriffstrupp"),
        _m("Lord-Anlauf der Assassinen", "micro/tasks/assassinen.py:Einzeln"),
    ),
    "einsatz_verteidigung": (
        _m("Waechter", "micro/tasks/waechter.py:Waechter", "waechter"),
        _m("Lordwache", "micro/tasks/lordwache.py", "lord_feuer"),
        _m("Fallenwache", "micro/tasks/fallenwache.py:Fallenwache", "fallen"),
        _m("Kornring", "macro/kornring.py:Kornring", "kornring gruben"),
        _m("Graben", "macro/kornring.py:Graben", "graben"),
        _m("Graben und Mauer setzen", _l("plane_graben schicke_graeber setze_mauer setze_grube")),
    ),
    "werkzeug": (
        _m(
            "Ausweichen",
            "baukasten/ausweichen.py kern/ausweichen.rs " + _l("ausweichen_kern"),
            "ausweichen",
        ),
        _m("Breite Aufstellung", "baukasten/formation.py:breit"),
        _m("Stapeln", "micro/tasks/assassinen.py:_stapel_rechnung"),
        _m("Zuweisung", "micro/zuweisung.py"),
    ),
    "scaling": (
        _m(
            "Raid-Sollzahlen",
            "micro/tasks/raids.py:werbung",
            "sklaven_soll reiter_soll deckung_soll",
        ),
        _m(
            "Bevoelkerung und Kasse",
            "macro/wirtschaft.py:Wirtschaft",
            "bevoelkerung_ziel kasse kasse_grenze kasse_stufe gold_ziel wachstum_boden penner",
        ),
    ),
    "acceleration": (
        _m("Eroeffnung", "macro/eroeffnung.py", "eroeffnung"),
        _m("Kausal-Entscheider", "learning/kausal.py", "entscheider kausal_horizont kausal_sparen"),
    ),
    "haende": (
        _m(
            "Befehlsweg",
            "execution/kernweg.py game/kern_port.py kern/haende.rs kern/leitung.rs kern/wege.rs kern/lib.rs "
            + _l("kernweg_senden"),
            "kernweg",
        ),
        _m("Auftragsbuch", "execution/auftragsbuch.py execution/ledger.py"),
        _m("Lord-Sperre", "execution/lordschutz.py"),
        _m("Spielbefehle", "game/ucp/befehl.py game/ucp/bauen.py game/ucp/drehwert.py"),
    ),
    "augen": (
        _m(
            "Lagebild",
            _l(
                "lords lage betriebe karte_laden pruefe_begehbar wegtest lies_mauer lies_logik lies_haltung runde_lesen eigene_gebaeude steht_bei"
            ),
        ),
        _m(
            "Weltbild des Kerns",
            "kern/welt.rs kern/beschuss.rs kern/feuer.rs kern/waechter.rs game/kern_leitung.py",
        ),
        _m(
            "Dienste",
            "services/bedrohung.py services/gefahrenzone.py services/gefecht.py services/schussfeld.py services/sicht.py "
            "services/spielwerte.py services/uebersicht.py services/wegkarte.py",
        ),
        _m("Spiel lesen", "game/ucp/aufbau.py game/ucp/steuerkarte.py"),
    ),
    "lernen": (
        _m(
            "Lernkreis",
            "learning/lernen.py learning/lernen_1v1.py learning/partie_lernen.py",
            "trainingsstand trainingsstand_ab",
        ),
    ),
    "rahmen": (
        _m(
            "Start und Ablauf",
            _l(
                "signal_da s32 schreib partie_pruefen warte_bis saat_laden saat_lesen saat_merken gefecht_starten ki_aus angleichen "
                "eins_gegen_eins_start anhaengen uebernehmen_start phase1 phase2 main"
            ),
            "angleich_tick anhaengen bis_tick eins_gegen_eins experiment fehlerprobe gegner gegner_erwartet gegner_ki karte kurz "
            "leere_ki mensch mensch_gegner minuten nur_phase2 pauseprobe plan plaetze regel50 start startliste stopp_tote tempo "
            "uebernehmen verbuendet ziel_tick zuschau_tempo",
        ),
        _m(
            "Wachen",
            "runtime/live/partner.py runtime/live/stillstand.py runtime/live/zielwaechter.py runtime/live/samurai_wache.py",
        ),
        _m("Laden und Speichern", "game/ucp/laden.py game/ucp/speichern.py"),
        _m("Baukasten", "baukasten/aufstellung.py baukasten/karte.py"),
    ),
}


def alle_module():
    return [m for module in KARTE.values() for m in module]


def module_von(teil):
    """Die Namen der Module eines Spielteils."""
    return [m.name for m in KARTE[teil]]


def teil_von(modul):
    """Die Spielteile eines Moduls: die andere Richtung der Karte."""
    return [t for t, module in KARTE.items() if any(m.name == modul for m in module)]


def _teile(stelle):
    datei, _, name = stelle.partition(":")
    return datei, name


def _pfad(datei):
    return KERN / datei[5:] if datei.startswith("kern/") else PAKET / datei


@functools.lru_cache(maxsize=None)
def _text(datei):
    return _pfad(datei).read_text(encoding="utf-8")


@functools.lru_cache(maxsize=None)
def _klassen_mit_schritt(datei):
    """{Klasse: Parameter von schritt} einer Python-Datei."""
    aus = {}
    if datei.endswith(".py"):
        for k in ast.parse(_text(datei)).body:
            if isinstance(k, ast.ClassDef):
                for f in k.body:
                    if isinstance(f, ast.FunctionDef) and f.name == "schritt":
                        aus[k.name] = tuple(a.arg for a in f.args.args[1:])
    return aus


def _klassen():
    """{Stelle: Parameter von schritt} jeder austauschbaren Klasse auf der Karte, jede einmal. Klassen im Lenker zaehlen nicht."""
    aus = {}
    for m in alle_module():
        datei, name = _teile(m.stellen[0])
        if datei != LENKER and name in _klassen_mit_schritt(datei):
            aus[m.stellen[0]] = _klassen_mit_schritt(datei)[name]
    return aus


def steckplaetze():
    """{Name des Steckplatzes: "paket.modul:Klasse"} fuer jede Klasse mit schritt auf der Karte."""
    aus = {}
    for stelle in _klassen():
        datei, name = _teile(stelle)
        aus[name.lower()] = "selfaware." + datei[:-3].replace("/", ".") + ":" + name
    return aus


def stand(modul):
    """Wie weit das Modul ist, gelesen aus dem Quelltext."""
    datei, name = _teile(modul.stellen[0])
    if datei.startswith("kern/"):
        return "Kern"
    if datei == LENKER:
        return "im Lenker"
    if name in _klassen_mit_schritt(datei):
        quelle = _text(LENKER) + _text("baukasten/raid.py")
        return "steckbar" if f'.klasse("{name.lower()}")' in quelle else "nicht benutzt"
    return "eigene Datei"


def _schalter_im_lenker():
    treffer = re.findall(r'arg\.get\("(\w+)"|arg\["(\w+)"\]|"(\w+)" in arg', _text(LENKER))
    return {t for gruppe in treffer for t in gruppe if t}


def fehlende_stellen():
    """Alle Stellen der Karte, die es im Code nicht gibt."""
    fehlt = []
    for m in alle_module():
        for stelle in m.stellen:
            datei, name = _teile(stelle)
            da = _pfad(datei).is_file() and (
                not name or re.search(rf"^\s*(class|def) {re.escape(name)}\b", _text(datei), re.M)
            )
            if not da:
                fehlt.append(stelle)
    return fehlt


def fehlende_schalter():
    """Alle Schalter der Karte, die der Lenker nicht kennt."""
    return sorted({s for m in alle_module() for s in m.schalter} - _schalter_im_lenker())


def schalter_ohne_modul():
    """Alle Schalter des Lenkers, die auf der Karte fehlen."""
    return sorted(_schalter_im_lenker() - {s for m in alle_module() for s in m.schalter})


def nicht_auf_der_karte():
    """Was es gibt, aber auf der Karte fehlt: Dateien von Gehirn und Haenden, Rust-Dateien des Kerns und alles, was oben im Lenker steht."""
    genannt = {s for m in alle_module() for s in m.stellen}
    dateien = {_teile(s)[0] for s in genannt}
    fehlt = []
    for ordner in ORDNER:
        for p in sorted((PAKET / ordner).glob("*.py")):
            rel = p.relative_to(PAKET).as_posix()
            if p.name != "__init__.py" and rel not in dateien:
                fehlt.append(rel)
    fehlt += [
        f"kern/{p.name}" for p in sorted(KERN.glob("*.rs")) if f"kern/{p.name}" not in dateien
    ]
    for k in ast.parse(_text(LENKER)).body:
        if isinstance(k, ast.FunctionDef | ast.ClassDef) and f"{LENKER}:{k.name}" not in genannt:
            fehlt.append(f"{LENKER}:{k.name}")
    return fehlt


def zahlen():
    """Die Messwerte oben auf der Karte."""
    baum = ast.parse(_text(LENKER))
    phase2 = next(k for k in baum.body if isinstance(k, ast.FunctionDef) and k.name == "phase2")
    klassen = _klassen()
    return {
        "zeilen": _text(LENKER).count("\n"),
        "phase2": phase2.end_lineno - phase2.lineno + 1,
        "schalter": len(_schalter_im_lenker()),
        "klassen": len(klassen),
        "formen": len(set(klassen.values())),
    }


def markdown():
    z = zahlen()
    zaehlung = collections.Counter(
        stand(m) for m in {m.stellen[0]: m for m in alle_module()}.values()
    )
    zeilen = [
        "# Modulkarte",
        "",
        "Erzeugt mit `python -m selfaware.baukasten.karte --schreiben`, nicht von Hand ändern. Quelle: `src/selfaware/baukasten/karte.py`. Plan: [Plan_Baukasten.md](Plan_Baukasten.md).",
        "",
        f"Gemessen: Der Lenker `{LENKER}` hat {z['zeilen']} Zeilen, `phase2` davon {z['phase2']}. Er kennt {z['schalter']} Schalter. "
        f"{z['klassen']} Klassen haben einen eigenen `schritt`, mit {z['formen']} verschiedenen Aufrufen.",
        "",
        "Bausteine je Stand: "
        + ", ".join(f"{k} {v}" for k, v in sorted(zaehlung.items()))
        + ". Eine Stelle mit zwei Rollen zählt einmal.",
        "",
        "| Stand | Bedeutung |",
        "|---|---|",
        "| steckbar | Eigene Klasse, der Lenker holt sie über den Steckplatz. Eine neue Version lässt sich per Aufstellung einsetzen. |",
        "| nicht benutzt | Eigene Klasse, die der Lenker nie baut. |",
        "| eigene Datei | Steht für sich, ist aber noch kein austauschbarer Baustein. |",
        "| im Lenker | Steht noch in `erstes_spiel.py`. |",
        "| Kern | Teil des Rust-Kerns. |",
    ]
    for teil, name in SPIELTEILE.items():
        zeilen += [
            "",
            f"## {name}",
            "",
            "| Modul | Stand | Stelle | Schalter |",
            "|---|---|---|---|",
        ]
        for m in KARTE[teil]:
            stellen = ", ".join("`" + s.replace(LENKER + ":", "Lenker ") + "`" for s in m.stellen)
            schalter = ", ".join(f"`{s}`" for s in m.schalter)
            zeilen.append(f"| {m.name} | {stand(m)} | {stellen} | {schalter} |")
    return "\n".join(zeilen) + "\n"


def main():
    if "--schreiben" in sys.argv[1:]:
        ZIEL.write_text(markdown(), encoding="utf-8", newline="\n")
    print(markdown())


if __name__ == "__main__":
    main()
