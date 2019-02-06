#!/usr/bin/env python3
from consts import *

# https://freenode.net/kb/answer/chat

IRC_CONFIG = {
    "reconnect_timeout": 5.0,  # Seconds
}

IRC_NETWORKS = {
    "freenode": {
        "host": "irc.freenode.net",
        "port": 6697,
        "ssl": True,
        "nickname": "ajhskjdha",
        "channels": {
            "#gynvaelstream-en": {}
        },
        "user_map": {
            "Gynvael": "Gynvael Coldwind"
        }
    }
}

ADMINS = {
    "Gynvael Coldwind": {
        "level": USER_LEVEL_ADMIN
    }
}


def __TestConfig():
  for network, cfg in IRC_NETWORKS.items():
    assert type(cfg["host"]) is str
    assert type(cfg["port"]) is int
    assert type(cfg["ssl"]) is bool
  # TODO add other tests (lol probably will never happen)
  print("All OK")

if __name__ == "__main__":
  __TestConfig()

