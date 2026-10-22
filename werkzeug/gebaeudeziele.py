"""Schadensfaehigkeit vor Zielwert: Spielcode und gesonderte Steinablagen-Regel."""
import json
from pathlib import Path
_DATEN=json.loads((Path(__file__).resolve().parents[1]/'daten/gebaeude_schadensregel.json').read_text())
UNZERSTOERBAR=frozenset(int(t) for t,w in _DATEN['values'].items() if not w)|{21}
def angreifbar(gebaeude):
 typ=gebaeude.get('typ')
 return str(typ) in _DATEN['values'] and typ not in UNZERSTOERBAR

def zielwerte(werte):
 return {typ:wert for typ,wert in werte.items() if angreifbar({'typ':typ})}
