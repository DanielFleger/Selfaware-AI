"""Automatic match receipts and lessons, alongside the existing online learner.

No opening experiments or tactical parameter changes. Learned loss/range model
values are already consumed by gefahrenschutz.Lage in subsequent rounds/matches.
"""
import json
import os
import re
import tempfile
import uuid
from pathlib import Path


def atomar(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def modell(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError) as ex:
        return {'lesefehler':str(ex)} # retain the original; telemetry must not disable the AI


def entdeckt_zaehlen(text):
    """B-213 (Daniel 24.10.: das Lernbuch soll vorarbeiten): je Partie zaehlen, vor wie vielen Schuetzen eine Assassine floh
    und mit welchem Leben - von Hand aus 14 Partien gezogen ergab das 42 % Fluchten vor EINEM Schuetzen bei vollem Leben.
    Dazu, wie oft stattdessen der Gegenschlag gerechnet wurde."""
    aus = {'gesamt': 0, 'ein_schuetze': 0, 'volles_leben': 0, 'gegenschlag_schuetze': text.count('GEGENSCHLAG SCHUETZE'),
           'trotz_entdeckt': text.count('TROTZ ENTDECKT')}
    for m in re.finditer(r'ENTDECKT \d+ bei \([^)]*\).*?: Spaeher Typ \d+ in \d+ Feldern, (\d+) Schuetzen mit Linie, Leben (\d+)', text):
        aus['gesamt'] += 1
        if int(m.group(1)) == 1:
            aus['ein_schuetze'] += 1
        if int(m.group(2)) >= 11000:
            aus['volles_leben'] += 1
    return aus


def ausgang(over, killers, player, enemies):
    enemies = set(enemies)
    if over != 1 or not enemies or player in enemies:
        return 'unbestaetigt'
    if any(p not in killers or not isinstance(killers[p], int) or killers[p] < 0 for p in enemies | {player}):
        return 'unbestaetigt'
    if killers[player] > 0:
        return 'niederlage'
    if all(killers[p] > 0 for p in enemies):
        return 'sieg'
    return 'unbestaetigt'


class Lernbuch:
    def __init__(self, daten):
        self.daten = Path(daten)
        self.modellpfad = Path(os.environ.get('SHC_LEARNING_DIR') or self.daten)/'verlust_raten.json'

    def beginnen(self, player, enemies, console, context):
        run = {'id': uuid.uuid4().hex, 'spieler': player, 'feinde': sorted(set(enemies)),
               'konsole': str(console), 'kontext': context, 'status': 'laeuft',
               'lernprofil':os.environ.get('SHC_LEARNING_PROFILE'),
               'modell_vorher': modell(self.modellpfad)}
        atomar(self.daten / 'lernen' / (run['id'] + '.json'), run)
        return run

    def beenden(self, run, over=0, killers=None, tick=None, reason='beendet'):
        path = self.daten / 'lernen' / (run['id'] + '.json')
        stored = modell(path)
        if stored.get('status') != 'laeuft':
            return stored
        run = dict(stored)
        run.update(status=ausgang(over, killers or {}, run['spieler'], run['feinde']),
                   native={'gameover': over, 'lord_killed_by': killers or {}, 'tick': tick}, grund=reason)
        try:
            text = Path(run['konsole']).read_text(encoding='utf-8', errors='replace')
        except OSError:
            text = ''
        run['beobachtungen'] = {k: text.count(k) for k in ('HUNGER', 'STILLSTAND', 'ABGELEHNT', 'angeworben')}
        run['entdeckt'] = entdeckt_zaehlen(text)
        after = modell(self.modellpfad)
        run['modell_nachher'] = after
        changed = ('lesefehler' not in run['modell_vorher'] and 'lesefehler' not in after
                   and run['modell_vorher'].get('typen', {}) != after.get('typen', {}))
        lessons = []
        if 'lesefehler' in run['modell_vorher'] or 'lesefehler' in after:
            lessons.append('Ein Modell war nicht lesbar; die Originaldatei wurde vom Lernbuch nicht ersetzt.')
        if changed:
            lessons.append('Gemessene Verluste und Laufzeiten haben das vorhandene Gefahrenmodell aktualisiert; folgende Entscheidungen laden diese Werte automatisch.')
        if run['beobachtungen']['HUNGER']:
            lessons.append('Nahrung war knapp: Nahrungsversorgung als Problem festgehalten; Ursache noch nicht belegt.')
        if run['beobachtungen']['STILLSTAND']:
            lessons.append('Stillstand gemeldet: Weg-/Arbeitsauftraege im Lageprotokoll pruefen; Ursache noch nicht belegt.')
        e = run.get('entdeckt') or {}
        if e.get('gesamt', 0) >= 20 and e['ein_schuetze'] * 100 >= 30 * e['gesamt']:
            lessons.append('Assassinen flohen %d-mal, davon %d-mal vor einem einzelnen Schuetzen (%d %% bei vollem Leben); Gegenschlag gerechnet: %d-mal. Die Gefechtsrechnung vor der Flucht (B-213) greift hier noch zu selten.' % (
                e['gesamt'], e['ein_schuetze'], 100 * e['volles_leben'] // max(1, e['gesamt']), e['gegenschlag_schuetze']))
        if run['status'] == 'sieg':
            lessons.append('Sieg durch native Lord-Daten bestaetigt. Daraus allein folgt keine bewiesene Ursache fuer den Sieg.')
        elif run['status'] == 'niederlage':
            lessons.append('Eigener Lord laut nativen Daten besiegt; Niederlage festgehalten.')
        else:
            lessons.append('Kein vollstaendig belegter Partieausgang; kein Sieg aus Konsolentext abgeleitet.')
        run['schluesse'] = lessons
        atomar(path, run)
        return run
