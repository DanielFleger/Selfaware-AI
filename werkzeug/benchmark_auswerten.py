"""Bewertet beobachtete Spielenden; fehlende Abnahmebelege bleiben offen.

Keine Logmeldung eines Lenkers kann den nativen Spielzustand ersetzen.
Aufruf: python werkzeug/benchmark_auswerten.py beobachtung.jsonl.gz
"""
import argparse
import gzip
import json
from pathlib import Path


def auswerten(rows, profil):
    rows = list(rows)
    if not rows:
        raise ValueError('Keine Beobachtungen')
    if any(r.get('coherent') is not True for r in rows):
        raise ValueError('Inkoharente Beobachtung')
    if any(b['tick'] <= a['tick'] for a, b in zip(rows, rows[1:])):
        raise ValueError('Takte nicht streng steigend; moeglicher Neustart')
    own = profil['our_players']
    enemies = profil['enemy_players']
    first, last = rows[0], rows[-1]
    for sp in own + enemies:
        if first.get('lords', {}).get(str(sp), {}).get('health', 0) <= 0:
            raise ValueError('Anfangsbeleg fuer Lord %s fehlt' % sp)
    expected = profil['enemy_ai_ids']
    if any([r['ai'][sp - 1] for sp in enemies] != expected for r in rows):
        raise ValueError('Gegner-KI weicht vom Profil ab')
    remaining = last.get('lords', {})
    fractions = {}
    for sp in own:
        start = first['lords'][str(sp)]
        end = remaining.get(str(sp), {})
        if end and end.get('uid') != start['uid']:
            raise ValueError('Eigener Lord ausgetauscht')
        fractions[str(sp)] = max(0, end.get('health', 0)) / start['health']
    # alive wird vom Spiel erst am Ende belegt; vorherige Nullen sind kein Tod.
    ended = last['over'] == 1 and last['view'] in (14, 16)
    enemy_dead = all(remaining.get(str(sp), {}).get('health', 0) <= 0
                     and last['alive'][sp - 1] == 0 for sp in enemies)
    own_alive = all(fractions[str(sp)] > 0 and last['alive'][sp - 1] == 1
                    for sp in own)
    won = ended and enemy_dead and own_alive
    dominant = won and min(fractions.values()) >= profil['evaluation']['minimum_own_lord_health_fraction']
    return {
        'observed_result': 'win' if won else ('other_end' if ended else 'incomplete'),
        'terminal_tick': last['tick'], 'terminal_tick_is_observation_upper_bound': True,
        'observations': len(rows), 'own_lord_health_fraction': fractions,
        'observed_dominant_win': dominant,
        'within_median_target_tick': won and last['tick'] <= profil['evaluation']['median_win_tick_max'],
        'evaluation_eligible': False,
        'qualification_pending': ['held-out seed and allocation', 'start gate by deadline',
                                  'command/write audit and natural-death provenance',
                                  'all controller snapshots coherent'],
        'note': 'Entwicklungslauf; zaehlt nicht zur vorab festgelegten 20-Partien-Abnahme.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('observation', type=Path)
    parser.add_argument('--profil', type=Path, default=Path(__file__).resolve().parents[1] / 'daten/benchmarks/branching_fortunes_v1.json')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    with gzip.open(args.observation, 'rt', encoding='utf-8') as f:
        result = auswerten((json.loads(line) for line in f), json.loads(args.profil.read_text(encoding='utf-8')))
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(text + '\n', encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
