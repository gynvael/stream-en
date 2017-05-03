#!/usr/bin/python
import subprocess
import random
import sys
import struct
import os
import shutil
from glob import glob

def load_file(fname):
  with open(fname, "rb") as f:
    return bytearray(f.read())

def save_file(fname, data):
  with open(fname, "wb") as f:
    f.write(str(data))

def mutate_bits(data):
  count = int((len(data) * 8) * 0.01)
  if count == 0:
    count = 1
  for _ in range(count):
    bit = random.randint(0, len(data) * 8 - 1)
    idx_bit = bit % 8
    idx_byte = bit / 8
    data[idx_byte] ^= 1 << idx_bit

  return data

def mutate_bytes(data):
  count = int(len(data) * 0.01)
  if count == 0:
    count = 1
  for _ in range(count):
    data[random.randint(0, len(data) - 1)] = random.randint(ord('a'), ord('z'))
  return data

def mutate_magic(data):
  numbers = [
     (1, struct.pack("B", 0xff)),  # malloc((unsigned char)(text_lenght + 3))
     (1, struct.pack("B", 0x7f)),
     (1, struct.pack("B", 0)),
     (2, struct.pack("H", 0xffff)),
     (2, struct.pack("H", 0)),     
     (4, struct.pack("I", 0xffffffff)),
     (4, struct.pack("I", 0)),
     (4, struct.pack("I", 0x80000000)),
     (4, struct.pack("I", 0x40000000)),
     (4, struct.pack("I", 0x7fffffff)),
  ]

  count = int(len(data) * 0.01)
  if count == 0:
    count = 1
  for _ in range(count):
    n_size, n = random.choice(numbers)
    sz = len(data) - n_size
    if sz < 0:
      continue
    idx = random.randint(0, sz)
    data[idx:idx + n_size] = bytearray(n)

  return data

def mutate(data):
  return random.choice([
    #mutate_bits,
    mutate_bytes,
    #mutate_magic
  ])(data[::])

def run_gdb(exename):
  p = subprocess.Popen(["gdb", "--batch", "-x", "detect.gdb", exename],
      stdout=subprocess.PIPE,
      stderr=None)
  output, _ = p.communicate()
  if "Program received signal" in output:
    return output.split("aposkjd9081j239dnm023emtunficjsandf8123")[1]
  return None

def get_coverage(covname):
  with open(covname, "rb") as f:
    cov = f.read()

  return set([
    struct.unpack("Q", cov[i:i+8])[0] for i in range(8, len(cov), 8)
  ])


def run_cov(exename):
  global errcode
  p = subprocess.Popen([exename, "test.sample"],
      env=os.environ,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
  output, error = p.communicate()
  errcode = p.returncode

  if output:
    print output

  if error:
    print error
 
  for cov in glob("./cov/*.sancov"):
    c = get_coverage(cov)
    os.unlink(cov)

    if not c.issubset(main_coverage):
      main_coverage.update(c)
      fname = "input_%u.sample" % len(main_coverage)      
      print "Found new bb:", len(main_coverage), fname


      shutil.copyfile("test.sample", fname)
      input_samples.pop(0)  ## Comment this out.
      input_samples.append(load_file(fname))

  return None


os.environ["ASAN_OPTIONS"] = "coverage=1,coverage_dir=./cov"

for cov in glob("./cov/*.sancov"):
  os.unlink(cov)

input_samples = [
    load_file("input.sample")
]

main_coverage = set()
errcode = 0
i = 0
while True:
  i += 1
  if True:
    sys.stdout.write("%i"%errcode)
    sys.stdout.flush()
  mutated_sample = mutate(random.choice(input_samples))
  save_file("test.sample", mutated_sample)

  output = run_cov("./a.out")
  if output is not None:
    print "CRASH!"
    save_file("crash.samples.%i" % i, mutated_sample)
    save_file("crash.samples.%i.txt" % i, output)
    print output


  
