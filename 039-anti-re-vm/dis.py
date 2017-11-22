import struct
d = bytearray(open("app.exe", "rb").read()[0x2a10:0x2a10+0x100])

i = 0

while i < len(d):
  print "%.2x: " % i,
  if d[i] == 0:
    print "vxor vr%i, vr%i" % (d[i+1], d[i+2])
    i += 3
    continue

  if d[i] == 1:
    print "vand vr%i, vr%i" % (d[i+1], d[i+2])
    i += 3
    continue

  if d[i] == 2:
    print "vor vr%i, vr%i" % (d[i+1], d[i+2])
    i += 3
    continue

  if d[i] == 0x11:
    print "vmov vr%i, vr%i" % (d[i+1], d[i+2])
    i += 3
    continue

  if d[i] == 0x10:
    print "vmovi vr%i, 0x%.8x" % (d[i+1], struct.unpack("I", d[i+2:i+2+4])[0])
    i += 6
    continue

  if d[i] == 0xff:
    print "vend"
    break




