#include <cstdio>
#include "NetSock.h"


class Context {
 public:
  bool is_initilized{};
};

void HandlerAB(Context &ctx, NetSock *s) {
  char buf[4];
  s->Read(buf, 4);

  if (buf[0] == 't')
    if (buf[1] == 'e')
      if (buf[2] == 's')
        if (buf[3] == 't')
          ctx.is_initilized = true;

}

void HandlerXY(Context &ctx, NetSock *s) {
  if (!ctx.is_initilized) {
    return;
  }

  char buf[8];
  char output[16];
  s->Read(buf, 8);
  sprintf(output, buf);

  s->WriteAll(output, 16);
}

void Handler(NetSock *s) {
  char buf[4];
  Context ctx;

  for (;;) {
    s->Read(buf, 2);

    if (buf[0] == 'Q') {
      break;
    }

    if (buf[0] == 'A' && buf[1] == 'B') {
      HandlerAB(ctx, s);  // Init.
      if (!ctx.is_initilized) {
        return;
      }
    }

    if (buf[0] == 'X' && buf[1] == 'Y') {
      HandlerXY(ctx, s);  // Do some work.
    }
  }
}

int main(void) {
  NetSock::InitNetworking();

  NetSock server;
  server.ListenAll(31337);

  for (;;) {
    NetSock *c = server.Accept();
    printf("%s:%u connected\n", c->GetStrIP(), c->GetPort());
    Handler(c);
    c->Disconnect();
  }




  return 0;
}
