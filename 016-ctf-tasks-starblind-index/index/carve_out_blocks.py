import sys
U = (
    open("Unalloc_84_1200128_25161728", "rb").read() + 
    open("zzzzz.png", "rb").read()
    )
D = open("index.img", "rb").read()

BLOCKS = []
for i in range(len(D) / 0x1000):
  BLOCKS.append(D[i*0x1000:i*0x1000+0x1000])

def drop_block(block):
  global BLOCKS
  for i, bl in enumerate(BLOCKS):
    if len(block) != 0x1000:
      bl = bl[:len(block)]
    if block == bl:
      BLOCKS.pop(i)
      return True
  return False

for i in range(len(U) / 0x1000):
  while drop_block(U[i*0x1000:i*0x1000+0x1000]):
    pass

  if i % 64 == 0:
    sys.stdout.write("  %i / %i\r" % (i, len(U) / 0x1000))
    sys.stdout.flush()

open("out.bin", "wb").write(''.join(BLOCKS))




