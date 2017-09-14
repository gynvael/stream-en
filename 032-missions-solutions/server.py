from socket import *
from threading import *
import os
import sys
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

def str_to_binary(s):
  bits = bytearray(len(s) * 8)
  i = 0
  for ch in s:
    ch = ord(ch)
    for bit in range(8):
      bits[i] = (ch >> bit) & 1
      i += 1

  return bits

def handler(s):
  s.settimeout(5)  # Somewhat short timeout.  
  handler_worker(s)
  s.shutdown(SHUT_RDWR)
  s.close()

def handler_worker(s):
  s.sendall("Enter shared secret mask you want to try:\n")
  status, mask = recvuntil(s, "\n")
  if status != "OK":
    return

  mask = mask.strip()
  if len(mask) != len(PASSWORD):
    s.sendall("Mask too short. Bye.\n")
    return

  for ch in mask:
    if ch not in "01":
      s.sendall("Meh.\n")
      return

  mask = bytearray([int(x)&1 for x in mask])
  mask_bits_set_cnt = sum(mask)
  if mask_bits_set_cnt < 64:
    s.sendall(
        "If you want to authenticate, prove that you know at least 64 bits.\n")
    return

  s.sendall("Alright, now send in the bits:\n")
  status, received_bits = recvuntil(s, "\n")
  received_bits = received_bits.strip()
  if len(received_bits) != mask_bits_set_cnt:
    s.sendall("You sent incorrect number of bits. Bye.\n")
    return

  for ch in received_bits:
    if ch not in "01":
      s.sendall("Meeeeh.\n")
      return

  received_bits = bytearray([int(x)&1 for x in received_bits])

  fault = 0
  for mask_bit, password_bit in zip(mask, PASSWORD):
    if not mask_bit:
      continue
    received_bit = received_bits.pop(0)
    if received_bit != password_bit:
      fault += 1

  if fault:
    s.sendall("Access Denied. Have a lovely day.\n")
    return

  s.sendall((
    "Access Granted\n"
    "You have received one secret message:\n"
    "---\n"
    "%s\n"
    "---\n"
    "End of messages.\n") % SECRET2)

SECRET1 = os.environ['SECRET1']
SECRET2 = os.environ['SECRET2']

if len(SECRET1) < 64:
  sys.exit("fatal: SECRET1 too short.")

if not SECRET2:
  sys.exit("fatal: SECRET2 too short.")

PASSWORD = str_to_binary(SECRET1)

s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 9393))
s.listen(10)

while True:
  conn, addr = s.accept()
  print time(), "New client:", addr[0], addr[1]
  th = Thread(target=handler, args=(conn,))
  th.daemon = True
  th.start()


