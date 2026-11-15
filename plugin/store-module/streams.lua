-- Resource payloads in bounded volatile RAM. No io/os/file APIs are used here.
-- Names are protocol keys, not paths opened by the game module.
return function(moduleRoot)
  local records,bytes={},0
  local CAP=32*1024*1024-4096
  local function emit(kind,key,data)
    assert(type(data)=='string' and type(key)=='string','Invalid memory record')
    local record=string.pack('<I1I4I4',kind,#key,#data)..key..data
    assert(bytes+#record<CAP,'Selfaware bridge: volatile response capacity exceeded')
    records[#records+1]=record;bytes=bytes+#record
  end
  local function resource(key)
    key=key:gsub('\\','/')
    assert(key:sub(1,18)=='ucp/villagestudio/','Unknown resource namespace')
    assert(not key:find('%.%.',1) and not key:find(':',1,true) and not key:find('//',1,true),
      'Invalid resource key')
    assert(not key:find('\0',1,true),'Invalid NUL in resource key')
    return key
  end
  return {
    emit=emit,
    log=function(text) emit(1,'',text..'\n') end,
    size=function() return bytes end,
    drain=function()
      local payload=table.concat(records);records={};bytes=0;return payload
    end,
    open=function(key,mode)
      if mode=='r' or mode=='rb' then
        -- The DLL was already opened and verified through UCP's proxy loader.
        if key==moduleRoot..'samurai_kern.dll' then return {close=function() end} end
        return nil
      end
      key=resource(key)
      assert(mode=='w' or mode=='wb' or mode=='a','Unsupported stream mode')
      local parts,size,closed={},0,false
      return {
        write=function(self,...)
          assert(not closed,'Closed memory stream')
          for i=1,select('#',...) do
            local text=tostring(select(i,...));size=size+#text
            assert(size+bytes<CAP,'Selfaware bridge: stream capacity exceeded')
            parts[#parts+1]=text
          end
          return self
        end,
        close=function()
          assert(not closed,'Closed memory stream');closed=true
          emit(mode=='a' and 3 or 2,key,table.concat(parts));parts={}
          return true
        end,
      }
    end,
  }
end
