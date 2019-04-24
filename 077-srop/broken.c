#include <stdio.h>

unsigned int calc(unsigned char *asdf, size_t len) {
  unsigned int a = 1234;
  for (size_t i = 0; i < len; i++) {
    a ^= asdf[i] << (i % 31);
  }
  return a;
}

void asdf() {
  unsigned char a[1024];
  puts("Hi!");
  fread(a, 1, 1024 + 0x10 + 1024, stdin);
  printf("hash: %.8x\n", calc(a, sizeof(a)));
}

int main(void) {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  setbuf(stderr, NULL);
  unsigned char a[1024] = {0};

  asdf();

  printf("hash: %.8x\n", calc(a, sizeof(a)));

  return 0;
}

