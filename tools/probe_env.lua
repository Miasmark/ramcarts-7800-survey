-- probe_env.lua: print what this MAME exposes (devices, spaces, ports, cpu state), then exit.
local M = manager.machine
local out = io.open("env.txt", "w")
for tag, dev in pairs(M.devices) do
  local sp = {}
  for name, _ in pairs(dev.spaces) do sp[#sp + 1] = name end
  out:write(string.format("dev %s spaces: %s\n", tag, table.concat(sp, ",")))
end
for tag, port in pairs(M.ioport.ports) do
  local fl = {}
  for name, _ in pairs(port.fields) do fl[#fl + 1] = name end
  out:write(string.format("port %s fields: %s\n", tag, table.concat(fl, " | ")))
end
local cpu = M.devices[":maincpu"]
for k, _ in pairs(cpu.state) do out:write("state " .. k .. "\n") end
for _, s in pairs(M.screens) do
  out:write(string.format("screen w %d h %d vpos? %s\n", s.width, s.height, tostring(s.vpos ~= nil)))
end
local n = 0
ENVF = emu.register_frame_done(function()
  n = n + 1
  if n == 3 then out:close(); M:exit() end
end)
