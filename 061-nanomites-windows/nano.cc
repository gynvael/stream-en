#include <cstdio>
#include <cstdlib>

#include "debugger.h"
#include "debuggee.h"

int main(void) {

  if (getenv("YOUARETHESECOND") == nullptr) {
    return Debugger();
  } else {
    return Debuggee();
  }
}
