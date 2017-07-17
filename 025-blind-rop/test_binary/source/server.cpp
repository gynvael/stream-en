// Windows  : g++ test.cpp NetSock.cpp -lws2_32
// GNU/Linux: g++ test.cpp
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include "NetSock.h"

void EchoServer() {
  char buf[16]{};
  int sz;
  char *p = buf;
  printf("Data size: ");
  scanf("%i", &sz);
  printf("%i bytes of data: ", sz);
  int ch = getchar();
  if (ch != '\n') {
    buf[0] = ch;
    p++;
    sz--;
  }

  fread(p, 1, sz, stdin);
  printf("Echo: ");
  puts(buf);
}

int Handler() {
  printf("%.16llx\n", (unsigned long long)(void*)Handler);

  EchoServer();

  puts("Done!");

  // Since technically I'm not closing correctly the connection, I'll give it a
  // milisec to make sure data ise actually sent out.
  usleep(1000);


  return 0;
}

int main() {
  NetSock::InitNetworking(); // Initialize WinSock
  
  NetSock s;
  if (!s.ListenAll(1337)) {
    perror("error");
    return 1;
  }

  for (;;) {
    NetSock *c = s.Accept();
    if (c == nullptr) {
      continue;
    }

    if (fork() == 0) {
      int fs = c->GetDescriptor();
      dup2(fs, 0);
      dup2(fs, 1);
      setbuf(stdout, NULL);
      setbuf(stdin, NULL);
      delete c;

      return Handler();
    } else {
      delete c;
    }

    // Clean up children. There might be some defunc processes, but they will be
    // cleaned up as soon as another connection is made.
    // This is not the best way to do it, but hey, this is an example of a buggy
    // program in the first place, right? ;)
    int status;
    while (waitpid(-1, &status, WNOHANG) > 0) {}
  }
  
  return 0;
}

