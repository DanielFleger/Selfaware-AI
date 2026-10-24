-- Resolve our tagged sender before native sorting, not only at execution.
-- Native getCommandIDFromCommandSelectionStuff rejects neutral player zero.
-- Contract: daten/dekomp_absender.c, translateMultiplayerIDsIntoPlayerIDs.
local original
return {
  install=function()
    local address=0x0047EAF0
    for i,v in ipairs({0x8B,0x91,0x18,0x06,0x00,0x00}) do
      assert(core.readByte(address+i-1)==v,'Selfaware AI: unexpected sender translator')
    end
    original=core.hookCode(function(this,id)
      if (id & 0xFFFFFF00)==0x53414D00 then
        local owner=id & 0xFF
        if owner>=1 and owner<=8 then return owner end
      end
      return original(this,id)
    end,address,2,1,6)
  end,
}
