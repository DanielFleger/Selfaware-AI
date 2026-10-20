#!/usr/bin/env bash
# B-140 Versuchsreihe (Daniel 20.10. 22:09: "es sind so viele Variablen, dass man das schwer bewerten kann, aber dafuer die
# Tests"): ab dem Pruefstand-Spielstand nacheinander mit fester Angriffsgroesse angreifen (angriff_ab=N) und einmal nach der
# Gefechtsrechnung; je Lauf eine Zeile in daten/pruefstand_reihe_<stempel>.txt.
# Aufruf: bash werkzeug/pruefstand_reihe.sh "40 70 100 150 rechnung" [Spielstand] [bis_tick]
cd "$(dirname "$0")"
VARIANTEN=${1:-"40 70 100 150 rechnung"}
STAND=${2:-"B140 Burg Franz T40126"}
BIS=${3:-100000}
REIHE=$(date +%Y%m%d_%H%M%S)
AUS=../daten/pruefstand_reihe_${REIHE}.txt
A=$(cat "$TEMP/liga_args.txt")
echo "Versuchsreihe $REIHE ab '$STAND' bis Tick $BIS: $VARIANTEN" | tee "$AUS"
for V in $VARIANTEN; do
    S=$(date +%Y%m%d_%H%M%S)
    LOG=../daten/pruefstand_${S}_${V}_konsole.txt
    EXTRA=""
    [ "$V" != "rechnung" ] && EXTRA="angriff_ab=$V"
    SHC_INSTANZ=5 SHC_SPIELER=1 python -u erstes_spiel.py $A tempo=300 minuten=40 bis_tick=$BIS gegner=1 gegner_ki=3 \
        "karte=Liga_Grumpy Neighbors" plaetze=0,2 stellung=nein "start=$STAND" $EXTRA > "$LOG" 2>&1
    ANGRIFF=$(grep -oE "FELDZUG ANGRIFF: [0-9]+ Truppen[^;]{0,60}bei Tick [0-9]+" "$LOG" | head -1 | sed -E 's/ \(.*\) gemeinsam auf Lord [0-9]+ \(Leben [0-9]+\)//')
    TOT=$(grep -oE "FELDZUG: Lord [0-9]+ tot bei Tick [0-9]+ - [0-9]+ Streitkolben ueberlebten" "$LOG" | head -1)
    ENDE=$(grep -oE "^[0-9]+ \|" "$LOG" | tail -1 | tr -d ' |')
    VERLUST=$(grep -oE "eigene Truppen verloren [0-9]+" "$LOG" | tail -1)
    VORBEI=$(grep -c "'over': 1" "$LOG")
    echo "$V | Angriff: ${ANGRIFF:-keiner} | Franz-Lord: ${TOT:-lebt} | letzter Tick $ENDE | $VERLUST | Spielende-Bildschirm: $VORBEI | $(basename "$LOG")" | tee -a "$AUS"
done
echo "Reihe fertig" | tee -a "$AUS"
