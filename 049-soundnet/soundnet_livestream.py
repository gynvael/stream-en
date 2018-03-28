import alsaaudio
import threading
import struct
import Queue
import time
import sys

SAMPLES_PER_SECOND = 44100
PERIOD = 1000

SEQ_START = "1" * 10
SEQ_END = "0" * 10

WIDTH_SIG = 20
WIDTH_PAUSE = 50

POWER = 32000

CH_PAUSE = struct.pack("h", 0) * WIDTH_PAUSE
CH_ZERO = struct.pack("h", -POWER) * WIDTH_SIG
CH_ONE = struct.pack("h", POWER) * WIDTH_SIG

TESTING = True  # THIS

inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
inp.setchannels(1)
inp.setrate(SAMPLES_PER_SECOND)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
inp.setperiodsize(PERIOD)

outp = alsaaudio.PCM()
outp.setchannels(1)
outp.setrate(SAMPLES_PER_SECOND)
outp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
outp.setperiodsize(PERIOD)

the_end = threading.Event()
send_queue = Queue.Queue()

class Calibrator:
  def __init__(self, count=SAMPLES_PER_SECOND):
    self.samples = []
    self.count = count

  def append(self, samples):
    self.samples.extend(samples)
    del self.samples[:-self.count]

  def get_levels(self):
    if len(self.samples) < self.count:
      return None

    level_1 = max(self.samples)
    level_0 = min(self.samples)

    zero = (level_1 + level_0) / 2

    return level_0, zero, level_1


def soundcard_recv():
  print "Thread soundcard_recv started"

  calib = Calibrator()

  bits = ""

  STATE_WAIT = 0
  STATE_SIGNAL = 1

  state = STATE_WAIT
  gathered = []
  zero_counter = 0

  while not the_end.is_set():
    count, samples = inp.read()
    if count <= 0:
      print "Warning: Data lost, try bigger period size"
      continue

    samples = struct.unpack("%ih" % (len(samples)/2), samples)
    calib.append(samples)

    res = calib.get_levels()
    if res is None:
      continue

    level_0, zero, level_1 = res

    if abs(level_0) < POWER / 2 or abs(level_1) < POWER / 2:
      continue

    det_0 = level_0 / 4
    det_1 = level_1 / 4

    for sample in samples:
      if state == STATE_WAIT:
        if sample > det_1 or sample < det_0:
          state = STATE_SIGNAL
          zero_counter = 0
          gathered = [sample]
        continue

      if state == STATE_SIGNAL:
        if sample > det_1 or sample < det_0:
          gathered.append(sample)
          zero_counter = 0
          continue
        gathered.append(sample)

        zero_counter += 1

        if zero_counter < WIDTH_PAUSE / 4:
          continue

        state = STATE_WAIT

        avg = sum(gathered) / len(gathered)

        if avg > det_1:
          bits += "1"
          #print "1",
        elif avg < det_0:
          bits += "0"
          #print "0",
        else:
          print "x", avg, gathered
          bits = ""
        sys.stdout.flush()

        #print bits

        if SEQ_END in bits:
          data = bits_to_data(bits)
          print `data`
          bits = ""

def bits_to_data(bits):
  data = []

  if SEQ_START not in bits:
    print "Warning: Missing SEQ_START"
    return None

  bits = bits.split(SEQ_START)[1]
  bits = bits.split(SEQ_END)[0]
  print bits

  if len(bits) % 10 != 0:
    print "Warning: Data not dividable by 10"
    return None

  i = 0
  while i < len(bits):
    packet = bits[i:i+10]
    if packet[0] != '0':
      print "Warning: Wrong leading bit"
      return None

    if packet[9] != '1':
      print "Warning: Wrong trailing bit"
      return None

    byte = chr(int(packet[1:9], 2))
    data.append(byte)

    i += 10

  return ''.join(data)

def data_to_bits(data):
  bits = [ SEQ_START ]

  for ch in data:
    ch = ord(ch)
    bits.append('0')
    for i in xrange(8):
      bit = str((ch >> (7 - i)) & 1)
      bits.append(bit)
    bits.append('1')

  bits.append(SEQ_END)

  return ''.join(bits)

def bits_to_signal(bits):
  signal = [ CH_PAUSE ]

  for bit in bits:
    if bit == "0":
      signal.append(CH_ZERO)
    else:
      signal.append(CH_ONE)
    signal.append(CH_PAUSE)

  return ''.join(signal)

def soundcard_send_data(data, bits = None):
  if bits is None:
    bits = data_to_bits(data)
  #print `data`, bits
  signal = bits_to_signal(bits)

  i = 0
  while i < len(signal):
    data = signal[i:i + PERIOD * 2]
    if len(data) < PERIOD * 2:
      data = data.ljust(PERIOD * 2, '\0')
    i += PERIOD * 2
    outp.write(data)

def soundcard_send():
  print "Thread soundcard_send started"
  while not the_end.is_set():
    try:
      data = send_queue.get(True, 0.1)
      soundcard_send_data(data)
    except Queue.Empty:
      soundcard_send_data(None, "1010")  # Calibrate the other side.
      continue


threads = [
  soundcard_recv,
  soundcard_send
]

th_handles = []

for thfunc in threads:
  th = threading.Thread(target=thfunc)
  th.daemon = True
  th.start()
  th_handles.append(th)


try:
  while True:
    time.sleep(1)
    if TESTING:
      send_queue.put('\xa5')

except KeyboardInterrupt:
  pass

the_end.set()

for th in th_handles:
  th.join()

print "Done!"





