#!/usr/bin/python
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
    if err != OK:
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

def conv(b):
  return ''.join(["01"[x] for x in b])
  
def go(test_bit, pattern):  
  print "TRYING", test_bit
  global HOST
  global PORT
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  
  # Put your code here!
  mask = bytearray(70 * 8)

  o = ""

  for i in range(70 * 8):
    if i == test_bit:
      mask[i] = 1
      o += "01"[pattern[i]]
      continue

    if i % 8 == 7:
      mask[i] = 1
      o += "01"[pattern[i]]     
      continue

  s.sendall(conv(mask) + "\n")
  s.sendall(o + "\n")

  ret = s.recvuntil("Access Granted")
  s.close()  
  if ret is False:
    return False

  return True



HOST = '31.133.0.131'
PORT = 9393

pattern = bytearray(70 * 8)
for i in range(0, 70 * 8):
  print i
  if not go(i, pattern):
    pattern[i] = 1

x = int(conv(pattern)[::-1], 2)
o = ""
while x:
  o += chr(x & 0xff)
  x >>= 8
print o
print o[::-1]







