from unicorn import *
from unicorn.x86_const import *
from capstone import *
from keystone import *
import os
import json
import random
import sys

cs = Cs(CS_ARCH_X86, CS_MODE_32)
uc = Uc(UC_ARCH_X86, UC_MODE_32)
ks = Ks(KS_ARCH_X86, KC_MODE_32)

MEM_INPUT  = 0x10000
MEM_OUTPUT = 0x20000
MEM_CODE   = 0x30000
MEM_STACK  = 0x40000

MAGIC_RET = 0x41414141

ZERO_PAGE = "\0" * 0x1000

uc.mem_map(MEM_INPUT, 0x1000, UC_PROT_READ)
uc.mem_map(MEM_OUTPUT, 0x1000, UC_PROT_READ | UC_PROT_WRITE)
uc.mem_map(MEM_CODE, 0x1000, UC_PROT_READ | UC_PROT_EXEC)
uc.mem_map(MEM_STACK, 0x1000, UC_PROT_READ | UC_PROT_WRITE)

def grade(code, test):
  uc = Uc(UC_ARCH_X86, UC_MODE_32)
  uc.mem_map(MEM_INPUT, 0x1000, UC_PROT_READ)
  uc.mem_map(MEM_OUTPUT, 0x1000, UC_PROT_READ | UC_PROT_WRITE)
  uc.mem_map(MEM_CODE, 0x1000, UC_PROT_READ | UC_PROT_EXEC)
  uc.mem_map(MEM_STACK, 0x1000, UC_PROT_READ | UC_PROT_WRITE)
  score = 0

  addr_in = MEM_INPUT
  size = len(test)

  uc.reg_write(UC_X86_REG_ESP, MEM_STACK + 0x800)
  uc.reg_write(UC_X86_REG_EBP, 0)
  uc.reg_write(UC_X86_REG_EAX, MEM_OUTPUT)
  uc.reg_write(UC_X86_REG_EBX, addr_in)
  uc.reg_write(UC_X86_REG_ECX, 0)
  uc.reg_write(UC_X86_REG_EDX, size)
  uc.reg_write(UC_X86_REG_ESI, 0)
  uc.reg_write(UC_X86_REG_EDI, 0)
  #uc.reg_write(UC_X86_REG_EIP, MEM_CODE)

  uc.mem_write(addr_in, test + ZERO_PAGE[:-size])

  uc.mem_write(MEM_OUTPUT, ZERO_PAGE)
  uc.mem_write(MEM_STACK, ZERO_PAGE)
  uc.mem_write(MEM_STACK + 0x800, "\x41\x41\x41\x41")

  uc.mem_write(MEM_CODE, code)

  no_crash_score = 0
  try:
    uc.emu_start(MEM_CODE, MAGIC_RET, count=size * 5)
  except unicorn.UcError as e:
    eip = uc.reg_read(UC_X86_REG_EIP)
    #print hex(uc.reg_read(UC_X86_REG_EBX))
    if eip != MAGIC_RET:
      #print e
      #for ins in cs.disasm(uc.mem_read(eip, 16), eip):
      #  print hex(eip), ins.mnemonic, ins.op_str
      #  break
      pass
    else:
      no_crash_score = 1

  mem_out = str(uc.mem_read(MEM_OUTPUT, len(test)))
  test = str(uc.mem_read(addr_in, len(test)))
  for x, y in zip(mem_out, test):
    #print x, y
    if x == y:
      score += 10

  if score > 0:
    score += no_crash_score

  return score

CODE_LEN = 64


class Spec:
  def __init__(self, initial_state=None):
    if initial_state is None:
      self.code = os.urandom(CODE_LEN)
    else:
      self.code = initial_state

  def disasm(self):
    o = []
    for ins in cs.disasm(self.code, MEM_CODE):
      o.append("%x %s %s" % (ins.address, ins.mnemonic, ins.op_str))
    return '\n'.join(o)

  def __repr__(self):
    return `self.code`

  def __str__(self):
    return self.code

  def mutate(self):
    data = []
    for b in self.code:
      if random.randint(0, 10) == 0:
        b = chr(random.randint(0, 255))
      data.append(b)

    return Spec(''.join(data))

def mix(sa, sb):
  data = bytearray(sa.code)
  size = random.randint(1, 8)
  loc = random.randint(0, 31)

  chunk = bytearray(sb.code[loc:loc+size])

  dst = random.randint(0, 31)
  data[dst:dst+size] = chunk

  data = data[:CODE_LEN]

  return Spec(str(data))

def state_save(name):
  with open(name, "wb") as f:
    for s in top_spec:
      f.write(s.code)

def state_load(name):
  global top_spec
  top_spec = []
  with open(name, "rb") as f:
    d = f.read()

  i = 0
  while i < len(d):
    s = Spec(d[i:i+CODE_LEN])
    top_spec.append(s)

    i += CODE_LEN

TOP_COUNT = 10
#top_spec = [Spec() for _ in range(TOP_COUNT)]
#state_save("initial")
state_load("initial")

code = ks.asm("""
  mov cl, [ebx]
  mov [eax], cl
  ret
  """, MEM_CODE)

code = str(bytearray(code[0]))
code = code.ljust(CODE_LEN, '\0')

#print grade(code, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
#sys.exit(1)

top_spec.append(Spec(code))

gen = -1

while True:
  gen += 1
  candidates = top_spec[::]
  for _ in xrange(1000):
    candidates.append(random.choice(top_spec).mutate())

  candidates_copy = candidates[::]

  for _ in xrange(1000):
    candidates.append(
      mix(random.choice(candidates_copy),
          random.choice(candidates_copy)))

  results = []

  for c in candidates:
    score = grade(c.code, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    score += grade(c.code, "A" * 50)
    results.append((score, c))

  results = sorted(results, key=lambda x: x[0])
  top_spec = []
  print gen,
  with open("res/%.4i.txt" % gen, "w") as f:
    for s, c in results[-10:]:
      top_spec.append(c)
      f.write("-------- %i\n" % s)
      print s,
      f.write(c.disasm())
      f.write("\n")

  print ""
  state_save("res/%.4i.bin" % gen)









