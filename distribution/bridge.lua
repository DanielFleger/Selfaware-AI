--[[
  Village Studio - Live-AIV-Tausch im laufenden Gefecht (ENTWURF, UNGETESTET)

  Idee
  ----
  Der Bauplan einer KI (AIV) wird vom Spiel nur EINMAL beim Start des Gefechts
  eingelesen und in die KI-Daten uebertragen:

      LaunchSkirmishGame (0x441270)
        -> setupAIVMetadata                 0x4ECEF0   Slot 1..8 belegen
        -> selectBestAIVwithRandomStart     0x4F13F0   Burg 1..8 auswaehlen
           bzw. tryPlaceAIVAndReturnFitPct  0x4F14F0   feste Burg pruefen
        -> applyAIV                         0x4EF0D0   Plan in die KI-Daten schreiben

  Danach baut die KI Tick fuer Tick aus diesen Daten weiter:
      processGameTick 0x45CD10
        -> updateBuildingsStateAndUpdateAIBuildingDecisions 0x4F1860
           -> aiDecideOnNewBuildings 0x4F15C0 -> aiPlaceAIVBuilding 0x4ED410

  Deshalb reicht modules.aivloader:setAIVFileForAI() mitten im Gefecht NICHT:
  das setzt nur die Dateiumleitung und die Pruefsumme, die beide erst beim
  naechsten LaunchSkirmishGame gelesen werden.

  Dieser Entwurf ruft daher zusaetzlich tryPlace... + applyAIV selbst auf,
  damit der neue Plan sofort in die KI-Daten geht.

  Warum das wirken MUSS (statisch belegt, 28.08.2026):
  applyAIV fuellt eine Bauliste je Slot (Schrittweite 0x922) und schreibt dort
  pro Eintrag  byte +0x38 = 1 (Zustand "offen")  und  word +0x3a = Gebaeudetyp
      0x4EF281  mov word  [ecx+0x3a], bx
      0x4EF28B  mov byte  [ecx+0x38], 1
  Genau diese beiden Felder liest aiPlaceAIVBuilding in JEDEM Tick wieder aus:
      0x4ED431  imul edx, edx, 0x922
      0x4ED443  movsx esi, word [ecx+edx*4 + 0x3a]
      0x4ED45E  mov   dl,   byte [ebx + 0x38]
  Die Liste wird also nicht einmalig ausgewertet, sondern Eintrag fuer Eintrag
  abgearbeitet. Ein erneutes applyAIV mitten im Gefecht fuellt sie neu.

  Aufrufkonventionen geprueft (ret-imm):
      applyAIV        ret 8  -> thiscall + 2 Argumente -> exposeCode(a, 3, 1)
      tryPlaceAIV     ret 8  -> thiscall + 2 Argumente -> exposeCode(a, 3, 1)
      processGameTick ret 0  -> thiscall + 0 Argumente -> hookCode(f, a, 1, 1, 7)

  Kein Vorbild vorhanden: aiSwapper 1.2.1 (scripts/aiv.lua) ruft ausschliesslich
  aivModule:setMultipleAIVForAi / resetAllAIVForAi auf - also genau den Weg, der
  im laufenden Gefecht nachweislich nichts bewirkt. Der Live-Teil hier ist neu.

  ACHTUNG: bereits gebaute Gebaeude des alten Plans bleiben stehen.
  Der neue Plan wirkt nur auf alles, was die KI noch NICHT gebaut hat.
]]--

--[[ Konstanten ]]--

local COMMAND_FILE   = "ucp/villagestudio/befehl.json"
local LOGIC_FILE     = "ucp/modules/selfaware-runtime-0.1.0/logik.lua"
local PLAN_FOLDER    = "ucp/villagestudio/aiv/"   -- hier liegen eigene BauplÃ¤ne
-- Auf 1 gesetzt: Befehlsdatei und Logik werden in JEDEM Spiel-Takt geprueft.
-- Eine Aenderung wirkt damit im naechstmoeglichen Tick, unabhaengig vom
-- Spieltempo. Ueber VS.setPollEvery(n) zur Laufzeit aenderbar, falls das
-- Dateilesen bei sehr hohem Tempo stoert.
local POLL_EVERY     = 1
local SLOT_SIZE      = 0x6D98      -- Groesse eines AIV-Slots
local SLOT_PLAYERID  = 0x04        -- +0x04 = PlayerID des Slots
local SLOT_LORDTYPE  = 0x08        -- +0x08 = Lord-Typ (2..17, also aivIndex+2)
local SLOT_ROTATION  = 0x0C        -- +0x0C = Drehung
local SLOT_CASTLE    = 0x10        -- +0x10 = gewaehlte Burg 0..7
local SLOT_VALID     = 0x14        -- +0x14 = 0 = noch kein Plan gesetzt

--[[ Adressen ]]--

local function scan(aob, name)
  local a = core.AOBScan(aob, 0x400000)
  if a == nil then
    error(string.format("villagestudio: Signatur '%s' nicht gefunden.", name))
  end
  return a
end

-- thiscall applyAIV(this, slotIndex, playerID)
local addrApplyAIV = scan("83 ec 24 8b 44 24 28 69 c0 98 6d 00 00 53", "applyAIV")
-- thiscall tryPlaceAIVAndReturnFitPercentage(this, slotIndex, castleIndex0based)
local addrTryPlace = scan("53 55 56 8b f1 57 8d 86 58 45 0b 00 50 6a", "tryPlaceAIV")
-- stdcall MenuView_MainMenu_DoEveryFrame() - laeuft im HAUPTMENUE jeden
-- Bildaufbau. Der Gefechtsstart braucht diesen Haken, weil processGameTick
-- im Menue gar nicht tickt.
-- renderBltAndFlip: schaltet das fertige Bild um und laeuft damit in JEDEM
-- Durchlauf. Die anderen Kandidaten scheiden aus: 0x424DA0 feuerte auch bei
-- sauberer Einzelinstanz nicht, 0x440430 nur bei Zustandswechsel.
local addrMenuFrame = scan("81 ec f4 07 00 00 a1 20 42 b9 00 33 c4 89 84 24 f0 07", "renderBltAndFlip")
-- thiscall takeScreenshot(this, nummer) - das Spiel schreibt sein eigenes
-- Bild. Ueber GDI geht das nicht: PrintWindow und BitBlt liefern bei DirectX
-- nur den Fensterrahmen.
local addrScreenshot = scan("6a ff 68 b4 9f 59 00 64 a1 00 00 00 00 50 81 ec c0 08", "takeScreenshot")
local WINDOW_DD = 0x00F98338

-- cdecl SetupSkirmishMode(missionNr) - setzt die Lobby auf, fuellt die
-- KI-Gegner aus der vorgegebenen Gefechtspfad-Mission und startet.
local addrSetupSkirmish = scan("8b 44 24 04 8b 0d ac 9c fe 01 8d 04 c0 c1 e0 04", "setupSkirmishMode")

-- thiscall processGameTick(this)
local addrGameTick = scan("83 3d 24 e4 91 01 00 56 8b f1 c7 05 5c 29", "processGameTick")

-- Der AIV-Manager (this). In LaunchSkirmishGame steht direkt vor dem
-- applyAIV-Aufruf "cmp dword [edi + this+0x14], 0" - daraus lesen wir ihn aus.
local addrThisRef = scan("8b 03 8b f8 69 ff 98 6d 00 00 83 bf", "aivManagerRef")
local AIV_MANAGER = core.readInteger(addrThisRef + 12) - 0x14

-- thiscall destroyBuilding(this, gebaeudeIndex)  -  0x41A7A0
local addrDestroy  = scan("53 8b 5c 24 08 8b c3 69 c0 2c 03 00 00 55 56 8b f1 57", "destroyBuilding")

--[[ Gebaeudetabelle (fuer den Abriss) ]]--
-- Basis 0xF98520, ein Eintrag 0x32C Bytes, Anzahl bei +0x08.
-- Belegt aus destroyBuilding 0x41A7A0 und destroyBuildings 0x41A860.
local BUILDINGS   = 0xF98520
local B_STRIDE    = 0x32C
local B_STATE     = 0xE4     -- 0 = kein Gebaeude, 3 = abgerissen
local B_TYPE      = 0xE6
local B_OWNER     = 0xEA
local B_GROUP     = 0x2BC    -- Gruppennummer: destroyBuilding reisst die ganze Gruppe mit
local RUBBLE_FLAG = 0x1FE7BAC   -- setzt destroyBuildings vor jedem Aufruf
local TYPE_TABLE  = 0x5B9EA8

-- Typnummern aus der Update-Sprungtabelle 0x5B79A8 (110 Eintraege, Platz = Typ).
-- Diese bleiben stehen, sonst waere die KI ausgeschieden statt umgebaut.
-- Diese Typen bleiben beim Abriss stehen. Der Kornspeicher steht bewusst NICHT
-- drin: viele Bauplaene setzen ihren eigenen. Mit "schuetze": [10,41] im Befehl
-- laesst sich die Liste zur Laufzeit ersetzen.
local PROTECTED = {
  [10] = "Lager",
  [40] = "Herrenhaus", [41] = "Steinburg", [42] = "Feste",
  [71] = "Bergfriedtuer links", [72] = "Bergfriedtuer rechts", [73] = "Bergfriedtuer",
}

local applyAIV = core.exposeCode(addrApplyAIV, 3, 1)
local tryPlace = core.exposeCode(addrTryPlace, 3, 1)
local destroyBuilding = core.exposeCode(addrDestroy, 2, 1)
-- cdecl, ein Argument, kein this
local setupSkirmish = core.exposeCode(addrSetupSkirmish, 1, 0)
-- thiscall mit einem Argument
local takeScreenshot = core.exposeCode(addrScreenshot, 2, 1)

--[[ Slot-Suche ]]--

local function slotAddr(slot)
  return AIV_MANAGER + slot * SLOT_SIZE
end

-- Findet den AIV-Slot eines Spielers (1..8), oder nil.
-- Belegt aus setupAIVMetadata 0x4ECEF0: das Spiel sucht dort einen freien Slot
-- ueber "[slot+4] == 0" und traegt dann bei 0x4ECF31 die PlayerID nach +0x04 ein.
-- Der Slot gehoert also genau dann zum Spieler, wenn +0x04 seine ID ist.
-- +0x14 ist NICHT das richtige Kriterium: setupAIVMetadata loescht es (0x4ECF40),
-- gesetzt wird es erst durch tryPlace/selectBest.
local function findSlotForPlayer(playerID)
  if playerID == nil or playerID == 0 then return nil end
  for slot = 1, 8 do
    if core.readInteger(slotAddr(slot) + SLOT_PLAYERID) == playerID then
      return slot
    end
  end
  return nil
end

-- aivIndex 0..15 (rat..abbot) des Slots
local function slotAivIndex(slot)
  return core.readInteger(slotAddr(slot) + SLOT_LORDTYPE) - 2
end

-- Schreibt alle 8 Slots ins Log - zum Nachsehen, welche Spielernummer stimmt
local function dumpSlots()
  for slot = 1, 8 do
    local a = slotAddr(slot)
    local pid  = core.readInteger(a + SLOT_PLAYERID)
    local lord = core.readInteger(a + SLOT_LORDTYPE)
    if pid ~= 0 then
      log(INFO, string.format(
        "  Slot %d: Spieler %d, Lord-Typ %d (aivIndex %d), Burg %d, Zustand %d",
        slot, pid, lord, lord - 2,
        core.readInteger(a + SLOT_CASTLE) + 1,
        core.readInteger(a + SLOT_VALID)))
    end
  end
end

-- Zaehlt, was ein Spieler noch besitzt - nach Gebaeudetyp.
-- Dient zum Nachsehen statt Raten, welche Typnummer der Bergfried wirklich hat.
local function reportBuildings(player)
  local count = core.readInteger(BUILDINGS + 8)
  if count == nil or count < 2 or count > 4000 then
    log(WARNING, string.format("villagestudio: Gebaeudeanzahl unplausibel (%s).", tostring(count)))
    return
  end

  local byType, total = {}, 0
  for i = 1, count - 1 do
    local b = BUILDINGS + i * B_STRIDE
    local state = core.readSmallInteger(b + B_STATE)
    if state ~= 0 and state ~= 3 and core.readSmallInteger(b + B_OWNER) == player then
      local t = core.readSmallInteger(b + B_TYPE)
      byType[t] = (byType[t] or 0) + 1
      total = total + 1
    end
  end

  log(INFO, string.format("villagestudio: Bestand Spieler %d - %d Gebaeude:", player, total))
  for t = 0, 109 do
    if byType[t] then
      log(INFO, string.format("   Typ %3d : %3d Stueck%s", t, byType[t],
        PROTECTED[t] and ("  <- geschuetzt (" .. PROTECTED[t] .. ")") or ""))
    end
  end
end

-- Reisst das Dorf eines Spielers ab, laesst Bergfried, Tueren, Lager und
-- Kornspeicher stehen. Gibt die Anzahl abgerissener Gebaeude zurueck.
local function razeVillage(player, protect)
  protect = protect or PROTECTED
  local count = core.readInteger(BUILDINGS + 8)
  if count == nil or count < 2 or count > 4000 then
    log(WARNING, string.format("villagestudio: Gebaeudeanzahl unplausibel (%s) - Abriss abgebrochen.", tostring(count)))
    return 0
  end

  -- Erster Durchgang: Gruppennummern der geschuetzten Gebaeude sammeln.
  -- destroyBuilding (0x41A80F ff.) reisst IMMER alle Gebaeude derselben Gruppe
  -- mit ab - Gruppennummer steht bei +0x2BC. Ohne diesen Schritt faellt der
  -- Bergfried mit, obwohl sein Typ geschuetzt ist (belegt am 28.08.2026:
  -- 52 abgerissen, 17 "verschont", danach war der Bergfried trotzdem weg).
  local safeGroup = {}
  for i = 1, count - 1 do
    local b = BUILDINGS + i * B_STRIDE
    if core.readSmallInteger(b + B_STATE) ~= 0
       and core.readSmallInteger(b + B_OWNER) == player
       and protect[core.readSmallInteger(b + B_TYPE)] then
      local grp = core.readInteger(b + B_GROUP)
      if grp ~= 0 then safeGroup[grp] = true end
    end
  end

  -- Zweiter Durchgang: abreissen, was weder geschuetzten Typ noch geschuetzte
  -- Gruppe hat.
  local torn, spared = 0, 0
  for i = 1, count - 1 do
    local b = BUILDINGS + i * B_STRIDE
    if core.readSmallInteger(b + B_STATE) ~= 0
       and core.readSmallInteger(b + B_OWNER) == player then
      local t   = core.readSmallInteger(b + B_TYPE)
      local grp = core.readInteger(b + B_GROUP)
      if protect[t] or (grp ~= 0 and safeGroup[grp]) then
        spared = spared + 1
      else
        -- destroyBuildings setzt dieses Flag vor jedem Aufruf genauso (0x41A894)
        local noRubble = 0
        if core.readInteger(TYPE_TABLE + t * 4) == 0 then noRubble = 1 end
        core.writeInteger(RUBBLE_FLAG, noRubble)
        destroyBuilding(BUILDINGS, i)
        torn = torn + 1
      end
    end
  end

  log(INFO, string.format(
    "villagestudio: Abriss bei Spieler %d - %d Gebaeude weg, %d verschont (Bergfried/Lager und deren Gruppen).",
    player, torn, spared))
  return torn
end

--[[ Der eigentliche Live-Tausch ]]--

-- ai:     0..15 oder "rat".."abbot"
-- castle: 1..8
-- file:   Pfad zur neuen .aiv-Datei (oder nil = zurueck auf Original)
-- player: PlayerID des Gefechts (1..8), dessen KI umgebaut werden soll
local function swapLive(ai, castle, file, player, strict, raze, protect)
  -- 0. Auf Wunsch erst das alte Dorf abreissen, damit sich die Plaene
  --    nicht uebereinanderstapeln.
  if raze then razeVillage(player, protect) end

  -- 1. Dateiumleitung + Pruefsumme setzen (macht aivloader fuer uns)
  modules.aivloader:setAIVFileForAI(ai, castle, file)

  -- 2. Slot des Spielers suchen
  local slot = findSlotForPlayer(player)
  if slot == nil then
    log(WARNING, string.format(
      "villagestudio: kein AIV-Slot fuer Spieler %s. Belegte Slots:", tostring(player)))
    dumpSlots()
    return false
  end

  -- 3. Plan neu einlesen und pruefen (setzt auch +0x10 und +0x14)
  --    tryPlace liefert vorzeichenbehaftet: -3 Datei nicht ladbar, -2 passt nicht,
  --    sonst 1..100 Prozent. core.exposeCode gibt die Zahl vorzeichenlos zurueck,
  --    deshalb hier zurueckrechnen (sonst wird aus -2 die Zahl 4294967294).
  local fit = tryPlace(AIV_MANAGER, slot, castle - 1)
  if fit == nil then
    log(WARNING, "villagestudio: tryPlace lieferte nichts.")
    return false
  end
  if fit > 0x7FFFFFFF then fit = fit - 0x100000000 end

  if fit == -3 then
    log(WARNING, string.format("villagestudio: Datei nicht ladbar: %s", tostring(file)))
    return false
  end

  -- fit == -2 heisst: die Burg passt an dieser Stelle nicht vollstaendig hin.
  -- Mitten im Gefecht ist das der Normalfall, weil der Boden dort schon bebaut
  -- ist - computeAIVPlacementFit (0x4EF8C0) prueft jede Kachel mit
  -- isBuildingPlacementAllowedAtTile (0x4F9A60) und zaehlt Besetztes als Fehlschlag.
  -- Deshalb wird trotzdem angewandt, sofern nicht "strict": true verlangt wird.
  if fit <= 0 and strict then
    log(WARNING, string.format(
      "villagestudio: Burg %d passt nicht (Code %d) - abgebrochen, weil strict gesetzt ist.", castle, fit))
    return false
  end

  -- 4. Plan in die KI-Daten schreiben
  applyAIV(AIV_MANAGER, slot, player)

  if fit > 0 then
    log(INFO, string.format(
      "villagestudio: AIV live getauscht - Spieler %d, Slot %d, KI %s, Burg %d, Passung %d%%.",
      player, slot, tostring(ai), castle, fit))
  else
    log(INFO, string.format(
      "villagestudio: AIV live getauscht - Spieler %d, Slot %d, KI %s, Burg %d (Boden bereits bebaut, Passung %d - trotzdem angewandt).",
      player, slot, tostring(ai), castle, fit))
  end
  return true
end

--[[ Befehlsdatei beobachten ]]--

local lastRaw = nil

local function readCommandFile()
  local f = io.open(COMMAND_FILE, "rb")
  if not f then return nil end
  local raw = f:read("*all")
  f:close()
  return raw
end

-- Eigene BauplÃ¤ne liegen in ucp/villagestudio/aiv/. Wer dort eine Datei ablegt,
-- schreibt im Befehl nur den Namen: "file": "meineburg.aiv".
-- Ein Pfad mit SchrÃ¤gstrich wird unveraendert durchgereicht (z.B. "aiv/Sultan1.aiv").
local function resolveFile(file)
  if file == nil or file == "" then return file end
  if file:find("/") or file:find("\\") then return file end
  return PLAN_FOLDER .. file
end

-- Ein einzelner Befehl. Gibt true zurueck, wenn getauscht wurde.
local function handleOne(cmd)
  if type(cmd) ~= "table" then
    log(WARNING, "villagestudio: Befehl ist kein Objekt.")
    return false
  end

  local player = cmd.player
  local castle = cmd.castle or 1
  local ai     = cmd.ai
  local file   = resolveFile(cmd.file)   -- nil => zuruecksetzen auf Original

  if player == nil then
    log(WARNING, "villagestudio: 'player' fehlt im Befehl.")
    return false
  end

  -- Reiner Bericht: nichts veraendern, nur auflisten was da ist.
  if cmd.bericht == true then
    reportBuildings(player)
    return true
  end

  if ai == nil then
    local slot = findSlotForPlayer(player)
    if slot == nil then
      log(WARNING, string.format(
        "villagestudio: Spieler %s hat keinen AIV-Slot. Belegte Slots:", tostring(player)))
      dumpSlots()
      return false
    end
    ai = slotAivIndex(slot)
  end

  local protect = nil
  if type(cmd.schuetze) == "table" then
    protect = {}
    for _, t in ipairs(cmd.schuetze) do protect[t] = "vom Befehl geschuetzt" end
  end

  local ok, err = pcall(swapLive, ai, castle, file, player, cmd.strict == true, cmd.abriss == true, protect)
  if not ok then
    log(WARNING, "villagestudio: " .. tostring(err))
    return false
  end
  return err == true   -- pcall liefert den Rueckgabewert von swapLive
end

-- Liste aller Spieler, die gerade einen AIV-Slot haben (1..8)
local function activePlayers()
  local out = {}
  for slot = 1, 8 do
    local pid = core.readInteger(slotAddr(slot) + SLOT_PLAYERID)
    if pid ~= 0 then out[#out + 1] = pid end
  end
  return out
end

-- Nimmt drei Formen entgegen:
--   1. ein einzelner Befehl:      { "player": 1, "file": "..." }
--   2. eine Liste:                [ { ... }, { ... } ]
--   3. eine Liste unter Schluessel: { "befehle": [ { ... }, { ... } ] }
-- Steht in einem Befehl "player": "alle", gilt er fuer jede KI mit Bauplan-Platz.
local function handleCommand(cmd)
  if type(cmd) ~= "table" then return end

  local list = cmd
  if type(cmd.befehle) == "table" then
    list = cmd.befehle
  elseif cmd[1] == nil then
    list = { cmd }                       -- einzelner Befehl
  end

  local done, failed = 0, 0
  for i = 1, #list do
    local c = list[i]
    if type(c) == "table" and (c.player == "alle" or c.player == "all") then
      for _, pid in ipairs(activePlayers()) do
        local copy = {}
        for k, v in pairs(c) do copy[k] = v end
        copy.player = pid
        if handleOne(copy) then done = done + 1 else failed = failed + 1 end
      end
    else
      if handleOne(c) then done = done + 1 else failed = failed + 1 end
    end
  end

  if done + failed > 1 then
    log(INFO, string.format("villagestudio: %d von %d Befehlen ausgefuehrt.", done, done + failed))
  end
end

--[[ Nachladbare Logik ]]--

-- Diese Datei wird - wenn vorhanden - im laufenden Spiel neu geladen, sobald
-- sich ihr Inhalt aendert. Damit lassen sich Aenderungen ohne Spielneustart
-- ausprobieren. Sie bekommt beim Laden die Werkzeugkiste VS uebergeben und
-- gibt eine Tabelle zurueck; enthaelt die ein Feld handleCommand, wird dieses
-- statt des eingebauten benutzt.
local VS = {
  core           = core,
  applyAIV       = applyAIV,
  tryPlace       = tryPlace,
  destroyBuilding= destroyBuilding,
  AIV_MANAGER    = AIV_MANAGER,
  BUILDINGS      = BUILDINGS,
  B_STRIDE       = B_STRIDE,
  B_STATE        = B_STATE,
  B_TYPE         = B_TYPE,
  B_OWNER        = B_OWNER,
  B_GROUP        = B_GROUP,
  RUBBLE_FLAG    = RUBBLE_FLAG,
  TYPE_TABLE     = TYPE_TABLE,
  PROTECTED      = PROTECTED,
  SLOT_SIZE      = SLOT_SIZE,
  slotAddr       = slotAddr,
  findSlotForPlayer = findSlotForPlayer,
  slotAivIndex   = slotAivIndex,
  dumpSlots      = dumpSlots,
  razeVillage    = razeVillage,
  reportBuildings= reportBuildings,
  swapLive       = swapLive,
  handleCommand  = handleCommand,
  takeScreenshot = takeScreenshot,
  WINDOW_DD      = WINDOW_DD,
  log            = log,
  setPollEvery   = function(n)
    if type(n) == "number" and n >= 1 then POLL_EVERY = n end
    return POLL_EVERY
  end,
}

local logicRaw, custom = nil, nil

local function checkLogic()
  local f = io.open(LOGIC_FILE, "rb")
  if not f then
    if custom ~= nil then
      custom, logicRaw = nil, nil
      log(INFO, "villagestudio: logik.lua ist weg - wieder eingebaute Fassung.")
    end
    return
  end
  local raw = f:read("*all")
  f:close()
  if raw == logicRaw then return end
  logicRaw = raw

  local chunk, err = load(raw, "logik.lua", "t", _ENV)
  if not chunk then
    log(WARNING, "villagestudio: logik.lua hat einen Syntaxfehler: " .. tostring(err))
    return
  end
  local ok, res = pcall(chunk, VS)
  if not ok then
    log(WARNING, "villagestudio: logik.lua lief auf einen Fehler: " .. tostring(res))
    return
  end
  custom = (type(res) == "table") and res or nil
  log(INFO, "villagestudio: logik.lua neu geladen - Aenderung ist sofort aktiv.")
end

local tickCounter = 0

local function onTick()
  -- JEDER Tick: die nachgeladene Logik darf hier arbeiten. Damit greifen
  -- DauerauftrÃ¤ge ab dem ersten Takt eines Gefechts, nicht erst Sekunden
  -- spaeter - unabhaengig vom Spieltempo.
  if custom ~= nil and type(custom.everyTick) == "function" then
    local ok, err = pcall(custom.everyTick)
    if not ok then
      log(WARNING, "villagestudio: logik.lua everyTick: " .. tostring(err))
      custom = nil   -- kaputte Logik nicht bei jedem Tick erneut ausfuehren
    end
  end

  tickCounter = tickCounter + 1
  if tickCounter < POLL_EVERY then return end
  tickCounter = 0

  pcall(checkLogic)

  local raw = readCommandFile()
  if raw == nil or raw == lastRaw then return end
  lastRaw = raw

  local ok, cmd = pcall(json.decode, json, raw)
  if not ok then
    log(WARNING, "villagestudio: befehl.json nicht lesbar: " .. tostring(cmd))
    return
  end

  if custom ~= nil and type(custom.handleCommand) == "function" then
    local ok2, err2 = pcall(custom.handleCommand, cmd)
    if not ok2 then
      log(WARNING, "villagestudio: logik.lua: " .. tostring(err2))
    end
    return
  end

  handleCommand(cmd)
end

--[[ Menue-Haken: Gefecht starten, ohne dass jemand klicken muss ]]--
--
-- Im Hauptmenue laeuft kein Spieltakt, also auch kein Befehls-Poll. Dieser
-- Haken schliesst die Luecke: er liest dieselbe befehl.json und fuehrt dort
-- NUR den Gefechtsstart aus. Alles andere braucht ein laufendes Gefecht und
-- wird hier bewusst ignoriert, damit im Menue nichts in leere Strukturen
-- schreibt.
--
-- Die Gegner sind nicht frei waehlbar: SetupSkirmishMode nimmt sie aus der
-- vorgegebenen Gefechtspfad-Mission. Welche Liste gilt, entscheidet
-- currentTrailType (0x01FE9CAC): 0 = Original, 1 = Warchest, 2 = Extreme.

--[[ Fenster sofort nach hinten - ohne Befehl von aussen

Daniel arbeitet weiter, waehrend das Spiel laeuft. Ein frisch gestartetes
Spiel nimmt ihm aber den Bildschirm weg, und von aussen laesst sich das nicht
beheben: der Prozess laeuft auf hoher Rechtestufe, jede Fensterfunktion von
einer normalen Sitzung aus scheitert mit Fehler 5 (01.09. dreimal gemessen).
Ein Befehl ueber die Befehlsdatei kaeme erst, wenn das Modul laeuft - das sind
rund 25 Sekunden Vollbild im Vordergrund.

Deshalb steht das hier im Modulkern und feuert beim ERSTEN gezeichneten Bild.
Das Handle holt sich das Modul selbst: beim ersten Bild ist das eigene Fenster
im Vordergrund, GetForegroundWindow liefert also genau dieses.
]]--

local IAT_SETWINDOWPOS      = 0x0059E1F4
local IAT_GETFOREGROUNDWND  = 0x0059E208
local ZIEL_X, ZIEL_Y        = 2560, 0     -- Monitor 2 beginnt bei x = 2560

local eigenesFenster = nil
local fensterWachtAn   = true      -- von aussen abschaltbar
local fensterWachtAlle = 300

-- Verdacht aus dem Speicherabzug vom 31.08.: in der Grafikstruktur steht bei
-- +0xAC ein Wert, der wie ein Fensterhandle aussieht. Ungeprueft - deshalb
-- wird er nicht blind benutzt, sondern gegen den Vordergrund gehalten.
local WINDOWSTRUKTUR_HWND = 0x00F98338 + 0xAC

local function fensterNachHinten(x, y)
  if eigenesFenster == nil then
    local ausStruktur = core.readInteger(WINDOWSTRUKTUR_HWND)
    local adrGet = core.readInteger(IAT_GETFOREGROUNDWND)
    local imVordergrund = nil
    if adrGet ~= nil and adrGet ~= 0 then
      imVordergrund = core.exposeCode(adrGet, 0, 0)()
    end

    -- Nur handeln, wenn beide Wege dasselbe Fenster nennen. Sonst koennte das
    -- Modul ein FREMDES Fenster nach hinten schieben - Daniel arbeitet
    -- daneben weiter, das waere schlimmer als ein Spiel im Vordergrund.
    if ausStruktur ~= nil and ausStruktur ~= 0 and ausStruktur == imVordergrund then
      eigenesFenster = ausStruktur
      log(INFO, string.format(
        "FENSTER: Handle 0x%X (Struktur und Vordergrund stimmen ueberein)",
        eigenesFenster))
    else
      log(WARNING, string.format(
        "FENSTER: kein sicheres Handle - Struktur sagt %s, Vordergrund %s. " ..
        "Es wird nichts verschoben; Handle bitte mit { \"fenster\": { \"hwnd\": N } } setzen.",
        tostring(ausStruktur), tostring(imVordergrund)))
      fensterWachtAn = false          -- nicht bei jedem Bild erneut jammern
      return false
    end
  end
  -- GELOEST 01.09.2026, 23:33. Der Aufruf hat den Prozess zweimal getoetet,
  -- solange er mit Aufrufart 0 (cdecl) lief: SetWindowPos ist stdcall und
  -- raeumt seine sieben Argumente selbst vom Stapel, exposeCode raeumte ein
  -- zweites Mal auf.
  --
  -- exposeCode kennt eine dritte Aufrufart: **2 = stdcall**. Damit kommt der
  -- Aufruf sauber zurueck (ok=true), das Spiel lebt weiter, und das Fenster
  -- liegt danach auf Platz 7 von 8 - nur der Desktop noch darunter.
  --
  -- Das war nie eine Rechtefrage: von aussen ist es gesperrt (Fehler 5), aber
  -- das Modul laeuft IM Spiel. Es fehlte nur die richtige Aufrufart.
  local adrSet = core.readInteger(IAT_SETWINDOWPOS)
  if adrSet == nil or adrSet == 0 then return false end
  -- HWND_BOTTOM = 1; NOMOVE|NOSIZE|NOACTIVATE = 0x13 - nimmt keinen Fokus weg
  core.exposeCode(adrSet, 7, 2)(eigenesFenster, 1, 0, 0, 0, 0, 0x13)
  return true
end

local function _unbenutzt_alt()
  fensterWachtAn = false
  return true
end

local menuCounter = 0
-- Offener Foto-Wunsch. Wird im Bild-Haken gesetzt und BEIM NAECHSTEN Aufruf
-- ausgefuehrt, bevor das Original zeichnet - sonst ist es ein Wiedereintritt
-- in die Zeichenkette und der Prozess stirbt.
local fotoWunsch = nil

local function onMenuFrame()
  -- nicht bei jedem Bild in die Datei schauen, das kostet nur
  menuCounter = menuCounter + 1
  -- Zustandsmeldung. Der Tick-Poll haengt an processGameTick und laeuft nur
  -- IM Gefecht; ob eines laeuft, war sonst nicht feststellbar. Der Bild-Haken
  -- laeuft immer.
  if menuCounter == 1 or menuCounter % 600 == 0 then
    local ticks = core.readInteger(0x0117CADC) or -1
    local einh  = core.readInteger(0x01387F38) or -1
    log(INFO, string.format(
      "ZUSTAND (Bild %d): Spielzeit %d Ticks, maxUnitCount %d -> %s",
      menuCounter, ticks, einh,
      ticks > 0 and "Gefecht laeuft" or "KEIN Gefecht"))
  end
  -- Beim allerersten Bild sofort nach hinten, danach regelmaessig nachfassen.
  -- Frueher geht es nicht: vorher hat das Spiel noch kein Fenster gezeichnet.
  -- ABGESCHALTET 01.09.2026. Zwei Startversuche endeten im Absturz, beide mit
  -- diesem Block als einzigem Unterschied. Der erste starb direkt beim Aufruf
  -- von SetWindowPos, der zweite kurz danach - auch die blosse Abfrage von
  -- GetForegroundWindow ueber exposeCode steht damit unter Verdacht.
  --
  -- Gebraucht wird der Block ohnehin nicht mehr: Die Fensterlage stellt jetzt
  -- der graphicsApiReplacer selbst ueber window.pos = topRight in der
  -- ucp-config.yml - das Modul erzeugt das Fenster und darf es platzieren.
  -- Im Bild bestaetigt: das Fenster geht auf dem rechten Schirm auf.
  --
  -- Wer das hier je wieder einschaltet, braucht zuerst eine belegte Antwort
  -- auf die Frage, wie exposeCode eine stdcall-Funktion ruft. Im ganzen UCP
  -- gibt es dafuer kein einziges Beispiel.
  -- Beim ersten Bild sofort nach hinten, danach regelmaessig nachfassen -
  -- das Spiel holt sich waehrend des Ladens mehrfach die Spitze zurueck.
  --
  -- Abschaltbar ueber eine Datei, nicht ueber einen Befehl: Die Wacht feuert
  -- schon beim ERSTEN Bild, lange bevor die Befehlsdatei zum ersten Mal
  -- gelesen wird. Ein Befehl kaeme also immer zu spaet. Wer das Spiel im
  -- Vordergrund braucht, legt ucp/villagestudio/vorn.txt an.
  if menuCounter == 1 then
    local f = io.open("ucp/villagestudio/vorn.txt", "r")
    if f ~= nil then
      f:close()
      fensterWachtAn = false
      log(INFO, "FENSTER: vorn.txt gefunden - das Fenster bleibt, wo es ist.")
    end
  end
  if fensterWachtAn and (menuCounter <= 60 or menuCounter % 300 == 0) then
    pcall(fensterNachHinten)
  end

  -- Menue-Takt der Logik: Kette und Fenster-Wacht arbeiten auch hier weiter.
  -- everyTick waere falsch - das ruft Wachten, die in Gefechtsstrukturen
  -- schreiben, die im Menue leer sind.
  if custom ~= nil and type(custom.menuTick) == "function" then
    pcall(custom.menuTick)
  end

  if menuCounter % 20 ~= 0 then return end

  local raw = readCommandFile()
  if raw == nil or raw == lastRaw then return end
  local ok, cmd = pcall(json.decode, json, raw)
  if not ok or type(cmd) ~= "table" then return end
  -- Foto nur VORMERKEN. Ausgefuehrt wird es beim naechsten Bild, bevor das
  -- Original zeichnet.
  if cmd.foto ~= nil then
    lastRaw = raw
    fotoWunsch = type(cmd.foto) == "number" and cmd.foto or 1
    log(INFO, string.format("FOTO: vorgemerkt (Nummer %d).", fotoWunsch))
    return
  end

  -- Alles, was die Logik im Menue selbst erledigen kann, wird durchgereicht.
  -- Bis 01.09. verwarf dieser Haken jeden anderen Befehl stillschweigend -
  -- ein neuer Befehl kam im Hauptmenue schlicht nie an, ohne eine einzige
  -- Zeile im Log. Genau das hat den ersten Anlauf zum eigenen Gefecht gekostet.
  -- Eine LISTE ist hier genauso gueltig wie ein einzelner Befehl. Ohne diese
  -- Zeile verwirft der Haken sie stillschweigend: bei { "befehle": [...] } ist
  -- cmd.menue leer, und keine der Einzelpruefungen greift. Am 02.09.2026 kam
  -- dadurch ein Menuesprung nie an - ohne eine Zeile im Log.
  if cmd.poke ~= nil or cmd.befehle ~= nil
     or cmd.eigenesGefecht ~= nil or cmd.fenster ~= nil
     or cmd.kette ~= nil or cmd.wo ~= nil or cmd.menue ~= nil
     or cmd.peek ~= nil or cmd.bild ~= nil or cmd.beenden ~= nil
     or cmd.hinten ~= nil or cmd.regel ~= nil or cmd.tausche ~= nil then
    lastRaw = raw
    checkLogic()          -- erst den neuesten Stand der Logik holen
    if custom ~= nil and type(custom.handleCommand) == "function" then
      local ok3, err3 = pcall(custom.handleCommand, cmd)
      if not ok3 then
        log(WARNING, "MENUE: Befehl lief auf einen Fehler: " .. tostring(err3))
      end
    else
      log(WARNING, "MENUE: logik.lua ist nicht geladen - Befehl verworfen.")
    end
    return
  end

  if type(cmd.gefecht) ~= "number" then return end
  -- Laeuft schon ein Gefecht? Der Einheitenzaehler taugt dafuer NICHT - er
  -- behaelt im Hauptmenue den Restwert des vorigen Gefechts. Die Spielzeit
  -- laeuft dagegen nur im Gefecht. Mit "trotzdem": true laesst sich die
  -- Pruefung uebergehen.
  local ticks = core.readInteger(0x0117CADC) or 0
  if ticks > 0 and cmd.trotzdem ~= true then
    log(WARNING, string.format(
      "MENUE: es laeuft bereits ein Gefecht (Tick %d) - Startbefehl ignoriert. " ..
      "Mit \"trotzdem\": true erzwingen.", ticks))
    lastRaw = raw
    return
  end

  lastRaw = raw
  log(INFO, string.format("MENUE: starte Gefechtspfad-Mission %d (Pfadart %s).",
    cmd.gefecht, tostring(core.readInteger(0x01FE9CAC))))
  local ok2, err = pcall(setupSkirmish, cmd.gefecht)
  if not ok2 then
    log(WARNING, "MENUE: Gefechtsstart fehlgeschlagen: " .. tostring(err))
  end
end

--[[ Modul ]]--

local originalGameTick = nil
local originalMenuFrame = nil

return {
  enable = function(self, config)
    if config ~= nil and config.commandFile ~= nil then
      COMMAND_FILE = config.commandFile
    end

    -- processGameTick beginnt mit 7 Bytes "cmp dword [..],0", die wir stehlen.
    originalGameTick = core.hookCode(function(this)
      local r = originalGameTick(this)
      local ok, err = pcall(onTick)
      if not ok then log(WARNING, "villagestudio: " .. tostring(err)) end
      return r
    end, addrGameTick, 1, 1, 7)

    -- MenuView_MainMenu_DoEveryFrame beginnt mit 8 Bytes an sauberer
    -- Anweisungsgrenze: "sub esp,0x68" (3) + "mov eax,[0xB94220]" (5).
    -- stdcall ohne Argumente -> hookCode(f, a, 0, 0, 8)
    local okHook, resHook = pcall(function()
      return core.hookCode(function(this, a1)
        -- offener Foto-Wunsch: JETZT, bevor gezeichnet wird
        if fotoWunsch ~= nil then
          local nr = fotoWunsch
          fotoWunsch = nil
          local okf, errf = pcall(takeScreenshot, WINDOW_DD, nr)
          log(okf and INFO or WARNING, okf
            and string.format("FOTO: takeScreenshot(%d) ausgefuehrt.", nr)
            or ("FOTO fehlgeschlagen: " .. tostring(errf)))
        end
        local r
        if originalMenuFrame ~= nil then r = originalMenuFrame(this, a1) end
        local ok, err = pcall(onMenuFrame)
        if not ok then log(WARNING, "villagestudio Menue: " .. tostring(err)) end
        return r
      end, addrMenuFrame, 2, 1, 6)
    end)
    if okHook then
      originalMenuFrame = resHook
      log(INFO, string.format("Bild-Haken gesetzt auf 0x%X (Gefechtsstart per Datei moeglich).",
        addrMenuFrame))
    else
      log(WARNING, "Menue-Haken konnte NICHT gesetzt werden: " .. tostring(resHook))
    end

    -- Logik und Befehlsdatei EINMAL sofort einlesen, noch bevor ein Gefecht
    -- laeuft. Nur so ist ein Dauerauftrag schon beim allerersten Takt scharf.
    pcall(checkLogic)
    local raw = readCommandFile()
    if raw ~= nil then
      lastRaw = raw
      local ok, cmd = pcall(json.decode, json, raw)
      if ok then
        if custom ~= nil and type(custom.handleCommand) == "function" then
          pcall(custom.handleCommand, cmd)
        else
          pcall(handleCommand, cmd)
        end
      end
    end

    log(INFO, string.format("villagestudio aktiv. AIV-Manager 0x%X, Befehlsdatei '%s'.",
      AIV_MANAGER, COMMAND_FILE))
  end,

  disable = function(self, config)
    log(WARNING, "villagestudio: Abschalten zur Laufzeit nicht unterstuetzt.")
  end,

  -- fuer die Konsole
  swapLive = function(self, ai, castle, file, player, strict, raze)
    return swapLive(ai, castle, file, player, strict, raze)
  end,
  findSlotForPlayer = function(self, player) return findSlotForPlayer(player) end,
  dumpSlots = function(self) return dumpSlots() end,
  razeVillage = function(self, player, protect) return razeVillage(player, protect) end,
  reportBuildings = function(self, player) return reportBuildings(player) end,
}

