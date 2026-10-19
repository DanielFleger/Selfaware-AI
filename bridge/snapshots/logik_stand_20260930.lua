--[[ Village Studio - Live-Logik fuer Stronghold Crusader
     Neu geschrieben am 30.08.2026.

     Die Vorgaengerfassung war ueber rund vierzig Textersetzungen gewachsen
     und dabei zerbrochen. Diese Fassung enthaelt nur, was im Spiel BELEGT
     ist - jede Adresse und jeder Wert wurde gemessen, nichts geraten.
     Die alte Datei liegt als logik_alt_20260830.lua daneben.

     Wird von init.lua nachgeladen: sobald sich diese Datei aendert, ist die
     neue Fassung im naechsten Tick aktiv. Bei einem Syntaxfehler bleibt die
     laufende Fassung stehen und es kommt eine Warnung ins Log.
]]--

local VS = ...

--============================================================================
-- 1. Adressen. Alle im laufenden Spiel gemessen.
--============================================================================

-- Kachel-Ebenen der Karte. NICHT ueber KACHELGRENZE hinaus lesen:
-- dahinter steht Zufallsspeicher (29.08.: erfundene Kacheln fuehrten zum
-- Absturz, weil sie an destroyWall weitergereicht wurden).
local LOGIK        = 0x01BF8368   -- int  je Kachel: Gelaende- und Baubits
local HOEHE        = 0x01D32C38   -- byte je Kachel: bei Mauern die GESUNDHEIT
local GRUNDHOEHE   = 0x01D46648   -- byte je Kachel: Hoehe ohne Bebauung
local BESITZER     = 0x01D5A058   -- byte je Kachel, zaehlt AB 0
local SCHADEN      = 0x01DBC2A8   -- byte je Kachel
local KACHELGRENZE = 80400

-- Mauerwerk: genau die Bits, die destroyWall loescht (ohne Schutt).
-- 0x100000 ist NICHT dabei - das ist L_RIVER, ein Irrtum vom 29.08.
local MAUERBIT = 0x100 | 0x200 | 0x800 | 0x10000 | 0x400000

-- Gebaeudetabelle. Ein Eintrag ist 0x32C Bytes, Anzahl steht bei +0x08.
--
-- ACHTUNG, der haeufigste Fehler: Das Array beginnt erst bei GEBAEUDE+0x14.
-- Unsere Basis laesst das weg, deshalb sind in ALLEN Offsets hier 0x14
-- eingerechnet - nicht nur beim Leben. Wer Werte aus der Ghidra-Referenz
-- uebernimmt, muss ueberall 0x14 addieren:
--   Referenz +0xD0 Zustand -> hier 0xE4      Referenz +0xD2 Typ -> hier 0xE6
--   Referenz +0xD6 Besitzer -> hier 0xEA     Referenz +0x10C Leben -> hier 0x120
local GEBAEUDE     = 0xF98520
local G_SCHRITT    = 0x32C
local G_ZUSTAND    = 0xE4    -- word: 0 = kein Gebaeude, 3 = abgerissen
local G_TYP        = 0xE6    -- word
local G_BESITZER   = 0xEA    -- word: Spielernummer (NICHT ab 0)
-- 30.08.: Hier fehlte der 0x14-Versatz - Gebaeude starben trotz Wacht.
local G_LEBEN      = 0x120   -- word
local G_MAXLEBEN   = 0x122   -- word

-- Spielerdaten: Waren bei +0x4D0 als int[25] (2 Holz, 4 Stein, 15 Gold).
local SPIELERDATEN = 0x0115BDF8
local SD_SCHRITT   = 0x39F4
local SD_WAREN     = 0x4D0

-- Baukosten: int[110][5] je 20 Byte (Holz, Stein, Eisen, Pech, Gold).
-- Index ist die Laufzeit-Gebaeudenummer. VOR dem Gefecht ist die Tabelle
-- leer - wer da liest, misst Nullen und haelt die Adresse fuer falsch.
local KOSTEN       = 0x01124CF4
local KOSTENFELD   = { holz = 0, stein = 4, eisen = 8, pech = 12, gold = 16 }

-- Zeit und Tempo. Ticks je Sekunde = Tempowert (gemessen bei 20/50/100/200).
-- Tag 50, Woche 200, Monat 800, Jahr 9600 Ticks.
local TICKZAEHLER  = 0x0117CADC
local TEMPO        = 0x1FE7DD8
local PAUSE        = 0x1FEA054
-- Tick-genaue Pause (30.09.2026, Selfaware-AI, Daniels Idee): { naechster, alle, bis, anzahl }
-- Oben deklariert, weil einzelbefehl und der Taktgeber beide darauf zugreifen.
local tickPause    = nil
-- Lade-Pause (30.09.2026, M7.02): { letzter, nachlauf } - haelt beim ersten Tick
-- nach einem Laden an, egal ob der geladene Stand frueher oder spaeter liegt.
local ladePause    = nil
-- Lord-Wacht (30.09.2026, M4.04): { lords = {nr -> {...}}, haltTreffer, haltTod, alle, naechste }
local lordWacht    = nil
-- Einheiten-Wacht (04.10.2026): { e = {nr -> {zx, zy}}, alle, naechste } - jede Zielaenderung je Tick
local einheitWacht = nil
-- Festhalten (04.10.2026): nr -> { x, y, gesetzt, letzter } - Ziel gegen KI/Arbeit/Lord-Logik halten
local festhalten   = {}
local angriffReserve = nil   -- Gruppen je Takt reserviert (modul-lokal: UCP verbietet globale Variablen - 04.10.)
local angriffSchlange = {}   -- Angriffsbefehle, die nacheinander abgesetzt werden (je einer, bis seine Gruppe steht)
local angriffWarten = nil    -- { gruppe, einheiten, tick } des zuletzt abgesetzten Angriffs
-- Zickzack (04.10.2026): { nr, a, b, alle, bis, t0, n } - Richtungswechsel je K Ticks, Feinposition je Tick
local zickzack     = nil

-- Einheiten befehligen (05.09.2026). Blosses Schreiben der Ziel-Felder bewegt
-- eine Einheit NICHT (gemessen) - der Wegplan wird in setDestinationForUnit
-- berechnet. Signatur am ret-imm geprueft: dreimal RET 0x10 = 4 Argumente,
-- thiscall -> exposeCode(adr, 5, 1), Aufruf (this, nr, x, y, reusePathing).
local UNITS_STATE  = 0x01387F38
local ADR_SETDEST  = 0x0053D3D0
local _setDest                 -- lazy, erst beim ersten Befehl scharfgestellt

--============================================================================
-- 2. Kleine Helfer
--============================================================================

local function ware(spieler, art)
  return core.readInteger(SPIELERDATEN + spieler * SD_SCHRITT + SD_WAREN + art * 4)
end

local function wareSetzen(spieler, art, menge)
  core.writeInteger(SPIELERDATEN + spieler * SD_SCHRITT + SD_WAREN + art * 4, menge)
end

-- Leere KI (06.10.2026, Daniel: "Spiel gegen eine leere KI um zu testen, wie man am schnellsten 10k Gold bekommt").
-- Ohne Gegner endet ein Gefecht sofort als Sieg (gemessen 06.10.: gameOver 1, Endbildschirm bei Tick 2.665). Darum
-- spielt ein echter Gegner mit, dem jede Runde alle Waren 2-24 (Holz bis Ruestung, Gold = 15) auf 0 gesetzt werden:
-- sein Lord steht, er kann aber nichts bauen und nichts anwerben.
local leereKI = {}
local function leereKITick()
  for sp, _ in pairs(leereKI) do
    for w = 2, 24 do wareSetzen(sp, w, 0) end
  end
end

local function tick()
  return core.readInteger(TICKZAEHLER) or 0
end

local function gebaeudeAnzahl()
  local n = core.readInteger(GEBAEUDE + 8)
  if n == nil or n < 2 or n > 4000 then return nil, n end
  return n
end

--============================================================================
-- 3. Mauerwacht
--
-- BELEGT am 30.08.2026, gemessen im Treffer-Moment:
--   Logik 0x100 -> 0x100 (unveraendert), Hoehe 98 -> 77, Schaden 0 -> 1
-- Beschuss laesst die Logikbits also unangetastet und senkt die HOEHE.
-- Die Hoehe ist die Gesundheit einer Mauerkachel.
--
-- Drei harte Grenzen, aus Fehlschlaegen desselben Tages gelernt:
--   1. Nur Kacheln EINES Besitzerwerts, nicht die ganze Karte.
--   2. Nur Kacheln, die beim Scharfstellen volle Mauerhoehe hatten.
--   3. Es werden NIE Logikbits geschrieben - nur Hoehe und Schaden. Damit
--      kann diese Wacht prinzipiell keine Mauer erzeugen, nur erhalten.
--      (Ohne Grenze 3 entstanden Phantommauern ueber die halbe Karte.)
--
-- Der Schadenswert MUSS mitzurueckgesetzt werden: sonst laeuft er hoch und
-- das Spiel zerstoert die Kachel trotz gehaltener Hoehe.
--============================================================================

local mauerwacht = {}   -- schluessel -> { kacheln, ziel, anzahl, wieder, modus }

local function mauerwachtStart(schluessel, besitzer, zielHoehe, modus)
  local roh, hoechstJeArt, gefunden = {}, {}, 0
  for k = 0, KACHELGRENZE - 1 do
    if core.readByte(BESITZER + k) == besitzer then
      local lg = core.readInteger(LOGIK + k * 4)
      if (lg & MAUERBIT) ~= 0 then
        local h = core.readByte(HOEHE + k)
        roh[k] = { lg, h }
        local art = lg & MAUERBIT
        if hoechstJeArt[art] == nil or h > hoechstJeArt[art] then
          hoechstJeArt[art] = h
        end
        gefunden = gefunden + 1
      end
    end
  end

  local kacheln, genommen, zuNiedrig = {}, 0, 0
  for k, v in pairs(roh) do
    local gesund = hoechstJeArt[v[1] & MAUERBIT]
    local eigene = v[2]                     -- Ursprungshoehe DIESER Kachel
    local ziel = zielHoehe or math.floor((gesund or eigene) / 2)
    if ziel < 1 then ziel = 1 end

    -- SICHERUNG, zweimal am 30.08. schmerzhaft gelernt:
    -- Ein Mauerbit auf einer Kachel heisst NICHT, dass dort eine Mauer steht.
    -- Es sitzt auch unter Lagerplaetzen, Torhaeusern und geplanten Bauten.
    -- Wird deren niedrige Kachel auf Mauerhoehe gehoben, entsteht eine
    -- Erhebung, ueber die niemand mehr laeuft - Softlock.
    -- Deshalb: Kacheln, die nicht klar ueber dem Ziel liegen, bleiben aussen
    -- vor. Angehoben wird grundsaetzlich nichts.
    if eigene > ziel then
      kacheln[k] = { ziel, eigene }         -- 1 = Zielhoehe, 2 = Ursprungshoehe
      genommen = genommen + 1
    else
      zuNiedrig = zuNiedrig + 1
    end
  end

  mauerwacht[schluessel] = { kacheln = kacheln, anzahl = genommen,
                             wieder = 0, modus = modus or "halten" }
  log(INFO, string.format(
    "MAUERWACHT %s: %d von %d Kacheln uebernommen, %d zu niedrig (Lager, Torhaeuser, Baufelder - werden NIE angehoben). Zielhoehe %s, Modus %s.",
    tostring(schluessel), genommen, gefunden, zuNiedrig, tostring(zielHoehe or "halb"), modus or "halten"))
  return true
end

local function mauerwachtTick()
  for schluessel, w in pairs(mauerwacht) do
    for k, v in pairs(w.kacheln) do
      local h = core.readByte(HOEHE + k)
      if h < v[2] then                       -- Ausloeser: Hoehe verloren
        if w.modus == "melden" then
          core.writeInteger(PAUSE, 1)
          log(INFO, string.format("TREFFER Tick %d | Kachel %d: Hoehe %d -> %d. SPIEL PAUSIERT.",
            tick(), k, v[2], h))
          mauerwacht[schluessel] = nil
          return
        elseif h ~= v[1] then
          core.writeByte(HOEHE + k, v[1])
          core.writeByte(SCHADEN + k, 0)
          w.wieder = w.wieder + 1
          if w.wieder <= 3 or w.wieder % 1000 == 0 then
            log(INFO, string.format("MAUER Tick %d | Kachel %d auf %d gehalten (insgesamt %d).",
              tick(), k, v[1], w.wieder))
          end
        end
      end
    end
  end
end

--============================================================================
-- 4. Gebaeudewacht
--
-- Gebaeude haben ein echtes Lebensfeld (+0x10C) samt Maximum (+0x10E) - hier
-- muss nichts ueber Hoehen erschlossen werden.
--
-- Verhalten nach Daniels Vorgabe: Sobald ein Gebaeude Leben verliert, faellt
-- es sofort auf den Zielwert (Standard 1) und bleibt dort. Es kann damit
-- nicht mehr zerstoert werden, sieht aber schwer beschaedigt aus.
--
-- Neue Gebaeude werden mitgenommen: die Wacht laeuft ueber die ganze
-- Tabelle, nicht ueber eine Liste vom Scharfstellen. Deshalb greift sie auch
-- bei allem, was erst spaeter gebaut wird.
--============================================================================

local gebaeudewacht = {}   -- spieler -> { ziel, wieder }

local function gebaeudewachtTick()
  local n = gebaeudeAnzahl()
  if n == nil then return end
  for spieler, w in pairs(gebaeudewacht) do
    for i = 1, n - 1 do
      local b = GEBAEUDE + i * G_SCHRITT
      local zustand = core.readSmallInteger(b + G_ZUSTAND)
      if zustand ~= 0 and core.readSmallInteger(b + G_BESITZER) == spieler then
        local leben = core.readSmallInteger(b + G_LEBEN)
        local maxLeben = core.readSmallInteger(b + G_MAXLEBEN)
        if leben ~= nil and maxLeben ~= nil and maxLeben > 0 then
          -- Bei genau 1 Leben toetet der naechste Treffer. Deshalb wird auch
          -- der Zustand 3 (zerstoert) zurueckgenommen - das Gebaeude kommt
          -- zurueck. UNGEPRUEFT: ob das Spiel mit einer Auferstehung sauber
          -- umgeht, muss der Test zeigen.
          if zustand == 3 then
            core.writeSmallInteger(b + G_ZUSTAND, 1)
            core.writeSmallInteger(b + G_LEBEN, w.ziel)
            w.wieder = w.wieder + 1
            if w.wieder <= 5 or w.wieder % 200 == 0 then
              log(INFO, string.format("GEBAEUDE Tick %d | Spieler %d Eintrag %d ZURUECKGEHOLT (war zerstoert), Leben %d.",
                tick(), spieler, i, w.ziel))
            end
          elseif leben < maxLeben and leben ~= w.ziel then
            core.writeSmallInteger(b + G_LEBEN, w.ziel)
            w.wieder = w.wieder + 1
            if w.wieder <= 3 or w.wieder % 500 == 0 then
              log(INFO, string.format("GEBAEUDE Tick %d | Spieler %d Eintrag %d (Typ %d): Leben %d/%d -> %d (insgesamt %d).",
                tick(), spieler, i, core.readSmallInteger(b + G_TYP),
                leben, maxLeben, w.ziel, w.wieder))
            end
          end
        end
      end
    end
  end
end

--============================================================================
-- 4b. Einheiten - Basis am 30.08.2026 aus dem Maschinencode von spawnUnit
--     (0x53E440) BELEGT, nicht aus einer Struktur abgeleitet:
--
--       0053e443  MOV ECX,0x1              Vergabe beginnt bei 1
--       0053e44b  LEA EAX,[EBX + 0xb30]    units[1].logicalState = 0x01388A68
--       0053e451  CMP word ptr [EAX],0x0   belegt-Test: logicalState gegen 0
--       0053e465  ADD EAX,0x490            Schrittweite 1168
--       0053e472  CMP EDI,dword ptr [EBX]  Grenze = UnitsState+0x00
--       0053e46a  CMP EDI,0x9c4            2500 Plaetze
--
--     UnitsState = 0x01387F38, units[] bei +0x614 -> units[0] = 0x0138854C
--     Gegenprobe: 0x0138854C + 1168 + 0x8C = 0x01388A68  geht auf
--
-- WARUM DER ERSTE ANLAUF SCHEITERTE - vier Fehler, KEINER in der Adresse:
--   1. Belegt-Test ueber Leben bzw. Typ. Ein freier Platz behaelt beides von
--      der gestorbenen Einheit. Das Spiel prueft logicalState (+0x8C).
--   2. Schleife ab 0. Platz 0 wird nie vergeben.
--   3. Grenze 0x01387F3C (DAT_UnitCount) statt 0x01387F38 (maxUnitCount).
--   4. DER EIGENTLICHE FEHLER: Besitzer 0 wurde als Spieler mitgeprueft.
--      Besitzer 0 ist die neutrale Seite - Tiere und herrenlose Bauern.
--      Die hat nie einen Lord. Der Messwert vom 30.08. um 21:36 war in
--      Wahrheit ein Treffer:  Spieler 1 -> 1 Lord,  Spieler 2 -> 1 Lord.
--============================================================================

local EINHEITEN   = 0x0138854C          -- units[0]
local E_SCHRITT   = 1168
local E_MAX       = 0x01387F38          -- maxUnitCount (UnitsState+0x00)
local E_ZUSTAND   = 0x08C               -- logicalState, 0 = ULS_INVISIBLE = frei
local E_TYP       = 0x08E
local E_BESITZER  = 0x096
local E_UID       = 0x098
local E_X         = 0x0C4   -- Standort  (short)
local E_Y         = 0x0C6
local E_ZIEL_X    = 0x0C8   -- Ziel      (short) - NICHT der Standort
local E_ZIEL_Y    = 0x0CA
local E_ZIEL_KACHEL = 0x0D8 -- destinationTilePosition (int)
local E_LEBEN     = 0x3C8   -- INT, nicht short
local UT_LORD     = 55

-- Belegt heisst logicalState ~= 0. NICHT ueber Typ oder Leben pruefen.
local function eBelegt(i)
  return (core.readSmallInteger(EINHEITEN + i * E_SCHRITT + E_ZUSTAND) or 0) ~= 0
end

--============================================================================
-- Totschlagtest - die Widerlegungskriterien stehen VOR der Messung fest.
--
--  1  Platz 0 ist frei.        spawnUnit vergibt ihn nie. Prueft die BASIS
--                              allein, ohne Typnummern und ohne Lord-Regel.
--  2  maxUnitCount in 1..2500. Sonst falsches Feld gelesen.
--  3  Kein belegter Platz mit unsinnigem Typ (1..78) oder Besitzer (0..8).
--                              Prueft die SCHRITTWEITE: bei falschem Abstand
--                              wandert der Lesepunkt mit jedem Index weiter.
--  4  Jeder Spieler AB 1 mit Einheiten hat genau einen Lord.
--                              Besitzer 0 ist neutral und ausgenommen.
--  5  Hoechstens 9 Lords insgesamt.
--============================================================================
local function einheitenBericht()
  local rot = 0
  local function pruefe(nr, was, ok, gemessen)
    if not ok then rot = rot + 1 end
    log(INFO, string.format("  %d %s  %s   (%s)", nr, ok and "GRUEN" or "ROT  ", was, gemessen))
  end
  log(INFO, "=== TOTSCHLAGTEST Einheiten-Array ===")

  -- 1) Basis-Test ueber die Zahlen: die belegten Plaetze muessen zu
  --    maxUnitCount passen. Belegte Plaetze liegen dicht ab 0; klafft eine
  --    Luecke oder zaehlt es weit darueber hinaus, zeigt die Basis falsch.
  --    (Der fruehere Satz "Platz 0 ist nie belegt" war falsch: spawnUnit
  --    sucht ab 1, aber Platz 0 wird anderweitig belegt - gemessen
  --    logicalState[0] = 2 bei maxUnitCount 48 und 47 Plaetzen ab 1.)

  -- 2) Grenze plausibel
  local n = core.readInteger(E_MAX)
  local nOk = n ~= nil and n >= 1 and n <= 2500
  pruefe(2, "maxUnitCount in 1..2500", nOk, "maxUnitCount = " .. tostring(n))
  if not nOk then n = 2500 end

  -- 3) und 4) in einem Durchlauf
  local jeBesitzer, jeTyp, lords = {}, {}, {}
  local belegt, schlechtTyp, schlechtOwner, letzter = 0, 0, 0, -1
  for i = 0, n - 1 do
    if eBelegt(i) then
      local b = EINHEITEN + i * E_SCHRITT
      local t = core.readSmallInteger(b + E_TYP) or -1
      local o = core.readSmallInteger(b + E_BESITZER) or -1
      belegt = belegt + 1
      jeBesitzer[o] = (jeBesitzer[o] or 0) + 1
      jeTyp[t] = (jeTyp[t] or 0) + 1
      if t == UT_LORD then lords[o] = (lords[o] or 0) + 1 end
      if t < 1 or t > 78 then schlechtTyp = schlechtTyp + 1; letzter = i end
      if o < 0 or o > 8 then schlechtOwner = schlechtOwner + 1; letzter = i end
    end
  end
  pruefe(1, "belegte Plaetze passen zu maxUnitCount (prueft die Basis)",
         belegt > 0 and belegt <= n and (n - belegt) <= 2,
         string.format("%d belegt, maxUnitCount %d", belegt, n))
  pruefe(3, "kein belegter Platz mit unsinnigem Typ/Besitzer (prueft die Schrittweite)",
         schlechtTyp == 0 and schlechtOwner == 0,
         string.format("%d belegt, %d Typ-, %d Besitzer-Ausreisser, zuletzt bei %d",
                       belegt, schlechtTyp, schlechtOwner, letzter))

  -- 4) Lord-Test - Besitzer 0 (neutral) ausgenommen
  local fehler, txt, geprueft = 0, {}, 0
  for o = 1, 8 do
    if jeBesitzer[o] and jeBesitzer[o] > 5 then
      geprueft = geprueft + 1
      local k = lords[o] or 0
      txt[#txt+1] = string.format("S%d:%d", o, k)
      if k ~= 1 then fehler = fehler + 1 end
    end
  end
  pruefe(4, "jeder Spieler ab 1 hat genau einen Lord (Besitzer 0 = neutral, ausgenommen)",
         fehler == 0 and geprueft > 0,
         string.format("%d Spieler geprueft, Lords %s", geprueft,
                       #txt > 0 and table.concat(txt, " ") or "keine"))

  -- 5) Lords gesamt
  local ges = 0
  for _, k in pairs(lords) do ges = ges + k end
  pruefe(5, "hoechstens 9 Lords insgesamt", ges <= 9, "Lords gesamt = " .. ges)

  -- Zahlen zum Mitlesen
  log(INFO, "--- belegte Einheiten je Besitzer ---")
  for o = 0, 8 do
    if jeBesitzer[o] then
      log(INFO, string.format("   Besitzer %d : %4d Einheiten, Lords: %d%s",
        o, jeBesitzer[o], lords[o] or 0, o == 0 and "   (neutral)" or ""))
    end
  end
  local liste = {}
  for t, k in pairs(jeTyp) do liste[#liste+1] = {t, k} end
  table.sort(liste, function(a, b) return a[2] > b[2] end)
  log(INFO, "--- haeufigste Typen ---")
  for i = 1, math.min(8, #liste) do
    log(INFO, string.format("   Typ %3d : %d", liste[i][1], liste[i][2]))
  end

  log(INFO, rot == 0
    and "=== ALLE GRUEN - Einheiten-Array im Spiel BESTAETIGT ==="
    or string.format("=== %d ROT - Array bleibt unbestaetigt ===", rot))
  return true
end

-- Zeigt die ersten belegten Plaetze roh. Zum Nachsehen, wenn ein Test rot ist.
local function einheitenRoh(wieviele)
  wieviele = wieviele or 12
  local n = core.readInteger(E_MAX) or 2500
  log(INFO, string.format("ROH: maxUnitCount = %s, Platz 0 logicalState = %s",
    tostring(n), tostring(core.readSmallInteger(EINHEITEN + E_ZUSTAND))))
  local gezeigt = 0
  for i = 1, math.min(n - 1, 2499) do
    if eBelegt(i) then
      local b = EINHEITEN + i * E_SCHRITT
      log(INFO, string.format("   [%4d] zustand=%s typ=%s owner=%s uid=%s leben=%s", i,
        tostring(core.readSmallInteger(b + E_ZUSTAND)),
        tostring(core.readSmallInteger(b + E_TYP)),
        tostring(core.readSmallInteger(b + E_BESITZER)),
        tostring(core.readInteger(b + E_UID)),
        tostring(core.readInteger(b + E_LEBEN))))
      gezeigt = gezeigt + 1
      if gezeigt >= wieviele then break end
    end
  end
  return true
end

--============================================================================
-- 5. Berichte und Werkzeuge
--============================================================================

local function mauerDiagnose(bis)
  bis = math.min(bis or KACHELGRENZE, KACHELGRENZE)
  local mitBit, jeBesitzer = 0, {}
  for k = 0, bis - 1 do
    local lg = core.readInteger(LOGIK + k * 4)
    if lg ~= nil and (lg & MAUERBIT) ~= 0 then
      mitBit = mitBit + 1
      local b = core.readByte(BESITZER + k)
      jeBesitzer[b] = (jeBesitzer[b] or 0) + 1
    end
  end
  log(INFO, string.format("DIAGNOSE: %d Kacheln mit Mauerwerk.", mitBit))
  for b = 0, 16 do
    if jeBesitzer[b] then
      log(INFO, string.format("   Besitzerwert %2d : %5d Kacheln", b, jeBesitzer[b]))
    end
  end
  return true
end

local function gebaeudeBericht(spieler)
  local n, roh = gebaeudeAnzahl()
  if n == nil then
    log(WARNING, string.format("logik: Gebaeudeanzahl unplausibel (%s).", tostring(roh)))
    return false
  end
  local jeTyp, gesamt, verletzt = {}, 0, 0
  for i = 1, n - 1 do
    local b = GEBAEUDE + i * G_SCHRITT
    local z = core.readSmallInteger(b + G_ZUSTAND)
    if z ~= 0 and z ~= 3 and core.readSmallInteger(b + G_BESITZER) == spieler then
      local t = core.readSmallInteger(b + G_TYP)
      jeTyp[t] = (jeTyp[t] or 0) + 1
      gesamt = gesamt + 1
      if core.readSmallInteger(b + G_LEBEN) < core.readSmallInteger(b + G_MAXLEBEN) then
        verletzt = verletzt + 1
      end
    end
  end
  log(INFO, string.format("BESTAND Spieler %d: %d Gebaeude, davon %d beschaedigt.",
    spieler, gesamt, verletzt))
  for t = 0, 109 do
    if jeTyp[t] then
      log(INFO, string.format("   Typ %3d : %3d Stueck", t, jeTyp[t]))
    end
  end
  return true
end

local function kostenBefehl(cmd)
  local typ = cmd.typ
  if type(typ) ~= "number" or typ < 0 or typ > 109 then
    log(WARNING, "logik: 'typ' fehlt oder liegt ausserhalb 0-109.")
    return false
  end
  local basis = KOSTEN + typ * 20
  local vorher = {}
  for name, off in pairs(KOSTENFELD) do vorher[name] = core.readInteger(basis + off) end
  for name, off in pairs(KOSTENFELD) do
    if type(cmd[name]) == "number" then core.writeInteger(basis + off, cmd[name]) end
  end
  log(INFO, string.format(
    "KOSTEN Typ %d: Holz %d->%d, Stein %d->%d, Eisen %d->%d, Pech %d->%d, Gold %d->%d",
    typ,
    vorher.holz,  core.readInteger(basis + 0),
    vorher.stein, core.readInteger(basis + 4),
    vorher.eisen, core.readInteger(basis + 8),
    vorher.pech,  core.readInteger(basis + 12),
    vorher.gold,  core.readInteger(basis + 16)))
  return true
end

--============================================================================
-- 6. Befehle
--============================================================================

local function bildSchreiben(wunsch)
    local W = 0x00F98338
    local welche = (wunsch.bild == "karte") and "karte" or "menue"
    local ptr = core.readInteger(W + (welche == "karte" and 0xD8 or 0xD4)) or 0

    -- GEMESSEN 01.09.: Die beiden Flaechen sind NICHT gleich gross. Hinter der
    -- Struktur stehen zwei DirectDraw-Flaechenbeschreibungen, und dort steht
    -- es schwarz auf weiss:
    --   Oberflaeche  0x00F98444  1080 hoch, 1920 breit, Zeile 3840 Byte
    --   Karte        0x00F984AC  2076 hoch, 4056 breit, Zeile 8112 Byte
    -- Wer die Karte mit 1920 Breite liest, bekommt Streifenmuster - so ist am
    -- 31.08. eine halbe Stunde in die Suche nach dem "richtigen Zeilenabstand"
    -- geflossen, den das Spiel die ganze Zeit selbst notiert hat.
    -- Aufbau ab dwSize: +0x08 Hoehe, +0x0C Breite, +0x10 Zeilenlaenge,
    -- +0x24 Zeiger auf die Pixel (der zum Zeiger bei 0xD4/0xD8 passt).
    local beschreibung = (welche == "karte") and 0x00F984A8 or 0x00F9843C
    local resY   = core.readInteger(beschreibung + 0x08) or 0
    local resX   = core.readInteger(beschreibung + 0x0C) or 0
    local zeile  = core.readInteger(beschreibung + 0x10) or (resX * 2)
    -- Notnagel, falls die Beschreibung einmal nicht passt
    if resX < 1 or resY < 1 then
      resX = core.readInteger(W + 0x38) or 0
      resY = core.readInteger(W + 0x3C) or 0
      zeile = resX * 2
    end
    -- Nur einen Ausschnitt lesen: { "aus": [x, y, breite, hoehe] }
    local ax, ay = 0, 0
    if type(wunsch.aus) == "table" and #wunsch.aus == 4 then
      ax, ay = wunsch.aus[1], wunsch.aus[2]
      resX, resY = wunsch.aus[3], wunsch.aus[4]
    end
    local ziel = type(wunsch.datei) == "string" and wunsch.datei
      or ("ucp/villagestudio/vs_" .. welche .. ".bmp")
    -- Der UCP-Sandkasten laesst io.open nur INNERHALB des Spielordners zu.
    -- Ein absoluter Pfad in die Dokumente scheitert mit "Invalid path"
    -- (gemessen 31.08. 23:18).

    log(INFO, string.format("BILD %s: %d x %d ab (%d,%d), Zeile %d Byte, Flaeche 0x%08X -> %s",
      welche, resX, resY, ax, ay, zeile, ptr, ziel))

    if resX < 1 or resX > 4096 or resY < 1 or resY > 4096
       or ptr < 0x10000 or ptr > 0x7FFFFFFF then
      log(WARNING, "BILD: Aufloesung oder Flaechenzeiger unplausibel - nichts geschrieben.")
      return false
    end

    -- Die Menueflaeche traegt NICHT von selbst das Kartenbild. Genau deshalb
    -- ruft takeScreenshot zuerst bltMapGameSurfaceToScreenMenuSurfaceComplete
    -- (0x00470610, thiscall, nur "this") - der kopiert die Karte hinein.
    -- Aus dem ZEICHENHAKEN ist dieser Aufruf ein Wiedereintritt und toetet den
    -- Prozess; hier laufen wir im Spieltick, also ausserhalb der Zeichenkette.
    -- Mit { "blt": true } anfordern.
    if wunsch.blt == true then
      local okB, blt = pcall(core.exposeCode, 0x00470610, 1, 1)
      if not okB then
        log(WARNING, "BILD: Blt nicht erreichbar: " .. tostring(blt))
      else
        local okB2, errB = pcall(blt, W)
        log(okB2 and INFO or WARNING, okB2
          and "BILD: Karte in die Menueflaeche kopiert."
          or ("BILD: Blt fehlgeschlagen: " .. tostring(errB)))
      end
    end

    local probe = {}
    for i = 0, 7 do
      probe[#probe + 1] = string.format("%04X", (core.readSmallInteger(ptr + i * 2) or 0) & 0xFFFF)
    end
    log(INFO, "BILD: erste acht Pixel " .. table.concat(probe, " "))

    local f = io.open(ziel, "wb")
    if not f then
      log(WARNING, "BILD: Datei nicht schreibbar: " .. ziel)
      return false
    end

    local function le32(n)
      return string.char(n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF, (n >> 24) & 0xFF)
    end
    local function le16(n) return string.char(n & 0xFF, (n >> 8) & 0xFF) end

    local zeilenBytes = resX * 3
    local rand = (4 - zeilenBytes % 4) % 4     -- BMP-Zeilen liegen auf 4 Byte
    local fuell = string.rep("\0", rand)
    local daten = (zeilenBytes + rand) * resY

    f:write("BM", le32(54 + daten), le16(0), le16(0), le32(54))
    f:write(le32(40), le32(resX), le32(resY), le16(1), le16(24), le32(0),
            le32(daten), le32(0), le32(0), le32(0), le32(0))

    -- GEMESSEN 31.08.: die Flaeche ist RGB555, NICHT RGB565. Das Dekompilat
    -- von takeScreenshot rechnet zwar 565 - unter graphicsApiReplacer 1.3.0
    -- kommt aber 555 aus dem Speicher. Mit 565 gelesen wird das ganze Bild
    -- rotstichig, mit 555 ist es einwandfrei. Messung schlaegt Ableitung.
    -- Mit { "format": 565 } laesst sich die alte Deutung erzwingen.
    local f555 = tonumber(wunsch.format) ~= 565
    local char, concat, lies = string.char, table.concat, core.readSmallInteger
    for y = resY - 1, 0, -1 do              -- BMP steht auf dem Kopf
      local basis = ptr + (ay + y) * zeile + ax * 2
      local zeile = {}
      for x = 0, resX - 1 do
        local v = lies(basis + x * 2) or 0
        if v < 0 then v = v + 65536 end
        if f555 then
          zeile[x + 1] = char((v & 0x1F) << 3, ((v >> 5) & 0x1F) << 3, ((v >> 10) & 0x1F) << 3)
        else
          zeile[x + 1] = char((v & 0x1F) << 3, ((v >> 5) & 0x3F) << 2, ((v >> 11) & 0x1F) << 3)
        end
      end
      f:write(concat(zeile))
      if rand > 0 then f:write(fuell) end
    end
    f:close()
    log(INFO, string.format("BILD %s: fertig, %d Byte -> %s", welche, 54 + daten, ziel))
    return true
end

--============================================================================
-- 6b. Fenster-Wacht: haelt das Spielfenster hinten und auf dem rechten Schirm
--
-- Warum aus dem Spiel heraus: Von aussen ist jeder Zugriff auf dieses Fenster
-- gesperrt - der Prozess laeuft auf hoher Rechtestufe, die Claude-Sitzung
-- nicht. SetWindowPos, Stop-Process und selbst das blosse Zuruecksetzen in
-- der Fensterreihenfolge scheitern mit Fehler 5 (am 01.09. dreimal gemessen).
-- Das Modul laeuft IM Spiel und hat dessen Rechte - hier geht es.
--
-- SetWindowPos wird ueber den Import-Eintrag bei 0x0059E1F4 gerufen; dort
-- steht die echte Adresse in user32.dll, die das Spiel selbst benutzt.
--============================================================================

local IAT_SETWINDOWPOS = 0x0059E1F4
local HWND_BOTTOM      = 1
-- NOSIZE|NOACTIVATE: nie den Tastaturfokus wegnehmen, nie die Groesse aendern
local SWP_NOSIZE       = 0x0001
local SWP_NOMOVE       = 0x0002
local SWP_NOACTIVATE   = 0x0010

local fensterWacht = nil        -- { hwnd, x, y, alle, zaehler }

local function fensterSetzen(hwnd, x, y)
  local adr = core.readInteger(IAT_SETWINDOWPOS)
  if adr == nil or adr == 0 then return false, "kein Import bei 0x59E1F4" end
  -- stdcall: alle Argumente auf dem Stack, die Funktion raeumt selbst auf.
  -- exposeCode mit Konvention 0 stellt den Stapelzeiger danach wieder her -
  -- dasselbe Muster, mit dem das Modul schon 'ret 8'-Funktionen ruft.
  -- ABGESCHALTET 01.09.2026 nach drei Abstuerzen in Folge.
  -- SetWindowPos ist stdcall und raeumt seine 7 Argumente (28 Byte) selbst vom
  -- Stapel. exposeCode raeumt bei Konvention 0 noch einmal auf - der
  -- Stapelzeiger wandert, der naechste Ruecksprung geht ins Leere. Eine
  -- stdcall-Konvention kennt exposeCode nicht; im ganzen UCP gibt es kein
  -- einziges Beispiel fuer den Aufruf einer Windows-Funktion mit Argumenten.
  --
  -- Der Aufruf stand an ZWEI Stellen (hier und in init.lua). Nach dem
  -- Abschalten der einen stuerzte das Spiel weiter ab, und der Verdacht fiel
  -- faelschlich auf die Fensterposition des Grafikmoduls.
  log(WARNING, string.format(
    "FENSTER: Verschieben von 0x%X abgelehnt - SetWindowPos ueber exposeCode " ..
    "toetet den Prozess (dreimal gemessen 01.09.). Fensterlage bitte ueber " ..
    "window.pos in der ucp-config.yml stellen.", hwnd))
  return false
end

local function fensterWachtTick()
  if fensterWacht == nil then return end
  fensterWacht.zaehler = fensterWacht.zaehler + 1
  if fensterWacht.zaehler % fensterWacht.alle ~= 0 then return end
  pcall(fensterSetzen, fensterWacht.hwnd, fensterWacht.x, fensterWacht.y)
end

-- Vorwaertsdeklaration. Beide Funktionen werden aus einzelbefehl gerufen,
-- stehen aber weiter unten. Ohne diese Zeile sucht Lua sie im globalen Raum,
-- findet nichts und bricht mit "attempt to call a nil value" ab - der
-- Bauwacht-Befehl war deshalb seit jeher wirkungslos (gefunden 31.08.2026).
local bauwachtStart, autobildStart

-- Zustand der Befehlskette. Muss hier oben stehen, weil einzelbefehl ihn
-- setzt und der Taktgeber ihn weiter unten liest.
local kette = nil

--============================================================================
-- Ereignis-Regeln: "wenn X, dann Y"
--
-- Der Sinn: Ein Testlauf soll von selbst reagieren, statt dass jemand
-- zuschaut. Beispiele, die Daniel genannt hat - pausieren, sobald eine KI zum
-- ersten Mal 100.000 Gold hat; das Spiel beenden, sobald jemand angreift.
--
-- Die Wacht laeuft in JEDEM Takt. Deshalb duerfen die Bedingungen nur
-- Speicherstellen lesen, keine Schleifen ueber 2500 Einheiten. Was teuer ist,
-- traegt ein eigenes Intervall.
--============================================================================

local regeln = {}          -- jede Regel merkt sich, ob sie schon gefeuert hat

-- Gold eines Spielers: EIN Lesezugriff.
-- playerDataArray 0x0115BDF8, je Spieler 0x39F4, currentResources +0x4D0,
-- Gold ist Ware 15. Am 01.09. gegengeprueft: Spieler 1 las 3960 - ein
-- normaler Startwert, wie er auch in der Anzeige steht.
local function goldVon(spieler)
  return core.readInteger(0x0115BDF8 + spieler * 0x39F4 + 0x4D0 + 15 * 4) or 0
end

local function einzelbefehl(cmd)
  if type(cmd) ~= "table" then return false end
  local spieler = cmd.player

  -- { "tickpause": { "bei": 1, "alle": 100, "bis": 5000 } }  oder  { "tickpause": "aus" }
  -- Haelt das Spiel an, sobald der Tickzaehler "bei" erreicht; mit "alle" danach
  -- wiederholt. Im Menue gesetzt, greift es beim naechsten Gefecht ab Tick 1.
  if cmd.tickpause ~= nil then
    local tp = cmd.tickpause
    if tp == "aus" or tp == false then
      tickPause = nil
      log(INFO, "TICKPAUSE: aus.")
      return true
    end
    if type(tp) ~= "table" or tonumber(tp.bei) == nil then
      log(WARNING, "TICKPAUSE: 'bei' fehlt.")
      return false
    end
    tickPause = { naechster = tonumber(tp.bei), alle = tonumber(tp.alle), bis = tonumber(tp.bis), anzahl = 0 }
    log(INFO, string.format("TICKPAUSE: scharf - Pause bei Tick %d%s (jetzt Tick %d).",
      tickPause.naechster, tickPause.alle and (", danach alle " .. tickPause.alle) or "", tick()))
    return true
  end

  -- { "ladepause": true }  oder  { "ladepause": "aus" }
  -- Haelt beim ersten Tick eines geladenen Stands an. Zwei Erkennungszeichen:
  --  1. die Spielzeit springt (nicht +0/+1),
  --  2. die Pause ist aufgehoben, obwohl beim Scharfmachen pausiert war -
  --     das Laden hebt die Pause auf (gemessen 02.09.). Zeichen 2 braucht es fuer
  --     das Wiederladen eines Stands mit DERSELBEN Spielzeit (gemessen 30.09.,
  --     23:26: M7-01 ueber M7-01, kein Sprung, das Spiel lief bis Tick 1564).
  -- Der Taktgeber laeuft auch in der Pause (gemessen 30.09., 23:26:48), die
  -- Spielzeit steht dabei - im pausierten Spiel loest also nichts aus.
  -- Die Tick-Pause taugt nicht: sie greift nur, wenn der Stand SPAETER liegt.
  if cmd.ladepause ~= nil then
    if cmd.ladepause == "aus" or cmd.ladepause == false then
      ladePause = nil
      log(INFO, "LADEPAUSE: aus.")
      return true
    end
    ladePause = { letzter = tick(), nachlauf = 0, pausiert = (core.readInteger(PAUSE) or 0) ~= 0 }
    log(INFO, string.format("LADEPAUSE: scharf (jetzt Tick %d, %s).", ladePause.letzter,
      ladePause.pausiert and "pausiert" or "NICHT pausiert - nur der Zeitsprung zaehlt"))
    return true
  end

  if cmd.pause ~= nil then
    core.writeInteger(PAUSE, cmd.pause == true and 1 or 0)
    log(INFO, "logik: Spiel " .. (cmd.pause == true and "pausiert" or "fortgesetzt") .. ".")
    return true
  end

  if cmd.tempo ~= nil then
    local alt = core.readInteger(TEMPO)
    if type(cmd.tempo) == "number" then core.writeInteger(TEMPO, cmd.tempo) end
    log(INFO, string.format("TEMPO: %s -> %s (Ticks je Sekunde = Tempowert).",
      tostring(alt), tostring(core.readInteger(TEMPO))))
    return true
  end

  if cmd.zeit == true then
    local t = tick()
    log(INFO, string.format("ZEIT: Tick %d | Tag %d/50 | Woche %d/200 | Monat %d/800 | Jahr = 9600",
      t, t % 50, t % 200, t % 800))
    return true
  end

  --==========================================================================
  -- Bild aus dem Speicher (31.08.2026)
  --
  -- Warum nicht takeScreenshot (0x479540): sie ruft als Erstes
  -- bltMapGameSurfaceToScreenMenuSurfaceComplete. Aus dem Zeichenhaken heraus
  -- ist das ein Wiedereintritt - der Prozess stirbt, zurueck bleibt eine
  -- 0-Byte-Datei (am 31.08. zweimal gemessen).
  --
  -- Aus dem Dekompilat derselben Funktion ist aber belegt, WIE sie die Pixel
  -- liest, und das laesst sich ohne jeden Zeichenaufruf nachbauen:
  --   WindowAndDirectDraw 0x00F98338
  --     +0x38 Breite   +0x3C Hoehe   +0x4C Breite*3*Hoehe
  --     +0xD4 Menueflaeche (die takeScreenshot liest)
  --     +0xD8 Kartenflaeche
  --   Die Flaeche ist ROHER Speicher: ushort je Pixel, RGB565, Zeilenlaenge
  --   genau Breite*2 Byte, kein Rand. Zeile 0 liegt oben.
  --   Farbe wie im Original: B=(v&0x1F)<<3, G=((v>>5)&0x3F)<<2, R=(v>>11)<<3.
  --
  -- Befehl: { "bild": "menue" } oder { "bild": "karte" }, dazu optional
  -- { "datei": "C:/.../name.bmp" }.
  --==========================================================================
  if cmd.autobild ~= nil then return autobildStart(cmd) end
  if cmd.bild ~= nil then return bildSchreiben(cmd) end

  -- Menueansicht wechseln: { "menue": 41 }  (41 = Hauptmenue, 16 = Spiel)
  --
  -- GameCore liegt bei 0x01FE7D10 (Ghidra-Symbol DAT_GameCore):
  --   +0x04 menuSwitchDelay   +0x0C currentMenuViewType   +0x18 menuViewToSwitchTo
  -- switchToMenuView (0x0046B340, thiscall, this + 2 Argumente) setzt Ziel und
  -- Verzoegerung; processMenuViewSwitch uebernimmt es im naechsten Bild.
  -- Nummern: 12 Landschaftseditor, 14 Baumenue, 16 Gebaeude-/Statusleiste,
  --          30 "Spiel verloren", 41 Hauptmenue, 58 Rangliste.
  if cmd.menue ~= nil then
    local ziel = tonumber(cmd.menue)
    if ziel == nil then log(WARNING, "MENUE: Nummer fehlt.") return false end
    local GC = 0x01FE7D10
    log(INFO, string.format("MENUE: aktuell %s, Ziel %d, Wechselfrist %s",
      tostring(core.readInteger(GC + 0x0C)), ziel, tostring(core.readInteger(GC + 0x04))))
    local ok, wechsel = pcall(core.exposeCode, 0x0046B340, 3, 1)
    if not ok then
      log(WARNING, "MENUE: switchToMenuView nicht erreichbar: " .. tostring(wechsel))
      return false
    end
    local ok2, err = pcall(wechsel, GC, ziel, 0)
    if not ok2 then
      log(WARNING, "MENUE: Wechsel fehlgeschlagen: " .. tostring(err))
      return false
    end
    log(INFO, string.format("MENUE: Wechsel nach %d angefordert.", ziel))
    return true
  end

  -- Rohe Speicherstelle ansehen: { "peek": 33325368, "worte": 16 }
  if cmd.peek ~= nil then
    local a = tonumber(cmd.peek)
    if a == nil then log(WARNING, "PEEK: Adresse nicht lesbar.") return false end
    local n = type(cmd.worte) == "number" and cmd.worte or 16
    local zeile = {}
    for k = 0, n - 1 do
      zeile[#zeile + 1] = string.format("%08X", core.readInteger(a + k * 4) or 0)
    end
    log(INFO, string.format("PEEK 0x%08X: %s", a, table.concat(zeile, " ")))
    return true
  end

  if cmd.kosten ~= nil then return kostenBefehl(cmd.kosten) end
  if cmd.mauerDiagnose ~= nil then
    return mauerDiagnose(type(cmd.mauerDiagnose) == "number" and cmd.mauerDiagnose or nil)
  end

  -- Spiel beenden. Von aussen ist das gesperrt: taskkill und Stop-Process
  -- scheitern beide mit Fehler 5, weil der Prozess auf hoher Rechtestufe
  -- laeuft. Das Modul laeuft IM Spiel und darf es.
  --
  -- Warum ausgerechnet ExitProcess und nicht die saubere Beenden-Funktion des
  -- Spiels: ExitProcess kehrt nie zurueck. Der Stapelschaden, an dem
  -- SetWindowPos den Prozess getoetet hat (stdcall gegen cdecl), kann hier
  -- also nicht mehr wirken - es gibt kein Danach. Genau die Eigenschaft, die
  -- den Aufruf sonst gefaehrlich macht, macht ihn hier verlaesslich.
  --
  -- Preis: Das Spiel raeumt nicht auf, das Log bricht mitten ab. Fuer einen
  -- Neustart ist das ohne Belang - ucp3.log wird beim naechsten Start
  -- ohnehin neu angelegt.
  if cmd.beenden == true then
    local adr = core.readInteger(0x0059E110)          -- IAT-Eintrag ExitProcess
    if adr == nil or adr == 0 then
      log(WARNING, "BEENDEN: kein Eintrag fuer ExitProcess bei 0x0059E110.")
      return true
    end
    log(INFO, "BEENDEN: Spiel wird jetzt beendet (ExitProcess).")
    core.exposeCode(adr, 1, 0)(0)
    return true                                       -- wird nie erreicht
  end

  -- "Wo bin ich?" - Fenster, Spielzeit und Stand der Kette in einer Zeile.
  if cmd.wo ~= nil then
    local ansicht = core.readInteger(0x01FE7D1C)
    local t = tick()
    log(INFO, string.format(
      "WO: Fenster %s | Spielzeit %d Ticks | Kette %s | Fenster-Wacht %s",
      tostring(ansicht), t,
      kette and string.format("Schritt %d von %d", kette.index, #kette.schritte)
             or "keine",
      fensterWacht and "an" or "aus"))
    return true
  end

  --==========================================================================
  -- Massentausch: alle Einheiten oder Gebaeude eines Typs in einen anderen
  --
  --   { "tausche": { "was": "einheit", "von": 22, "nach": 28, "spieler": 2 } }
  --   { "tausche": { "was": "gebaeude", "von": 20, "nach": 12 } }
  --
  -- "spieler" ist freiwillig; ohne ihn werden alle Besitzer erfasst.
  -- Gezaehlt wird immer, auch wenn nichts passt - eine 0 ist ein Ergebnis
  -- und keine Panne.
  --==========================================================================
  if cmd.tausche ~= nil then
    local t = cmd.tausche
    local von, nach = tonumber(t.von), tonumber(t.nach)
    local nurSpieler = tonumber(t.spieler)
    if von == nil or nach == nil then
      log(WARNING, "TAUSCH: 'von' und 'nach' werden gebraucht.")
      return false
    end
    local was = (t.was == "gebaeude") and "gebaeude" or "einheit"
    local getroffen, geprueft = 0, 0

    if was == "einheit" then
      -- Einheit: Basis 0x0138854C, Schrittweite 1168 (aus spawnUnit gelesen).
      -- Belegt heisst logicalState (+0x8C) ~= 0 - NICHT unitType, denn ein
      -- freier Platz behaelt den Typ der gestorbenen Einheit.
      local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
      for i = 0, grenze - 1 do
        local b = 0x0138854C + i * 1168
        if (core.readSmallInteger(b + 0x8C) or 0) ~= 0 then
          geprueft = geprueft + 1
          local besitzer = core.readSmallInteger(b + 0x96) or -1
          if (core.readSmallInteger(b + 0x8E) or -1) == von
             and (nurSpieler == nil or besitzer == nurSpieler) then
            core.writeSmallInteger(b + 0x8E, nach)
            getroffen = getroffen + 1
          end
        end
      end
    else
      -- Gebaeude: Basis 0xF98520 + 0x14, Schrittweite 812 (0x32C).
      -- Der Typ steht bei +0xD2, der Besitzer bei +0xD6.
      local anzahl = math.min(core.readInteger(0x00F98520) or 0, 2000)
      for i = 0, anzahl - 1 do
        local b = 0x00F98520 + 0x14 + i * 812
        local zustand = core.readSmallInteger(b + 0xD0) or 0
        if zustand ~= 0 then
          geprueft = geprueft + 1
          local besitzer = core.readSmallInteger(b + 0xD6) or -1
          if (core.readSmallInteger(b + 0xD2) or -1) == von
             and (nurSpieler == nil or besitzer == nurSpieler) then
            core.writeSmallInteger(b + 0xD2, nach)
            getroffen = getroffen + 1
          end
        end
      end
    end

    log(INFO, string.format("TAUSCH %s: Typ %d -> %d%s | %d von %d geaendert",
      was, von, nach,
      nurSpieler and (" bei Spieler " .. nurSpieler) or " (alle Spieler)",
      getroffen, geprueft))
    return true
  end

  --==========================================================================
  -- Fenster nach ganz unten - aus dem Spiel heraus
  --
  --   { "hinten": true }              Aufrufart 0 (cdecl)
  --   { "hinten": true, "art": 2 }    andere Aufrufart probieren
  --
  -- Von aussen ist das gesperrt (Fehler 5, hohe Rechtestufe). Das Modul laeuft
  -- IM Spiel und darf es. Am 01.09. starb der Prozess bei Aufrufart 0, weil
  -- SetWindowPos stdcall ist und seine sieben Argumente selbst vom Stapel
  -- raeumt - exposeCode raeumt bei cdecl ein zweites Mal auf. Deshalb ist die
  -- Aufrufart hier von aussen einstellbar: der Neustart kostet nur Sekunden,
  -- also lassen sich die Kandidaten der Reihe nach messen.
  --
  -- Das Fensterhandle steht in der Grafikstruktur bei +0xAC. Am 01.09. belegt:
  -- der Wert stimmte mit dem ueberein, den Windows fuer das Spielfenster nennt.
  --==========================================================================
  if cmd.hinten ~= nil then
    local hwnd = core.readInteger(0x00F98338 + 0xAC)
    if hwnd == nil or hwnd == 0 then
      log(WARNING, "HINTEN: kein Fensterhandle in der Grafikstruktur.")
      return true
    end
    local adr = core.readInteger(0x0059E1F4)          -- IAT SetWindowPos
    if adr == nil or adr == 0 then
      log(WARNING, "HINTEN: kein Import-Eintrag bei 0x0059E1F4.")
      return true
    end
    local art = tonumber(cmd.art) or 0
    log(INFO, string.format("HINTEN: Fenster 0x%X, SetWindowPos 0x%X, Aufrufart %d",
      hwnd, adr, art))
    -- HWND_BOTTOM = 1; NOMOVE|NOSIZE|NOACTIVATE = 0x13 - kein Fokusraub
    local ok, err = pcall(function()
      core.exposeCode(adr, 7, art)(hwnd, 1, 0, 0, 0, 0, 0x13)
    end)
    log(INFO, "HINTEN: Aufruf zurueck, ok=" .. tostring(ok) ..
      (ok and "" or (" - " .. tostring(err))))
    return true
  end

  --==========================================================================
  -- Einen Knopf im Hauptmenue druecken: { "hauptmenue": 5 }
  --
  -- MenuItemActionHandler_MainMenu_Main (0x004251A0, cdecl, ein Argument) ist
  -- genau die Funktion, die das Spiel beim Anklicken ruft. Aus dem Dekompilat
  -- vom 02.09.2026:
  --   1 Historische Kampagnen   2 Kreuzzug        3 Burgenbau
  --   4 Mehrspieler             5 Beenden (Tor)   6 Tutorial (Buch)
  --   7 Abspann                 8 Einstellungen (Schluessel)
  --   9 Eigene Szenarien
  --
  -- ACHTUNG bei 5: Der Knopf beendet NICHT sofort, sondern oeffnet einen
  -- Ja/Nein-Dialog. Wer danach nichts weiter tut, steht im Dialog fest.
  --==========================================================================
  if cmd.hauptmenue ~= nil then
    local nr = tonumber(cmd.hauptmenue)
    if nr == nil then
      log(WARNING, "HAUPTMENUE: Nummer fehlt.")
      return false
    end
    local vorher = core.readInteger(0x01FE7D1C)
    local ok, err = pcall(function()
      core.exposeCode(0x004251A0, 1, 0)(nr)
    end)
    log(INFO, string.format("HAUPTMENUE: Knopf %d gedrueckt (Ansicht vorher %s), ok=%s%s",
      nr, tostring(vorher), tostring(ok), ok and "" or (" - " .. tostring(err))))
    return true
  end

  --==========================================================================
  -- Den Ja-Knopf eines Dialogs druecken: { "dialogJa": 9 }
  --
  -- Alle Ja/Nein-Dialoge laufen ueber DIESELBE Funktion:
  -- MenuItemActionHandler_General_LaunchOrQuitMultiplayerGameUnk
  -- (0x00494950, cdecl, ein Argument).
  --
  -- WICHTIG: Das Argument ist NICHT der Zweck, sondern welcher Knopf gedrueckt
  -- wurde: 22 (0x16) = Ja, 23 (0x17) = Nein. Den Zweck liest die Funktion aus
  -- DAT_MenuTextInputState.DAT_MenuOptionsActionParameter - dort hinterlegt
  -- ihn der Knopf, der den Dialog geoeffnet hat (das Tor im Hauptmenue: 9).
  --
  -- Am 02.09. erst mit dem Zweck 9 als Argument gerufen: Die Funktion lief
  -- sauber durch, meldete ok=true - und tat nichts, weil weder 22 noch 23
  -- getroffen war. Ein Aufruf, der zurueckkehrt, hat nichts bewiesen.
  --==========================================================================
  if cmd.dialogJa ~= nil then
    local knopf = (cmd.dialogJa == false) and 23 or 22    -- 22 = Ja, 23 = Nein
    local zweck = core.readInteger(0x00F02D24)            -- nur zum Mitschreiben
    log(INFO, string.format("DIALOG: Knopf %d (%s), hinterlegter Zweck %s",
      knopf, knopf == 22 and "Ja" or "Nein", tostring(zweck)))
    local ok, err = pcall(function()
      core.exposeCode(0x00494950, 1, 0)(knopf)
    end)
    log(INFO, "DIALOG: zurueck, ok=" .. tostring(ok) ..
      (ok and "" or (" - " .. tostring(err))))
    return true
  end

  --==========================================================================
  -- Einen Knopf im Optionen-Dialog druecken: { "optionen": 2 }
  --
  -- MenuItemActionHandler_OptionsMenu_Buttons (0x00496B80, cdecl, ein
  -- Argument). Nummern aus dem Dekompilat vom 02.09.2026:
  --   2  Laden        3  Speichern    7  Mission verlassen
  --   9  Crusader verlassen           10 Spiel fortsetzen
  --   26 Hilfe        39 Briefing     44 Mission neu starten
  --==========================================================================
  if cmd.optionen ~= nil then
    local nr = tonumber(cmd.optionen)
    if nr == nil then
      log(WARNING, "OPTIONEN: Nummer fehlt.")
      return false
    end
    local ok, err = pcall(function()
      core.exposeCode(0x00496B80, 1, 0)(nr)
    end)
    log(INFO, string.format("OPTIONEN: Knopf %d gedrueckt, ok=%s%s",
      nr, tostring(ok), ok and "" or (" - " .. tostring(err))))
    return true
  end

  --==========================================================================
  -- Knopf im Laden-/Speichern-Dialog: { "laden": 2 }
  --
  -- MenuItemActionHandler_SaveLoadMap_Buttons (0x004943B0, cdecl, ein
  -- Argument). Aus dem Dekompilat vom 02.09.2026:
  --   2  Laden      3  Speichern      17 Zurueck
  -- Geladen wird der Eintrag, der in der Liste markiert ist - beim Oeffnen
  -- ist das der oberste, also der neueste Spielstand.
  --==========================================================================
  if cmd.laden ~= nil then
    local nr = tonumber(cmd.laden)
    if nr == nil then
      log(WARNING, "LADEN: Nummer fehlt.")
      return false
    end
    local ok, err = pcall(function()
      core.exposeCode(0x004943B0, 1, 0)(nr)
    end)
    log(INFO, string.format("LADEN: Knopf %d gedrueckt, ok=%s%s",
      nr, tostring(ok), ok and "" or (" - " .. tostring(err))))
    return true
  end

  -- Untereintraege des Optionen-Dialogs: { "unteropt": 1 }
  -- MenuItemActionHandler_OptionsMenu_SubOptionsButtons (0x00493BD0, cdecl).
  -- Das sind Spieloptionen / Grafikoptionen / Soundoptionen / Identitaet -
  -- die Nummern des Haupt-Optionenhandlers (0x00496B80) greifen dort NICHT,
  -- am 02.09.2026 mit 1, 4, 5, 6 und 8 durchprobiert: keine Wirkung.
  if cmd.unteropt ~= nil then
    local nr = tonumber(cmd.unteropt)
    if nr == nil then return false end
    local ok, err = pcall(function()
      core.exposeCode(0x00493BD0, 1, 0)(nr)
    end)
    log(INFO, string.format("UNTEROPT: Knopf %d, ok=%s%s", nr, tostring(ok),
      ok and "" or (" - " .. tostring(err))))
    return true
  end

  -- Speicher schreiben: { "poke": 17982500, "wert": 2 }
  -- Gegenstueck zu peek. Liest den alten Wert mit, damit im Log steht, was
  -- ueberschrieben wurde - ohne das ist ein Fehlgriff spaeter nicht mehr
  -- nachvollziehbar.
  if cmd.poke ~= nil then
    local adr = tonumber(cmd.poke)
    local wert = tonumber(cmd.wert)
    if adr == nil or wert == nil then
      log(WARNING, "POKE: Adresse oder Wert fehlt.")
      return false
    end
    local alt = core.readInteger(adr)
    core.writeInteger(adr, wert)
    log(INFO, string.format("POKE 0x%08X: %s -> %d", adr, tostring(alt), wert))
    return true
  end

  -- Einheit auf eine Kachel schicken: { "einheit_ziel": { "nr": N, "x": X, "y": Y } }
  -- Koordinaten 0..399; ungueltiges Ziel -> Rueckgabe FALSE (Gueltigkeitskarte).
  --==========================================================================
  -- Lords (30.09.2026, Selfaware M4.04 Lord-Duell)
  --   { "lords": true }                     alle Lords (Typ 55): Nummer, Spieler, Ort, Leben
  --   { "lordwacht": true, "halt": ["treffer", "tod"], "alle": 50 }   /   { "lordwacht": false }
  -- Die Wacht prueft jeden Tick die Leben (+0x3C8) aller Lords und meldet: alle "alle"
  -- Ticks Ort und Leben beider Lords samt Abstand, das erste Treffen (Abstand <= 3),
  -- den ersten Treffer (mit Angreifer +0x3AE), jede 10-%-Stufe und den Tod
  -- (Leben <= 0, Platz frei oder Typ nicht mehr 55). "halt" pausiert dort.
  --==========================================================================
  local function lordListe()
    local liste = {}
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    -- ab Platz 1: Platz 0 ist ein Sonderplatz des Spiels (belegt, aber keine echte
    -- Einheit) - am 01.10., 00:05 stand dort eine Kopie eines Lords (Typ 55).
    for i = 1, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0 and (core.readSmallInteger(b + 0x8E) or -1) == 55 then
        -- Ort = Mikro-Position / 8 (+0xB6/+0xB8) - dasselbe System wie einheit_ziel und das Ziel
        -- (+0xC8/+0xCA). Die Kachel (+0xD4) ist NICHT y*400+x (gemessen 01.10., 00:02).
        table.insert(liste, { nr = i, sp = core.readSmallInteger(b + 0x96) or -1,
          x = math.floor((core.readSmallInteger(b + 0xB6) or 0) / 8), y = math.floor((core.readSmallInteger(b + 0xB8) or 0) / 8),
          hp = core.readInteger(b + 0x3C8) or 0, max = core.readInteger(b + 0x3CC) or 0 })
      end
    end
    return liste
  end

  if cmd.lords ~= nil then
    local liste = lordListe()
    for _, l in ipairs(liste) do
      log(INFO, string.format("LORD %d: Spieler %d bei (%d,%d), Leben %d von %d", l.nr, l.sp, l.x, l.y, l.hp, l.max))
    end
    log(INFO, string.format("LORDS: %d gefunden (Tick %d).", #liste, tick()))
    return true
  end

  if cmd.lordwacht ~= nil then
    if cmd.lordwacht == false then
      lordWacht = nil
      log(INFO, "LORDWACHT: aus.")
      return true
    end
    local halt = {}
    if type(cmd.halt) == "table" then for _, h in ipairs(cmd.halt) do halt[h] = true end
    elseif type(cmd.halt) == "string" then halt[cmd.halt] = true end
    -- "ziel": [x, y] - die Wacht haelt dieses Ziel fuer alle Lords fest (die KI holt ihre
    -- Lords sonst zur Burg zurueck, gemessen 01.10., 00:02), bis sie sich treffen.
    -- "spaeter": { "137": 20 } - dieser Lord bekommt sein Ziel erst N Ticks spaeter.
    local ziel = (type(cmd.ziel) == "table" and #cmd.ziel == 2) and { tonumber(cmd.ziel[1]), tonumber(cmd.ziel[2]) } or nil
    lordWacht = { lords = {}, haltTreffer = halt.treffer, haltTod = halt.tod, ziel = ziel, start = tick(),
                  alle = tonumber(cmd.alle) or 50, naechste = tick(), getroffen = false, getroffenWo = false }
    local n = 0
    for _, l in ipairs(lordListe()) do
      local spaeter = (type(cmd.spaeter) == "table" and tonumber(cmd.spaeter[tostring(l.nr)])) or 0
      lordWacht.lords[l.nr] = { sp = l.sp, hp = l.hp, max = l.max, stufe = 10, tot = false,
                                abTick = tick() + spaeter, gesetzt = 0, angekommen = false }
      n = n + 1
    end
    log(INFO, string.format("LORDWACHT: scharf fuer %d Lords (Tick %d), halt bei%s%s%s.", n, tick(),
      halt.treffer and " Treffer" or "", halt.tod and " Tod" or (halt.treffer and "" or " nichts"),
      ziel and string.format(", Ziel (%d,%d) wird gehalten", ziel[1], ziel[2]) or ""))
    return true
  end

  --==========================================================================
  -- Gruppen befehligen (01.10.2026, Selfaware): alle Einheiten eines Spielers und Typs
  --   { "gruppe": { "spieler": 2, "typ": 13, "x": 180, "y": 120 } }   alle dorthin
  --   { "gruppe": { "spieler": 2, "typ": 13, "zu": 19 } }             zum Eingang des 1. Gebaeudes Typ 19
  --   { "gruppe": { "spieler": 2, "typ": 13, "halt": true } }         auf der Stelle anhalten (Ziel = eigener Ort)
  --   { "gruppe": { "spieler": 2, "typ": 13 } }                       nur auflisten
  --   "nr": [5, 9]  statt typ/spieler: genau diese Einheiten
  -- Ort = Mikro-Position / 8 (+0xB6/+0xB8). Gebaeude: Referenz-Offsets + 0x14 (siehe
  -- Kopf), Eingang buildingEntryX/Y = Referenz +0xFE/+0x100 -> hier +0x112/+0x114.
  --   { "gebaeude": { "spieler": 2, "typ": 19 } }   Gebaeude dieses Typs: Nummer, Ort, Eingang
  --==========================================================================
  local function gebaeudeVon(sp, typ)
    local liste = {}
    local n = gebaeudeAnzahl() or 0
    for i = 1, n - 1 do
      local b = GEBAEUDE + i * G_SCHRITT
      if (core.readSmallInteger(b + G_ZUSTAND) or 0) ~= 0 and core.readSmallInteger(b + G_TYP) == typ
         and (sp == nil or core.readSmallInteger(b + G_BESITZER) == sp) then
        table.insert(liste, { nr = i, sp = core.readSmallInteger(b + G_BESITZER),
          x = core.readSmallInteger(b + 0x102) or -1, y = core.readSmallInteger(b + 0x104) or -1,
          ex = core.readSmallInteger(b + 0x112) or -1, ey = core.readSmallInteger(b + 0x114) or -1 })
      end
    end
    return liste
  end

  if cmd.gebaeude ~= nil and type(cmd.gebaeude) == "table" then
    local g = cmd.gebaeude
    local liste = gebaeudeVon(tonumber(g.spieler), tonumber(g.typ))
    for _, e in ipairs(liste) do
      log(INFO, string.format("GEBAEUDE %d: Typ %d, Spieler %d, Ort (%d,%d), Eingang (%d,%d)",
        e.nr, tonumber(g.typ), e.sp, e.x, e.y, e.ex, e.ey))
    end
    log(INFO, string.format("GEBAEUDE: %d gefunden.", #liste))
    return true
  end

  if cmd.gruppe ~= nil and type(cmd.gruppe) == "table" then
    local g = cmd.gruppe
    local sp, typ = tonumber(g.spieler), tonumber(g.typ)
    local nummern = {}
    if type(g.nr) == "table" then
      for _, n in ipairs(g.nr) do table.insert(nummern, tonumber(n)) end
    else
      local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
      for i = 1, grenze - 1 do
        local b = 0x0138854C + i * 1168
        if (core.readSmallInteger(b + 0x8C) or 0) ~= 0
           and (typ == nil or core.readSmallInteger(b + 0x8E) == typ)
           and (sp == nil or core.readSmallInteger(b + 0x96) == sp) then
          table.insert(nummern, i)
        end
      end
    end
    local zx, zy = tonumber(g.x), tonumber(g.y)
    if g.zu ~= nil then
      local geb = gebaeudeVon(sp, tonumber(g.zu))[1]
      if geb == nil then log(WARNING, "GRUPPE: kein Gebaeude Typ " .. tostring(g.zu)) return false end
      zx, zy = geb.ex, geb.ey
      log(INFO, string.format("GRUPPE: Ziel = Eingang Gebaeude %d (Typ %d) bei (%d,%d).", geb.nr, g.zu, zx, zy))
    end
    _setDest = _setDest or core.exposeCode(ADR_SETDEST, 5, 1)
    local ok, teile = 0, {}
    for _, nr in ipairs(nummern) do
      local b = 0x0138854C + nr * 1168
      local x = math.floor((core.readSmallInteger(b + 0xB6) or 0) / 8)
      local y = math.floor((core.readSmallInteger(b + 0xB8) or 0) / 8)
      local tx, ty = zx, zy
      if g.halt == true then tx, ty = x, y end
      local rv = "-"
      if tx ~= nil and ty ~= nil then
        local gut, r = pcall(_setDest, UNITS_STATE, nr, tx, ty, 0)
        rv = gut and tostring(r) or "Fehler"
        if gut and r == 1 then ok = ok + 1 end
      end
      if #teile < 30 then
        table.insert(teile, string.format("%d:T%d@(%d,%d)%s", nr, core.readSmallInteger(b + 0x8E) or -1, x, y,
          rv ~= "-" and ("=" .. rv) or ""))
      end
    end
    log(INFO, string.format("GRUPPE Tick %d: %d Einheiten%s%s, angenommen %d: %s", tick(), #nummern,
      typ and (" Typ " .. typ) or "", sp and (" Spieler " .. sp) or "", ok, table.concat(teile, " ")))
    return true
  end

  --==========================================================================
  -- Einheiten-Wacht (04.10.2026): gehorcht eine Einheit, und wer ueberschreibt ihr Ziel?
  --   { "einheitwacht": { "nr": [3, 137], "alle": 10 } }   /   { "einheitwacht": false }
  -- Nur im laufenden Spiel (in der Pause laeuft der Taktgeber weiter, die Zeit nicht):
  -- jede Aenderung des Ziels (+0xC8/+0xCA) mit Tick und Ort, alle "alle" Ticks die Orte.
  --   { "typen": { "spieler": 2 } }   Anzahl Einheiten je Typ (ohne spieler: je Spieler und Typ)
  --==========================================================================
  if cmd.einheitwacht ~= nil then
    if cmd.einheitwacht == false then
      einheitWacht = nil
      log(INFO, "EINHEITWACHT: aus.")
      return true
    end
    local w = cmd.einheitwacht
    einheitWacht = { e = {}, alle = tonumber(w.alle) or 10, naechste = tick() }
    local n = 0
    for _, nr in ipairs(w.nr or {}) do einheitWacht.e[tonumber(nr)] = {}; n = n + 1 end
    log(INFO, string.format("EINHEITWACHT: scharf fuer %d Einheiten (Tick %d), Orte alle %d Ticks.", n, tick(), einheitWacht.alle))
    return true
  end

  --   { "halten": { "spieler": 2, "typ": 13, "zu": 19 } }       Gruppe zum Gebaeude-Eingang, festhalten
  --   { "halten": { "spieler": 2, "typ": 13, "hier": true } }   Gruppe auf der Stelle einfrieren
  --   { "halten": { "nr": [3], "x": 180, "y": 109 } }           einzelne Einheiten auf ein Feld
  --   { "halten": false }  alle loslassen   /   { "halten": { "los": [3, 5] } }  diese loslassen
  --   { "halten": { "zurueck": true } }  alle loslassen UND ihr altes Ziel wiederherstellen
  --     (gemessen 04.10.: nach blossem Loslassen nahmen 18 von 24 Apfelbauern 600 Ticks lang
  --     keine Arbeit wieder auf - sie blieben am Kornspeicher stehen)
  -- Die Wacht setzt das Ziel nach, sobald KI, Arbeit oder Lord-Logik es aendern - nur im
  -- laufenden Spiel und hoechstens alle 10 Ticks je Einheit (wie die Lord-Wacht, 01.10.).
  if cmd.halten ~= nil then
    local h = cmd.halten
    if h == false then
      local n = 0
      for _ in pairs(festhalten) do n = n + 1 end
      festhalten = {}
      log(INFO, string.format("HALTEN: alle %d losgelassen (Tick %d).", n, tick()))
      return true
    end
    if h.zurueck == true or h.zurueck == "arbeit" then
      -- "arbeit": zum Eingang des eigenen Arbeitsgebaeudes (+0x338, gemessen 04.10.: zeigt bei
      -- Apfelbauern auf Apfelplantagen, bei Milchbauern auf Milchhoefe). Ohne Arbeitsgebaeude:
      -- altes Ziel. Anlass: 7 von 24 Apfelbauern waren beim Zurueckrufen mit Ware zum Kornspeicher
      -- unterwegs (Zustand 7) - ihr "altes Ziel" war der Kornspeicher, dort blieben sie stehen.
      _setDest = _setDest or core.exposeCode(ADR_SETDEST, 5, 1)
      local n, ok, arbeit = 0, 0, 0
      for nr, f in pairs(festhalten) do
        n = n + 1
        local tx, ty = f.altx, f.alty
        if h.zurueck == "arbeit" then
          local w = core.readSmallInteger(0x0138854C + nr * 1168 + 0x338) or 0
          if w > 0 and w < 2000 then
            local g = GEBAEUDE + w * G_SCHRITT
            if (core.readSmallInteger(g + G_ZUSTAND) or 0) ~= 0 then
              tx, ty = core.readSmallInteger(g + 0x112), core.readSmallInteger(g + 0x114)
              arbeit = arbeit + 1
            end
          end
        end
        if tx and tx > 0 then
          local gut, r = pcall(_setDest, UNITS_STATE, nr, tx, ty, 0)
          if gut and r == 1 then ok = ok + 1 end
        end
      end
      if h.zurueck == "arbeit" then
        festhalten = {}
        log(INFO, string.format("HALTEN: alle %d losgelassen, %d zum Arbeitsgebaeude, angenommen %d (Tick %d).", n, arbeit, ok, tick()))
        return true
      end
      festhalten = {}
      log(INFO, string.format("HALTEN: alle %d losgelassen, altes Ziel bei %d wiederhergestellt (Tick %d).", n, ok, tick()))
      return true
    end
    if type(h.los) == "table" then
      for _, nr in ipairs(h.los) do festhalten[tonumber(nr)] = nil end
      log(INFO, string.format("HALTEN: %d losgelassen (Tick %d).", #h.los, tick()))
      return true
    end
    local sp, typ = tonumber(h.spieler), tonumber(h.typ)
    local nummern = {}
    if type(h.nr) == "table" then
      for _, n in ipairs(h.nr) do table.insert(nummern, tonumber(n)) end
    else
      local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
      for i = 1, grenze - 1 do
        local b = 0x0138854C + i * 1168
        if (core.readSmallInteger(b + 0x8C) or 0) ~= 0 and (typ == nil or core.readSmallInteger(b + 0x8E) == typ)
           and (sp == nil or core.readSmallInteger(b + 0x96) == sp) then
          table.insert(nummern, i)
        end
      end
    end
    local zx, zy = tonumber(h.x), tonumber(h.y)
    if h.zu ~= nil then
      local geb = gebaeudeVon(sp, tonumber(h.zu))[1]
      if geb == nil then log(WARNING, "HALTEN: kein Gebaeude Typ " .. tostring(h.zu)) return false end
      zx, zy = geb.ex, geb.ey
    end
    _setDest = _setDest or core.exposeCode(ADR_SETDEST, 5, 1)
    local ok = 0
    for _, nr in ipairs(nummern) do
      local b = 0x0138854C + nr * 1168
      local tx, ty = zx, zy
      if h.hier == true then
        tx = math.floor((core.readSmallInteger(b + 0xB6) or 0) / 8)
        ty = math.floor((core.readSmallInteger(b + 0xB8) or 0) / 8)
      end
      if tx ~= nil and ty ~= nil then
        -- altes Ziel ZUERST lesen: setDestinationForUnit schreibt +0xC8/+0xCA sofort
        -- (gemessen 04.10., 19:03 - so gemerkt war das "alte" Ziel schon der Kornspeicher)
        local vorher = festhalten[nr]       -- schon gehalten: das urspruengliche alte Ziel behalten
        local ax = vorher and vorher.altx or core.readSmallInteger(b + 0xC8)
        local ay = vorher and vorher.alty or core.readSmallInteger(b + 0xCA)
        local gut, r = pcall(_setDest, UNITS_STATE, nr, tx, ty, 0)
        if gut and r == 1 then ok = ok + 1 end
        festhalten[nr] = { x = tx, y = ty, gesetzt = 0, letzter = -100, uid = core.readInteger(b + 0x98),
          altx = ax, alty = ay }
      end
    end
    log(INFO, string.format("HALTEN Tick %d: %d Einheiten festgehalten%s, Befehl angenommen %d.", tick(), #nummern,
      (zx and not h.hier) and string.format(" bei (%d,%d)", zx, zy) or (h.hier and " auf der Stelle" or ""), ok))
    return true
  end

  --   { "arbeitsplatz": { "spieler": 2, "typ": 13 } }  je Einheit: Zustand (+0x2C0), Unterzustand
  --   (+0x380), abzuliefernde Ware (+0x388), Arbeitsgebaeude (+0x338) mit Typ und Eingang.
  --   Felder aus der Strukturliste (Unit), Deutung ungeprueft - genau das soll das hier pruefen.
  if cmd.arbeitsplatz ~= nil and type(cmd.arbeitsplatz) == "table" then
    local sp, typ = tonumber(cmd.arbeitsplatz.spieler), tonumber(cmd.arbeitsplatz.typ)
    local teile = {}
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    for i = 1, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0 and (typ == nil or core.readSmallInteger(b + 0x8E) == typ)
         and (sp == nil or core.readSmallInteger(b + 0x96) == sp) then
        local w = core.readSmallInteger(b + 0x338) or -1
        local gt, ex, ey = -1, -1, -1
        if w > 0 and w < 2000 then
          local g = GEBAEUDE + w * G_SCHRITT
          gt, ex, ey = core.readSmallInteger(g + G_TYP) or -1, core.readSmallInteger(g + 0x112) or -1, core.readSmallInteger(g + 0x114) or -1
        end
        table.insert(teile, string.format("%d:Z%d/U%d/W%d/G%d(T%d@%d,%d)", i, core.readSmallInteger(b + 0x2C0) or -1,
          core.readSmallInteger(b + 0x380) or -1, core.readSmallInteger(b + 0x388) or -1, w, gt, ex, ey))
      end
    end
    log(INFO, string.format("ARBEITSPLATZ Tick %d (%d): %s", tick(), #teile, table.concat(teile, " ")))
    return true
  end

  --   { "aufloesen": { "nr": [154, 155] } }  oder  { "aufloesen": { "spieler": 2, "typ": 22, "anzahl": 3 } }
  --   Ruft disbandUnit (0x0052EDC0, thiscall UnitsState, 1 Argument) - der Weg des Spiels:
  --   mit Lagerfeuer wird die Einheit Bauer und geht dorthin, ohne Lagerfeuer verschwindet sie
  --   (abgelesen 04.10., daten/dekomp_aufloesen.c).
  if cmd.aufloesen ~= nil and type(cmd.aufloesen) == "table" then
    local a = cmd.aufloesen
    local sp, typ, anzahl = tonumber(a.spieler), tonumber(a.typ), tonumber(a.anzahl) or 9999
    local nummern = {}
    if type(a.nr) == "table" then
      for _, n in ipairs(a.nr) do table.insert(nummern, tonumber(n)) end
    else
      local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
      for i = 1, grenze - 1 do
        if #nummern >= anzahl then break end
        local b = 0x0138854C + i * 1168
        if (core.readSmallInteger(b + 0x8C) or 0) ~= 0 and core.readSmallInteger(b + 0x8E) == typ
           and (sp == nil or core.readSmallInteger(b + 0x96) == sp) then
          table.insert(nummern, i)
        end
      end
    end
    local auf = core.exposeCode(0x0052EDC0, 2, 1)
    local teile = {}
    for _, nr in ipairs(nummern) do
      local ok, r = pcall(auf, UNITS_STATE, nr)
      table.insert(teile, string.format("%d=%s", nr, ok and tostring(r) or "Fehler"))
    end
    log(INFO, string.format("AUFLOESEN Tick %d: %d Einheiten (Rueckgabe 1 = mit Lagerfeuer zum Bauern): %s",
      tick(), #nummern, table.concat(teile, " ")))
    return true
  end

  --   { "zickzack": { "nr": 147, "a": [159, 108], "b": [171, 108], "alle": 5, "ticks": 200 } }
  --   Schickt die Einheit ab dem naechsten laufenden Tick abwechselnd nach a und b, alle "alle"
  --   Ticks (1 = jeden Tick), und schreibt JEDEN Tick ihre Feinposition (+0xB6/+0xB8, 8 je Feld)
  --   und ihr Ziel: "ZZ t dx/dy x y ziel". Befehle je Tick gehen nur so - der Weg ueber die
  --   Befehlsdatei liest alle ~20 Bilder.
  if cmd.zickzack ~= nil then
    if cmd.zickzack == false then zickzack = nil; log(INFO, "ZICKZACK: aus.") return true end
    local z = cmd.zickzack
    zickzack = { nr = tonumber(z.nr), a = z.a, b = z.b, alle = math.max(1, tonumber(z.alle) or 10),
                 ticks = tonumber(z.ticks) or 200, t0 = nil, n = 0 }
    log(INFO, string.format("ZICKZACK: Einheit %d zwischen (%d,%d) und (%d,%d), Wechsel alle %d Ticks, %d Ticks lang.",
      zickzack.nr, z.a[1], z.a[2], z.b[1], z.b[2], zickzack.alle, zickzack.ticks))
    return true
  end

  --==========================================================================
  -- Bauen und Anwerben wie ein Klick des Menschen (04.10.2026, Selfaware M11/M12)
  -- Weg: Parameter in DAT_GameCommandParam0..5 (GameSynchronyState + 0x7A850, je 4 Byte),
  -- dann queueCommand (0x00489100, thiscall GameSynchronyState, 1 Argument). Das Spiel fuehrt
  -- den Befehl als Handlung des eigenen Spielers aus - mit Platz- und Kostenpruefung.
  --   { "baue": { "mapper": 51, "x": 175, "y": 108, "groesse": 3, "richtung": 0 } }
  --     GCT_PLACE_BUILDING = 28 -> ClickPlaceBuilding: P0 x, P1 y, P2 Mapper, P3 Groesse,
  --     P4 Drehung, P5 Trupp (abgelesen, daten/dekomp_bauen_anwerben.c). Mapper und Groesse
  --     je Gebaeude: VillageStudio lib/gebaeude.json.
  --   { "werbe": { "typ": 22, "gebaeude": 12 } }
  --     GCT_RECRUIT_UNIT = 31 -> ClickRecruitUnit -> ProcessRecruitUnit(Spieler, P0 Typ, P1 Gebaeude)
  --   { "vorrat": 1 }   Gold und Waren des Spielers (PlayerData + 0x4D0 + Ware*4)
  --==========================================================================
  local PARAM = 0x0191D768 + 0x7A850
  local function befehlAbsetzen(nr, werte)
    for i = 0, 5 do core.writeInteger(PARAM + i * 4, tonumber(werte[i + 1]) or 0) end
    local ok, err = pcall(function() core.exposeCode(0x00489100, 2, 1)(0x0191D768, nr) end)
    return ok, err
  end

  --   { "eigenerPlatz": 1 }  welcher Spieler "ich" bin (GameSynchronyState + 0x109E74). Gemessen
  --   04.10.: nach unserem eigenen Gefecht (Mensch auf Platz 1) stand hier 0 - jeder Bau- und
  --   Anwerbebefehl lief dann still fuer den neutralen Spieler 0 und tat nichts.
  --   Zweiter Teil (gemessen 04.10., 21:20): Ein geladener Spielstand traegt den Menschen NICHT in
  --   currentPlayerFullIDArray (0x0191DE10) ein - alles steht auf -1. Der Platz gilt dann weder als
  --   Mensch noch als KI; checkSkirmishGameDefeat sieht nur noch Rotkaeppchens Mannschaft und beendet
  --   das Spiel im ersten Takt (gameOver 1, Endbildschirm). Darum hier wie in eigenesGefecht:
  --   Platz ohne KI -> fullID = 1 ("Mensch da").
  if cmd.eigenerPlatz ~= nil then
    local sp = tonumber(cmd.eigenerPlatz) or 1
    local alt = core.readInteger(0x0191D768 + 0x109E74)
    core.writeInteger(0x0191D768 + 0x109E74, sp)
    local fullAlt = core.readInteger(0x0191DE10 + sp * 4)
    if sp >= 1 and sp <= 8 and (core.readInteger(0x0191DE7C + sp * 4) or 0) == 0 then
      core.writeInteger(0x0191DE10 + sp * 4, 1)
    end
    log(INFO, string.format("EIGENER PLATZ: %s -> %s; Mensch-Eintrag Platz %d: %s -> %s; gameOver %s",
      tostring(alt), tostring(core.readInteger(0x0191D768 + 0x109E74)), sp, tostring(fullAlt),
      tostring(core.readInteger(0x0191DE10 + sp * 4)), tostring(core.readInteger(0x0117D500))))
    return true
  end

  --   { "platz": { "spieler": 1, "mapper": 51, "groesse": 3, "x": 186, "y": 116 } }
  --   { "platzsuche": { "spieler": 1, "mapper": 51, "groesse": 3, "x": 172, "y": 109, "r": 15, "max": 8 } }
  -- Fragt die Pruefung des Spiels (checkBuildingCanBePlacedHere 0x005037B0, thiscall TileMapState,
  -- 5 Argumente) - baut nichts, kostet nichts. Ergebnis: TileMapState.buildingPlacementFail
  -- (0x01FE7B3C; 0 = geht) und ...FailReason (0x01FE7B40). Die Suche geht ringweise nach aussen
  -- und meldet die naechsten freien Stellen (Abstand = Schachbrett-Abstand zum Mittelpunkt).
  local function platzGeht(sp, mapper, groesse, x, y)
    -- wie placeBuilding: vorher die Bau-Drehung setzen (TileMapState+0x5549B4 = Drehung/2, hier 0)
    core.writeInteger(0x01FE7BBC, 0)
    local ok = pcall(core.exposeCode(0x005037B0, 6, 1), 0x01A93208, sp, x, y, mapper, groesse)
    return ok and (core.readInteger(0x01FE7B3C) or 1) == 0, core.readInteger(0x01FE7B3C), core.readInteger(0x01FE7B40)
  end

  if cmd.platz ~= nil and type(cmd.platz) == "table" then
    local p = cmd.platz
    local geht, f, grund = platzGeht(tonumber(p.spieler) or 1, tonumber(p.mapper), tonumber(p.groesse), tonumber(p.x), tonumber(p.y))
    log(INFO, string.format("PLATZ (%d,%d) Mapper %d Groesse %d: %s (Fehler %s, Grund %s)", p.x, p.y, p.mapper,
      p.groesse, geht and "GEHT" or "geht nicht", tostring(f), tostring(grund)))
    return true
  end

  if cmd.platzsuche ~= nil and type(cmd.platzsuche) == "table" then
    local p = cmd.platzsuche
    local sp, m, g = tonumber(p.spieler) or 1, tonumber(p.mapper), tonumber(p.groesse)
    local cx, cy, r, max = tonumber(p.x), tonumber(p.y), tonumber(p.r) or 15, tonumber(p.max) or 8
    local frei, geprueft = {}, 0
    for ring = 0, r do
      for dx = -ring, ring do
        for dy = -ring, ring do
          if math.max(math.abs(dx), math.abs(dy)) == ring and #frei < max then
            geprueft = geprueft + 1
            if platzGeht(sp, m, g, cx + dx, cy + dy) then table.insert(frei, string.format("(%d,%d)", cx + dx, cy + dy)) end
          end
        end
      end
      if #frei >= max then break end
    end
    log(INFO, string.format("PLATZSUCHE Mapper %d Groesse %d um (%d,%d): %d frei von %d geprueft: %s", m, g, cx, cy,
      #frei, geprueft, table.concat(frei, " ")))
    return true
  end

  --   { "platzkarte": { "spieler": 1, "mapper": 72, "groesse": 10, "x0": 130, "y0": 70, "x1": 230, "y1": 170 } }
  --   Fragt die Spielpruefung fuer JEDE Stelle im Rechteck und schreibt nach
  --   ucp/villagestudio/abzug/platzkarte.txt: "+" geht, sonst der Grund als Zeichen (0-9, a-z = Grund
  --   0-35, "?" groesser). Baut nichts, kostet nichts.
  if cmd.platzkarte ~= nil and type(cmd.platzkarte) == "table" then
    local p = cmd.platzkarte
    local sp, m, g = tonumber(p.spieler) or 1, tonumber(p.mapper), tonumber(p.groesse)
    local x0, y0, x1, y1 = tonumber(p.x0), tonumber(p.y0), tonumber(p.x1), tonumber(p.y1)
    local zeichen = "0123456789abcdefghijklmnopqrstuvwxyz"
    local f = io.open("ucp/villagestudio/abzug/platzkarte.txt", "w")
    f:write(string.format("mapper=%d groesse=%d x0=%d y0=%d x1=%d y1=%d" .. string.char(10), m, g, x0, y0, x1, y1))
    local gut, alle = 0, 0
    for y = y0, y1 do
      local zeile = {}
      for x = x0, x1 do
        alle = alle + 1
        local geht, _, grund = platzGeht(sp, m, g, x, y)
        if geht then gut = gut + 1; zeile[#zeile + 1] = "+"
        else
          local gr = tonumber(grund) or -1
          zeile[#zeile + 1] = (gr >= 0 and gr < 36) and zeichen:sub(gr + 1, gr + 1) or "?"
        end
      end
      f:write(table.concat(zeile) .. string.char(10))
    end
    f:close()
    log(INFO, string.format("PLATZKARTE Mapper %d Groesse %d (%d,%d)-(%d,%d): %d von %d gehen -> abzug/platzkarte.txt",
      m, g, x0, y0, x1, y1, gut, alle))
    return true
  end

  --   { "rohstoffkarte": { "x0": 0, "y0": 0, "x1": 399, "y1": 399 } }  (04.10.2026)
  --   abzug/rohstoffe.txt: je Feld b Stein (LogicLayer 0x20000), i Eisen (0x80000), o Pech (Vorzeichenbit),
  --   x Fluss (0x100000), # Rand (0x30), w Wasser (0x01), B Gebaeude (BuildingLayer), G Gruenland, s Gestruepp, . sonst.
  --   abzug/baeume.txt: jeder Baum aus LandscapeState.trees (0x00F2CC38 + 28 + i*156): Nummer, Art (+70),
  --   Zustand (+68), x (+98), y (+100), Stufe (+128), rest (+120, zaehlt beim Hacken herunter - gemessen 04.10.),
  --   voll (+122), groesse (+108). Felder abgelesen aus OpenSHC-Strukturen.
  if cmd.rohstoffkarte ~= nil and type(cmd.rohstoffkarte) == "table" then
    local g = cmd.rohstoffkarte
    local x0, y0, x1, y1 = tonumber(g.x0) or 0, tonumber(g.y0) or 0, tonumber(g.x1) or 399, tonumber(g.y1) or 399
    local NL = string.char(10)
    local f = io.open("ucp/villagestudio/abzug/rohstoffe.txt", "w")
    local n = {}
    f:write(string.format("x0=%d y0=%d x1=%d y1=%d", x0, y0, x1, y1) .. NL)
    for y = y0, y1 do
      local zeile = {}
      local basis = core.readInteger(0x023372F8 + y * 12 + 8) or 0
      for x = x0, x1 do
        local k = basis + x
        local l = core.readInteger(0x01BF8368 + k * 4) or 0
        local l2 = core.readByte(0x01C471E8 + k) or 0
        local geb = core.readSmallInteger(0x01C95BB8 + k * 2) or 0
        local c = "."
        if g.mauern and (l & MAUERBIT) ~= 0 then         -- 05.10.: Mauerfelder fuer den Klettertest (nur mit "mauern": true)
          -- T = Torhaus/Turm (Gebaeude auf dem Feld), sonst Mauer: Ziffer = Besitzer-Ebene (zaehlt ab 0, 9 = 9 und mehr)
          c = (geb ~= 0) and "T" or tostring(math.min(core.readByte(BESITZER + k) or 9, 9))
        elseif (l & 0x30) ~= 0 then c = "#"
        elseif geb ~= 0 then c = "B"
        elseif (l & 0x20000) ~= 0 then c = "b"
        elseif (l & 0x80000) ~= 0 then c = "i"
        elseif l < 0 or (l & 0x80000000) ~= 0 then c = "o"
        elseif (l & 0x100000) ~= 0 then c = "x"
        elseif (l & 0x01) ~= 0 then c = "w"
        elseif (l2 & 0x90) ~= 0 then c = "G"
        elseif (l2 & 0x01) ~= 0 then c = "s" end
        n[c] = (n[c] or 0) + 1
        zeile[#zeile + 1] = c
      end
      f:write(table.concat(zeile) .. NL)
    end
    f:close()
    local LS = 0x00F2CC38
    local anzahl = core.readInteger(LS + 16) or 0
    local fb = io.open("ucp/villagestudio/abzug/baeume.txt", "w")
    fb:write("nr art zustand x y stufe rest voll groesse" .. NL)
    local lebend = 0
    for i = 1, math.min(anzahl, 1999) do
      local t = LS + 28 + i * 156
      local zust = core.readSmallInteger(t + 68) or 0
      if zust ~= 0 then
        lebend = lebend + 1
        fb:write(string.format("%d %d %d %d %d %d %d %d %d", i, core.readSmallInteger(t + 70) or -1, zust,
          core.readSmallInteger(t + 98) or -1, core.readSmallInteger(t + 100) or -1, core.readInteger(t + 128) or -1,
          core.readSmallInteger(t + 120) or -1, core.readSmallInteger(t + 122) or -1, core.readSmallInteger(t + 108) or -1) .. NL)
      end
    end
    fb:close()
    local teile = {}
    for c, z in pairs(n) do teile[#teile + 1] = c .. "=" .. z end
    log(INFO, string.format("ROHSTOFFKARTE (%d,%d)-(%d,%d): %s; Baeume %d von maxTreeCount %d -> abzug/rohstoffe.txt, baeume.txt",
      x0, y0, x1, y1, table.concat(teile, " "), lebend, anzahl))
    return true
  end

  --   { "lagebild": true }  (04.10.2026, Daniel: ALLE Einheiten verfolgen, besonders wer uns angreift)
  --   abzug/lagebild.txt: je lebende Einheit nr besitzer typ x y leben zustand zielart zieleinheit zieluid
  --   zielgebaeude ziel zielx ziely. Felder (Unit, 1168 Byte, Referenz = unsere Basis 0x0138854C):
  --   +924 targetingType, +926 targetedUnitID, +928 targetedUID/buildingUID, +822 targetID_OR_targetBuildingID,
  --   +782 target, +784/+786 targetX/Y, +968 health, +704 state, +672 dying, Laufziel +0xC8/+0xCA (KI-Angriffe stehen
  --   hier, nicht in den Befehlsfeldern - gemessen 04.10.). Ort = Mikro +0xB6/+0xB8 / 8.
  if cmd.lagebild ~= nil then
    local NL = string.char(10)
    local E = 0x0138854C
    local f = io.open("ucp/villagestudio/abzug/lagebild.txt", "w")
    f:write(string.format("tick %d", tick()) .. NL .. "nr besitzer typ x y leben zustand zielart zieleinheit zieluid zielgebaeude ziel zielx ziely laufx laufy auswahlvon auswahlmarke gruppe gruppenuid ladung arbeitsplatz erreichbar nahziel nahangreifer" .. NL)
    local WEGNETZ = 0x01DF6FD8
    local kannHin = core.exposeCode(0x004A5320, 5, 1)
    local function feld(x, y) return (core.readInteger(0x023372F8 + y * 12 + 8) or 0) + x end
    local ex, ey = (lagebildVon or {})[1] or 165, (lagebildVon or {})[2] or 111
    local vonGebiet = core.readSmallInteger(WEGNETZ + feld(ex, ey) * 2) or 0
    local ich = core.readInteger(0x01A275DC) or 1
    local n, maxN = 0, core.readInteger(0x01387F38) or 0
    for i = 1, math.min(maxN, 2999) do
      local u = E + i * 1168
      local typ = core.readSmallInteger(u + 0x8E) or 0
      if typ > 0 and (core.readSmallInteger(u + 0x8C) or 0) ~= 0 and (core.readSmallInteger(u + 672) or 0) == 0 then
        n = n + 1
        -- erreichbar (05.10., Daniel: "da stehen einfach Bogenschuetzen und farmen unsere Assassinen ab"): liegt das
        -- Feld einer fremden Einheit in einem Wegnetz-Gebiet, das wir vom Bergfried aus erreichen? Schuetzen auf
        -- Mauern und Tuermen in einer geschlossenen Burg sind es nicht. Eigene Einheiten: -1 (nicht geprueft).
        local erreichbarE = -1
        local besE = core.readSmallInteger(u + 0x96) or -1
        if besE ~= ich and besE > 0 and vonGebiet > 0 then
          local ux, uy = (core.readSmallInteger(u + 0xB6) or 0) // 8, (core.readSmallInteger(u + 0xB8) or 0) // 8
          erreichbarE = 0
          if ux >= 0 and ux < 400 and uy >= 0 and uy < 400 then
            local a = core.readSmallInteger(WEGNETZ + feld(ux, uy) * 2) or 0
            if a > 0 then
              local ok, r = pcall(kannHin, 0x012BB8C8, ich, vonGebiet, a, 0)
              if ok and r ~= 0 then erreichbarE = 1 end
            end
          end
        end
        f:write(string.format("%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d", i, core.readSmallInteger(u + 0x96) or -1, typ,
          (core.readSmallInteger(u + 0xB6) or 0) // 8, (core.readSmallInteger(u + 0xB8) or 0) // 8,
          core.readInteger(u + 968) or -1, core.readSmallInteger(u + 704) or -1, core.readSmallInteger(u + 924) or -1,
          core.readSmallInteger(u + 926) or -1, core.readInteger(u + 928) or -1, core.readSmallInteger(u + 822) or -1,
          core.readSmallInteger(u + 782) or -1, core.readSmallInteger(u + 784) or -1, core.readSmallInteger(u + 786) or -1,
          core.readSmallInteger(u + 0xC8) or -1, core.readSmallInteger(u + 0xCA) or -1,
          -- Auswahl und Gruppe (04.10. 23:58: alle Assassinen folgten dem letzten Befehl - Gruppe nachsehen)
          core.readSmallInteger(u + 178) or -1, core.readSmallInteger(u + 180) or -1,
          core.readSmallInteger(u + 728) or -1, core.readInteger(u + 740) or -1,
          -- Ladung und Arbeitsplatz (05.10.: Lager erst bauen, wenn der erste Traeger abliefern will; rechtzeitig erweitern)
          core.readSmallInteger(u + 904) or -1, core.readSmallInteger(u + 824) or -1, erreichbarE,
          -- Nahkampf (06.10., gemessen zielfeld_20261006_190019: bei Feinden zeigt +830 attackedUnitID auf das Opfer,
          -- 16 von 16 Treffern, 0 Fehlgriffe; beim Opfer zaehlt +942 attackedBy, wie viele es gerade angreifen)
          core.readSmallInteger(u + 830) or -1, core.readSmallInteger(u + 942) or -1) .. NL)
      end
    end
    f:close()
    -- dazu alle Gebaeude (eigene UND fremde): nr besitzer typ x y leben uid -> abzug/gebaeude.txt
    local fg = io.open("ucp/villagestudio/abzug/gebaeude.txt", "w")
    fg:write("nr besitzer typ x y leben uid erreichbar vorrat grenze verbund ware" .. NL)
    -- erreichbar (04.10., Daniel: zugebaute Gebaeude erkennen): irgendein Feld rund um den Grundriss liegt in einem
    -- Wegnetz-Gebiet (PathConnectionLayer, TileMapState +0x363DD0 = 0x01DF6FD8, ushort je Feld), das Spieler 1 vom
    -- Gebiet seines Bergfried-Eingangs aus erreichen kann (calculateCanPlayerUnitsNavigateToAreaFromArea 0x004A5320,
    -- thiscall PathFindingState 0x012BB8C8 - dieselbe Pruefung nimmt der Holzfaeller in findTree).
    local ng, anzG = 0, gebaeudeAnzahl() or 0
    for i = 1, anzG - 1 do
      local b = GEBAEUDE + i * G_SCHRITT
      if (core.readSmallInteger(b + G_ZUSTAND) or 0) ~= 0 then
        ng = ng + 1
        local bx, by = core.readSmallInteger(b + 0x102) or -1, core.readSmallInteger(b + 0x104) or -1
        local gr = core.readInteger(b + 0x10C) or 1
        if gr < 1 or gr > 12 then gr = 3 end
        local erreichbar = 0
        if vonGebiet > 0 and bx >= 1 and by >= 1 then
          for d = -1, gr do
            for _, xy in ipairs({ { bx + d, by - 1 }, { bx + d, by + gr }, { bx - 1, by + d }, { bx + gr, by + d } }) do
              if erreichbar == 0 and xy[1] >= 0 and xy[1] < 400 and xy[2] >= 0 and xy[2] < 400 then
                local a = core.readSmallInteger(WEGNETZ + feld(xy[1], xy[2]) * 2) or 0
                if a > 0 then
                  local ok, r = pcall(kannHin, 0x012BB8C8, ich, vonGebiet, a, 0)
                  if ok and r ~= 0 then erreichbar = 1 end
                end
              end
            end
          end
        end
        -- vorrat/grenze (05.10., Daniel: "nicht genug Ochsenjoche ... nicht geschaut, wann sich Steine sammeln"):
        -- Building +0x184 currentNumberOfResource / +0x188 currentLimitOfResource (hier b = Datensatz - 0x14),
        -- gemessen: Steinhaufen am Steinbruch (Typ 21) 7/47/42/34 von 48, Eisenmine 1-2 von 48.
        -- verbund: Building +0x192 quarryStockpileID - der Steinbruch zeigt auf seinen Steinhaufen (gemessen nr+1).
        -- ware (06.10. 20:45, Aufbau: der Schmied holt Eisen am Teil MIT Eisen): Building +0x18C Warenart des Lagerteils
        -- (gemessen 19:58: 2 Holz, 4 Stein) - hier b + 0x1A0
        fg:write(string.format("%d %d %d %d %d %d %d %d %d %d %d %d", i, core.readSmallInteger(b + G_BESITZER) or -1,
          core.readSmallInteger(b + G_TYP) or -1, bx, by, core.readSmallInteger(b + G_LEBEN) or -1,
          core.readInteger(b + 0xEC) or 0, erreichbar, core.readInteger(b + 0x198) or -1, core.readInteger(b + 0x19C) or -1,
          core.readSmallInteger(b + 0x1A6) or -1, core.readInteger(b + 0x1A0) or -1) .. NL)
      end
    end
    fg:close()
    log(INFO, string.format("LAGEBILD Tick %d: %d Einheiten, %d Gebaeude -> abzug/lagebild.txt, gebaeude.txt", tick(), n, ng))
    return true
  end

  --   { "wegkarte": { "x0": 130, "y0": 240, "x1": 190, "y1": 300 } }  (06.10.2026, Daniel: "alle moeglichen Wege durch
  --   Gebaeude durch"). Nur lesen. abzug/wegkarte.txt: Kopfzeile, dann je Kartenzeile je Feld "link:geb:gebiet:logik:hoehe:typ".
  --   link = PathLinkageLayer (TileMapState 0x01A93208 +3715824 = 0x01E1E4F8, 1 Byte je Feld): erlaubte Schritte zum
  --   Nachbarn, Bits im Uhrzeigersinn 1 N (y-1), 2 NO, 4 O (x+1), 8 SO, 0x10 S, 0x20 SW, 0x40 W, 0x80 NW (abgelesen aus
  --   updateSeparateAreaTileMap; die Regel steht in updatePathLinkageLayerBasedOnBuildingsUnk, daten/dekomp_weglinks2.c).
  --   geb = BuildingLayer, gebiet = PathConnectionLayer (Wegnetz, das Spiel baut es hoechstens alle 200 Takte neu),
  --   logik = LogicLayer (hex), hoehe = HeightLayer (+2751024 = 0x01D32C38).
  if cmd.wegkarte ~= nil and type(cmd.wegkarte) == "table" then
    local g = cmd.wegkarte
    local x0, y0 = tonumber(g.x0) or 0, tonumber(g.y0) or 0
    local x1, y1 = tonumber(g.x1) or 399, tonumber(g.y1) or 399
    local NL = string.char(10)
    local f = io.open("ucp/villagestudio/abzug/wegkarte.txt", "w")
    f:write(string.format("tick %d x0=%d y0=%d x1=%d y1=%d", tick(), x0, y0, x1, y1) .. NL)
    local n, offen = 0, 0
    for y = y0, y1 do
      local basis = core.readInteger(0x023372F8 + y * 12 + 8) or 0
      local zeile = {}
      for x = x0, x1 do
        local k = basis + x
        local link = core.readByte(0x01E1E4F8 + k) or 0
        local geb = core.readSmallInteger(0x01C95BB8 + k * 2) or 0
        local gtyp = (geb > 0) and (core.readSmallInteger(GEBAEUDE + geb * G_SCHRITT + G_TYP) or -1) or 0
        zeile[#zeile + 1] = string.format("%x:%d:%d:%x:%d:%d", link, geb,
          core.readSmallInteger(0x01DF6FD8 + k * 2) or 0, (core.readInteger(0x01BF8368 + k * 4) or 0) & 0xFFFFFFFF,
          core.readByte(0x01D32C38 + k) or 0, gtyp)
        n = n + 1
        if link ~= 0 then offen = offen + 1 end
      end
      f:write(table.concat(zeile, " ") .. NL)
    end
    f:close()
    log(INFO, string.format("WEGKARTE Tick %d (%d,%d)-(%d,%d): %d Felder, %d mit Weg -> abzug/wegkarte.txt", tick(),
      x0, y0, x1, y1, n, offen))
    return true
  end

  --   { "gruenland": { "x0": 140, "y0": 80, "x1": 220, "y1": 160 } }  Textkarte nach
  --   ucp/villagestudio/abzug/gruenland.txt: G Gruenland (Logic2Layer 0x10/0x80), s nur Gestruepp
  --   (0x01), # blockiert (LogicLayer 0x30), x unfruchtbar (LogicLayer 0x100000), . sonst.
  --   Regel abgelesen aus checkBuildingCanBePlacedHere (Farmen: alle Felder fruchtbar, >= 50 Gruenland).
  --   Feldnummer = translationMatrix[y].addXgetTile (0x023372F8 + y*12 + 8) + x.
  if cmd.gruenland ~= nil and type(cmd.gruenland) == "table" then
    local g = cmd.gruenland
    local x0, y0, x1, y1 = tonumber(g.x0), tonumber(g.y0), tonumber(g.x1), tonumber(g.y1)
    local f = io.open("ucp/villagestudio/abzug/gruenland.txt", "w")
    local n = { G = 0, s = 0, ["#"] = 0, x = 0, ["."] = 0 }
    f:write(string.format("x0=%d y0=%d x1=%d y1=%d\n", x0, y0, x1, y1))
    for y = y0, y1 do
      local zeile = {}
      local basis = core.readInteger(0x023372F8 + y * 12 + 8) or 0
      for x = x0, x1 do
        local k = basis + x
        local l = core.readInteger(0x01BF8368 + k * 4) or 0
        local l2 = core.readByte(0x01C471E8 + k) or 0
        local c = "."
        if (l & 0x30) ~= 0 then c = "#"
        elseif (l & 0x100000) ~= 0 then c = "x"
        elseif (l2 & 0x90) ~= 0 then c = "G"
        elseif (l2 & 0x01) ~= 0 then c = "s" end
        n[c] = n[c] + 1
        zeile[#zeile + 1] = c
      end
      f:write(table.concat(zeile) .. "\n")
    end
    f:close()
    log(INFO, string.format("GRUENLAND (%d,%d)-(%d,%d): G=%d s=%d #=%d x=%d .=%d -> abzug/gruenland.txt",
      x0, y0, x1, y1, n.G, n.s, n["#"], n.x, n["."]))
    return true
  end

  --   { "abreissen": { "nr": 6 } }   Gebaeude abreissen wie der Mensch per Klick: Spielbefehl 29
  --   (ClickDestroyBuilding: Nummer, Rueckgabe in Prozent, uid). Das Spiel prueft den Besitzer NICHT -
  --   darum hier: nur Gebaeude des eigenen Platzes (Fairness-Regel). Rueckgabe 50 %: genau das traegt der
  --   Abriss-Knopf ein (MenuItemActionHandler_BuildMenu_DeleteAction 0x00438ad9: Param1 = 0x32, gefunden 06.10.);
  --   hoeher als 50 wird gedeckelt - nie mehr als ein Mensch.
  --   uid = Referenz +0xD8 -> hier +0xEC (siehe Kopf: alle Gebaeude-Offsets + 0x14).
  if cmd.abreissen ~= nil and type(cmd.abreissen) == "table" then
    local nr = tonumber(cmd.abreissen.nr) or 0
    local b = GEBAEUDE + nr * G_SCHRITT
    local ich = core.readInteger(0x01A275DC) or -1
    local besitzer = core.readSmallInteger(b + G_BESITZER) or -1
    local typ = core.readSmallInteger(b + G_TYP) or -1
    local uid = core.readInteger(b + 0xEC) or 0
    if nr < 1 or (core.readSmallInteger(b + G_ZUSTAND) or 0) == 0 or besitzer ~= ich then
      log(INFO, string.format("ABREISSEN Nr %d abgelehnt: Besitzer %d, ich %d, Zustand %s", nr, besitzer, ich,
        tostring(core.readSmallInteger(b + G_ZUSTAND))))
      return true
    end
    local ok = befehlAbsetzen(29, { nr, math.max(0, math.min(50, tonumber(cmd.abreissen.rueckgabe) or 50)), uid })
    log(INFO, string.format("ABREISSEN Tick %d: Nr %d (Typ %d, uid %d) - abgesetzt=%s", tick(), nr, typ, uid, tostring(ok)))
    return true
  end

  --   { "angriff": { "einheiten": [nr, ...], "ziel": nr } }       Einheit angreifen  (Art 4)
  --   { "angriff": { "einheiten": [nr, ...], "gebaeude": nr } }   Gebaeude angreifen (Art 9)
  --   { "angriff": { "einheiten": [nr, ...], "halt": true } }     anhalten           (Art 31)
  --   { "angriff": { "einheiten": [nr, ...], "lauf": [x, y] } }   hinlaufen wie ein Mensch-Klick: Spielbefehl 17
  --   ClickMoveUnit (Gruppe, x, y, Sammeln 0, Tempo 0). Abgelesen 05.10.2026 (daten/dekomp_klettern.c): nur dieser
  --   Laufbefehl sucht fuer eine Gruppe NUR aus Assassinen einen Kletterweg (giveTribeMoveInstruction ->
  --   isTribeAllAssassins -> findPathUsingClimbingWithHeightMargin16); Befehl 36 kennt das nicht.
  --   Wie der Mensch (gelesen 04.10.): Auswahl-Bits (UnitsState 0x01387F38 +116, 400 Byte, Bit je
  --   Einheitennummer) setzen, Spielbefehl 16 MakeUnitSelection mit einer freien Gruppennummer
  --   (createPlayerTribe legt die Gruppe genau unter dieser Nummer an; frei = tribeState +24 == 0,
  --   Gruppen ab 0x01667F78 + 40, je 0x334 Byte), dann Spielbefehl 36 ClickGiveUnitsInstruction
  --   (Gruppe, Art, Ziel-Nr, Ziel-uid, 0). Nur eigene Einheiten werden ausgewaehlt (Fairness).
  --   { "wegtest": { "nr": <eigene Einheit>, "punkte": [[x, y], ...] } }  (05.10.2026, Lord-Trupp Schritt 0)
  --   Fragt den Wegfinder des Spiels selbst: setDestinationForUnit (0x0053D3D0) gibt FALSE, wenn es keinen Weg gibt
  --   (abgelesen: UpdateWoodcutter wertet genau das aus). Je Punkt 1/0 in "WEGTEST <nr>: 1011...", danach bekommt die
  --   Einheit ihr altes Laufziel zurueck. Nur eigene Einheiten (Fairness).
  if cmd.wegtest ~= nil and type(cmd.wegtest) == "table" then
    local w = cmd.wegtest
    local nr = tonumber(w.nr) or 0
    local u = 0x0138854C + nr * 1168
    local ich = core.readInteger(0x01A275DC) or -1
    if nr <= 0 or core.readSmallInteger(u + 0x96) ~= ich then
      log(INFO, string.format("WEGTEST %d: keine eigene Einheit", nr))
      return true
    end
    _setDest = _setDest or core.exposeCode(ADR_SETDEST, 5, 1)
    local altX, altY = core.readSmallInteger(u + 0xC8) or -1, core.readSmallInteger(u + 0xCA) or -1
    local aus = {}
    for _, p in ipairs(w.punkte or {}) do
      local ok, r = pcall(_setDest, UNITS_STATE, nr, tonumber(p[1]) or 0, tonumber(p[2]) or 0, 0)
      aus[#aus + 1] = (ok and r ~= 0 and r ~= false) and "1" or "0"
    end
    if altX >= 0 then pcall(_setDest, UNITS_STATE, nr, altX, altY, 0) end
    log(INFO, string.format("WEGTEST %d: %s (Typ %d, altes Laufziel (%d,%d) zurueck)", nr, table.concat(aus, ""),
      core.readSmallInteger(u + 0x8E) or -1, altX, altY))
    return true
  end

  if cmd.angriff ~= nil and type(cmd.angriff) == "table" then
    local a = cmd.angriff
    if not cmd.ausSchlange then
      -- Warteschlange (gemessen 04.10. nachts, pruefe_einzelbefehl.py): drei Angriffe im selben Takt landeten alle
      -- in der letzten Gruppe und liefen zum letzten Ziel - das Spiel arbeitet die Auswahl (Befehl 16) erst spaeter
      -- ab und liest dann die Auswahl-Bits des letzten Befehls. Darum setzt angriffSchlangeTick je Befehl ab und
      -- wartet, bis dessen Einheiten in ihrer Gruppe stehen (Einheit +728 tribeID), bevor der naechste kommt.
      table.insert(angriffSchlange, a)
      log(INFO, string.format("ANGRIFF eingereiht Tick %d: %d Einheiten, Schlange %d", tick(), #(a.einheiten or {}),
        #angriffSchlange))
      return true
    end
    local ich = core.readInteger(0x01A275DC) or -1
    local BITS = 0x01387F38 + 116
    -- Auswahlmarken aller eigenen Einheiten loeschen (gemessen 04.10. 23:58): playerMakeUnitSelection setzt bei jeder
    -- ausgewaehlten Einheit ifSelectedThenPlayerID (+178) und selectionRelatedFlag (+180), und diese Marken blieben
    -- stehen. Jede Einheit, die je einen Befehl bekam, rutschte in jede neue Gruppe - am Ende steckten 78 Assassinen,
    -- alle Bogenschuetzen, Speertraeger und der Lord in Gruppe 1249 und folgten einem Befehl fuer EINEN Assassinen.
    local maxN = core.readInteger(0x01387F38) or 0
    for i = 1, math.min(maxN, 2999) do
      local u = 0x0138854C + i * 1168
      if core.readSmallInteger(u + 0x96) == ich and (core.readSmallInteger(u + 178) or 0) ~= 0 then
        core.writeSmallInteger(u + 178, 0)
        core.writeSmallInteger(u + 180, 0)
      end
    end
    for k = 0, 99 do core.writeInteger(BITS + k * 4, 0) end
    local n, gewaehlt = 0, {}
    for _, nr in ipairs(a.einheiten or {}) do
      nr = tonumber(nr) or 0
      local u = 0x0138854C + nr * 1168
      if nr > 0 and core.readSmallInteger(u + 0x96) == ich and (core.readSmallInteger(u + 672) or 0) == 0 then
        festhalten[nr] = nil                    -- ein Angriffsbefehl hebt das Festhalten auf
        local b = BITS + (nr // 8)
        core.writeByte(b, (core.readByte(b) or 0) | (1 << (nr % 8)))
        n = n + 1
        gewaehlt[n] = nr
      end
    end
    local TR = 0x01667F78 + 40
    local gruppe = nil
    -- Gruppen, die in diesem Takt schon vergeben sind, reservieren (04.10.: die Gruppe entsteht erst im naechsten
    -- Takt - zwei Angriffe in derselben Runde bekamen dieselbe Nummer, die zweite Auswahl ueberschrieb die erste,
    -- und alle Trupps liefen auf ein Ziel)
    if angriffReserve == nil or angriffReserve.tick ~= tick() then angriffReserve = { tick = tick(), vergeben = {} } end
    for g = 1249, 1, -1 do
      if not angriffReserve.vergeben[g] and (core.readSmallInteger(TR + g * 0x334 + 24) or 1) == 0 then gruppe = g; break end
    end
    if gruppe then angriffReserve.vergeben[gruppe] = true end
    if n == 0 or gruppe == nil then
      log(INFO, string.format("ANGRIFF abgelehnt: %d eigene Einheiten, Gruppe %s", n, tostring(gruppe)))
      return true
    end
    local art, zielNr, zielUid = 31, 0, 0
    if a.ziel then
      art, zielNr = 4, tonumber(a.ziel)
      zielUid = core.readInteger(0x0138854C + zielNr * 1168 + 0x98) or 0
    elseif a.gebaeude then
      art, zielNr = 9, tonumber(a.gebaeude)
      zielUid = core.readInteger(GEBAEUDE + zielNr * G_SCHRITT + 0xEC) or 0
    end
    local ok1 = befehlAbsetzen(16, { gruppe })
    local ok2
    if type(a.lauf) == "table" then
      art, zielNr, zielUid = 17, tonumber(a.lauf[1]) or 0, tonumber(a.lauf[2]) or 0   -- im Log: Art 17, Ziel = x, uid = y
      ok2 = befehlAbsetzen(17, { gruppe, zielNr, zielUid, 0, 0 })
    else
      ok2 = befehlAbsetzen(36, { gruppe, art, zielNr, zielUid, 0 })
    end
    angriffWarten = { gruppe = gruppe, einheiten = gewaehlt, tick = tick() }
    log(INFO, string.format("ANGRIFF Tick %d: %d Einheiten, Gruppe %d, Art %d, Ziel %d (uid %d) - Auswahl=%s Befehl=%s",
      tick(), n, gruppe, art, zielNr, zielUid, tostring(ok1), tostring(ok2)))
    return true
  end

  if cmd.baue ~= nil and type(cmd.baue) == "table" then
    local b = cmd.baue
    local ok, err = befehlAbsetzen(28, { b.x, b.y, b.mapper, b.groesse, b.richtung or 0, b.trupp or 0 })
    log(INFO, string.format("BAUE Tick %d: Mapper %s bei (%s,%s), Groesse %s, Drehung %s - abgesetzt=%s%s",
      tick(), tostring(b.mapper), tostring(b.x), tostring(b.y), tostring(b.groesse), tostring(b.richtung or 0),
      tostring(ok), ok and "" or (" - " .. tostring(err))))
    return true
  end

  --   { "spielbefehl": { "nr": 38, "werte": [13, 0] } }  beliebiger Spielbefehl wie ein Klick.
  --   Belegte Nummern (Handler-Tabelle 0x00B38E10 + 4*Nr, abgelesen 04.10.): 28 Bauen, 31 Anwerben,
  --   34 Steuern (Stufe), 35 Rationen (Stufe), 38 Kaufen/Verkaufen (Ware, zweiter Wert).
  if cmd.spielbefehl ~= nil and type(cmd.spielbefehl) == "table" then
    local s = cmd.spielbefehl
    local ok, err = befehlAbsetzen(tonumber(s.nr), s.werte or {})
    log(INFO, string.format("SPIELBEFEHL Tick %d: Nr %s Werte [%s] - abgesetzt=%s%s", tick(), tostring(s.nr),
      table.concat(s.werte or {}, ","), tostring(ok), ok and "" or (" - " .. tostring(err))))
    return true
  end

  if cmd.werbe ~= nil and type(cmd.werbe) == "table" then
    local w = cmd.werbe
    local ok, err = befehlAbsetzen(31, { w.typ, w.gebaeude })
    log(INFO, string.format("WERBE Tick %d: Typ %s in Gebaeude %s - abgesetzt=%s%s", tick(), tostring(w.typ),
      tostring(w.gebaeude), tostring(ok), ok and "" or (" - " .. tostring(err))))
    return true
  end

  if cmd.vorrat ~= nil then
    local sp = tonumber(cmd.vorrat) or 1
    local namen = { [2] = "Holz", [3] = "Hopfen", [4] = "Stein", [6] = "Eisen", [7] = "Pech", [9] = "Weizen",
      [10] = "Brot", [11] = "Kaese", [12] = "Fleisch", [13] = "Apfel", [14] = "Bier", [15] = "Gold", [16] = "Mehl",
      [17] = "Bogen", [18] = "Armbrust", [19] = "Speer", [20] = "Pike", [21] = "Keule", [22] = "Schwert",
      [23] = "Leder", [24] = "Ruestung" }
    local teile = {}
    for w = 2, 24 do
      if namen[w] then table.insert(teile, string.format("%s=%d", namen[w], ware(sp, w) or -1)) end
    end
    log(INFO, string.format("VORRAT Spieler %d Tick %d: %s", sp, tick(), table.concat(teile, " ")))
    return true
  end

  --   { "status": 1 }  ALLES fuer eine Lenker-Runde in EINER Logzeile (04.10.2026: einzelne Abfragen kosteten
  --   je ~1 s, eine Runde ~20 s). STATUS t= ansicht= pause= over= mensch= beliebt= leute= platz= feuer=
  --   Waren (wie vorrat) G<typ>=<anzahl eigener Gebaeude> T<typ>=<anzahl eigener Einheiten>.
  if cmd.status ~= nil then
    local sp = tonumber(cmd.status) or 1
    local PDs = 0x0115BDF8 + sp * 0x39F4
    local function s32(v) v = v or 0; if v > 0x7FFFFFFF then return v - 0x100000000 end return v end
    local teile = { string.format("t=%d ansicht=%d pause=%d over=%d mensch=%d beliebt=%d leute=%d platz=%d feuer=%d",
      tick(), core.readInteger(0x01FE7D1C) or -1, core.readInteger(0x01FEA054) or -1, core.readInteger(0x0117D500) or -1,
      s32(core.readInteger(0x0191DE10 + sp * 4)), s32(core.readInteger(PDs + 0x60)), s32(core.readInteger(PDs + 8576)),
      s32(core.readInteger(PDs + 116)), s32(core.readInteger(PDs + 136))) }
    local namen = { [2] = "holz", [3] = "hopfen", [4] = "stein", [6] = "eisen", [7] = "pech", [9] = "weizen",
      [10] = "brot", [11] = "kaese", [12] = "fleisch", [13] = "apfel", [14] = "bier", [15] = "gold", [16] = "mehl" }
    for w = 2, 16 do
      if namen[w] then table.insert(teile, string.format("%s=%d", namen[w], ware(sp, w) or -1)) end
    end
    local gz, ez = {}, {}
    local n = gebaeudeAnzahl() or 0
    for i = 1, n - 1 do
      local b = GEBAEUDE + i * G_SCHRITT
      if (core.readSmallInteger(b + G_ZUSTAND) or 0) ~= 0 and core.readSmallInteger(b + G_BESITZER) == sp then
        local t = core.readSmallInteger(b + G_TYP) or -1
        gz[t] = (gz[t] or 0) + 1
      end
    end
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2999)
    for i = 1, grenze - 1 do
      local u = 0x0138854C + i * 1168
      if (core.readSmallInteger(u + 0x8C) or 0) ~= 0 and core.readSmallInteger(u + 0x96) == sp then
        local t = core.readSmallInteger(u + 0x8E) or -1
        ez[t] = (ez[t] or 0) + 1
      end
    end
    for t, z in pairs(gz) do table.insert(teile, string.format("G%d=%d", t, z)) end
    for t, z in pairs(ez) do table.insert(teile, string.format("T%d=%d", t, z)) end
    log(INFO, "STATUS " .. table.concat(teile, " "))
    return true
  end

  if cmd.typen ~= nil and type(cmd.typen) == "table" then
    local sp = tonumber(cmd.typen.spieler)
    local zaehl, schluessel = {}, {}
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    for i = 1, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0 then
        local bes = core.readSmallInteger(b + 0x96) or -1
        if sp == nil or bes == sp then
          local k = string.format("S%d:T%d", bes, core.readSmallInteger(b + 0x8E) or -1)
          if zaehl[k] == nil then table.insert(schluessel, k) end
          zaehl[k] = (zaehl[k] or 0) + 1
        end
      end
    end
    table.sort(schluessel)
    local teile = {}
    for _, k in ipairs(schluessel) do table.insert(teile, k .. "=" .. zaehl[k]) end
    log(INFO, "TYPEN: " .. table.concat(teile, " "))
    return true
  end

  -- { "zielsuche": { "nr": 3, "x": 200, "y": 199, "r": 25 } } - naechstes Feld um (x,y), das
  -- setDestinationForUnit fuer Einheit nr annimmt (Rueckgabe 1), ringweise nach aussen.
  -- Achtung: setzt dabei das Ziel der Einheit (Probe-Befehl, danach neu laden oder neu setzen).
  if cmd.zielsuche ~= nil then
    local z = cmd.zielsuche
    local nr, x0, y0, r = tonumber(z.nr), tonumber(z.x), tonumber(z.y), tonumber(z.r) or 25
    _setDest = _setDest or core.exposeCode(ADR_SETDEST, 5, 1)
    for ring = 0, r do
      for dx = -ring, ring do
        for dy = -ring, ring do
          if math.max(math.abs(dx), math.abs(dy)) == ring then
            local ok, rv = pcall(_setDest, UNITS_STATE, nr, x0 + dx, y0 + dy, 0)
            if ok and rv == 1 then
              log(INFO, string.format("ZIELSUCHE: (%d,%d) gueltig, Ring %d um (%d,%d).", x0 + dx, y0 + dy, ring, x0, y0))
              return true
            end
          end
        end
      end
    end
    log(INFO, string.format("ZIELSUCHE: kein gueltiges Feld bis Ring %d um (%d,%d).", r, x0, y0))
    return true
  end

  if cmd.einheit_ziel ~= nil then
    local z = cmd.einheit_ziel
    local nr, x, y = tonumber(z.nr), tonumber(z.x), tonumber(z.y)
    if nr == nil or x == nil or y == nil then
      log(WARNING, "EINHEIT: nr/x/y fehlt.") return false
    end
    _setDest = _setDest or core.exposeCode(ADR_SETDEST, 5, 1)
    local ok, r = pcall(_setDest, UNITS_STATE, nr, x, y, 0)
    if not ok then log(WARNING, "EINHEIT: Aufruf fehlgeschlagen: " .. tostring(r)) return false end
    if type(r) == "number" and r > 0x7FFFFFFF then r = r - 0x100000000 end
    log(INFO, string.format("EINHEIT %d -> (%d,%d): Rueckgabe %s", nr, x, y, tostring(r)))
    return true
  end

  --==========================================================================
  -- Wo stehen die Einheiten eines Typs? { "woSind": 24, "spieler": 1 }
  --
  -- Gibt Schwerpunkt und Streuung der Kacheln aus. Der Sinn: Ein Bildbeweis
  -- ist nur dann einer, wenn die geaenderten Einheiten auch im Ausschnitt
  -- liegen. Am 02.09.2026 zeigte ein Differenzbild 4,3 Prozent Aenderung -
  -- das waren aber Baeume im Wind und ein Ochsengespann, weil das Spiel
  -- wieder lief. Die getauschten Einheiten standen ganz woanders.
  --
  -- Kachel -> Karte: x = kachel % 400, y = math.floor(kachel / 400)
  --==========================================================================
  if cmd.woSind ~= nil then
    local typ = tonumber(cmd.woSind)
    local nurSpieler = tonumber(cmd.spieler)
    if typ == nil then return false end
    local n, sx, sy = 0, 0, 0
    local minx, maxx, miny, maxy = 9999, -1, 9999, -1
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    for i = 0, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0
         and (core.readSmallInteger(b + 0x8E) or -1) == typ
         and (nurSpieler == nil or (core.readSmallInteger(b + 0x96) or -1) == nurSpieler) then
        local k = core.readInteger(b + 0xD4) or 0
        local x, y = k % 400, math.floor(k / 400)
        n = n + 1; sx = sx + x; sy = sy + y
        if x < minx then minx = x end
        if x > maxx then maxx = x end
        if y < miny then miny = y end
        if y > maxy then maxy = y end
      end
    end
    if n == 0 then
      log(INFO, string.format("WOSIND Typ %d: keine gefunden.", typ))
    else
      log(INFO, string.format(
        "WOSIND Typ %d%s: %d Stueck, Schwerpunkt (%d,%d), Bereich x %d-%d y %d-%d",
        typ, nurSpieler and (" Spieler " .. nurSpieler) or "",
        n, math.floor(sx/n), math.floor(sy/n), minx, maxx, miny, maxy))
    end
    return true
  end

  -- Welche Einheiten stehen in einem Kachelbereich?
  --   { "dortSind": [x1, y1, x2, y2] }
  -- Zaehlt nach Typ und Besitzer. Damit laesst sich pruefen, WAS man im Bild
  -- sieht, bevor man etwas aendert - der Umweg ueber "ich tausche mal und
  -- schaue" hat am 02.09.2026 zwei Fehlversuche gekostet.
  if cmd.dortSind ~= nil then
    local r = cmd.dortSind
    if type(r) ~= "table" or #r ~= 4 then return false end
    local x1, y1, x2, y2 = r[1], r[2], r[3], r[4]
    local zaehler = {}
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    for i = 0, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0 then
        local k = core.readInteger(b + 0xD4) or 0
        local x, y = k % 400, math.floor(k / 400)
        if x >= x1 and x <= x2 and y >= y1 and y <= y2 then
          local typ = core.readSmallInteger(b + 0x8E) or -1
          local bes = core.readSmallInteger(b + 0x96) or -1
          local schl = string.format("Typ %d / Spieler %d", typ, bes)
          zaehler[schl] = (zaehler[schl] or 0) + 1
        end
      end
    end
    local liste = {}
    for k, v in pairs(zaehler) do table.insert(liste, {k, v}) end
    table.sort(liste, function(a, b) return a[2] > b[2] end)
    log(INFO, string.format("DORTSIND x %d-%d y %d-%d:", x1, x2, y1, y2))
    for i = 1, math.min(#liste, 8) do
      log(INFO, string.format("   %-24s %d", liste[i][1], liste[i][2]))
    end
    if #liste == 0 then log(INFO, "   nichts gefunden") end
    return true
  end

  --==========================================================================
  -- Kamera steuern
  --
  --   { "kamera": [233, 168] }     auf eine Kartenstelle springen
  --   { "grundriss": true }        Grundrissmodus (Leertaste)
  --   { "drehen": 2 }              Karte drehen: 0, 2, 4 oder 6
  --
  -- focusOnCoordinate 0x004E8CA0, thiscall, ECX = ViewportRenderState
  -- (0x021AEBD8), zwei Argumente. Bei thiscall zaehlt "this" mit, also drei.
  -- Grundriss: toggleFlatView 0x004F70B0, ECX = TileMapState (0x01A93208).
  -- Drehen:    setMapRotation 0x004F70E0, ECX ebenso. Der Wert ist nur ein
  --            Auftrag - processGameTick fuehrt ihn im naechsten Bild aus.
  --==========================================================================
  if cmd.kamera ~= nil then
    local k = cmd.kamera
    if type(k) ~= "table" or #k ~= 2 then
      log(WARNING, "KAMERA: [x, y] erwartet.")
      return false
    end
    local ok, err = pcall(function()
      core.exposeCode(0x004E8CA0, 3, 1)(0x021AEBD8, k[1], k[2])
    end)
    log(INFO, string.format("KAMERA: auf (%d,%d), ok=%s%s", k[1], k[2],
      tostring(ok), ok and "" or (" - " .. tostring(err))))
    return true
  end

  if cmd.grundriss ~= nil then
    local an = (cmd.grundriss == true) and 1 or 0
    local ok, err = pcall(function()
      core.exposeCode(0x004F70B0, 2, 1)(0x01A93208, an)
    end)
    log(INFO, string.format("GRUNDRISS: %d, ok=%s%s", an, tostring(ok),
      ok and "" or (" - " .. tostring(err))))
    return true
  end

  if cmd.drehen ~= nil then
    local vorher = core.readInteger(0x01FE7AA4)
    -- "links"/"rechts" = ein Schritt wie Strg+Pfeil im Spiel (WindowMsgProcessingFunc):
    -- Strg+Links = Ausrichtung + 2, Strg+Rechts = Ausrichtung + 6 (also - 2), je mod 8.
    local w = tonumber(cmd.drehen)
    if cmd.drehen == "links" then w = ((vorher or 0) + 2) % 8
    elseif cmd.drehen == "rechts" then w = ((vorher or 0) + 6) % 8 end
    if w == nil then return false end
    local ok, err = pcall(function()
      core.exposeCode(0x004F70E0, 2, 1)(0x01A93208, w)
    end)
    log(INFO, string.format("DREHEN: %s -> Auftrag %d, ok=%s%s",
      tostring(vorher), w, tostring(ok), ok and "" or (" - " .. tostring(err))))
    return true
  end

  -- Navigation wie Daniel sie im Spiel bedient (30.09.2026, M9). Abgelesen aus
  -- WindowMsgProcessingFunc (Tasten) und ..._PeasantBuildAndRightClickMenuSelection
  -- (Rechtsklick-Menue), Dekompilat: Selfaware-AI/daten/dekomp_navigation*.c
  --   { "leiste": true }             Leiste unten weg/zurueck (Tab): hideOrUnhideUI
  --                                  0x00471AA0, thiscall, ECX = GameCore. Umschalter.
  --   { "zoom": "raus" | "rein" }    wie Strg+Hoch / Rechtsklick rechts: resetupViewport
  --                                  0x004E7770 (ViewportRenderState, Zoomwert), dann
  --                                  WindowAndDirectDraw+0xC0 = 2 und MenuView_TriggerInitial = 1.
  --   { "absenken": true | false }   Rechtsklick unten / Strg+Runter: triggerLoweredView
  --                                  0x004F6FD0 mit 3 (abgesenkt) bzw. 4 (normal).
  --                                  Bei eingeschaltetem Grundriss setzt das Spiel selbst 2.
  if cmd.leiste ~= nil then
    local h0 = core.readInteger(0x021AEC60)
    local ok, err = pcall(function()
      core.exposeCode(0x00471AA0, 1, 1)(0x01FE7D10)
    end)
    log(INFO, string.format("LEISTE: umgeschaltet, ok=%s%s (Ansichtshoehe vorher %s)", tostring(ok),
      ok and "" or (" - " .. tostring(err)), tostring(h0)))
    return true
  end

  if cmd.zoom ~= nil then
    local soll = (cmd.zoom == "raus" or cmd.zoom == 1 or cmd.zoom == true) and 1 or 0
    local vorher = core.readInteger(0x021AEC68)
    local ok, err = pcall(function()
      core.exposeCode(0x004E7770, 2, 1)(0x021AEBD8, soll)
      core.writeInteger(0x00F983F8, 2)       -- WindowAndDirectDraw.unk_resetViewportRelated
      core.writeInteger(0x00B48EE4, 1)       -- UIDragDropDefinedData.DAT_MenuView_TriggerInitial
    end)
    log(INFO, string.format("ZOOM: %s -> %d, ok=%s%s", tostring(vorher), soll, tostring(ok),
      ok and "" or (" - " .. tostring(err))))
    return true
  end

  if cmd.absenken ~= nil then
    local w = (cmd.absenken == true) and 3 or 4
    local ok, err = pcall(function()
      core.exposeCode(0x004F6FD0, 2, 1)(0x01A93208, w)
    end)
    log(INFO, string.format("ABSENKEN: %d, ok=%s%s (Modus jetzt %s)", w, tostring(ok),
      ok and "" or (" - " .. tostring(err)), tostring(core.readInteger(0x01FE7AC0))))
    return true
  end

  -- Wo stehen die meisten Einheiten eines Spielers dicht beieinander?
  --   { "dichteste": 1 }   (Spielernummer)
  -- Rastert die Karte in 20x20-Felder und nennt das vollste. Ein Schwerpunkt
  -- taugt dafuer NICHT: Bei ueber die halbe Karte verstreuten Einheiten liegt
  -- er im Nichts - am 02.09.2026 zeigte die Kamera dort vier neutrale Tiere.
  if cmd.dichteste ~= nil then
    local sp = tonumber(cmd.dichteste)
    if sp == nil then return false end
    local feld = {}
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    for i = 0, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0
         and (core.readSmallInteger(b + 0x96) or -1) == sp then
        local k = core.readInteger(b + 0xD4) or 0
        local fx = math.floor((k % 400) / 20)
        local fy = math.floor(math.floor(k / 400) / 20)
        local schl = fx * 100 + fy
        feld[schl] = (feld[schl] or 0) + 1
      end
    end
    local besteSchl, besteZahl = nil, 0
    for k, v in pairs(feld) do
      if v > besteZahl then besteSchl, besteZahl = k, v end
    end
    if besteSchl == nil then
      log(INFO, string.format("DICHTESTE Spieler %d: keine Einheiten.", sp))
    else
      local fx, fy = math.floor(besteSchl / 100), besteSchl % 100
      log(INFO, string.format(
        "DICHTESTE Spieler %d: %d Einheiten im Feld x %d-%d y %d-%d, Mitte (%d,%d)",
        sp, besteZahl, fx*20, fx*20+19, fy*20, fy*20+19, fx*20+10, fy*20+10))
    end
    return true
  end

  -- Rohe Kachelnummern der Einheiten eines Spielers: { "kacheln": 1 }
  -- Ohne Umrechnung, damit sichtbar wird, ob die Annahme "x = k % 400"
  -- ueberhaupt stimmt. Am 02.09.2026 fand die Bereichssuche am Bergfried nur
  -- zehn Einheiten, waehrend im Bild rund 25 standen - ein Zeichen, dass die
  -- Umrechnung und nicht die Suche falsch war.
  if cmd.kacheln ~= nil then
    local sp = tonumber(cmd.kacheln)
    local liste, n = {}, 0
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    for i = 0, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0
         and (sp == nil or (core.readSmallInteger(b + 0x96) or -1) == sp) then
        n = n + 1
        if n <= 20 then
          table.insert(liste, string.format("%d:Typ%d", core.readInteger(b + 0xD4) or -1,
            core.readSmallInteger(b + 0x8E) or -1))
        end
      end
    end
    log(INFO, string.format("KACHELN Spieler %s: %d Einheiten, erste 20:",
      tostring(sp), n))
    log(INFO, "   " .. table.concat(liste, "  "))
    return true
  end

  --==========================================================================
  -- Zwei Einheiten desselben Typs Feld fuer Feld vergleichen
  --   { "vergleiche": 27, "a": 1, "b": 5 }
  --
  -- Sinn: Am 02.09.2026 kam heraus, dass ein Typwechsel die Darstellung NICHT
  -- aendert. Also muss es ein zweites Feld geben, das die Grafik traegt und
  -- beim Erzeugen gesetzt wird. Wer eine ECHTE Einheit des Zieltyps mit einer
  -- getauschten vergleicht, findet es: Es ist das Feld, das sich
  -- unterscheidet, obwohl unitType gleich ist.
  --==========================================================================
  if cmd.vergleiche ~= nil then
    local typ = tonumber(cmd.vergleiche)
    local spA, spB = tonumber(cmd.a), tonumber(cmd.b)
    if typ == nil or spA == nil or spB == nil then return false end

    local function finde(sp)
      local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
      for i = 0, grenze - 1 do
        local b = 0x0138854C + i * 1168
        if (core.readSmallInteger(b + 0x8C) or 0) ~= 0
           and (core.readSmallInteger(b + 0x8E) or -1) == typ
           and (core.readSmallInteger(b + 0x96) or -1) == sp then
          return i, b
        end
      end
      return nil, nil
    end

    local iA, bA = finde(spA)
    local iB, bB = finde(spB)
    if bA == nil or bB == nil then
      log(WARNING, string.format("VERGLEICHE: Typ %d nicht bei beiden gefunden (A=%s B=%s)",
        typ, tostring(iA), tostring(iB)))
      return true
    end

    log(INFO, string.format("VERGLEICHE Typ %d: Einheit %d (Spieler %d) gegen %d (Spieler %d)",
      typ, iA, spA, iB, spB))
    local anders = {}
    -- Nur die ersten 0x120 Byte: dort liegen Typ, Zustand, Besitzer, Position
    -- und alles, was mit Darstellung zu tun haben koennte.
    for off = 0, 0x11C, 4 do
      local va = core.readInteger(bA + off) or 0
      local vb = core.readInteger(bB + off) or 0
      if va ~= vb then
        table.insert(anders, string.format("+0x%03X: %08X / %08X", off, va, vb))
      end
    end
    log(INFO, string.format("   %d Felder unterscheiden sich:", #anders))
    for i = 1, math.min(#anders, 14) do
      log(INFO, "   " .. anders[i])
    end
    return true
  end

  -- Eine einzelne Einheit tauschen und dabei ALLE Felder mitschreiben.
  --   { "einzelTausch": 27, "nach": 22, "spieler": 1 }
  -- Zeigt, welche Felder sich beim Tausch aendern und welche NICHT. Das Feld,
  -- das die Darstellung traegt, gehoert zur zweiten Gruppe.
  if cmd.einzelTausch ~= nil then
    local von = tonumber(cmd.einzelTausch)
    local nach = tonumber(cmd.nach)
    local sp = tonumber(cmd.spieler)
    if von == nil or nach == nil then return false end
    local gefunden = nil
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    for i = 0, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0
         and (core.readSmallInteger(b + 0x8E) or -1) == von
         and (sp == nil or (core.readSmallInteger(b + 0x96) or -1) == sp) then
        gefunden = b
        break
      end
    end
    if gefunden == nil then
      log(WARNING, string.format("EINZELTAUSCH: keine Einheit vom Typ %d.", von))
      return true
    end
    -- Die GANZE Struktur, nicht nur der Anfang: Unit ist 1168 Byte lang
    -- (0x490). Beim ersten Versuch am 02.09. reichte der Blick nur bis 0x11C -
    -- und fand deshalb nur das Feld, in das ich selbst geschrieben hatte.
    local vorher = {}
    for off = 0, 0x48C, 4 do vorher[off] = core.readInteger(gefunden + off) or 0 end
    core.writeSmallInteger(gefunden + 0x8E, nach)
    local geaendert = {}
    for off = 0, 0x48C, 4 do
      local jetzt = core.readInteger(gefunden + off) or 0
      if jetzt ~= vorher[off] then
        table.insert(geaendert, string.format("+0x%03X", off))
      end
    end
    log(INFO, string.format("EINZELTAUSCH Typ %d -> %d: %d Feld(er) haben sich geaendert: %s",
      von, nach, #geaendert, table.concat(geaendert, " ")))
    return true
  end

  --==========================================================================
  -- Einheiten WIRKLICH umwandeln - mit Figur, nicht nur mit Zahl
  --   { "wandle": { "von": 72, "nach": 27, "spieler": 1 } }
  --
  -- Warum nicht einfach unitType schreiben: Die Figur haengt an spriteID
  -- (+0x0C), und die wird nur ZWEIMAL aus dem Typ abgeleitet - beim Erzeugen
  -- und beim Umwandeln. Wer nur unitType setzt, aendert das Verhalten
  -- (die Update-Funktion wird jeden Tick neu aus einer Zeigertabelle geholt),
  -- aber die Figur bleibt, wie sie war. Am 02.09.2026 im Bild belegt.
  --
  -- Das Spiel hat einen eigenen Umwandlungs-Pfad; er laeuft ueber
  -- changeUnitType (0x0053E6C0), das im naechsten Tick setUnitValues ruft -
  -- dieselbe Funktion wie beim Erzeugen. Drei Felder anstossen, den Rest
  -- macht das Spiel:
  --   +0x2CC state_2              = 0
  --   +0x2CA unitTypeToChangeInto = Zieltyp
  --   +0x8C  logicalState         = 4 (ULS_TRANSITIONING)
  -- unitType selbst NICHT anfassen - setUnitValues schreibt ihn.
  --
  -- Nebenwirkung: Leben, Tempo und Sichtweite werden auf die Werte des neuen
  -- Typs gesetzt. Das ist gewollt - es ist eine echte Umwandlung.
  --==========================================================================
  if cmd.wandle ~= nil then
    local w = cmd.wandle
    local von, nach = tonumber(w.von), tonumber(w.nach)
    local sp = tonumber(w.spieler)
    if von == nil or nach == nil then
      log(WARNING, "WANDLE: 'von' und 'nach' werden gebraucht.")
      return false
    end
    local getroffen = 0
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    for i = 0, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0
         and (core.readSmallInteger(b + 0x8E) or -1) == von
         and (sp == nil or (core.readSmallInteger(b + 0x96) or -1) == sp) then
        core.writeSmallInteger(b + 0x2CC, 0)      -- state_2
        core.writeSmallInteger(b + 0x2CA, nach)   -- unitTypeToChangeInto
        core.writeSmallInteger(b + 0x8C, 4)       -- ULS_TRANSITIONING
        getroffen = getroffen + 1
      end
    end
    log(INFO, string.format("WANDLE: Typ %d -> %d%s | %d Einheiten angestossen",
      von, nach, sp and (" bei Spieler " .. sp) or " (alle)", getroffen))
    return true
  end

  -- Knopf im Kreuzzug-Bildschirm: { "kreuzzug": 2 }
  -- MenuItemActionHandler_SelectCrusade_Main (0x0042BF00, cdecl):
  --   -1 zurueck ins Hauptmenue   1 Gefechtspfad   2 EIGENES GEFECHT (Lobby)
  --    3 Warchest-Pfad            4 Extreme-Pfad
  -- Knopf 2 richtet die Lobby vollstaendig ein (InitSkirmishLobbyData,
  -- setupSkirmishLobby, isHost, Spielmodus) - genau das, was der Direktsprung
  -- von Hand nachbaute und dabei die Platzvergabe uebersprang.
  if cmd.kreuzzug ~= nil then
    local nr = tonumber(cmd.kreuzzug)
    if nr == nil then return false end
    local ok, err = pcall(function()
      core.exposeCode(0x0042BF00, 1, 0)(nr)
    end)
    log(INFO, string.format("KREUZZUG: Knopf %d, ok=%s%s", nr, tostring(ok),
      ok and "" or (" - " .. tostring(err))))
    return true
  end

  -- Ereignis-Regel setzen oder alle loeschen.
  --   { "regel": { "name": "...", "wenn": {...}, "dann": [...], "einmal": true } }
  --   { "regeln": "aus" }
  if cmd.regeln ~= nil then
    regeln = {}
    log(INFO, "REGELN: alle geloescht.")
    return true
  end
  if cmd.regel ~= nil then
    local r = cmd.regel
    if type(r) ~= "table" or type(r.wenn) ~= "table" then
      log(WARNING, "REGEL: 'wenn' fehlt.")
      return false
    end
    r.dann = (type(r.dann) == "table") and r.dann or {}
    r.einmal = (r.einmal ~= false)          -- Vorgabe: nur einmal ausloesen
    r.gefeuert = false
    r.name = r.name or ("Regel " .. tostring(#regeln + 1))
    table.insert(regeln, r)
    log(INFO, string.format("REGEL '%s' scharf: %d Regel(n) aktiv.", r.name, #regeln))
    return true
  end

  -- Kette annehmen: eine Liste von Schritten, die der Taktgeber abarbeitet.
  if cmd.kette ~= nil then
    if type(cmd.kette) ~= "table" then return false end
    kette = { schritte = cmd.kette, index = 1, wartetBis = nil }
    log(INFO, string.format("KETTE: %d Schritte angenommen.", #cmd.kette))
    return true
  end

  -- Fenster hinten halten. Das Handle kommt von aussen, weil das Spiel es
  -- nirgends unter einem auffindbaren Namen ablegt und es sich bei jedem
  -- Start aendert. { "fenster": { "hwnd": 526086, "x": 2560, "y": 0 } }
  -- Ohne "alle" wird einmal gesetzt, mit "alle": 300 alle 300 Takte.
  if cmd.fenster ~= nil then
    local f = type(cmd.fenster) == "table" and cmd.fenster or {}
    local hwnd = tonumber(f.hwnd) or (fensterWacht and fensterWacht.hwnd)
    if hwnd == nil then
      log(WARNING, "FENSTER: kein Handle - bitte hwnd mitgeben.")
      return true
    end
    if f.aus == true then
      fensterWacht = nil
      log(INFO, "FENSTER: Wacht abgeschaltet.")
      return true
    end
    local x, y = tonumber(f.x), tonumber(f.y)
    local ok, ergebnis = pcall(fensterSetzen, hwnd, x, y)
    fensterWacht = { hwnd = hwnd, x = x, y = y,
                     alle = tonumber(f.alle) or 300, zaehler = 0 }
    log(INFO, string.format("FENSTER: 0x%X nach hinten%s - Rueckgabe %s, Wacht alle %d Takte",
      hwnd, x and string.format(" auf (%d,%d)", x, y or 0) or "",
      tostring(ok and ergebnis or "Fehler"), fensterWacht.alle))
    return true
  end

  --==========================================================================
  -- Eigenes Gefecht aufsetzen, ohne das Menue zu bedienen (01.09.2026)
  --
  -- Nachgebaut aus SetupSkirmishMode (0x4C68D0), Schritt fuer Schritt in
  -- derselben Reihenfolge - aber mit eigenen Werten statt denen einer
  -- Kampagnenmission. Der Kampagnenweg taugt hier nicht: in diesem Mod ist
  -- kein Spieler 1 vorgesehen, die Partie ist nach 87 Ticks entschieden.
  --
  -- Die Reihenfolge ist nicht beliebig. Der Code verlangt sie so:
  --   isHost und currentGameMode VOR dem Slot-Befehl, sonst laeuft
  --   addPlayerToCurrentPlayerArray ins Leere und der Mensch bleibt ohne Burg.
  --==========================================================================
  if cmd.eigenesGefecht ~= nil then
    local GSS  = 0x0191D768
    local CORE = 0x01FE7D10

    local fullID   = 0x0191DE10     -- currentPlayerFullIDArray   int[9]
    local aiArr    = 0x0191DE7C     -- currentAIArray             int[9]
    local aiVar    = 0x0191DEA0     -- SEC_AIVariationArray       int[9]
    local bereit   = 0x01A24518     -- DAT_PlayerSlotArraySomeValue int[9]
    local gruppe   = 0x01A275B5     -- DAT_PlayerGroupArray       byte[9]
    local posArr   = 0x01A275D0     -- playerPositionsArray       byte[8]
    local kartName = 0x01A22F9C     -- mapName char[1000], OHNE ".map"
    local namen    = 0x01A23384     -- DAT_PlayerNames char[9][250]

    local setupLobby    = core.exposeCode(0x00487650, 1, 1)   -- this
    local queueBefehl   = core.exposeCode(0x00489100, 2, 1)   -- this + Befehl
    local resetAiVar    = core.exposeCode(0x00428050, 1, 0)
    local platziereZuf  = core.exposeCode(0x00428480, 1, 0)
    local starteGefecht = core.exposeCode(0x00441270, 1, 0)
    local zeigeMenue    = core.exposeCode(0x0046B340, 3, 1)   -- this + Ansicht + 0

    local karte = cmd.karte or "!KOphase Map 1"
    -- Die Nummer ist aiType+1, weil 0 in currentAIArray "leer" bedeutet.
    -- Rotkaeppchen sitzt in diesem Mod auf dem Vanilla-Platz "rat" = aiType 0.
    local ki    = tonumber(cmd.ki) or 1
    local anzKI = tonumber(cmd.gegner) or 2

    setupLobby(GSS)
    core.writeInteger(0x0191DEF8, 1)                  -- isHost
    core.writeInteger(0x0191DD80, 99)                 -- GM_SKIRMISH_SINGLE_PLAYER
    core.writeInteger(0x0191DE04, 1)                  -- DPLAYX_ReceivedPlayerID
    core.writeInteger(0x01FE7D78, 3)                  -- gameMode_2 = Gefecht
    core.writeInteger(CORE + 0x152C, 0)               -- mapU4Int0
    core.writeInteger(CORE + 0x1F94, 0)               -- isSkirmishTrail = FALSE

    for i = 0, 8 do
      core.writeInteger(fullID + i*4, 0xFFFFFFFF)
      core.writeInteger(aiArr  + i*4, 0)
      core.writeInteger(aiVar  + i*4, 0xFFFFFFFF)
      core.writeByte(namen + i*250, 0)
    end
    for i, c in ipairs({68, 97, 110, 105, 101, 108, 0}) do   -- "Daniel"
      core.writeByte(namen + 250 + (i-1), c)
    end

    queueBefehl(GSS, 4)                               -- soll den Menschen eintragen

    -- GEMESSEN 01.09.: queueCommand(4) traegt hier NICHTS ein - nach dem Aufruf
    -- steht currentPlayerFullIDArray noch komplett auf -1, und der Mensch fehlt
    -- im fertigen Gefecht (zwei Lords statt drei, Besitzer 1 gar nicht da).
    -- Der Befehl ist auf den Lobby-Ablauf mit Netzwerkschicht ausgelegt; aus
    -- einem Haken heraus fehlt ihm offenbar etwas. Deshalb wird das Ergebnis
    -- geprueft und notfalls von Hand nachgezogen - genau das, was
    -- addPlayerToCurrentPlayerArray(1) tun wuerde.
    -- Ohne Pruefung setzen: core.readInteger liefert die -1 vorzeichenbehaftet,
    -- ein Vergleich mit 0xFFFFFFFF greift also nie (Betriebsregel 4). Zweimal
    -- setzen schadet nicht, einmal zu wenig kostet den ganzen Lauf.
    core.writeInteger(fullID + 4, 1)                  -- Slot 1 = der Mensch
    core.writeInteger(0x01A275DC, 1)                  -- currentPlayerSlotID
    log(INFO, string.format("GEFECHT: Mensch in Slot 1 (steht jetzt: %s)",
      tostring(core.readInteger(fullID + 4))))

    for i = 0, 8 do core.writeInteger(bereit + i*4, 1) end

    for slot = 2, 1 + anzKI do
      core.writeInteger(aiArr + slot*4, ki)
      resetAiVar(slot)
    end

    for i = 0, 7 do core.writeByte(posArr + i, 0xF6) end
    -- Teams: { "teams": [1, 1, 2, 2] } - je Gegner eine Mannschaftsnummer.
    -- Gleiche Zahl heisst verbuendet. Ohne Angabe bekommt jeder sein eigenes
    -- Team, 0xFF heisst "Platz nicht besetzt".
    local teams = (type(cmd.teams) == "table") and cmd.teams or nil
    for i = 0, 8 do
      local wert = 0xFF
      if i == 1 then
        wert = 0                                   -- der Mensch
      elseif i >= 2 and i <= 1 + anzKI then
        wert = teams and (tonumber(teams[i - 1]) or (i - 1)) or (i - 1)
      end
      core.writeByte(gruppe + i, wert)
    end
    if teams then
      log(INFO, "GEFECHT: Mannschaften " .. table.concat(teams, ", "))
    end
    -- GEMESSEN 01.09. an Gefechtspfad-Mission 0 (0x00B3EC48): das Spiel selbst
    -- benutzt fairness = 2 und startLevels = 1.
    -- Vorher stand hier 0/0 - das war geraten und falsch: Daniel bekam 1 Stueck
    -- von jedem Startgut, Tierhaeute (die es in Crusader gar nicht gibt) und
    -- 5,9 Millionen Gold. Die 0 ist kein gueltiger Index in die Gueter-Tabelle.
    core.writeInteger(0x01A24A4C, tonumber(cmd.ausgleich) or 2)    -- fairness
    core.writeInteger(0x01A245A4, tonumber(cmd.startgueter) or 1)  -- startLevels

    for i = 1, #karte do core.writeByte(kartName + i - 1, karte:byte(i)) end
    core.writeByte(kartName + #karte, 0)

    -- Selbstspiel (30.09.2026, Selfaware-AI): GEMESSEN an Daniels Lobby-Aufbau
    -- auf Liga_Grumpy Neighbors - kein Mensch (fullID leer, Mannschaft 255),
    -- beide KIs Mannschaft 0, feste Startplatz-Liste, Varianten 0/1. Die
    -- Zufallsplatzierung faellt weg. { "selbstspiel": true } plus optional
    -- "startliste": [8 Byte] und "varianten": [je KI].
    if cmd.selbstspiel == true then
      core.writeInteger(fullID + 4, 0xFFFFFFFF)            -- Platz 1 wieder leer
      for i = 0, 8 do
        core.writeByte(gruppe + i, (i >= 2 and i <= 1 + anzKI) and 0 or 0xFF)
        core.writeInteger(aiVar + i * 4, 0)
      end
      local liste = (type(cmd.startliste) == "table") and cmd.startliste
                    or { 246, 2, 1, 246, 246, 246, 246, 246 }
      for i = 0, 7 do core.writeByte(posArr + i, tonumber(liste[i + 1]) or 246) end
      local var = (type(cmd.varianten) == "table") and cmd.varianten or { 0, 1 }
      for slot = 2, 1 + anzKI do core.writeInteger(aiVar + slot * 4, tonumber(var[slot - 1]) or 0) end
      log(INFO, "GEFECHT: Selbstspiel-Aufbau (kein Mensch, feste Startplaetze) nach Lobby-Messung 30.09.")
    else
      for slot = 1, 1 + anzKI do platziereZuf(slot) end
      -- 05.10.2026 (Daniel 22:52 "starte bei Tick 0"): feste Startplaetze auch mit Mensch, sonst Zufall. Gemessen im
      -- Startstand M19: playerPositionsArray = 0, 1, 246... (Mensch Platz 0, Rotkaeppchen Platz 1).
      if type(cmd.startliste) == "table" then
        for i = 0, 7 do core.writeByte(posArr + i, tonumber(cmd.startliste[i + 1]) or 246) end
        log(INFO, "GEFECHT: feste Startplaetze " .. table.concat(cmd.startliste, ","))
      end
    end

    log(INFO, string.format("GEFECHT: Karte '%s', %d Gegner vom Typ %d", karte, anzKI, ki))
    -- "startpause": N haelt das neue Gefecht bei Tick N an (30.09.2026). Eigener
    -- Name, weil ein Befehl mit "tickpause" schon weiter oben abgefangen wird -
    -- und weil im Hauptmenue nur Startbefehle durchkommen (gemessen).
    if tonumber(cmd.startpause) then
      tickPause = { naechster = tonumber(cmd.startpause), alle = tonumber(cmd.startpauseAlle), anzahl = 0 }
      log(INFO, "GEFECHT: Startpause scharf bei Tick " .. tickPause.naechster)
    end
    starteGefecht(0)                                  -- 0 = Burgen selbst waehlen
    -- Feste Saat (05.10.2026, Daniel 23:13 "ja, feste Saat einbauen"), nach dem Vorbild ucp_recorder (onStartSkirmish,
    -- Referenz/ucp_recorder/code/recorder.lua): Karten-Saat schreiben, Zufallstabelle neu fuellen (0x0046A760), dann
    -- Partie-Saat, Zufallswerte und Zaehler. Hier direkt NACH dem Start statt im Haken bei 0x004428B5 - ob das reicht,
    -- zeigt der Vergleich zweier Partien mit gleicher Saat. Jeder Start schreibt die Werte ins Log (SAAT ...).
    if type(cmd.saat) == "table" then
      local s = cmd.saat
      core.writeInteger(0x01A279C4, tonumber(s.karte))
      pcall(core.exposeCode(0x0046A760, 1, 1), 0x01A279C0)
      core.writeInteger(0x01A279C4, tonumber(s.partie))
      core.writeInteger(0x01A3160C, tonumber(s.zaehler1))
      core.writeInteger(0x01A31608, tonumber(s.zaehler2))
      core.writeSmallInteger(0x01A279C0, tonumber(s.wert1))
      core.writeSmallInteger(0x01A279C2, tonumber(s.wert2))
      log(INFO, "GEFECHT: feste Saat gesetzt")
    end
    log(INFO, string.format("SAAT karte=%d partie=%d wert1=%d wert2=%d zaehler1=%d zaehler2=%d",
      tonumber(cmd.saat and cmd.saat.karte) or -1, core.readInteger(0x01A279C4) or -1, core.readSmallInteger(0x01A279C0) or -1,
      core.readSmallInteger(0x01A279C2) or -1, core.readInteger(0x01A3160C) or -1, core.readInteger(0x01A31608) or -1))
    zeigeMenue(CORE, 14, 0)                           -- MVT_BUILD_MENU
    log(INFO, "GEFECHT: LaunchSkirmishGame zurueck")
    return true
  end

  if spieler == nil then
    log(WARNING, "logik: 'player' fehlt im Befehl.")
    return false
  end

  if cmd.ware ~= nil then
    local art = cmd.ware.typ or 4
    local alt = ware(spieler, art)
    if type(cmd.ware.menge) == "number" then wareSetzen(spieler, art, cmd.ware.menge) end
    log(INFO, string.format("WARE %d bei Spieler %d: %s -> %s",
      art, spieler, tostring(alt), tostring(ware(spieler, art))))
    return true
  end

  --   { "leereKI": [2] }  diese Spieler bekommen jede Runde alle Waren auf 0; { "leereKI": false } hebt das auf.
  if cmd.leereKI ~= nil then
    if cmd.leereKI == false then
      leereKI = {}
      log(INFO, "LEERE KI: aus")
      return true
    end
    local liste = {}
    for _, sp in ipairs(cmd.leereKI) do
      sp = tonumber(sp)
      if sp ~= nil and sp >= 1 and sp <= 8 then leereKI[sp] = true; table.insert(liste, tostring(sp)) end
    end
    leereKITick()
    log(INFO, "LEERE KI: Spieler " .. table.concat(liste, ", ") .. " ohne Waren und Gold (jede Runde)")
    return true
  end

  if cmd.gold ~= nil then
    local alt = ware(spieler, 15)
    if type(cmd.gold) == "number" then wareSetzen(spieler, 15, cmd.gold) end
    log(INFO, string.format("GOLD Spieler %d: %s -> %s",
      spieler, tostring(alt), tostring(ware(spieler, 15))))
    return true
  end

  if cmd.bestand == true then return gebaeudeBericht(spieler) end
  if cmd.einheiten == true then return einheitenBericht() end

  -- Schnappschuss (30.09.2026, Selfaware-AI): alle bekannten Speicherbereiche
  -- roh in Dateien, ohne sie zu deuten. Erst sammeln, dann vergleichen, dann das
  -- Klare herausfischen (Daniel). { "abzug": "name" } schreibt nach
  -- ucp/villagestudio/abzug/<name>_t<tick>_<bereich>.bin (Ordner muss existieren).
  if cmd.abzug ~= nil then
    local name, t0, t = tostring(cmd.abzug), os.clock(), tick()
    local nE = core.readInteger(E_MAX) or 2500
    if nE < 1 or nE > 2500 then nE = 2500 end
    local bereiche = {
      { "spieler",     0x0115BDF8, 9 * 0x39F4 },        -- PlayerData[9]
      { "einheiten",   0x0138854C, nE * 1168 },         -- units[0..maxUnitCount)
      { "gebaeude",    0x00F98520, 0x14 + 2000 * 812 }, -- BuildingsState: Kopf + buildings[2000]
      { "aiv",         0x01866AB0, 4 + 9 * 0x6D98 },    -- AIVState: Kopf + aivs[9]
      { "sync",        0x0191D768, 0x800 },             -- GameSynchronyState (Anfang)
      { "kern",        0x01FE7D10, 0x2000 },            -- GameCore (Anfang)
      { "k_logik",     0x01BF8368, 80400 * 4 },         -- LogicLayer
      { "k_gebaeude",  0x01C95BB8, 80400 * 2 },         -- BuildingLayer
      { "k_hoehe",     0x01D32C38, 80400 },             -- HeightLayer
      { "k_schaden",   0x01DBC2A8, 80400 },             -- DamageLayer
      { "k_gfx",       0x01AE5688, 80400 * 2 },         -- GfxLayer
    }
    local lies, char, concat = core.readInteger, string.char, table.concat
    local summe = 0
    for _, b in ipairs(bereiche) do
      local pfad = string.format("ucp/villagestudio/abzug/%s_t%d_%s.bin", name, t, b[1])
      local f = io.open(pfad, "wb")
      if not f then
        log(WARNING, "ABZUG: nicht schreibbar: " .. pfad)
        return false
      end
      for start = 0, b[3] - 1, 4096 do
        local teil, ende = {}, math.min(start + 4096, b[3])
        for o = start, ende - 1, 4 do
          local v = lies(b[2] + o) or 0
          teil[#teil + 1] = char(v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF)
        end
        f:write(concat(teil))
      end
      f:close()
      summe = summe + b[3]
    end
    log(INFO, string.format("ABZUG '%s' bei Tick %d: %d Bereiche, %d Byte, %d Einheitenplaetze, %.2f s",
      name, t, #bereiche, summe, nE, os.clock() - t0))
    return true
  end
  -- Bild vom Spiel. Laeuft im Spieltick, weil takeScreenshot selbst
  -- zeichnet - aus dem Zeichenhaken heraus stirbt der Prozess.
  -- Die Datei landet im Dokumente-Ordner:
  --   Dokumente/Stronghold Crusader/screen_capture_NNN.bmp
  -- Sie ist erst fertig, wenn die Groesse 0x36 + Breite*Hoehe*3 erreicht -
  -- die Logzeile kommt frueher.
  if cmd.foto ~= nil then
    local nr = type(cmd.foto) == "number" and cmd.foto or 1
    if VS ~= nil and VS.takeScreenshot ~= nil then
      log(INFO, string.format("FOTO: fordere screen_capture_%03d.bmp an ...", nr))
      local ok, err = pcall(VS.takeScreenshot, VS.WINDOW_DD or 0x00F98338, nr)
      if not ok then log(WARNING, "FOTO fehlgeschlagen: " .. tostring(err)) end
      return true
    end
    log(WARNING, "FOTO: takeScreenshot fehlt in der Werkzeugkiste.")
    return false
  end

  if cmd.bauwacht ~= nil then
    if cmd.bauwacht == false then return bauwachtStart(nil) end
    return bauwachtStart(spieler, type(cmd.bauwacht) == "number" and cmd.bauwacht or nil)
  end

  if cmd.einheitenroh ~= nil then
    return einheitenRoh(type(cmd.einheitenroh) == "number" and cmd.einheitenroh or nil)
  end

  if cmd.mauerwacht ~= nil then
    if cmd.mauerwacht == false then
      mauerwacht[spieler] = nil
      log(INFO, string.format("MAUERWACHT %d aus.", spieler))
      return true
    end
    -- besitzer: Wert in der Besitzer-Ebene. Sie zaehlt ab 0, aber die
    -- Zuordnung Spieler -> Besitzerwert ist nicht immer spieler-1, deshalb
    -- ist sie direkt angebbar.
    return mauerwachtStart(spieler, cmd.besitzer or (spieler - 1), cmd.hoehe,
      type(cmd.mauerwacht) == "string" and cmd.mauerwacht or nil)
  end

  if cmd.gebaeudewacht ~= nil then
    if cmd.gebaeudewacht == false then
      gebaeudewacht[spieler] = nil
      log(INFO, string.format("GEBAEUDEWACHT %d aus.", spieler))
      return true
    end
    gebaeudewacht[spieler] = { ziel = cmd.leben or 1, wieder = 0 }
    log(INFO, string.format(
      "GEBAEUDEWACHT Spieler %d an: beschaedigte Gebaeude fallen sofort auf %d Leben und bleiben dort.",
      spieler, gebaeudewacht[spieler].ziel))
    return true
  end

  -- Unbekannt hier heisst nicht unbekannt ueberhaupt: der AIV-Tausch
  -- (ai/file/castle), abriss und bericht sitzen in init.lua. Ohne dieses
  -- Durchreichen liesse sich keine Messburg laden.
  if VS ~= nil and type(VS.handleCommand) == "function" then
    VS.handleCommand(cmd)
    return true
  end
  log(WARNING, "logik: unbekannter Befehl.")
  return false
end

-- Befehle koennen einzeln oder als Liste kommen. Eine "id" wird gemerkt,
-- damit derselbe Befehl nicht zweimal ausgefuehrt wird - so kann die
-- Befehlsdatei gefahrlos mehrfach geschrieben werden.
local erledigt = {}

local function handleCommand(cmd)
  if type(cmd) ~= "table" then return end
  local liste = cmd
  if type(cmd.befehle) == "table" then liste = cmd.befehle
  elseif cmd[1] == nil then liste = { cmd } end

  local ok, fehler, uebersprungen = 0, 0, 0
  for i = 1, #liste do
    local c = liste[i]
    if type(c) == "table" and c.id ~= nil and erledigt[c.id] then
      uebersprungen = uebersprungen + 1
    else
      local gut, err = pcall(einzelbefehl, c)
      if gut and err then ok = ok + 1 else
        fehler = fehler + 1
        if not gut then log(WARNING, "logik: " .. tostring(err)) end
      end
      if type(c) == "table" and c.id ~= nil then erledigt[c.id] = true end
    end
  end
  if ok + fehler > 1 or uebersprungen > 0 then
    log(INFO, string.format("logik: %d von %d Befehlen ausgefuehrt, %d schon erledigt.",
      ok, ok + fehler, uebersprungen))
  end
  -- Quittung (05.10.2026, Daniel 23:01 "feste Zeit warten - Sekunden sind Killer"): der Kanal (befehl.py) wartet auf
  -- genau diese Zeile statt eine feste Zeit. Die Datei wird jeden Tick gelesen, die Quittung kommt also im selben Tick.
  if cmd.id ~= nil then log(INFO, "QUITTUNG " .. tostring(cmd.id)) end
end

--============================================================================
-- 6b. Bauwacht - wann entsteht welcher Bauschritt?
--
-- Zaehlt in festem Abstand die Mauerkacheln eines Besitzers und meldet jeden
-- Zuwachs mit Tick. Ein Bauschritt dauert belegte 50 Ticks, die Schrittnummer
-- laesst sich also aus dem Tick zurueckrechnen; ausgefallene Schritte
-- erscheinen als Luecke.
--
-- Warum ueber die Kacheln und nicht ueber die Bauliste: die Bauliste haette
-- die Schrittnummer direkt, aber ihr Eintragsabstand ist noch nicht gemessen.
-- Die Kachelzaehlung braucht nichts Unbelegtes.
--
-- Der Besitzerwert zaehlt AB 0 - Spieler 3 steht dort als 2.
--============================================================================

local bauwacht = nil

local function mauernZaehlen(besitzerWert)
  local n = 0
  for k = 0, KACHELGRENZE - 1 do
    local lg = core.readInteger(LOGIK + k * 4)
    if lg ~= nil and (lg & MAUERBIT) ~= 0 then
      if besitzerWert == nil or core.readByte(BESITZER + k) == besitzerWert then
        n = n + 1
      end
    end
  end
  return n
end

bauwachtStart = function(spieler, abstand)
  if spieler == nil then
    bauwacht = nil
    log(INFO, "BAUWACHT: aus.")
    return true
  end
  local bw = spieler - 1                    -- Besitzerschicht zaehlt ab 0
  local t = tick()
  bauwacht = {
    besitzer = bw,
    abstand  = abstand or 10,
    zahl     = mauernZaehlen(bw),
    naechste = t,
    start    = t,
    stufen   = 0,
  }
  log(INFO, string.format(
    "BAUWACHT: an fuer Spieler %d (Besitzerwert %d), Startbestand %d Mauern bei Tick %d, Pruefabstand %d.",
    spieler, bw, bauwacht.zahl, t, bauwacht.abstand))
  return true
end

local function bauwachtTick()
  if bauwacht == nil then return end
  local t = tick()
  if t < bauwacht.naechste then return end
  bauwacht.naechste = t + bauwacht.abstand

  local neu = mauernZaehlen(bauwacht.besitzer)
  if neu == bauwacht.zahl then return end

  bauwacht.stufen = bauwacht.stufen + 1
  local seitStart = t - bauwacht.start
  -- Bei 50 Ticks je Schritt: welcher Schritt ist das rechnerisch?
  log(INFO, string.format(
    "BAU Tick %d (+%d seit Start) | Mauern %d -> %d (%+d) | Stufe %d | rechnerisch Schritt %.1f",
    t, seitStart, bauwacht.zahl, neu, neu - bauwacht.zahl, bauwacht.stufen, seitStart / 50.0))
  bauwacht.zahl = neu
end

--============================================================================
-- 6c. Selbstausloeser fuer ein Bild aus dem laufenden Gefecht (31.08.2026)
--
-- Das Problem: Zwischen Gefechtsstart und dem Moment, in dem ein Befehl aus
-- der Datei ankommt, vergehen Sekunden - und bei hohem Spieltempo ist das
-- Gefecht dann schon entschieden (gemessen: nach rund 4000 Ticks steht der
-- Auswertungsbildschirm). Im Menue laeuft der Tick-Poll gar nicht, ein
-- vorbereitender Tempobefehl kommt also nie durch.
--
-- Deshalb wird der Auftrag VORHER scharf gestellt und wartet im Spieltakt:
-- Sobald ein frisches Gefecht anlaeuft (Tick klein), wird zuerst das Tempo
-- gedrosselt und danach beim Zieltick das Bild geschrieben.
--
--   { "autobild": true, "tempo2": 10, "beiTick": 150 }
--   { "autobild": false }   schaltet ab
--============================================================================

local autobild = nil

autobildStart = function(cmd)
  if cmd.autobild == false then
    autobild = nil
    log(INFO, "AUTOBILD: aus.")
    return true
  end
  autobild = {
    tempo    = tonumber(cmd.tempo2) or 10,
    beiTick  = tonumber(cmd.beiTick) or 150,
    datei    = type(cmd.datei) == "string" and cmd.datei or "ucp/villagestudio/vs_auto.bmp",
    gedrosselt = false,
  }
  log(INFO, string.format(
    "AUTOBILD: scharf. Sobald ein frisches Gefecht laeuft: Tempo %d, Bild bei Tick %d -> %s",
    autobild.tempo, autobild.beiTick, autobild.datei))
  return true
end

local function autobildTick()
  if autobild == nil then return end
  local t = tick()
  if t == nil or t <= 0 then return end
  -- Ein altes, schon entschiedenes Gefecht hat einen hohen Tickstand. Nur ein
  -- frisch gestartetes soll den Auftrag ausloesen.
  if not autobild.gedrosselt then
    if t > 600 then return end
    core.writeInteger(TEMPO, autobild.tempo)
    autobild.gedrosselt = true
    log(INFO, string.format("AUTOBILD: frisches Gefecht bei Tick %d - Tempo auf %d gedrosselt.",
      t, core.readInteger(TEMPO)))
    return
  end
  if t < autobild.beiTick then return end
  local ziel = autobild.datei
  autobild = nil                        -- nur einmal ausloesen
  log(INFO, string.format("AUTOBILD: Tick %d erreicht - Bild wird geschrieben.", t))
  bildSchreiben({ bild = "menue", blt = true, datei = ziel })
end

--============================================================================
-- 6c. Befehlskette: kleine Schritte, jeder einzeln pruefbar
--
-- Warum nicht ein grosser Sprung: Der direkte Weg (alles setzen, dann
-- LaunchSkirmishGame) startet zwar ein Gefecht, laesst aber Zustaende zurueck,
-- die niemand geprueft hat - am 01.09. waren das 1 Stueck Startgueter und
-- 5,9 Millionen Gold. Eine Kette macht jeden Schritt sichtbar und haltbar.
--
-- Gewartet wird auf SPIELZEIT, nicht auf Sekunden: bei Tempo 400 vergeht ein
-- Spieljahr in 24 Sekunden, bei Tempo 20 in acht Minuten. Eine feste Pause
-- waere mal zu kurz und mal sinnlos lang.
--============================================================================

local function ketteTick()
  if kette == nil then return end
  local t = tick()

  if kette.wartetBis ~= nil then
    if t < kette.wartetBis then return end
    kette.wartetBis = nil
  end

  local schritt = kette.schritte[kette.index]
  if schritt == nil then
    log(INFO, string.format("KETTE: alle %d Schritte erledigt.", kette.index - 1))
    kette = nil
    return
  end
  local nr = kette.index

  -- Vor jedem Schritt nachsehen, in welchem Fenster wir wirklich stehen.
  -- Daniel kann jederzeit selbst klicken, und ein Schritt kann einen anderen
  -- Wechsel ausgeloest haben als erwartet. Eine Kette, die das nicht prueft,
  -- fuehrt ihre Befehle im falschen Fenster aus - und keiner merkt es.
  if schritt.erwarte ~= nil then
    local jetzt = core.readInteger(0x01FE7D1C)      -- currentMenuViewType
    local ziel  = tonumber(schritt.erwarte)
    if jetzt ~= ziel then
      kette.versuche = (kette.versuche or 0) + 1
      if kette.versuche > 40 then
        log(WARNING, string.format(
          "KETTE %d: stehe in Fenster %s, brauche %d - komme nicht hin, Abbruch.",
          nr, tostring(jetzt), ziel))
        kette = nil
        return
      end
      -- Nur alle acht Takte anstossen; der Wechsel braucht ein paar Bilder.
      if kette.versuche % 8 == 1 then
        log(INFO, string.format("KETTE %d: bin in Fenster %s, gehe nach %d",
          nr, tostring(jetzt), ziel))
        pcall(einzelbefehl, { menue = ziel })
      end
      return
    end
    kette.versuche = 0
  end

  kette.index = kette.index + 1

  if schritt.warte ~= nil then
    local w = schritt.warte
    local dauer = (tonumber(w.ticks) or 0)
                + (tonumber(w.tage)  or 0) * 50
                + (tonumber(w.jahre) or 0) * 9600
    kette.wartetBis = t + dauer
    log(INFO, string.format("KETTE %d/%d: warte %d Ticks (bis %d)",
      nr, #kette.schritte, dauer, kette.wartetBis))
    return
  end

  log(INFO, string.format("KETTE %d/%d: %s",
    nr, #kette.schritte, schritt.name or "Schritt"))
  local gut, err = pcall(einzelbefehl, schritt)
  if not gut then
    log(WARNING, string.format("KETTE %d: abgebrochen - %s", nr, tostring(err)))
    kette = nil
  end
end

--============================================================================
-- 6d. Regelwacht: prueft die Bedingungen und fuehrt die Folgen aus
--============================================================================

local function bedingungErfuellt(w)
  local sp = tonumber(w.spieler)

  if w.gold ~= nil and sp ~= nil then
    return goldVon(sp) >= tonumber(w.gold)
  end
  if w.tick ~= nil then
    return tick() >= tonumber(w.tick)
  end
  if w.jahr ~= nil then
    return tick() >= tonumber(w.jahr) * 9600
  end
  -- Teuer: laeuft ueber alle Einheiten. Deshalb nur jeden 25. Takt.
  if w.einheiten ~= nil and sp ~= nil then
    if tick() % 25 ~= 0 then return false end
    local n = 0
    local grenze = math.min(core.readInteger(0x01387F38) or 0, 2500)
    for i = 0, grenze - 1 do
      local b = 0x0138854C + i * 1168
      if (core.readSmallInteger(b + 0x8C) or 0) ~= 0
         and (core.readSmallInteger(b + 0x96) or -1) == sp then
        n = n + 1
      end
    end
    return n >= tonumber(w.einheiten)
  end
  return false
end

local function regelwachtTick()
  if #regeln == 0 then return end
  for _, r in ipairs(regeln) do
    if not (r.einmal and r.gefeuert) then
      local gut, erfuellt = pcall(bedingungErfuellt, r.wenn)
      if gut and erfuellt then
        r.gefeuert = true
        log(INFO, string.format("REGEL '%s' hat ausgeloest (Tick %d).", r.name, tick()))
        for _, aktion in ipairs(r.dann) do
          local ok, err = pcall(einzelbefehl, aktion)
          if not ok then
            log(WARNING, string.format("REGEL '%s': %s", r.name, tostring(err)))
          end
        end
      end
    end
  end
end

--============================================================================
-- 7. Taktgeber
--============================================================================

local function tickPauseTick()
  if tickPause == nil then return end
  local t = tick()
  -- GEMESSEN 30.09.: waehrend des Gefechtsaufbaus liefert der Tickzaehler kurz
  -- Unsinn (7.807.163). Werte weit ueber dem Ziel werden deshalb ignoriert.
  if t > tickPause.naechster + 200000 then return end
  if t >= tickPause.naechster then
    core.writeInteger(PAUSE, 1)
    tickPause.anzahl = tickPause.anzahl + 1
    log(INFO, string.format("TICKPAUSE: angehalten bei Tick %d (Ziel %d, Nr. %d).",
      t, tickPause.naechster, tickPause.anzahl))
    local weiter = tickPause.alle and tickPause.naechster + tickPause.alle
    if weiter and (tickPause.bis == nil or weiter <= tickPause.bis) then
      tickPause.naechster = weiter
    else
      tickPause = nil
    end
  end
end

local function ladePauseTick()
  if ladePause == nil then return end
  local t = tick()
  if ladePause.nachlauf > 0 then
    -- Nach dem Sprung noch ein paar Ticks nachhalten: kommt hier noch ein Tick an,
    -- hat das Laden die Pause wieder aufgehoben.
    core.writeInteger(PAUSE, 1)
    ladePause.nachlauf = ladePause.nachlauf - 1
    log(INFO, string.format("LADEPAUSE: nachgehalten bei Tick %d.", t))
    if ladePause.nachlauf == 0 then ladePause = nil end
    return
  end
  local d = t - ladePause.letzter
  ladePause.letzter = t
  local aufgehoben = ladePause.pausiert and (core.readInteger(PAUSE) or 0) == 0
  if (d == 0 or d == 1) and not aufgehoben then return end
  core.writeInteger(PAUSE, 1)
  ladePause.nachlauf = 3
  log(INFO, string.format("LADEPAUSE: Laden erkannt (%s) bei Tick %d - angehalten.",
    (d ~= 0 and d ~= 1) and ("Spielzeit sprang um " .. d) or "Pause aufgehoben", t))
end

local function lordWachtTick()
  if lordWacht == nil then return end
  local t = tick()
  local orte = {}
  for nr, l in pairs(lordWacht.lords) do
    local b = 0x0138854C + nr * 1168
    local zust = core.readSmallInteger(b + 0x8C) or 0
    local typ = core.readSmallInteger(b + 0x8E) or -1
    local hp = core.readInteger(b + 0x3C8) or 0
    local x = math.floor((core.readSmallInteger(b + 0xB6) or 0) / 8)
    local y = math.floor((core.readSmallInteger(b + 0xB8) or 0) / 8)
    if not l.tot then table.insert(orte, { nr = nr, sp = l.sp, x = x, y = y, hp = hp }) end
    -- Ziel festhalten, bis die Lords sich treffen
    local z = lordWacht.ziel
    if z and not lordWacht.getroffenWo and not l.tot and t >= l.abTick then
      local zx, zy = core.readSmallInteger(b + 0xC8) or -1, core.readSmallInteger(b + 0xCA) or -1
      -- Nur im laufenden Spiel und hoechstens alle 10 Ticks: das Spiel traegt das Ziel erst
      -- beim naechsten Tick ein; in der Pause setzte die Wacht sonst in jedem Bild neu
      -- (gemessen 01.10., 00:05: ueber 1000 Mal bei Tick 1100).
      local laeuft = (core.readInteger(PAUSE) or 1) == 0
      if laeuft and (zx ~= z[1] or zy ~= z[2]) and t - (l.letzterSatz or -100) >= 10 then
        l.letzterSatz = t
        _setDest = _setDest or core.exposeCode(ADR_SETDEST, 5, 1)
        pcall(_setDest, UNITS_STATE, nr, z[1], z[2], 0)
        l.gesetzt = l.gesetzt + 1
        if l.gesetzt <= 3 or l.gesetzt % 100 == 0 then
          log(INFO, string.format("LORDWACHT: Tick %d - Ziel fuer Lord %d gesetzt (Nr. %d, KI-Ziel war (%d,%d)).",
            t, nr, l.gesetzt, zx, zy))
        end
      end
      if not l.angekommen and math.max(math.abs(x - z[1]), math.abs(y - z[2])) <= 1 then
        l.angekommen = true
        log(INFO, string.format("LORDWACHT: ANKUNFT Tick %d - Lord %d (Spieler %d) bei (%d,%d), %d Ticks nach Start.",
          t, nr, l.sp, x, y, t - lordWacht.start))
      end
    end
    if hp ~= l.hp and not l.tot then
      if not lordWacht.getroffen then
        lordWacht.getroffen = true
        log(INFO, string.format("LORDWACHT: ERSTER TREFFER Tick %d - Lord %d (Spieler %d) %d -> %d bei (%d,%d), Angreifer Einheit %d.",
          t, nr, l.sp, l.hp, hp, x, y, core.readSmallInteger(b + 0x3AE) or -1))
        if lordWacht.haltTreffer then core.writeInteger(PAUSE, 1) end
      end
      local stufe = (l.max > 0) and math.floor(hp * 10 / l.max) or 0
      if stufe ~= l.stufe then
        log(INFO, string.format("LORDWACHT: Tick %d - Lord %d (Spieler %d) Leben %d (%d Prozent).",
          t, nr, l.sp, hp, (l.max > 0) and math.floor(hp * 100 / l.max) or 0))
        l.stufe = stufe
      end
      l.hp = hp
    end
    if not l.tot and (hp <= 0 or zust == 0 or typ ~= 55) then
      l.tot = true
      log(INFO, string.format("LORDWACHT: LORD TOT Tick %d - Lord %d (Spieler %d), Leben %d, Zustand %d, Typ %d, bei (%d,%d).",
        t, nr, l.sp, hp, zust, typ, x, y))
      if lordWacht.haltTod then core.writeInteger(PAUSE, 1) end
    end
  end
  if #orte == 2 then
    local d = math.max(math.abs(orte[1].x - orte[2].x), math.abs(orte[1].y - orte[2].y))
    if d <= 3 and not lordWacht.getroffenWo then
      lordWacht.getroffenWo = true
      log(INFO, string.format("LORDWACHT: TREFFEN Tick %d - Lord %d bei (%d,%d), Lord %d bei (%d,%d), Abstand %d.",
        t, orte[1].nr, orte[1].x, orte[1].y, orte[2].nr, orte[2].x, orte[2].y, d))
    end
    if t >= lordWacht.naechste then
      lordWacht.naechste = t + lordWacht.alle
      log(INFO, string.format("LORDWACHT Tick %d: Lord %d (%d,%d) %d | Lord %d (%d,%d) %d | Abstand %d",
        t, orte[1].nr, orte[1].x, orte[1].y, orte[1].hp, orte[2].nr, orte[2].x, orte[2].y, orte[2].hp, d))
    end
  end
end

local function einheitWachtTick()
  if einheitWacht == nil then return end
  if (core.readInteger(PAUSE) or 1) ~= 0 then return end
  local t = tick()
  local alle = t >= einheitWacht.naechste
  if alle then einheitWacht.naechste = t + einheitWacht.alle end
  local teile = {}
  for nr, e in pairs(einheitWacht.e) do
    local b = 0x0138854C + nr * 1168
    local zx, zy = core.readSmallInteger(b + 0xC8) or -1, core.readSmallInteger(b + 0xCA) or -1
    local x = math.floor((core.readSmallInteger(b + 0xB6) or 0) / 8)
    local y = math.floor((core.readSmallInteger(b + 0xB8) or 0) / 8)
    -- Kennnummer (+0x98): wechselt sie, ist es eine ANDERE Einheit auf demselben Platz
    -- (gemessen 04.10.: ein Huhn verschwand, sein Platz wurde spaeter neu vergeben).
    local uid = core.readInteger(b + 0x98) or 0
    local leer = (core.readSmallInteger(b + 0x8C) or 0) == 0
    if e.uid ~= nil and (uid ~= e.uid or leer) and not e.weg then
      e.weg = true
      log(INFO, string.format("EW Tick %d: %d WEG (Kennung %d -> %d, Platz %s)", t, nr, e.uid, uid,
        leer and "frei" or "neu belegt"))
    end
    e.uid = e.uid or uid
    if (zx ~= e.zx or zy ~= e.zy) and not e.weg then
      log(INFO, string.format("EW Tick %d: %d Ziel (%s,%s)->(%d,%d) bei (%d,%d)",
        t, nr, tostring(e.zx), tostring(e.zy), zx, zy, x, y))
      e.zx, e.zy = zx, zy
    end
    if alle then table.insert(teile, string.format("%d@(%d,%d)", nr, x, y)) end
  end
  if alle then log(INFO, "EW Orte Tick " .. t .. ": " .. table.concat(teile, " ")) end
end

local function festhaltenTick()
  if next(festhalten) == nil then return end
  if (core.readInteger(PAUSE) or 1) ~= 0 then return end
  local t = tick()
  for nr, f in pairs(festhalten) do
    local b = 0x0138854C + nr * 1168
    if (core.readSmallInteger(b + 0x8C) or 0) == 0 or core.readInteger(b + 0x98) ~= f.uid then
      festhalten[nr] = nil                      -- Einheit weg oder Platz neu belegt
      log(INFO, string.format("HALTEN Tick %d: %d ist weg - losgelassen.", t, nr))
    else
      local zx, zy = core.readSmallInteger(b + 0xC8) or -1, core.readSmallInteger(b + 0xCA) or -1
      if (core.readSmallInteger(b + 924) or 0) ~= 0 then
        -- Einheit hat einen Angriffsbefehl (Zielart +924) - loslassen statt zurueckziehen (04.10.: die Wache holte
        -- Assassinen von ihren Zielen zurueck, "sie sammeln sich nur und machen nichts")
        festhalten[nr] = nil
      elseif (zx ~= f.x or zy ~= f.y) and t - f.letzter >= 10 then
        f.letzter = t
        _setDest = _setDest or core.exposeCode(ADR_SETDEST, 5, 1)
        pcall(_setDest, UNITS_STATE, nr, f.x, f.y, 0)
        f.gesetzt = f.gesetzt + 1
        if f.gesetzt <= 2 then
          log(INFO, string.format("HALTEN Tick %d: %d nachgesetzt (Nr. %d, fremdes Ziel war (%d,%d)).", t, nr, f.gesetzt, zx, zy))
        end
      end
    end
  end
end

local function angriffSchlangeTick()
  if (core.readInteger(PAUSE) or 1) ~= 0 then return end
  local t = tick()
  local w = angriffWarten
  if w ~= nil then
    local fertig = true
    for _, nr in ipairs(w.einheiten) do
      local u = 0x0138854C + nr * 1168
      if (core.readSmallInteger(u + 0x8C) or 0) ~= 0 and (core.readSmallInteger(u + 672) or 0) == 0
         and core.readSmallInteger(u + 728) ~= w.gruppe then fertig = false; break end
    end
    if not fertig and t - w.tick < 20 then return end
    if not fertig then
      log(WARNING, string.format("ANGRIFF Tick %d: Gruppe %d stand nach 20 Ticks nicht - naechster Befehl trotzdem.", t, w.gruppe))
    end
    angriffWarten = nil
  end
  if #angriffSchlange == 0 then return end
  local a = table.remove(angriffSchlange, 1)
  local gut, err = pcall(einzelbefehl, { angriff = a, ausSchlange = true })
  if not gut then log(WARNING, "logik: " .. tostring(err)) end
end

local function zickzackTick()
  local z = zickzack
  if z == nil then return end
  if (core.readInteger(PAUSE) or 1) ~= 0 then return end
  local t = tick()
  if z.letzterTick == t then return end            -- je Tick genau einmal
  z.letzterTick = t
  z.t0 = z.t0 or t
  local i = t - z.t0
  local b = 0x0138854C + z.nr * 1168
  local befohlen = ""
  if i < z.ticks and i % z.alle == 0 then
    local ziel = (math.floor(i / z.alle) % 2 == 0) and z.b or z.a
    _setDest = _setDest or core.exposeCode(ADR_SETDEST, 5, 1)
    local ok, r = pcall(_setDest, UNITS_STATE, z.nr, ziel[1], ziel[2], 0)
    befohlen = string.format(" BEFEHL->(%d,%d)=%s", ziel[1], ziel[2], ok and tostring(r) or "Fehler")
  end
  log(INFO, string.format("ZZ %d %d %d %d %d%s", t, core.readSmallInteger(b + 0xB6) or -1,
    core.readSmallInteger(b + 0xB8) or -1, core.readSmallInteger(b + 0xC8) or -1,
    core.readSmallInteger(b + 0xCA) or -1, befohlen))
  if i >= z.ticks then zickzack = nil; log(INFO, "ZICKZACK: fertig.") end
end

local function everyTick()
  pcall(ladePauseTick)        -- zuerst: die Pause soll vor allem anderen greifen
  pcall(leereKITick)
  pcall(zickzackTick)
  pcall(tickPauseTick)
  pcall(lordWachtTick)
  pcall(einheitWachtTick)
  pcall(festhaltenTick)
  pcall(angriffSchlangeTick)
  pcall(mauerwachtTick)
  pcall(gebaeudewachtTick)
  pcall(bauwachtTick)
  pcall(autobildTick)
  pcall(fensterWachtTick)
  pcall(ketteTick)
  pcall(regelwachtTick)
end

log(INFO, "logik.lua (31.08.2026): + Bauwacht, + Durchreichen an init.lua.")

-- Im Hauptmenue laeuft processGameTick nicht, also auch everyTick nicht.
-- Kette und Fenster-Wacht muessen dort trotzdem arbeiten - beide fassen nur
-- Menue- und Fensterzustand an, nichts aus einem laufenden Gefecht.
local function menuTick()
  pcall(fensterWachtTick)
  pcall(ketteTick)
end

return {
  menuTick        = menuTick,
  handleCommand   = handleCommand,
  bauwachtStart   = bauwachtStart,
  mauernZaehlen   = mauernZaehlen,
  everyTick       = everyTick,
  mauerwachtStart = mauerwachtStart,
  gebaeudeBericht = gebaeudeBericht,
  mauerDiagnose   = mauerDiagnose,
}
