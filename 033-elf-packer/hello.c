// gcc hello.c -o hello -fno-PIE -static

#include<stdio.h>

int main(void) {
  puts("Hello world!");

  return 0;
}

