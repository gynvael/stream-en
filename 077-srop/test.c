#include <stdio.h>
#include <signal.h>
#include <sys/types.h>
#include <unistd.h>


void myhandler(int num) {
  printf("myhandler: %i\n", num);
}

int main(void) {
  signal(1, myhandler);
  kill(getpid(), 1);


  return 0;
}
