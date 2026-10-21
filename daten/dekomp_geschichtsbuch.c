##### PrepareHistoryBook @ 0x004db210

/* decompilerscript: committed: 2025-01-30 21:57:43.216000 */

int __cdecl _HoldStrong::Global::PrepareHistoryBook(void)

{
  int iVar1;
  uint uVar2;
  int *piVar3;
  int *piVar4;
  
  DAT_TextureRenderCoreObject.totalLoadedGfx = 0;
  UI::Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"sand.tgx");
  UI::Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"pc0.tgx");
  UI::Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"pc1.tgx");
  UI::Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"pc2.tgx");
  UI::Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"pc3.tgx");
  UI::Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"pc4.tgx");
  UI::Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"pc5.tgx");
  UI::Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"pc6.tgx");
  UI::Rendering::TextureRenderCore::loadGfxFile(&DAT_TextureRenderCoreObject,"pc7.tgx");
  piVar3 = INT_ARRAY_ARRAY_00eb0b28[0] + 1;
  do {
    iVar1 = OS::_rand();
    (*(int (*) [4])(piVar3 + -1))[0] = iVar1 % 900 << 8;
    iVar1 = OS::_rand();
    *piVar3 = iVar1 % 600 << 8;
    uVar2 = OS::_rand();
    uVar2 = uVar2 & 0x80000007;
    if ((int)uVar2 < 0) {
      uVar2 = (uVar2 - 1 | 0xfffffff8) + 1;
    }
    piVar3[1] = uVar2;
    iVar1 = OS::_rand();
    piVar4 = piVar3 + 4;
    piVar3[2] = iVar1 % 10 + 10;
    piVar3 = piVar4;
  } while ((int)piVar4 < 0xeb0e2c);
  return iVar1 / 10;
}


