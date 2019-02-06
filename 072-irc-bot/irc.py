#!/usr/bin/env python3
import config
import logging
import socket
import ssl
import threading
import time
import queue
from consts import *

# TODO: https://docs.python.org/3/library/ssl.html#ssl-security

IRC_EVENT_MESSAGE = "MESSAGE"
IRC_EVENT_DISCONNECT = "DISCONNECT"


class IRCEvent():
  def __init__(self, ev_type, ev_data=None):
    self.type = ev_type
    self.data = ev_data

  def __repr__(self):
    return "IRCEventType(%s, %s)" % (self.type, repr(self.data))


class IRCException(Exception):
  pass

class IRC:
  def __init__(self, cfg):
    self.cfg = cfg
    self.s = None  # Low-level socket.
    self.raw_s = None  # In case of SSL this is the raw socket.

    self.handling_th = threading.Thread(target=self.handling_thread_run)
    self.handling_th.daemon = True
    self.handling_th.start()

  def connect(self):
    if self.cfg["ssl"]:
      return self.connect_ssl()
    else:
      return self.connect_nossl()

  def disconnect(self):
    if self.cfg["ssl"]:
      return self.disconnect_ssl()
    else:
      return self.disconnect_nossl()

  def disconnect_ssl(self):
    self.s.shutdown(socket.SHUT_RDWR)
    self.s.close()

  def disconnect_nossl(self):
    self.s.shutdown(socket.SHUT_RDWR)
    self.s.close()

  def connect_ssl(self):
    logging.info("Connecting to %s:%i (SSL)",
        self.cfg["host"], self.cfg["port"])

    self.raw_s = socket.create_connection((self.cfg["host"], self.cfg["port"]))
    self.ssl_ctx = ssl.create_default_context()
    self.s = self.ssl_ctx.wrap_socket(
        self.raw_s, server_hostname=self.cfg["host"])

    logging.info("Connection established!")
    return True

  def connect_nossl(self):
    logging.info("Connecting to %s:%i (NO SSL)",
        self.cfg["host"], self.cfg["port"])

    self.s = socket.create_connection((self.cfg["host"], self.cfg["port"]))

    logging.info("Connection established!")
    return True

  def sender_thread_run(self):
    while not self.the_end.is_set() and not self.end_sender_receiver.is_set():
      try:
        msg = self.send_queue.get(block=True, timeout=0.5)
      except queue.Empty:
        continue
      self.s.sendall(bytes(msg, "utf-8") + b"\r\n")

  def receiver_thread_run(self):
    buffers = []
    while not self.the_end.is_set() and not self.end_sender_receiver.is_set():
      try:
        data = self.s.recv(12345)
      except socket.timeout:
        continue

      if data == b'':
        self.recv_queue.put(
            IRCEvent(IRC_EVENT_DISCONNECT))
        return

      buffers.append(data)

      while b'\n' in data:  # BUG: data was not updated, inf loop ftw
        res = b''.join(buffers).split(b'\n', 1)
        line = res[0]
        if len(res) == 1:
          buffers = []
          data = b''  # BUG FIXED
        else:
          buffers = [res[1]]
          data = res[1]  # BUG FIXED

        if not line:
          logging.warning("Received an empty line.")
          continue

        if line[-1] == b'\r'[0]:
          line = line[:-1]

        if not line:
          logging.warning("Received an empty line.")
          continue

        self.recv_queue.put(
            IRCEvent(IRC_EVENT_MESSAGE, str(line, 'utf-8', errors='replace')))

  def handling_thread_run(self):
    self.the_end = threading.Event()
    self.send_queue = queue.Queue()
    self.recv_queue = queue.Queue()

    while not self.the_end.is_set():

      if not self.connect():
        logging.warning("Failed to connect. Retrying in 5 seconds.")
        time.sleep(config.IRC_CONFIG["reconnect_timeout"])
        continue

      self.s.settimeout(0.5)  # Seconds.

      self.end_sender_receiver = threading.Event()

      self.sender_th = threading.Thread(target=self.sender_thread_run)
      self.sender_th.daemon = True
      self.sender_th.start()

      self.receiver_th = threading.Thread(target=self.receiver_thread_run)
      self.receiver_th.daemon = True
      self.receiver_th.start()

      while not self.the_end.is_set():
        try:
          event = self.recv_queue.get(block=True, timeout=0.5)
        except queue.Empty:
          continue

        logging.debug("Event %s", repr(event))  # TODO: remove this

        if event.type == IRC_EVENT_DISCONNECT:
          break

      # Clean up connection before reconnecting.
      self.end_sender_receiver.set()
      self.sender_th.join()
      self.receiver_th.join()
      self.disconnect()

      time.sleep(config.IRC_CONFIG["reconnect_timeout"])


if __name__ == "__main__":
  # TODO remove this
  logging.getLogger().setLevel(logging.DEBUG)
  IRC(config.IRC_NETWORKS["freenode"])

  time.sleep(100)


