#!/bin/bash
set -e
g++ nano.cc debugger.cc debuggee.cc \
    -Wall -Wextra -Wno-format -Wno-unused-variable \
    -o nano




