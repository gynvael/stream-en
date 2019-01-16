with open("dump.hex", "r") as f:
  d = f.read()

d = d.replace("Start---", "")
d = d.replace("Done!", "")
d = d.replace("\r", "")  #
d = d.replace("\n", "")

d = d.decode('hex')

with open("dump.bin", "wb") as f:
  f.write(d)


