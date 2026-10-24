-- Native start table contract from aiSwapper 1.3.0 scripts/troops.lua.
-- Only SamurAI's packaged Abbot slot is replaced; other lords keep their troops.
local kinds = {'EuropArcher','Crossbowman','Spearman','Pikeman','Maceman',
  'Swordsman','Knight','Unknown','Engineer','Monk','ArabArcher','Slave',
  'Slinger','Assassin','HorseArcher','ArabSwordsman','FireThrower','FireBallista'}
local defaults = {Assassin=4, ArabArcher=6}
return {
  configure = function(config)
    local values, total = {}, 0
    for i,name in ipairs(kinds) do
      local n = (config.startTroops or {})[name]
      if n == nil then n = defaults[name] or 0 end
      assert(type(n)=='number' and n==math.floor(n) and n>=0 and n<=100,
        'Selfaware AI: invalid start troop count for '..name)
      assert(name~='Unknown' or n==0,'Selfaware AI: Unknown troop is unsupported')
      values[i]=n; total=total+n
    end
    assert(total<=100,'Selfaware AI: at most 100 starting troops')
    local signature=assert(core.AOBScan('8d bf ? ? ? ? c7 44 24 1c 14',0x400000),
      'Selfaware AI: native starting troop table not found')
    local base=core.readInteger(signature+2)+0x140
    for mode=0,2 do
      local address=base+(15*60+mode*20)*4
      for i=0,19 do core.writeInteger(address+i*4,values[i+1] or 0) end
    end
    log(INFO,'Selfaware AI: starting troops set for Abbot slot; total '..total)
  end,
}
