-- Taktring (B-251, SRE 25.10.2026): jeden Spieltakt die Rohbloecke Einheiten + Geschosse in einen Ring im Spielspeicher
-- kopieren, damit das Auge (werkzeug/auge.py, Klasse Taktring) auch die Takte bekommt, die das Spiel innerhalb EINES Bilds
-- doppelt rechnet (gemessen 25.10.: bei 100 Takten/s jedes vierte Bild zwei Takte, von aussen sind nur 75 % zu sehen).
--
-- Einbau in logik.lua: oben `local taktring = require("taktring")` (das Zip laedt Module per require wie init.lua),
-- in everyTick() als erste Zeile `pcall(taktring.tick)` (tick() ruft start() beim ersten Mal selbst). Je Takt ~5,3 MB memcpy.
-- Quelle: Selfaware-AI/werkzeug/taktring.lua (SAI 19:29: EINE Quelle); Kopie im Zip selfaware-runtime-0.1.0.zip.
--
-- Aufbau: RING = core.allocate(KOPF + SLOTS * SLOT); Kopf: int32 magic 0x54414B54 ("TAKT"), int32 SLOTS, int32 SLOT,
-- int32 letzter_index, int32 letzter_takt. Slot i bei RING + KOPF + i * SLOT: int32 takt, int32 takt_kern, int32 maxUnitCount,
-- int32 maxBuildingsCount, dann Einheiten (2500 x 1168 ab 0x0138854C), Geschosse (3000 x 232 ab 0x02350314), Gebaeude
-- (2000 x 812 ab 0x00F98534; SAI 19:29: Feuer/Abklingzeit/Leben je Takt), dann HeightLayer (80400 x 1), BuildingLayer
-- (80400 x 2), LogicLayer (80400 x 4). Je Platz 5,8 MB, 16 Plaetze = 93 MB.
-- Die Basisadresse schreibt start() nach ucp/villagestudio/taktring.txt (eine Zeile, dezimal), Python liest sie dort.

local M = {}

local TICK = 0x0117CADC
local TICK_KERN = 0x01FE7DA8
local UNITS_STATE = 0x01387F38
local UNITS = 0x0138854C
local UNITS_BYTES = 2500 * 1168
local ENTITIES = 0x02350314
local ENTITIES_BYTES = 3000 * 232
local BUILDINGS_STATE = 0x00F98520
local BUILDINGS = 0x00F98534
local BUILDINGS_BYTES = 2000 * 812
-- Karten-Ebenen (B-252, 19:40: Steine prallen an Daechern ab - Boden = HeightLayer + Gebaeudehoehe; dafuer je Takt noetig)
local HEIGHT_LAYER = 0x01D32C38      -- 1 Byte je Feld
local BUILDING_LAYER = 0x01C95BB8    -- 2 Byte je Feld
local LOGIC_LAYER = 0x01BF8368       -- 4 Byte je Feld
local FELDER = 80400
local MEMCPY = 0x00582050            -- _HoldStrong::OS::_memcpy (cdecl: dst, src, n)

local SLOTS = 16
local KOPF = 32
local LAYER_BYTES = FELDER * (1 + 2 + 4)
local SLOT = 16 + UNITS_BYTES + ENTITIES_BYTES + BUILDINGS_BYTES + LAYER_BYTES

local ring, memcpy, index = nil, nil, -1

-- B-253 Gegendruck (Daniel 26.10. 21:04, Plan B): waehrend einer Aufnahme haelt das Modul das Spiel an, bevor es Plaetze
-- ueberschreibt, die das Auge noch nicht gelesen hat. Freigabe kommt ueber den Befehlskanal ({"taktring_frei": T} =
-- gelesen bis Takt T), weil das Auge nur liest (B-161). Ohne {"taktring_gegendruck": true} bleibt alles wie vorher.
-- Pausiert wird nur ueber die Spielpause; aufgehoben wird nur eine Pause, die das Modul selbst gesetzt hat.
local PAUSE = 0x1FEA054
local VORLAUF = SLOTS - 2            -- zwei Plaetze Reserve fuer Takte, die im selben Bild noch nachkommen
local gegendruck, frei_bis, eigene_pause = false, 0, false

function M.start()
  if ring ~= nil then return ring end
  ring = core.allocate(KOPF + SLOTS * SLOT)
  memcpy = core.exposeCode(MEMCPY, 3, 0)
  core.writeInteger(ring + 0, 0x54414B54)
  core.writeInteger(ring + 4, SLOTS)
  core.writeInteger(ring + 8, SLOT)
  core.writeInteger(ring + 12, -1)
  core.writeInteger(ring + 16, 0)
  local f = io.open("ucp/villagestudio/taktring.txt", "w")
  if f then f:write(string.format("%d\n", ring)); f:close() end
  log(INFO, string.format("TAKTRING: %d Plaetze a %d Byte ab 0x%X", SLOTS, SLOT, ring))
  return ring
end

function M.tick()
  if ring == nil then M.start() end
  local t = core.readInteger(TICK) or 0
  if t == core.readInteger(ring + 16) then return end       -- derselbe Takt, nichts zu tun
  index = (index + 1) % SLOTS
  local s = ring + KOPF + index * SLOT
  core.writeInteger(s + 0, t)
  core.writeInteger(s + 4, core.readInteger(TICK_KERN) or 0)
  core.writeInteger(s + 8, core.readInteger(UNITS_STATE) or 0)
  core.writeInteger(s + 12, core.readInteger(BUILDINGS_STATE + 8) or 0)
  memcpy(s + 16, UNITS, UNITS_BYTES)
  memcpy(s + 16 + UNITS_BYTES, ENTITIES, ENTITIES_BYTES)
  memcpy(s + 16 + UNITS_BYTES + ENTITIES_BYTES, BUILDINGS, BUILDINGS_BYTES)
  local l = s + 16 + UNITS_BYTES + ENTITIES_BYTES + BUILDINGS_BYTES
  memcpy(l, HEIGHT_LAYER, FELDER)
  memcpy(l + FELDER, BUILDING_LAYER, FELDER * 2)
  memcpy(l + FELDER * 3, LOGIC_LAYER, FELDER * 4)
  core.writeInteger(ring + 12, index)
  core.writeInteger(ring + 16, t)
  if gegendruck and t >= frei_bis and (core.readInteger(PAUSE) or 0) == 0 then
    core.writeInteger(PAUSE, 1)
    eigene_pause = true
  end
end

-- Befehle aus logik.lua: {"taktring_gegendruck": true|false} und {"taktring_frei": <Takt>}
function M.befehl(cmd)
  local t = core.readInteger(TICK) or 0
  if cmd.taktring_gegendruck ~= nil then
    gegendruck = (cmd.taktring_gegendruck == true or cmd.taktring_gegendruck == "an")
    frei_bis = t + VORLAUF
    if not gegendruck and eigene_pause then
      core.writeInteger(PAUSE, 0)
      eigene_pause = false
    end
    log(INFO, string.format("TAKTRING: Gegendruck %s (Takt %d)", gegendruck and "an" or "aus", t))
    return true
  end
  if cmd.taktring_frei ~= nil then
    frei_bis = (tonumber(cmd.taktring_frei) or 0) + VORLAUF
    if eigene_pause and t < frei_bis then
      core.writeInteger(PAUSE, 0)
      eigene_pause = false
    end
    return true
  end
  return false
end

return M
