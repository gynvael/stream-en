good = "4e5d4e92865a4e495a86494b5a5d49525261865f5758534d4a89".decode("hex")


 # ((ord(cs) - 89) & 255) ^ 115 ^ 50 --> cg

o = ""
for cg in good:
  o += chr(((ord(cg) ^ 115 ^ 50) + 89) & 255)
print o

