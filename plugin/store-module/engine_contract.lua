-- OpenSHC source contract, pinned reference 9007b1dabea103650a4832be364cfd42cce1e98e.
-- Synchrony/GameSynchronyState.hpp and Game/Player/PlayerData.hpp.
-- Local SHC 1.41 ABI only. The legacy bridge still has addresses to migrate.
local synchrony=0x0191D768
return {
  currentAI=synchrony+0x714,
  fullID=synchrony+0x6A8,
  localSlot=synchrony+0x109E74,
  playerData=0x0115BDF8,
  playerStride=0x39F4,
  aiType=0x2300,
  senderTranslatorPattern='8b 91 18 06 00 00 33 c0 85 d2 75 09 8b 81 74 9e 10 00 c2 04 00 83 fa 63',
}
