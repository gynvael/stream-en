# NOTE: You'll need to patch zipfile yourself ;)
# 1. Remove CRC32 checking
# 2. Hardcode that the file is not encrypted
# See the stream for details - sorry.
import os
import zipfile
import zlib
import hashlib
from struct import pack, unpack
import sys
from z3 import *

POLY_SZ = 20


class BitStream:
  def __init__(self, data, sz=None):
    if sz is None:
      sz = len(data) * 8

    self.sz = sz
    self.data = bytearray(data)
    self.idx = 0

  def get_bit(self):
    if self.idx >= self.sz:
      raise Exception('All bits used. Go away.')

    i_byte = self.idx / 8
    i_bit = self.idx % 8

    bit = (self.data[i_byte] >> i_bit) & 1
    self.idx += 1

    return bit

  def get_bits(self, sz):
    v = 0
    for i in xrange(sz):
      v |= self.get_bit() << i

    return v


class LFSR:
  def __init__(self, poly, iv, sz):
    self.sz = sz
    self.poly = poly
    self.r = iv
    self.mask = (1 << sz) - 1

  def get_bit(self):
    bit = (self.r >> (self.sz - 1)) & 1

    new_bit = 1
    masked = self.r & self.poly
    for i in xrange(self.sz):
      new_bit ^= (masked >> i) & 1

    self.r = ((self.r << 1) | new_bit) & self.mask
    return bit


class LFSRCipher:
  def __init__(self, key, poly_sz=8, key_iv=None, cipher_iv=None):
    if len(key) < poly_sz:
      raise Exception('LFSRCipher key length must be at least %i' % poly_sz)
    key = BitStream(key)

    if key_iv is None:
      key_iv = os.urandom(poly_sz)
    self.key_iv = key_iv
    key_iv_stream = BitStream(key_iv)

    if cipher_iv is None:
      cipher_iv = os.urandom(poly_sz)
    self.cipher_iv = cipher_iv
    cipher_iv_stream = BitStream(cipher_iv)

    self.lfsr = []
    for i in xrange(8):
      l = LFSR(key.get_bits(poly_sz) ^ key_iv_stream.get_bits(poly_sz),
               cipher_iv_stream.get_bits(poly_sz), poly_sz)
      self.lfsr.append(l)

  def get_keystream_byte(self):
    b = 0
    for i, l in enumerate(self.lfsr):
      b |= l.get_bit() << i
    return b

  def get_headers(self):
    return self.key_iv + self.cipher_iv

  def crypt(self, s):
    s = bytearray(s)
    for i in xrange(len(s)):
      s[i] ^= self.get_keystream_byte()
    return str(s)


class SolveLFSRCipher:
  def __init__(self, keys=None, cipher_iv=None):
    poly_sz = POLY_SZ
    cipher_iv_stream = BitStream(cipher_iv)

    self.lfsr = []
    for i in xrange(8):
      l = LFSR(keys[i], cipher_iv_stream.get_bits(poly_sz), poly_sz)
      self.lfsr.append(l)

  def get_keystream_byte(self):
    b = 0
    for i, l in enumerate(self.lfsr):
      b |= l.get_bit() << i
    return b

  def get_headers(self):
    return self.key_iv + self.cipher_iv

  def crypt(self, s):
    s = bytearray(s)
    for i in xrange(len(s)):
      s[i] ^= self.get_keystream_byte()
    return str(s)



# P = 1 ^ ( C0 & B0 ) ^ ( C1 & B1 ) ^ ( C2 & B2 ) ^ ( C3 & B3 )  ...
def Z3LFSR(C, R):
  bit = Extract(POLY_SZ - 1, POLY_SZ - 1, R)

  new_bit = BitVec(1, 1)

  for i in xrange(POLY_SZ):
    new_bit = new_bit ^ (Extract(i, i, C) & Extract(i, i, R))

  new_R = Concat( Extract(POLY_SZ - 2, 0, R), new_bit )

  return bit, new_R

def solve(cipher_iv, data, enc_hash):
  data = bytearray(data)
  known_bytes = [
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x02, 0x80,

    0x00, 0x00, None, None,  # Height
    0x08, # Bit depth
    2, # Color type (this might be different)
    0, # Compression method
    0, # Filters
    0, # Interlace (this might be 1)

    None, None, None, None,  # No idea.

    #0, 0, 0, 9,
    #0x70, 0x48, 0x59, 0x73,


    0, 0, 0, 1,
    0x73, 0x52, 0x47, 0x42,
    0, # 0-3
    0xae, 0xce, 0x1c, 0xe9,

    0, 0, 0, 4,
    0x67, 0x41, 0x4D, 0x41,
    #None, None, None, None,
    #None, None, None, None,


  ]

  C = []
  R = []

  cipher_iv_stream = BitStream(cipher_iv)

  s = Solver()

  for i in xrange(8):
    C.append(BitVec("C%i" % i, POLY_SZ))  # Unknown.
    R.append(BitVecVal(cipher_iv_stream.get_bits(POLY_SZ), POLY_SZ))


  all_C = Concat(
      C[7], C[6], C[5], C[4], C[3], C[2], C[1], C[0]
    )

  for j in xrange(20):
    for i in xrange(8):
      bit, new_R = Z3LFSR(C[i], R[i])
      R[i] = new_R

  for j in xrange(20, len(known_bytes)):
    bits = []
    for i in xrange(8):
      bit, new_R = Z3LFSR(C[i], R[i])
      R[i] = new_R
      bits.append(bit)

    if known_bytes[j] is not None:
      key_stream_byte_eq = Concat(
        bits[7], bits[6], bits[5], bits[4], bits[3], bits[2], bits[1], bits[0])
      key_stream_byte = known_bytes[j] ^ data[j]
      s.add(key_stream_byte_eq == key_stream_byte)

  counter = 0
  while True:
    #counter += 1
    #print counter

    ch = s.check()
    print ch
    if ch.r == -1:
      return

    m = s.model()

    poly = []
    for i in xrange(8):
      poly.append(m[C[i]].as_long())

    c = SolveLFSRCipher(poly, cipher_iv)
    dec_data = c.crypt(data)
    dec_hash = c.crypt(enc_hash)

    dec_data_hash = hashlib.sha256(dec_data).digest()

    if dec_hash == dec_data_hash:
      print "YEAH!"
      with open("flag.png", "wb") as f:
        f.write(dec_data)
      return

    current_poly = Concat(
      m[C[7]], m[C[6]], m[C[5]], m[C[4]], m[C[3]], m[C[2]], m[C[1]], m[C[0]]
    )

    s.add(current_poly != all_C)


# A super short ZIP implementation.
def SETBIT(n):
  return 1 << n

def db(v):
  return pack("<B", v)

def dw(v):
  return pack("<H", v)

def dd(v):
  return pack("<I", v)

z = zipfile.ZipFile("flag.zip")
d = z.read("flag.png")
key_iv = d[:20]
cipher_iv = d[20:40]
enc_hash = d[-32:]
data = d[40:-32]
#print len(data)

#l = LFSRCipher("A" * 20, POLY_SZ, None, cipher_iv)
#start = l.crypt(data[:20])

solve(cipher_iv, data, enc_hash)



#with open("start.bin", "wb") as f:
  #f.write(start)






