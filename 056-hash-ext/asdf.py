class StupidHash:
  def __init__(self):
    self.r = 42

  def update(self, data):
    for ch in data:
      ch = ord(ch)
      self.r = (ch + self.r) & 0xff

  def finalize(self):
    pass

  def digest(self):
    return chr(self.r)

  def hexdigest(self):
    return self.digest().encode('hex')

SECRET = "secret8123"
MSG = "public message"

# HMAC
# how not to: hash(secret | msg)
sh = StupidHash()
sh.update(SECRET)
sh.update(MSG)
sh.finalize()
print sh.hexdigest()

add = "yyyyyy"
USR_MSG = "public message"
USR_HASH = "02"
r = 2
for ch in USR_MSG[::-1]:
  r = (r - ord(ch)) & 0xff
USR_MSG = "private yyyyyyy"
sh = StupidHash()
sh.r = r
sh.update(USR_MSG)
sh.finalize()
USR_HASH = sh.hexdigest()
print USR_MSG
print USR_HASH


sh = StupidHash()
sh.update(SECRET)
sh.update(USR_MSG)
sh.finalize()
print sh.hexdigest() == USR_HASH








