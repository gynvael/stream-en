#include <cstdio>
#include <cstdlib>

extern "C" int AddTwoNumber(int, int);
__asm(
  ".globl AddTwoNumber\n"
  ".text\n"
  "AddTwoNumber:\n"
  "  ud2\n"
  "  ret\n"
  "# asdf"
);

int Debuggee() {
  puts("Debuggee (child starting)"); fflush(stdout);

  // 345
  printf("result: %i\n", AddTwoNumber(123, 222));

  puts("Debuggee (child exiting)"); fflush(stdout);

  return 0;
}

