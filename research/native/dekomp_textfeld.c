// ================= getCurrentText @ 0x004697c0 =================

char * __thiscall _HoldStrong::Text::UserTextHandler::getCurrentText(UserTextHandler *this)

{
  if (DAT_UserTextHandlerState.unknown01 == 0) {
    return (char *)0x0;
  }
  return DAT_UserTextHandlerState.textArray[DAT_UserTextHandlerState.textArrayIndex];
}



// ================= getTextArrayPointer @ 0x004697e0 =================

int __thiscall
_HoldStrong::Text::UserTextHandler::getTextArrayPointer(UserTextHandler *this,int param_1)

{
  return param_1 * 0xfa + 0x1652890;
}



// ================= setTextEntryAndUpdateCursor @ 0x00469800 =================

/* Copies the string param_2 into the text slot at index param_1 in the global text array (base
   0x1652890, stride 250). After copying, computes and stores the string length in
   textContentLengthArray[param_1] and the cursor position in textCursorIndexArray[param_1] (both
   derived from pointer arithmetic on the null terminator). Called when programmatically setting a
   text field's content.
   
   renamed by: Claude Sonnet 4.6 */

void __thiscall
_HoldStrong::Text::UserTextHandler::setTextEntryAndUpdateCursor
          (UserTextHandler *this,int param_1,char *param_2)

{
  char cVar1;
  char *pcVar2;
  
  pcVar2 = param_2;
  do {
    cVar1 = *pcVar2;
    pcVar2[(param_1 * 0xfa + 0x1652890) - (int)param_2] = cVar1;
    pcVar2 = pcVar2 + 1;
  } while (cVar1 != '\0');
  pcVar2 = param_2;
  do {
    cVar1 = *pcVar2;
    pcVar2 = pcVar2 + 1;
  } while (cVar1 != '\0');
  DAT_UserTextHandlerState.textContentLengthArray[param_1] = (int)pcVar2 - (int)(param_2 + 1);
  pcVar2 = param_2 + 1;
  do {
    cVar1 = *param_2;
    param_2 = param_2 + 1;
  } while (cVar1 != '\0');
  DAT_UserTextHandlerState.textCursorIndexArray[param_1] = (int)param_2 - (int)pcVar2;
  return;
}



// ================= resetToTextIndex @ 0x00469790 =================

void __thiscall
_HoldStrong::Text::UserTextHandler::resetToTextIndex
          (UserTextHandler *this,TextArrayIndexTypeInt textIndex)

{
  if ((DAT_UserTextHandlerState.allowUserTextInput == 0) && (textIndex < 0x10)) {
    DAT_UserTextHandlerState.textArrayIndex = textIndex;
    DAT_UserTextHandlerState.textCursorIndexArray[textIndex] = 0;
    DAT_UserTextHandlerState.unknown01 = 1;
    DAT_UserTextHandlerState.returnPressed = 0;
  }
  return;
}



