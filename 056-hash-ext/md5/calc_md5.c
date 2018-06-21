#include <stdio.h>
#include "md5.h"
#include <string.h>

unsigned int be_to_le(unsigned int r) {
  //return r;
  return
    (((r >> 0) & 0xff) << 24) |
    (((r >> 8) & 0xff) << 16) |
    (((r >> 16) & 0xff) << 8) |
    (((r >> 24) & 0xff) << 0);
}

int main(void) {
  int i;

  // this can be brute-forced
  const int len_secret = 27;

  // error=Incorrectly filled form%80%00%00%00%00%00%90%01%00%00%00%00%00%00<script>alert(2)</script>
  // hmac=5689f6dd832597e0fc50b19e18797e19

  const char *error="Incorrectly filled form"; // 23
  // hmac=7f8cf0b2 0b826797 c2218fe7 db229301

  MD5_CTX ctx;
  MD5_Init(&ctx);

  printf("%.8x %.8x %.8x %.8x\n", ctx.a, ctx.b, ctx.c, ctx.d);
  MD5_Update(&ctx, "AAAAAAAAAAAAAAAAAAAAAAAAAAA", 27);
  printf("%.8x %.8x %.8x %.8x\n", ctx.a, ctx.b, ctx.c, ctx.d);
  MD5_Update(&ctx, error, strlen(error));
  printf("%.8x %.8x %.8x %.8x\n", ctx.a, ctx.b, ctx.c, ctx.d);

  // 50 --> 14
  MD5_Update(&ctx, "\x80\0\0\0\0\0", 6);

  unsigned long long lenght = 50; // 0x32
  MD5_Update(&ctx, &lenght, 8);


  printf("%.8x %.8x %.8x %.8x\n", ctx.a, ctx.b, ctx.c, ctx.d);

  printf("%.8x\nfilling\n", be_to_le(0x12345678));

  ctx.a = be_to_le(0x7f8cf0b2);
  ctx.b = be_to_le(0x0b826797);
  ctx.c = be_to_le(0xc2218fe7);
  ctx.d = be_to_le(0xdb229301);
  printf("%.8x %.8x %.8x %.8x\n", ctx.a, ctx.b, ctx.c, ctx.d);

  MD5_Update(&ctx, "<script>alert(1)</script>", 25);

  unsigned char res[16];
  MD5_Final(res, &ctx);

  for(i = 0; i < 16; i++) {
    printf("%.2x", res[i]);
  }

  putchar('\n');
  return 0;
}

