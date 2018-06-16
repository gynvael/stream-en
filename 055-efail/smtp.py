# Echo server program
import socket

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

  def sendall(self, txt):
    print txt
    return self._sock.sendall(txt)

s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 1025))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr
s.close()

s._sock = conn # Don't do this at home.

s.sendall('220 Whatever <something@somewhere>\n')

while True:
  r = s.recvuntil('\n')
  print 'C:', r

  if r.startswith("HELP"):
    s.sendall("250 no czesc\n")
    continue

  if r.startswith("QUIT"):
    s.sendall("221 bye\n")
    break

  if r.startswith("MAIL FROM"):
    s.sendall("250 OK\n")
    continue

  if r.startswith("RCPT TO"):
    s.sendall("250 OK\n")
    continue

  if r.startswith("DATA"):
    s.sendall('354 Enter message, ending with "." on a line by itself\n')

    d = s.recvuntil('\n.\r\n')
    print d
    s.sendall("250 OK\n")
    continue

  if r.startswith("AUTH"):
    s.sendall(
"""235 OK Authenticated
""")
    continue

  if r.startswith("EHLO"):
    s.sendall(
"""250-example.com Hello
250-SIZE 1000000
250 AUTH LOGIN PLAIN
""")
    continue

  print "-- unhandled"
  break

s.shutdown(socket.SHUT_RDWR)
s.close()
