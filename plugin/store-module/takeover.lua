-- Shared takeover semantics, injected volatile status writer.
return function(save)
-- Called BEFORE processGameTick. Native placeholder AI never gets its first turn.
local active=false
local abi=require('engine_contract')
local sequence=0
local saved={}
save({active=false}) -- never reuse a record from another game process
return {
  tick=function()
    local view=core.readInteger(0x01FE7D1C)
    if view~=14 and view~=16 then
      if active then
        for sp,old in pairs(saved) do
          if core.readInteger(abi.currentAI+sp*4)==0 then
            core.writeInteger(abi.currentAI+sp*4,old.ai)
            core.writeInteger(abi.playerData+sp*abi.playerStride+abi.aiType,old.kind)
            core.writeInteger(abi.fullID+sp*4,old.full)
          end
        end
        saved={};active=false;save({active=false})
      end
      return
    end
    if core.readInteger(0x0117D500)~=0 then return end
    if active then return end
    local original,slots={},{}
    for sp=1,8 do
      local ai=core.readInteger(abi.currentAI+sp*4)
      original[tostring(sp)]=ai
      if ai==16 then
        saved[sp]={ai=ai,kind=core.readInteger(abi.playerData+sp*abi.playerStride+abi.aiType),
          full=core.readInteger(abi.fullID+sp*4)}
        -- Mark alive before disabling AI, preserving the native defeat contract.
        core.writeInteger(abi.fullID+sp*4,1)
        core.writeInteger(abi.playerData+sp*abi.playerStride+abi.aiType,0)
        core.writeInteger(abi.currentAI+sp*4,0)
        slots[#slots+1]=sp
      end
    end
    if #slots==0 then return end -- arrays may not be initialized yet
    active=true;sequence=sequence+1
    local t=core.readInteger(0x0117CADC)
    save({active=true,sequence=sequence,tick=t,original_ai=original,slots=slots})
    log(INFO,'Selfaware AI: native takeover BEFORE game tick '..t..'; slots '..table.concat(slots,','))
  end,
}

end
