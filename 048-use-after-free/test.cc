#include <string>

int main(void) {
  std::string x{"AAAAAAAAAAAAAAAA"};

  printf("%zu\n", sizeof(x));

  fwrite(&x, 1, sizeof(x), stdout);


}
