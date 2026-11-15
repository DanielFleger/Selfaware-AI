-- LOCAL DEVELOPMENT BRIDGE, not a Store-compatible module.
-- Runtime setup, process launch and learning state belong to the external app.
local bridge = nil

return {
  enable = function(self, config)
    require('starttroops').configure(config or {})
    require('command_owner').install()
    bridge = require('bridge')
    bridge:setBeforeTick(require('takeover').tick)
    bridge:enable(config)
    log(INFO, 'Selfaware AI local development bridge ready; runtime is managed by the external starter')
  end,
  disable = function(self, config)
    if bridge then bridge:disable(config) end
  end,
}
