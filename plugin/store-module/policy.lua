-- Validate the entire transaction before executing any nested/deferred command.
-- The Store bridge exposes game decisions, never screenshots, disk operations,
-- dynamic DLL replacement, or desktop/window control.
local forbidden={foto=true,bild=true,autobild=true,datei=true,laden=true,
  fenster=true,hinten=true,leiste=true,kamera=true,zoom=true,beenden=true,file=true}
local function check(value,depth)
  assert(depth<32,'Selfaware bridge: command nesting exceeds limit')
  if type(value)~='table' then return end
  for key,child in pairs(value) do
    assert(not forbidden[key],'Selfaware bridge: unsupported external operation '..tostring(key))
    if key=='knopf' and type(child)=='string' then
      local name=child:lower()
      assert(not name:find('save') and not name:find('load') and not name:find('screenshot'),
        'Selfaware bridge: file/menu operation is unavailable')
    end
    if type(child)=='table' then check(child,depth+1) end
  end
end
return {check=function(command) return check(command,0) end}
