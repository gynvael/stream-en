#include <stdio.h>
#include <malloc.h>


void *my_hook(size_t size, const void *caller) {
  puts("my_hook called");
  fflush(stdout);
  return NULL;
}



int main(void) {
  printf("asdf\n");
  __malloc_hook = my_hook;
  printf("%70000s\n", "asdf");


  return 0;
}
