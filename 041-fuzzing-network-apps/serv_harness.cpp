#include <cstdio>
#include <vector>
#include <string>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

class NetSock {
  std::vector<uint8_t> data;
  size_t idx;


 public:
  bool ReadBlobFromFile(const char* fname) {
    FILE *f = fopen(fname, "rb");
    if (f == nullptr) {
      return false;
    }

    fseek(f, 0, SEEK_END);
    const size_t sz = ftell(f);
    fseek(f, 0, SEEK_SET);

    data.resize(sz);
    fread(&data[0], 1, sz, f);

    idx = 0;

    return true;
  }

  int WriteAll(const void */*Buffer*/, int /*Size*/) {}
  int Read(void *Buffer, int Size) {
    if (data.size() == idx) {
      return 0;
    }
    size_t sz = data[idx];

    idx ++;
    if (sz > data.size() - idx) {
      sz = data.size() - idx;
    }

    if (sz > Size) {
      sz = Size;
    }

    idx += sz;


    memcpy(Buffer, &data[idx], sz);
    return (int)sz;
  }
};


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
    if (s->Read(buf, 2) == 0) {
      break;
    }

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

int main(int argc, char **argv) {
  if (argc != 2) {
    printf("usage: serv_harness <file>\n");
    return 1;
  }


  NetSock c;
  if (!c.ReadBlobFromFile(argv[1])) {
    puts("ReadBlobFromFile()");
    return 1;
  }
  Handler(&c);

  return 0;
}
