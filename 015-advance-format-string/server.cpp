// g++ server.cpp NetSock.cpp -fno-stack-protector -ggdb -m32
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include "NetSock.h"

char fmt_buf[5120];

int main(int argc, char **argv) {
  NetSock::InitNetworking();

  NetSock server;
  server.ListenAll(1337);

  for (;;) {
    NetSock *s = server.Accept();
    printf("New client: %s:%u\n", s->GetStrIP(), s->GetPort());
    fflush(stdout);

    pid_t pid = fork();
    if (pid == 0) {
      // Child.
      s->ReadAll(fmt_buf, sizeof(fmt_buf));
      dup2(s->GetDescriptor(), 1);
      printf("%p\n", &argc);
      fflush(stdout);
      printf(fmt_buf);
      fflush(stdout);
      exit(0);
    } else {
      // Parent. Wait for child to exit.
      int status;
      waitpid(pid, &status, 0);
      printf("Child exited: %i\n", status);
      fflush(stdout);
    }    
  }

  return 0;
}

