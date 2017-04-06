data = """
55 73 9A EE 4B F3 D6 14  8E C6 47 3E 39 2F 47 2E 4F C9 5F 74 72 65 34 6D  32 76 31 3C DF 34 6A 64 5F 30 57 09 6E 66 23 F8  7D
"""

data = bytearray(data.replace(" ","").strip().decode("hex"))
print data

x = bytearray("DrgnS{")

k = ''.join([chr(a ^ b) for a, b in zip(data[:6], x)])
print k.encode("hex")

key = bytearray("1101FD801888E74BEDF2335F0840000210800004200001084000021080000420000108400002108000042000010840000210081338A802FA4CB8041B0210800004200001084000021080000420000108".replace(" ","").decode("hex"))

o = ""
for i, ch in enumerate(data):
  o += chr(ch ^ key[i % len(key)])

print o





