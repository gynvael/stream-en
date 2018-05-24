#include <stdio.h>

struct data_st {
  int b;
  char ch;

  //struct data_st *next;

  // ...
};

int main(void) {

  struct data_st s = {1234, 'A'};

  FILE *f = fopen("asdf.bin", "wb"); // -->

  fwrite(&s, 1, sizeof(struct data_st), f);

  //fwrite(&s.b, 1, 4, f);
  //fwrite(&s.ch, 1, 1, f); // -->

  // ...

  fclose(f);

  return 0;
}
