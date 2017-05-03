#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
  FILE *f = fopen(argv[1], "rb");
  if (!f) {
    return 1;
  }

  char buf[16] = {0};

  fread(buf, 1, 16, f);
  fclose(f);

  if (buf[0] == 'a') {
    if (buf[1] == 'b') {
      if (buf[2] == 'c') {
        if (buf[3] == 'd') {
          if (buf[4] == 'e') {
            if (buf[5] == 'f') {
              if (buf[6] == 'g') {
                if (buf[7] == 'h') {
                  if (buf[8] == 'i') {
                    if (buf[9] == 'j') {
                      if (buf[10] == 'k') {
                        if (buf[11] == 'l') {
                          if (buf[12] == 'm') {
                            if (buf[13] == 'n') {
                              if (buf[14] == 'o') {
                                if (buf[15] == 'p') {
                                  abort();
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  return 0;
}

