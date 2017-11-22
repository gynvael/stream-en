#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <vector>
#include <string>

#define IMPORT_DATA_AS_STRING(str_name, symbol_name) \
  extern "C" char symbol_name ## _start; \
  extern "C" char symbol_name ##_end; \
  const std::string str_name( \
    &symbol_name ## _start, \
    &symbol_name ## _end - &symbol_name ## _start)

IMPORT_DATA_AS_STRING(bytecode, _binary_keycheck);

class VM {
 public:
  uint32_t r[16]{};
  uint32_t pc{};
  std::vector<uint8_t> mem;

  bool exec_instr();
  bool check(char key[16]);
};

bool VM::exec_instr() {
  switch (mem[pc]) {
    case 0x00: {  // XOR dst_reg, src_reg
      r[mem[pc+1]] ^= r[mem[pc+2]];
      pc += 3;
      return false;
    }

    case 0x01: {  // AND dst_reg, src_reg
      r[mem[pc+1]] &= r[mem[pc+2]];
      pc += 3;
      return false;
    }

    case 0x02: {  // OR dst_reg, src_reg
      r[mem[pc+1]] |= r[mem[pc+2]];
      pc += 3;
      return false;
    }

    case 0x10: {  // MOVI dst_reg, imm32
      memcpy(&r[mem[pc+1]], &mem[pc+2], 4);
      pc += 6;
      return false;
    }

    case 0x11: {  // MOV dst_reg, std_reg
      r[mem[pc+1]] = r[mem[pc+2]];
      pc += 3;
      return false;
    }

    case 0xff: {  // END
      return true;
    }
  }

  printf("Should never get here.\n");
  exit(1);
}

bool VM::check(char key[16]) {
  memcpy(&r[0], key+0, 4);
  memcpy(&r[1], key+4, 4);
  memcpy(&r[2], key+8, 4);
  memcpy(&r[3], key+12, 4);

  bool end = false;
  while (!end) {
    /*for (int i = 0; i < 8; i++)
      printf("r%i: %.8x  ", i, r[i]);
    putchar('\n');*/
    end = exec_instr();
  }

  return !(bool)r[0];
}

int main() {
  char key[256]{};

  printf("Hello There!\n"
         "Please enter your key: ");
  fflush(stdout);

  if (scanf("%16s", key) != 1) {
    puts("Bye.");
    return 1;
  }

  VM vm;

  vm.mem.resize(4096);
  memcpy(&vm.mem[0], bytecode.data(), bytecode.size());

  bool key_valid = vm.check(key);


  if (key_valid) {
    puts("Yup.");
  } else {
    puts("Nope.");
  }
}
