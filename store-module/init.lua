-- Store candidate: no extraction, disk IPC, persistent state or process spawning.
local ROOT='ucp/modules/selfaware-bridge-0.1.0/'
local REQUEST,REQUEST_CAP=4096,1024*1024
local RESPONSE,RESPONSE_CAP=4096+REQUEST_CAP,32*1024*1024
local before,logic,streams,base,native=nil,nil,nil,nil,nil
local busy,enabled=false,false
local originalLog=log

local function bind(handle,name,count)
  return core.exposeCode(assert(handle:getProcAddress(name),'Missing native export '..name),count,0)
end

local function publishStatus(value)
  local raw=json:encode(value)
  assert(#raw<4032,'Selfaware bridge: status too large')
  local address=assert(native.statusBegin())
  local ok,err=pcall(core.writeString,address,raw)
  native.statusEnd(ok and #raw or 0)
  assert(ok,err)
end

local function logger(level,message)
  local text=tostring(message)
  originalLog(level,text) -- Framework-owned logging, never a module-created file.
  streams.log('[selfaware-runtime]: '..text)
end

local function pump()
  if busy or not enabled then return end
  local sequence=native.pending()
  if sequence==0 then return end
  busy=true
  local success,err=pcall(function()
    local length=core.readInteger(base+24)
    assert(length>0 and length<REQUEST_CAP,'Invalid request length')
    local raw=core.readString(base+REQUEST,length)
    local command=json:decode(raw)
    require('policy').check(command)
    if command.poll~=true then logic.handleCommand(command) end
  end)
  if not success then logger(WARNING,'logik: '..tostring(err)) end
  -- Include bounded kernel diagnostics without opening a separate kernel log.
  for i=1,128 do
    local p=native.nextLog();if p==0 then break end
    logger(INFO,'KERN: '..core.readString(p))
  end
  local raw=streams.drain()
  assert(#raw<RESPONSE_CAP,'Selfaware bridge: reply too large')
  -- Binary frame headers contain NULs. Use the explicit byte API, not C strings.
  for start=1,#raw,4096 do
    core.writeBytes(base+RESPONSE+start-1,{raw:byte(start,math.min(start+4095,#raw))})
  end
  assert(native.reply(#raw,sequence,success and 0 or 1)==1,'Cannot publish bridge reply')
  busy=false
end

local function guarded(callback)
  local ok,err=pcall(callback)
  if not ok then
    enabled=false;busy=false
    if native then pcall(native.close) end
    originalLog(ERROR,'Selfaware memory bridge stopped: '..tostring(err))
  end
end

return {
  enable=function(self,config)
    assert(not enabled,'Selfaware bridge cannot be enabled twice')
    local handle=assert(core.openLibraryHandle(ROOT..'samurai_kern.dll'))
    native={open=bind(handle,'bridge_open',0),ready=bind(handle,'bridge_ready',0),
      pending=bind(handle,'bridge_pending',0),reply=bind(handle,'bridge_reply',3),
      statusBegin=bind(handle,'bridge_status_begin',0),statusEnd=bind(handle,'bridge_status_end',1),
      nextLog=bind(handle,'bridge_log_next',0),close=bind(handle,'bridge_close',0)}
    base=assert(native.open());assert(base~=0,'Cannot allocate volatile bridge')
    streams=require('streams')(ROOT)
    require('starttroops').configure(config or {})
    require('command_owner').install()
    before=require('takeover')(publishStatus)
    -- Load only our own source through UCP's read-only module path.
    local factory=require('game_logic')
    logic=factory({storage=streams,moduleRoot=ROOT,log=logger,nativeHandle=handle,
      handleCommand=function() error('AIV file swapping is unavailable in the Store bridge') end})
    local tickAddress=assert(core.AOBScan('83 3d 24 e4 91 01 00 56 8b f1 c7 05 5c 29',0x400000))
    local frameAddress=assert(core.AOBScan('81 ec f4 07 00 00 a1 20 42 b9 00 33 c4 89 84 24 f0 07',0x400000))
    local tickOriginal
    tickOriginal=core.hookCode(function(this)
      if enabled then guarded(function() before.tick() end) end
      local result=tickOriginal(this)
      if enabled then
        guarded(function() logic.everyTick();pump() end)
      end
      return result
    end,tickAddress,1,1,7)
    local frameOriginal
    frameOriginal=core.hookCode(function(this,a1)
      if enabled then guarded(function() before.tick() end) end
      local result=frameOriginal(this,a1)
      if enabled then
        guarded(function() logic.menuTick();pump() end)
      end
      return result
    end,frameAddress,2,1,6)
    enabled=true;assert(native.ready()==1)
    originalLog(INFO,'Selfaware AI memory bridge ready; external application required')
  end,
  disable=function(self)
    enabled=false;if native then native.close() end
  end,
}
