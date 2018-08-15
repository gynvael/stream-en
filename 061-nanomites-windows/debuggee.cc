#include <cstdio>
#include <cstdlib>

__attribute__((naked)) int AddTwoNumber(int, int) {
  __asm("ud2");
  __asm("ret");
}

int Debuggee() {
  puts("Debuggee (child starting)"); fflush(stdout);

  // 345
  printf("result: %i\n", AddTwoNumber(123, 222));

  puts("Debuggee (child exiting)"); fflush(stdout);

  return 0;
}

