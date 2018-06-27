#include <stdio.h>
#include <stdlib.h>

void strrchr() {
  FILE *f = fopen("/home/adminimum/flag", "rb");
  char buf[1234]={0};
  fread(buf, 1, 1234, f);
  puts(buf);
}

