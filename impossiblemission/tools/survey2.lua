-- survey2.lua (Impossible Mission): survey.lua with bank-tagged PCs (bank digit, then the PC: 4A92C = bank 4 $A92C,
-- 7xxxx = fixed bank) and a write tap on console RAM $1800-$27FF (conw.txt).
-- survey.lua: the live survey of a cart with RAM at $4000-$7FFF. Windowless run; writes into the cwd.
--   SCRIPT  "frames:stick:button;..." stick letters l r u d or -, button 0/1/2/3 (+4 pause, +8 select, +16 reset)
--   SNAPS   "a,b,c" frames: screenshot + memory dump mem_fNNNNN.bin ($0000-$7FFF, registers read as 0)
--           + regs_fNNNNN.txt (DPP, CTRL, CHARBASE, palettes, bank: the last values written)
--   END     frame to exit on (default: end of script)
--   POKES   "frame:addr=val,addr=val;..." hex addr/val
-- Output:
--   cpuw.txt   per frame with writes to $4000-$7FFF: frame total | pc:count:lo-hi ...
--   cpur.txt   the same for CPU reads of $4000-$7FFF
--   mariar.txt per frame with MARIA (dma space) reads of $4000-$7FFF: frame total | page:count ...
--   regs.txt   CTRL/CHARBASE/DPPH/DPPL writes of a frame as "reg=val@line(pc)", only when the
--              frame's sequence differs from the previous frame's
--   bank.txt   bank-register writes ($8000-$FFFF) of a frame as "val@line(pc)", only when changed
--   summary.txt at the end: per PC totals (writes, reads), MARIA pages, PCs seen inside cart RAM
local M = manager.machine
local cpu = M.devices[":maincpu"]
local mem = cpu.spaces["program"]
local dma = M.devices[":maria"].spaces["dma"]
local P = M.ioport.ports
local scr
for _, s in pairs(M.screens) do scr = s break end

local function fld(n)
  for _, t in ipairs({":JOYSTICKS", ":BUTTONS", ":CONSOLE"}) do
    local f = P[t] and P[t].fields[n]
    if f then return f end
  end
end
local stick = {l = fld("P1 Left"), r = fld("P1 Right"), u = fld("P1 Up"), d = fld("P1 Down")}
local fire, fire2 = fld("P1 Button 1"), fld("P1 Button 2")
local pause, select, reset = fld("Pause"), fld("Select"), fld("Reset")
local steps = {}
for n, s, b in string.gmatch(os.getenv("SCRIPT") or "600:-:0", "(%d+):([lrud%-]+):(%d+)") do
  steps[#steps + 1] = {tonumber(n), s, tonumber(b)}
end
local total = 0
for _, s in ipairs(steps) do total = total + s[1] end
local snaps = {}
for w in string.gmatch(os.getenv("SNAPS") or "", "%d+") do snaps[tonumber(w)] = true end
local END = tonumber(os.getenv("END") or tostring(total))
local pokes = {}
for fr, list in string.gmatch(os.getenv("POKES") or "", "(%d+):([^;]+)") do
  local t = pokes[tonumber(fr)] or {}
  for ad, val in string.gmatch(list, "(%x+)=(%x+)") do t[#t + 1] = {tonumber(ad, 16), tonumber(val, 16)} end
  pokes[tonumber(fr)] = t
end

local bank = -1
local function PC()
  local pc = cpu.state["CURPC"].value
  if pc >= 0xC000 then return 0x70000 + pc end
  if pc >= 0x8000 then return ((bank >= 0 and bank or 0) % 8) * 0x10000 + pc end
  return pc
end
local function line()
  local lines = scr.frame_period / scr.scan_period
  local left = scr:time_until_pos(0, 0) / scr.scan_period
  return math.floor((lines - left) % lines)
end

local f = 0
local fw, fr, fm = {}, {}, {}          -- this frame: pc -> {count, lo, hi}; page -> count
local nw, nr, nm = 0, 0, 0
local tw, tr, tm = {}, {}, {}          -- totals
local ramexec = {}
local reglast = {}                     -- last value written to each MARIA register
local regseq, bankseq = {}, {}
local lastreg, lastbank = "", ""
local ow = io.open("cpuw.txt", "w")
local orr = io.open("cpur.txt", "w")
local om = io.open("mariar.txt", "w")
local oreg = io.open("regs.txt", "w")
local obank = io.open("bank.txt", "w")

local function note(tbl, tot, pc, a)
  local e = tbl[pc]
  if not e then e = {0, a, a}; tbl[pc] = e end
  e[1] = e[1] + 1
  if a < e[2] then e[2] = a end
  if a > e[3] then e[3] = a end
  local t = tot[pc]
  if not t then t = {0, a, a, f, f, 0}; tot[pc] = t end
  t[1] = t[1] + 1
  if a < t[2] then t[2] = a end
  if a > t[3] then t[3] = a end
  if t[5] ~= f or t[6] == 0 then t[6] = t[6] + 1 end
  t[5] = f
end

TAP_W = mem:install_write_tap(0x4000, 0x7FFF, "sv_w", function(a, d)
  local pc = PC()
  note(fw, tw, pc, a); nw = nw + 1
  if pc >= 0x4000 and pc < 0x8000 then ramexec[pc] = (ramexec[pc] or 0) + 1 end
  return d
end)
local fc, tc, nc = {}, {}, 0
TAP_C = mem:install_write_tap(0x1800, 0x27FF, "sv_c", function(a, d)
  local pc = PC()
  note(fc, tc, pc, a); nc = nc + 1
  return d
end)
local oc = io.open("conw.txt", "w")
local dumping = false
TAP_R = mem:install_read_tap(0x4000, 0x7FFF, "sv_r", function(a, d)
  if dumping then return d end
  local pc = PC()
  note(fr, tr, pc, a); nr = nr + 1
  if pc >= 0x4000 and pc < 0x8000 then ramexec[pc] = (ramexec[pc] or 0) + 1 end
  return d
end)
TAP_M = dma:install_read_tap(0x4000, 0x7FFF, "sv_m", function(a, d)
  local pg = a >> 8
  fm[pg] = (fm[pg] or 0) + 1; nm = nm + 1
  tm[pg] = (tm[pg] or 0) + 1
  return d
end)
TAP_REG = mem:install_write_tap(0x20, 0x3F, "sv_reg", function(a, d)
  reglast[a] = d
  if a == 0x3C or a == 0x34 or a == 0x2C or a == 0x30 then
    local pc = cpu.state["CURPC"].value
    if pc >= 0x4000 and pc < 0x8000 then ramexec[pc] = (ramexec[pc] or 0) + 1 end
    regseq[#regseq + 1] = string.format("%02X=%02X@%d(%05X)", a, d, line(), PC())
  end
  return d
end)
TAP_BANK = mem:install_write_tap(0x8000, 0xFFFF, "sv_bank", function(a, d)
  bank = d
  bankseq[#bankseq + 1] = string.format("%02X@%d(%05X)", d, line(), PC())
  return d
end)

local function flush(o, tbl, n, fmtkey)
  if n == 0 then return end
  local keys = {}
  for k, _ in pairs(tbl) do keys[#keys + 1] = k end
  table.sort(keys)
  local parts = {}
  for _, k in ipairs(keys) do
    local e = tbl[k]
    if type(e) == "table" then
      parts[#parts + 1] = string.format("%05X:%d:%04X-%04X", k, e[1], e[2], e[3])
    else
      parts[#parts + 1] = string.format("%02X:%d", k, e)
    end
  end
  o:write(string.format("%d %d | %s\n", f, n, table.concat(parts, " ")))
end

local function dump()
  local name = string.format("mem_f%05d.bin", f)
  local o = io.open(name, "wb")
  local buf = {}
  dumping = true
  for a = 0, 0x7FFF do
    local v = 0
    if (a >= 0x40 and a < 0x100) or (a >= 0x140 and a < 0x200) or (a >= 0x1800 and a < 0x2800) or a >= 0x4000 then
      v = mem:read_u8(a)
    end
    buf[#buf + 1] = string.char(v)
    if #buf == 4096 then o:write(table.concat(buf)); buf = {} end
  end
  o:write(table.concat(buf)); o:close()
  dumping = false
  local t = io.open(string.format("regs_f%05d.txt", f), "w")
  t:write(string.format("frame %d bank %d pc %04X\n", f, bank, cpu.state["CURPC"].value))
  for a = 0x20, 0x3F do t:write(string.format("%02X %s\n", a, reglast[a] and string.format("%02X", reglast[a]) or "--")) end
  t:close()
end

FRAME_CB = emu.register_frame_done(function()
  -- close the frame that just ended (frame number f)
  flush(ow, fw, nw); flush(orr, fr, nr); flush(om, fm, nm); flush(oc, fc, nc)
  fw, fr, fm, fc = {}, {}, {}, {}; nw, nr, nm, nc = 0, 0, 0, 0
  local s = table.concat(regseq, " ")
  if s ~= lastreg then oreg:write(string.format("%d %s\n", f, s)); lastreg = s end
  s = table.concat(bankseq, " ")
  if s ~= lastbank then obank:write(string.format("%d %s\n", f, s)); lastbank = s end
  regseq, bankseq = {}, {}
  local pc = cpu.state["CURPC"].value
  if pc >= 0x4000 and pc < 0x8000 then ramexec[pc] = (ramexec[pc] or 0) + 1 end
  f = f + 1
  local t, cur = f, nil
  for _, st in ipairs(steps) do
    if t <= st[1] then cur = st break end
    t = t - st[1]
  end
  for k, fl in pairs(stick) do fl:set_value((cur and cur[2]:find(k)) and 1 or 0) end
  fire:set_value((cur and cur[3] % 2 == 1) and 1 or 0)
  fire2:set_value((cur and math.floor(cur[3] / 2) % 2 == 1) and 1 or 0)
  pause:set_value((cur and cur[3] % 8 >= 4) and 1 or 0)
  select:set_value((cur and cur[3] % 16 >= 8) and 1 or 0)
  reset:set_value((cur and cur[3] >= 16) and 1 or 0)
  local p = pokes[f]
  if p then for _, w in ipairs(p) do mem:write_u8(w[1], w[2]) end end
  if snaps[f] then M.video:snapshot(); dump() end
  if f >= END then M:exit() end
end)

local function summary()
  local o = io.open("summary.txt", "w")
  local function sect(title, tot)
    o:write(title .. "\n")
    local keys = {}
    for k, _ in pairs(tot) do keys[#keys + 1] = k end
    table.sort(keys, function(a, b) return tot[a][1] > tot[b][1] end)
    for _, k in ipairs(keys) do
      local t = tot[k]
      o:write(string.format("  pc %05X  n %8d  addr %04X-%04X  frames %d-%d (%d frames)\n", k, t[1], t[2], t[3], t[4], t[5], t[6]))
    end
  end
  sect("CPU writes to $4000-$7FFF by PC", tw)
  sect("CPU reads of $4000-$7FFF by PC", tr)
  sect("CPU writes to $1800-$27FF by PC", tc)
  o:write("MARIA reads of $4000-$7FFF by page\n")
  for pg = 0x40, 0x7F do if tm[pg] then o:write(string.format("  %02X00  %d\n", pg, tm[pg])) end end
  o:write("PCs seen inside $4000-$7FFF (code run from cart RAM)\n")
  for pc, n in pairs(ramexec) do o:write(string.format("  %04X %d\n", pc, n)) end
  o:write(string.format("frames %d\n", f))
  o:close(); ow:close(); orr:close(); om:close(); oreg:close(); obank:close(); oc:close()
end
STOP_CB = emu.add_machine_stop_notifier(summary)
