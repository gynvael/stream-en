d = open("out.bin", "rb").read()

open("macho.bin", "wb").write(''.join([
    d[0xD9000:],
    d[0x7000 + 0x1000 * 1:]
]))



