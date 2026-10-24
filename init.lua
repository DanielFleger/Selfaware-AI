-- Trusted module entry point. The Store signs the complete runtime archive.
local ROOT = 'ucp/modules/selfaware-runtime-0.1.0/'
local launcher = nil
local bridge = nil

local function copyFile(name)
  local source = assert(io.open(ROOT .. name, 'rb'))
  local target = assert(io.open('ucp/villagestudio/' .. name, 'wb'))
  while true do
    local block = source:read(1048576)
    if not block then break end
    target:write(block)
  end
  source:close()
  target:close()
end

return {
  enable = function(self, config)
    launcher = assert(core.openLibraryHandle(ROOT .. 'sai_launcher.dll'))
    local prepare = core.exposeCode(launcher:getProcAddress('sai_prepare'), 0, 0)
    assert(prepare() == 1, 'Selfaware AI: runtime directory is not writable')
    copyFile('runtime.zip')
    copyFile('bootstrap.ps1')
    local command = assert(io.open('ucp/villagestudio/befehl.json', 'w'))
    command:write('{}'); command:close()
    -- The deployed logic is part of the verified module, not an editable repo path.
    bridge = require('bridge')
    bridge:enable(config)
    local start = core.exposeCode(launcher:getProcAddress('sai_start'), 0, 0)
    assert(start() == 1, 'Selfaware AI: could not start autonomous controller')
    log(INFO, 'Selfaware AI: autonomous runtime launch requested; see Local AppData/Selfaware AI/start.log for readiness')
  end,
  disable = function(self, config)
    if bridge then bridge:disable(config) end
  end,
}
