"""B-145 (Entwurf): GamePort ueber den SamurAI-Kern - jeden Takt beobachten, ueber den Auftragsring handeln.

Beobachtung: Weltbild aus dem gemeinsamen Speicher (selfaware.game.kern_leitung), je Takt. Handeln: "move" (Argumente
x, y; actors = Einheiten) und "attack" (targets[0] = Einheit oder Gebaeude) werden zu Ring-Auftraegen; die Einheiten
werden dabei dem Kern uebergeben (ein Schreiber je Einheit). Bestaetigt wird erst, wenn die Wirkung im Speicher sichtbar
ist (neue Gruppe und Laufziel bzw. Angriffsziel), nie wegen der Quittung. Abgelehnt, wenn der Kern -4/-5 meldet.
"""

from selfaware.domain import Entity, EntityRef, Resources, Snapshot
from selfaware.game import kern_leitung as KL
from selfaware.game.ports import (
    Observation,
    ObservedOutcome,
    OutcomeStatus,
    Receipt,
    ReceiptStatus,
)

ZIEL_ABSTAND = 2


class KernPort:
    def __init__(self, leitung):
        self.leitung = leitung
        self._offen = {}
        self._zuletzt = None

    def epoche_kennung(self):
        w = self.leitung.lesen()
        return f"{self.leitung.name}-e{w.epoche}"

    def _snapshot(self, session, w):
        if session.epoch != f"{self.leitung.name}-e{w.epoche}":
            raise ValueError(
                f"Spiel-Epoche gewechselt: {session.epoch} -> {self.leitung.name}-e{w.epoche}"
            )
        entities = [
            Entity(
                EntityRef("unit", e["nr"], None),
                e["besitzer"],
                e["typ"],
                e["x"],
                e["y"],
                max(e["leben"], 0),
            )
            for e in w.einheiten.values()
            if e["besitzer"] >= 0 and e["typ"] >= 0
        ]
        entities += [
            Entity(
                EntityRef("building", g["nr"], None),
                g["besitzer"],
                g["typ"],
                g["x"],
                g["y"],
                max(g["leben"], 0),
            )
            for g in w.gebaeude.values()
            if g["besitzer"] >= 0 and g["typ"] >= 0
        ]
        facts = {
            "kern_version": w.kern,
            "epoche": w.epoche,
            "graben_geplant": w.graben_geplant,
            "graben_ausgehoben": w.graben_ausgehoben,
        }
        vorrat = {k: max(v, 0) for k, v in w.vorrat.get(session.player, {}).items()}
        snapshot_id = f"{session.epoch}-t{w.tick}"
        return Snapshot(session, snapshot_id, w.tick, Resources(vorrat), tuple(entities), facts)

    def observe(self, session):
        w = self.leitung.lesen()
        if w is None:
            raise RuntimeError("kein vollstaendiges Weltbild gelesen")
        snapshot = self._snapshot(session, w)
        self._zuletzt = w
        outcomes = []
        for action_id, auftrag in list(self._offen.items()):
            status = self._pruefen(auftrag, w)
            if status is not None:
                outcomes.append(
                    ObservedOutcome(action_id, status, snapshot.snapshot_id, auftrag["art"])
                )
                del self._offen[action_id]
        return Observation(snapshot, tuple(outcomes))

    def _pruefen(self, auftrag, w):
        ergebnisse = [self.leitung.ergebnis(n) for n in auftrag["nummern"]]
        if any(e is not None and e < 0 for e in ergebnisse):
            return OutcomeStatus.REJECTED
        lebend = [w.einheiten[nr] for nr in auftrag["einheiten"] if nr in w.einheiten]
        if not lebend:
            return None
        neu = [e for e in lebend if e["gruppe"] != auftrag["gruppen"].get(e["nr"])]
        if len(neu) != len(lebend):
            return None
        if auftrag["art"] == "move":
            x, y = auftrag["ziel"]
            ok = all(max(abs(e["laufx"] - x), abs(e["laufy"] - y)) <= ZIEL_ABSTAND for e in lebend)
        else:
            ok = all(
                e["zieleinheit"] == auftrag["ziel"] or e["zielgebaeude"] == auftrag["ziel"]
                for e in lebend
            )
        return OutcomeStatus.CONFIRMED if ok else None

    def submit(self, session, intent):
        name = intent.command.name
        einheiten = [a.slot for a in intent.actors if a.kind == "unit"]
        if name not in ("move", "attack") or not einheiten:
            return Receipt(
                intent.intent_id,
                ReceiptStatus.REJECTED,
                f"nicht unterstuetzt: {name} / {len(einheiten)}",
            )
        if name == "attack" and not intent.targets:
            return Receipt(intent.intent_id, ReceiptStatus.REJECTED, "attack ohne Ziel")
        w = self._zuletzt or self.leitung.lesen()
        gruppen = {nr: w.einheiten[nr]["gruppe"] for nr in einheiten if nr in w.einheiten}
        nummern = [self.leitung.auftrag(KL.UEBERNEHMEN, nr) for nr in einheiten]
        if name == "move":
            ziel = (int(intent.command.arguments["x"]), int(intent.command.arguments["y"]))
            nummern += [self.leitung.auftrag(KL.LAUF, nr, *ziel) for nr in einheiten]
        else:
            t = intent.targets[0]
            ziel = t.slot
            art = KL.ANGRIFF_EINHEIT if t.kind == "unit" else KL.ANGRIFF_GEBAEUDE
            nummern += [self.leitung.auftrag(art, nr, ziel) for nr in einheiten]
        self._offen[intent.intent_id] = {
            "art": name,
            "einheiten": einheiten,
            "ziel": ziel,
            "nummern": nummern,
            "gruppen": gruppen,
        }
        return Receipt(intent.intent_id, ReceiptStatus.DISPATCHED, f"{len(nummern)} Ring-Auftraege")

    def close(self):
        self._offen.clear()
