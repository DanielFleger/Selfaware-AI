-- Called BEFORE processGameTick. Native placeholder AI never gets its first turn.
-- B-280 (Daniel 28.10.2026 00:26/00:39: Neustart im Spiel gab andere Starteinheiten, ein geladener Spielstand endete sofort in
-- "Niederlage"): die Uebernahme gilt jetzt auch nach Neustart und Laden.
--  * Solange eine Uebernahme gilt, wird ein Platzhalter, der wieder KI 16 hat (die Wache stellt ihn in der Pause zurueck, damit
--    Spielstand und Neustart den echten SamurAI-Platz sehen), vor jedem Takt wieder abgeschaltet und als lebend markiert.
--  * Springt der Spieltakt zurueck (Neustart, Laden), ist das eine neue Partie: neuer Eintrag mit neuer Folge-Nummer, die Wache
--    startet daran einen neuen Lenker.
--  * Ein geladener Spielstand (erster Takt > LADEN_AB) mit einem Platz ohne KI, der in einer frueheren Partie unserer war
--    (Datei PLAETZE), wird wieder uebernommen - sonst hat der Platz weder KI noch Menschen und scheidet nach 3 Takten aus.
local active=false
local abi=require('engine_contract')
local sequence=0
local saved={}
local original={}
local last_t=nil
local PATH='ucp/villagestudio/uebernahme.json'
local PLAETZE='ucp/villagestudio/samurai_plaetze.json'
local LADEN_AB=100
local function save(value)
  local f=assert(io.open(PATH,'w'))
  f:write(json:encode(value));f:close()
end
local function remember()
  local f=io.open(PLAETZE,'w')
  if not f then return end
  local list={}
  for sp,old in pairs(saved) do list[#list+1]={sp=sp,ai=old.ai,kind=old.kind,full=old.full} end
  f:write(json:encode({plaetze=list}));f:close()
end
local function remembered()
  local f=io.open(PLAETZE,'r')
  if not f then return {} end
  local text=f:read('*a');f:close()
  local ok,value=pcall(function() return json:decode(text) end)
  if not ok or type(value)~='table' or type(value.plaetze)~='table' then return {} end
  return value.plaetze
end
local function mark(sp)
  -- Mark alive before disabling AI, preserving the native defeat contract.
  core.writeInteger(abi.fullID+sp*4,1)
  core.writeInteger(abi.playerData+sp*abi.playerStride+abi.aiType,0)
  core.writeInteger(abi.currentAI+sp*4,0)
end
local function record(t,reason)
  local slots={}
  for sp,_ in pairs(saved) do slots[#slots+1]=sp end
  table.sort(slots)
  local values={}
  for sp,old in pairs(saved) do values[tostring(sp)]={ai=old.ai,kind=old.kind,full=old.full} end
  active=true;sequence=sequence+1
  save({active=true,sequence=sequence,tick=t,original_ai=original,slots=slots,saved=values,reason=reason})
  log(INFO,'Selfaware AI: native takeover ('..reason..') BEFORE game tick '..t..'; slots '..table.concat(slots,','))
end
save({active=false}) -- never reuse a record from another game process
return {
  tick=function()
    local view=core.readInteger(0x01FE7D1C)
    if view~=14 and view~=16 then
      if active then
        for sp,old in pairs(saved) do
          if core.readInteger(abi.currentAI+sp*4)==0 then
            core.writeInteger(abi.currentAI+sp*4,old.ai)
            -- B-280: aus samurai_plaetze.json koennen Typ/Mensch fehlen (Spielstand von vor B-280) - dann nur die KI-Nummer
            if old.kind~=nil then core.writeInteger(abi.playerData+sp*abi.playerStride+abi.aiType,old.kind) end
            if old.full~=nil then core.writeInteger(abi.fullID+sp*4,old.full) end
          end
        end
        saved={};active=false;save({active=false})
      end
      last_t=nil
      return
    end
    if core.readInteger(0x0117D500)~=0 then return end
    local t=core.readInteger(0x0117CADC)
    local new_game=last_t~=nil and t<last_t
    last_t=t
    if active then
      local back=false
      for sp,_ in pairs(saved) do
        if core.readInteger(abi.currentAI+sp*4)~=0 then mark(sp);back=true end
      end
      if new_game then
        for sp,_ in pairs(saved) do mark(sp) end
        record(t,'Takt sprang zurueck - Neustart oder Laden')
      elseif back then
        log(INFO,'Selfaware AI: placeholder AI restored during pause, disabled again before tick '..t)
      end
      return
    end
    original={}
    local slots=0
    for sp=1,8 do
      local ai=core.readInteger(abi.currentAI+sp*4)
      original[tostring(sp)]=ai
      if ai==16 then
        saved[sp]={ai=ai,kind=core.readInteger(abi.playerData+sp*abi.playerStride+abi.aiType),
          full=core.readInteger(abi.fullID+sp*4)}
        mark(sp)
        slots=slots+1
      end
    end
    if slots==0 and t>LADEN_AB then
      for _,p in ipairs(remembered()) do
        local sp=tonumber(p.sp)
        if sp and core.readInteger(abi.currentAI+sp*4)==0 then
          saved[sp]={ai=p.ai,kind=p.kind,full=p.full}
          original[tostring(sp)]=p.ai
          mark(sp)
          slots=slots+1
        end
      end
      if slots>0 then record(t,'geladener Spielstand, Platz aus frueherer Partie');return end
    end
    if slots==0 then return end -- arrays may not be initialized yet
    remember()
    record(t,'Partiestart')
  end,
}
