import struct
import sys
import alsaaudio
import threading
import pytun
import socket
import select
import time
import bisect
import collections
from Queue import Queue, Empty

TUN_ENABLED = True  # THIS

SAMPLES_PER_SECOND = 44100

host = socket.gethostname()
MTU = 1500
PERIOD = 1000
PAUSE_LENGTH = 3  # Note: Low frequency == normalization on some soundcards.
BIT_LENGTH = 3
SEND_AMPLITUDE = 10000

MSG_PROLOGUE = "0" * 10
MSG_EPILOGUE = "1" * 10

inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
inp.setchannels(2)
inp.setrate(SAMPLES_PER_SECOND)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
inp.setperiodsize(PERIOD)

outp = alsaaudio.PCM()
outp.setchannels(2)
outp.setrate(SAMPLES_PER_SECOND)
outp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
outp.setperiodsize(PERIOD)

send_queue = Queue()
recv_queue = Queue()

if TUN_ENABLED:
  tun = pytun.TunTapDevice(flags=pytun.IFF_TUN|pytun.IFF_NO_PI)
  tun.addr = {
    "daemon": "192.168.133.7",
    "elias": "192.168.133.8"
  }[host]
  tun.dstaddr = {
    "daemon": "192.168.133.8",
    "elias": "192.168.133.7"
  }[host]
  tun.netmask = "255.255.255.0"
  tun.mtu = MTU
  tun.up()
else:
  tun = None

the_end = threading.Event()

class Calibrator:
  def __init__(self, count=SAMPLES_PER_SECOND*2):
    self.samples = []
    self.count = count

  def add(self, new_samples):
    self.samples.extend(new_samples)
    del self.samples[:-self.count]

  def get_levels(self):
    if len(self.samples) < self.count:
      return None

    level_1 = max(self.samples)
    level_0 = min(self.samples)
    zero = (level_0 + level_1) / 2

    amp_1 = level_1 - zero
    amp_2 = zero - level_0
    amp = (amp_1 + amp_2) / 2

    if amp < SEND_AMPLITUDE / 2:
      return None  # Not calibrated.

    return zero - amp / 2, zero, zero + amp / 2

def recv_thread():
  bits_received = ""
  state = "PRE"
  state_opt = 0

  samples = []

  calib = Calibrator()

  while not the_end.is_set():
    l, data = inp.read()
    #print l, len(data),
    if l <= 0 or len(data) < 2:
      continue

    sample_count = (len(data)/2)

    data = struct.unpack("%ih" % (len(data)/2), data)

    left_channel = data[::2] # Only one channel for now.
    calib.add(left_channel)

    levels = calib.get_levels()
    if levels is None:
      continue
    #print levels

    level_0, zero, level_1 = levels

    for d in left_channel:
      if state == "PRE":
        if d < level_0 or d > level_1:
          state = "GATHERING"
          state_opt = 0
          samples = [d]
          continue
        continue

      if state == "GATHERING":
        if d < level_0 or d > level_1:
          samples.append(d)
          continue

        state_opt += 1

        if state_opt < (PAUSE_LENGTH / 2):
          continue

        state = "PRE"
        av = sum(samples) / len(samples)
        if av >= level_1 / 2:
          bits_received += "1"
          #print "1",
          #sys.stdout.flush()
        elif av <= level_0 / 2:
          bits_received += "0"
          #print "0",
          #sys.stdout.flush()
        else:
          print "x", av, len(samples), levels
          sys.stdout.flush()
          continue

        if MSG_EPILOGUE in bits_received:
          packet = decode_bits(bits_received)
          if packet is not False:
            recv_queue.put(packet)
            print "Recv:", packet.encode("hex")
            #print levels
          else:
            print "Recv false packet"
          bits_received = ""


    #p = "    %6i %6i | %6i %6i\r" % (min(k[::2]), max(k[::2]), min(k[1::2]), max(k[1::2]))
    #sys.stdout.write(p)
    #sys.stdout.flush()

def decode_bits(bits):
  if MSG_PROLOGUE not in bits:
    print "Error: missing starter"
    return False

  idx = bits.rfind(MSG_PROLOGUE)
  bits = bits[idx+len(MSG_PROLOGUE):]

  idx = bits.find(MSG_EPILOGUE)
  bits = bits[:idx]

  if len(bits) % 10 != 0:
    print "Error: wrong length"
    return False

  data = []
  for i in xrange(len(bits) / 10):
    b = bits[i * 10:(i+1) * 10]
    if b[0] != "1":
      print "Error: wrong byte start marker"
      return False

    if b[9] != "0":
      print "Error: wrong byte end marker"
      return False

    data.append(chr(int(b[1:9], 2)))

  return ''.join(data)



def encode_bits(data):
  out = [MSG_PROLOGUE]

  for b in bytearray(data):
    bits = bin(b)[2:].rjust(8, "0")
    out.append("1" + bits + "0")

  out.append(MSG_EPILOGUE)

  return ''.join(out)

def bits_to_waveform(bits):
  samples = []
  samples.extend([0] * PAUSE_LENGTH)

  for b in bits:
    if b == "0":
      samples.extend([-SEND_AMPLITUDE] * BIT_LENGTH)
    else:
      samples.extend([SEND_AMPLITUDE] * BIT_LENGTH)
    samples.extend([0] * PAUSE_LENGTH)

  samples.extend([0] * PAUSE_LENGTH)

  #with open("dump.txt", "w") as f:
  #  f.write(' '.join(["%i" % s for s in samples]))

  return samples

def send_thread():
  while not the_end.is_set():
    calib = False
    try:
      to_forward = send_queue.get(True, 0.010)
      bits = encode_bits(to_forward)
    except Empty:
      # In case the bandwidth is empty, send calibration signal.
      bits = "01" * 10  # TODO: Calc this in a little more sane way.
      calib = True

    samples = bits_to_waveform(bits)  # Just one channel.
    if not calib:
      print "send_queue -> soundcard: %i, %i" % (len(bits), len(samples))

    while len(samples) % PERIOD != 0:
      samples.append(0)

    data = []
    for s in samples:
      data.append(struct.pack("hh", s, s))

    data = ''.join(data)

    outp.write(data)

def tun_to_send_thread():
  while not the_end.is_set():
    if TUN_ENABLED:
      to_send = tun.read(MTU)
      print "TUN -> send_queue:", len(to_send)
      send_queue.put(to_send)
    else:
      time.sleep(0.5)

def tun_just_received_thread():
  while not the_end.is_set():
    if TUN_ENABLED:
      try:
        to_forward = recv_queue.get(True, 1)
        print "recv_queue -> TUN:", len(to_forward)
        tun.write(to_forward)
      except Empty:
        continue
    else:
      time.sleep(0.5)


th = []
for func in [
    recv_thread, send_thread,
    tun_just_received_thread, tun_to_send_thread
]:
  t = threading.Thread(target=func)
  t.daemon = True
  t.start()
  th.append(t)

try:
  while True:
    time.sleep(1)
    if not TUN_ENABLED:
      print "Sending test!"
      send_queue.put("\x5A")

except KeyboardInterrupt:
  pass

print "Shutting down."

the_end.set()

if TUN_ENABLED:
  tun.down()

for t in th[:3]:
  print "Joining ", t
  t.join()

print "Bye."











