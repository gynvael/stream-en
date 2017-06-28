from z3 import *

# int --> BitVec("eax", 32)

v4 = 0x12345678
v5 = 0x89765443
v6 = 0x41414141
v7 = 0xABCDEF12

Str = []
for i in range(16):
  Str.append(BitVec("Str_%i" % i, 8))

v4 = (((v4 >> 3)) | (v4 << 3)) ^ (0x3039 * ZeroExt(24, Str[i]))
v5 = (((v5 >> 5)) | (v5 << 5)) ^ (0xAEDCE * ZeroExt(24, Str[i]))
v6 = (((v6 >> 7)) | (v6 << 7)) ^ (0x2EF8F * ZeroExt(24, Str[i]))
v7 = (((v7 >> 9)) | (v7 << 9)) ^ (0xDEDC7 * ZeroExt(24, Str[i]))

for i in range(1, 16):
  v4 = ((LShR(v4, 3)) | (v4 << 3)) ^ (0x3039 * ZeroExt(24, Str[i]))
  v5 = ((LShR(v5, 5)) | (v5 << 5)) ^ (0xAEDCE * ZeroExt(24, Str[i]))
  v6 = ((LShR(v6, 7)) | (v6 << 7)) ^ (0x2EF8F * ZeroExt(24, Str[i]))
  v7 = ((LShR(v7, 9)) | (v7 << 9)) ^ (0xDEDC7 * ZeroExt(24, Str[i]))


s = Solver()
s.add(v4 == 0xFFF4A1CE)
s.add(v5 == 0xB5A4A9A7)
s.add(v6 == 0xF05A945C)
s.add(v7 == 0x9504A82D)

for i in range(16):
  s.add(Str[i] >= 0x21, Str[i] <= 0x7e)

print s.check()
print s.model()






