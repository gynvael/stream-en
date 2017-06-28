from z3 import *

# int --> BitVec("eax", 32)

a = BitVec("a", 32)
b = BitVec("b", 32)

c = a + b
d = a ^ b

s = Solver()
s.add(c == d)
s.add(c != 0, d != 0)

print s.check()
print s.model()






