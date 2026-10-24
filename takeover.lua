-- Called BEFORE processGameTick. Native placeholder AI never gets its first turn.
local active=false
local sequence=0
local saved={}
local PATH='ucp/villagestudio/uebernahme.json'
local function save(value)
  local f=assert(io.open(PATH,'w'))
  f:write(json:encode(value));f:close()
end
save({active=false}) -- never reuse a record from another game process
return {
  tick=function()
    local view=core.readInteger(0x01FE7D1C)
    if view~=14 and view~=16 then
      if active then
        for sp,old in pairs(saved) do
          if core.readInteger(0x0191DE7C+sp*4)==0 then
            core.writeInteger(0x0191DE7C+sp*4,old.ai)
            core.writeInteger(0x0115BDF8+sp*0x39F4+0x2300,old.kind)
            core.writeInteger(0x0191DE10+sp*4,old.full)
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
      local ai=core.readInteger(0x0191DE7C+sp*4)
      original[tostring(sp)]=ai
      if ai==16 then
        saved[sp]={ai=ai,kind=core.readInteger(0x0115BDF8+sp*0x39F4+0x2300),
          full=core.readInteger(0x0191DE10+sp*4)}
        -- Mark alive before disabling AI, preserving the native defeat contract.
        core.writeInteger(0x0191DE10+sp*4,1)
        core.writeInteger(0x0115BDF8+sp*0x39F4+0x2300,0)
        core.writeInteger(0x0191DE7C+sp*4,0)
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
