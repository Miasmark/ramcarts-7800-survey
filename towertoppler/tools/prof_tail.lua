-- prof.lua (Tower Toppler): cycles per frame by main-loop routine. Built from the toolkit's
-- cyclebudget.lua (its opcode tables are above this text); see mkprof.py.
--   SCRIPT, POKES  as survey.lua (input script, pokes)
--   FROM, END      frames logged
--   TOPLO, TOPHI   hex PC range of the main loop's body (default FCBC-FD52): a fetch inside it
--                  names the routine about to be called; cycles are charged to that name
--   WAITLO, WAITHI hex PC range of the vblank wait (default FD94-FD9B), charged to "w<name>"
-- Output prof.txt, one line per frame:
--   f N exec E nmi M dma D wsync COUNT/CYCLES | name:cycles ... (in order of first appearance in the frame)
-- NMI entry is the fetch at $FE6C (JMP ($0060)); it ends at the RTI that pops that frame.
local P = MACHINE.ioport.ports
local function fld(n)
  for _, t in ipairs({":JOYSTICKS", ":BUTTONS", ":CONSOLE"}) do
    local f = P[t] and P[t].fields[n]
    if f then return f end
  end
end
local stick = {l = fld("P1 Left"), r = fld("P1 Right"), u = fld("P1 Up"), d = fld("P1 Down")}
local fire, fire2 = fld("P1 Button 1"), fld("P1 Button 2")
local steps = {}
for n, s, b in string.gmatch(os.getenv("SCRIPT") or "600:-:0", "(%d+):([lrud%-]+):(%d+)") do
  steps[#steps + 1] = {tonumber(n), s, tonumber(b)}
end
local pokes = {}
for fr, list in string.gmatch(os.getenv("POKES") or "", "(%d+):([^;]+)") do
  local t = pokes[tonumber(fr)] or {}
  for ad, val in string.gmatch(list, "(%x+)=(%x+)") do t[#t + 1] = {tonumber(ad, 16), tonumber(val, 16)} end
  pokes[tonumber(fr)] = t
end
local FROM = tonumber(os.getenv("FROM") or "0")
local END = tonumber(os.getenv("END") or "600")
local TOPLO = tonumber(os.getenv("TOPLO") or "FCBC", 16)
local TOPHI = tonumber(os.getenv("TOPHI") or "FD52", 16)
local WAITLO = tonumber(os.getenv("WAITLO") or "FD94", 16)
local WAITHI = tonumber(os.getenv("WAITHI") or "FD9B", 16)
local FRAME = 29850.5
local NMI = 0xFE6C

local function r(a) return mem:read_u8(a & 0xFFFF) end
local executed, innmi, slow, f = 0, 0, 0, 0
local lastpc, lastop = -1, 0
local in_nmi, nmi_sp = false, 0
local reading = false
local cur = 0
local buck, order = {}, {}
local function add(k, c)
  if not buck[k] then buck[k] = 0; order[#order + 1] = k end
  buck[k] = buck[k] + c
end

local wsync_t, wsync_cyc, wsyncs = nil, 0, 0
TAPS = {}
TAPS[6] = mem:install_write_tap(0x24, 0x24, "cb-wsync", function(a, d)
  wsync_t = emu.time(); wsyncs = wsyncs + 1
  return d
end)
TAPS[1] = mem:install_read_tap(0x0000, 0xFFFF, "cb-fetch", function(a, d)
  if reading or a ~= PCs.value then return d end
  local cost = 0
  if wsync_t then
    wsync_cyc = wsync_cyc + (emu.time() - wsync_t) * 1789772.5
    wsync_t = nil
  end
  if lastpc >= 0 and MODE[lastop + 1] == "rel" and a ~= ((lastpc + 2) & 0xFFFF) then
    cost = cost + 1
    if (a & 0xFF00) ~= ((lastpc + 2) & 0xFF00) then cost = cost + 1 end
  end
  if a == NMI and not in_nmi then
    in_nmi, nmi_sp = true, SPs.value & 0xFF
    cost = cost + 7
  end
  cost = cost + CYC[d + 1]
  if PEN[d + 1] == 1 then
    reading = true
    local m, base, idx = MODE[d + 1], 0, 0
    if m == "abx" or m == "aby" then
      base = r(a + 1) | (r(a + 2) << 8)
      idx = (m == "abx") and Xs.value or Ys.value
    elseif m == "izy" then
      local z = r(a + 1)
      base = r(z) | (r((z + 1) & 0xFF) << 8)
      idx = Ys.value
    end
    reading = false
    if ((base + idx) & 0xFF00) ~= (base & 0xFF00) then cost = cost + 1 end
  end
  executed = executed + cost
  if in_nmi then
    innmi = innmi + cost
    if d == 0x40 and (SPs.value & 0xFF) == nmi_sp then in_nmi = false end
  else
    if a >= TOPLO and a <= TOPHI then cur = a end
    if a >= WAITLO and a <= WAITHI then
      add(string.format("w%04X", cur), cost)
    else
      add(string.format("%04X", cur), cost)
    end
  end
  lastpc, lastop = a, d
  return d
end)
local function slowtap(a, d) slow = slow + 0.5 return d end
TAPS[2] = mem:install_read_tap(0x0000, 0x001F, "cb-slow1", slowtap)
TAPS[3] = mem:install_write_tap(0x0000, 0x001F, "cb-slow2", slowtap)
TAPS[4] = mem:install_read_tap(0x0280, 0x02FF, "cb-slow3", slowtap)
TAPS[5] = mem:install_write_tap(0x0280, 0x02FF, "cb-slow4", slowtap)

local o = io.open("prof.txt", "w")
STOPCB = emu.add_machine_stop_notifier(function() pcall(function() o:close() end) end)
FRAMECB = emu.register_frame_done(function()
  if f >= FROM then
    local parts = {}
    for _, k in ipairs(order) do parts[#parts + 1] = k .. ":" .. buck[k] end
    o:write(string.format("f %d exec %d nmi %d dma %.0f wsync %d/%.0f | %s\n", f, executed, innmi,
                          FRAME - executed - slow - wsync_cyc, wsyncs, wsync_cyc, table.concat(parts, " ")))
  end
  executed, innmi, slow = 0, 0, 0
  wsync_cyc, wsyncs = 0, 0
  buck, order = {}, {}
  f = f + 1
  local t, c = f, nil
  for _, st in ipairs(steps) do
    if t <= st[1] then c = st break end
    t = t - st[1]
  end
  for k, fl in pairs(stick) do fl:set_value((c and c[2]:find(k)) and 1 or 0) end
  fire:set_value((c and c[3] % 2 == 1) and 1 or 0)
  fire2:set_value((c and math.floor(c[3] / 2) % 2 == 1) and 1 or 0)
  local p = pokes[f]
  if p then for _, w in ipairs(p) do mem:write_u8(w[1], w[2]) end end
  if f >= END then MACHINE:exit() end
end)
