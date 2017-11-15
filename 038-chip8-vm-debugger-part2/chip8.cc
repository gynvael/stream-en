#include <cstdio>
#include <ctype.h>
#include <stdint.h>
#include <algorithm>
#include <functional>
#include <memory>
#include <unordered_map>
#include <cstdlib>
#include <vector>
#include <stack>
#include <unordered_set>
#include <SDL2/SDL.h>

#undef main

const int PIXEL_SIZE = 16;  // Pixels.

class Chip8 {
 private:
  struct OpcodeTableEntry {
    uint16_t opcode;
    uint16_t mask;
    void (Chip8::*handler)(uint16_t);
    std::string mnemonic;
    std::string args;
  };

  uint8_t *screen{};
  uint32_t screen_w{}, screen_h{};

  // In case this fails, just use 0xEA0-0xEFF area for the stack.
  std::stack<uint16_t> call_stack;

  void InitializeOpcodeTable();

  void Opcode0NNN(uint16_t opcode);
  void Opcode00E0(uint16_t opcode);
  void Opcode00EE(uint16_t opcode);
  void Opcode1NNN(uint16_t opcode);
  void Opcode2NNN(uint16_t opcode);
  void Opcode3XNN(uint16_t opcode);
  void Opcode4XNN(uint16_t opcode);
  void Opcode5XY0(uint16_t opcode);
  void Opcode6XNN(uint16_t opcode);
  void Opcode7XNN(uint16_t opcode);
  void Opcode8XY0(uint16_t opcode);
  void Opcode8XY1(uint16_t opcode);
  void Opcode8XY2(uint16_t opcode);
  void Opcode8XY3(uint16_t opcode);
  void Opcode8XY4(uint16_t opcode);
  void Opcode8XY5(uint16_t opcode);
  void Opcode8XY6(uint16_t opcode);
  void Opcode8XY7(uint16_t opcode);
  void Opcode8XYE(uint16_t opcode);
  void Opcode9XY0(uint16_t opcode);
  void OpcodeANNN(uint16_t opcode);
  void OpcodeBNNN(uint16_t opcode);
  void OpcodeCXNN(uint16_t opcode);
  void OpcodeDXYN(uint16_t opcode);
  void OpcodeEX9E(uint16_t opcode);
  void OpcodeEXA1(uint16_t opcode);
  void OpcodeFX07(uint16_t opcode);
  void OpcodeFX0A(uint16_t opcode);
  void OpcodeFX15(uint16_t opcode);
  void OpcodeFX18(uint16_t opcode);
  void OpcodeFX1E(uint16_t opcode);
  void OpcodeFX29(uint16_t opcode);
  void OpcodeFX33(uint16_t opcode);
  void OpcodeFX55(uint16_t opcode);
  void OpcodeFX65(uint16_t opcode);

  void RedrawScreen();
  void DrawBigPixel(int x, int y, uint8_t color);

 public:
  Chip8();
  bool ReadMemoryImage(const char *fname);
  void Reset();
  void MainLoop();  // Can be run in a separate thread.
  void SetScreenBuffer(uint8_t *buf, uint32_t w, uint8_t h);

  uint16_t ArgNNN(uint16_t opcode) const;
  uint16_t ArgNN(uint16_t opcode) const;
  uint16_t ArgN(uint16_t opcode) const;
  uint16_t ArgX(uint16_t opcode) const;
  uint16_t ArgY(uint16_t opcode) const;

  std::vector<OpcodeTableEntry> opcode_table;
  std::vector<uint8_t> fb;
  std::vector<uint8_t> mem;
  uint8_t v[16]{};
  uint16_t i{};
  uint16_t pc{};

  uint8_t delay_timer{};
  uint8_t sound_timer{};

  bool key_pressed[0x10]{}; // 0-9 A-F
  int last_key_pressed{};
  // TODO(gynvael): add thread sync

  // Debugger stuff.
  std::unordered_set<int> debug_breakpoints;
  SDL_mutex *debug_breakpoints_mutex;

  bool debug_break_execution;


  SDL_atomic_t the_end{};
};

// https://dev.krzaq.cc/post/you-dont-need-a-stateful-deleter-in-your-unique_ptr-usually/
struct FileDeleter {
  void operator()(FILE* ptr) const {
    fclose(ptr);
  }
};

void Chip8::InitializeOpcodeTable() {
  // Bug spotted by Jan Vojtesek!
  opcode_table = std::vector<OpcodeTableEntry>{
    { /* 0x00E0 */ 0x00E0, 0xFFFF, &Chip8::Opcode00E0, "CLS", "" },
    { /* 0x00EE */ 0x00EE, 0xFFFF, &Chip8::Opcode00EE, "RET", "" },
    { /* 0x0NNN */ 0x0000, 0xF000, &Chip8::Opcode0NNN, "SYS", "NNN" },
    { /* 0x1NNN */ 0x1000, 0xF000, &Chip8::Opcode1NNN, "JP",  "NNN" },
    { /* 0x2NNN */ 0x2000, 0xF000, &Chip8::Opcode2NNN, "CALL", "NNN" },
    { /* 0x3XNN */ 0x3000, 0xF000, &Chip8::Opcode3XNN, "SE", "XNN" },
    { /* 0x4XNN */ 0x4000, 0xF000, &Chip8::Opcode4XNN, "SNE", "XNN" },
    { /* 0x5XY0 */ 0x5000, 0xF00F, &Chip8::Opcode5XY0, "SE", "XY" },
    { /* 0x6XNN */ 0x6000, 0xF000, &Chip8::Opcode6XNN, "LD", "XNN" },
    { /* 0x7XNN */ 0x7000, 0xF000, &Chip8::Opcode7XNN, "ADD", "XNN" },
    { /* 0x8XY0 */ 0x8000, 0xF00F, &Chip8::Opcode8XY0, "LD", "XY" },
    { /* 0x8XY1 */ 0x8001, 0xF00F, &Chip8::Opcode8XY1, "OR", "XY" },
    { /* 0x8XY2 */ 0x8002, 0xF00F, &Chip8::Opcode8XY2, "AND", "XY" },
    { /* 0x8XY3 */ 0x8003, 0xF00F, &Chip8::Opcode8XY3, "XOR", "XY"  },
    { /* 0x8XY4 */ 0x8004, 0xF00F, &Chip8::Opcode8XY4, "ADD", "XY"  },
    { /* 0x8XY5 */ 0x8005, 0xF00F, &Chip8::Opcode8XY5, "SUB", "XY"  },
    { /* 0x8XY6 */ 0x8006, 0xF00F, &Chip8::Opcode8XY6, "SHR", "XY"  },
    { /* 0x8XY7 */ 0x8007, 0xF00F, &Chip8::Opcode8XY7, "SUBN", "XY"  },
    { /* 0x8XYE */ 0x800E, 0xF00F, &Chip8::Opcode8XYE, "SHL", "XY"  },
    { /* 0x9XY0 */ 0x9000, 0xF00F, &Chip8::Opcode9XY0, "SNE", "XY"  },
    { /* 0xANNN */ 0xA000, 0xF000, &Chip8::OpcodeANNN, "LD", "NNN"  },
    { /* 0xBNNN */ 0xB000, 0xF000, &Chip8::OpcodeBNNN, "JP", "NNN"  },
    { /* 0xCXNN */ 0xC000, 0xF000, &Chip8::OpcodeCXNN, "RND", "XNN"  },
    { /* 0xDXYN */ 0xD000, 0xF000, &Chip8::OpcodeDXYN, "DRW", "XYN"  },
    { /* 0xEX9E */ 0xE09E, 0xF0FF, &Chip8::OpcodeEX9E, "SKP", "X"  },
    { /* 0xEXA1 */ 0xE0A1, 0xF0FF, &Chip8::OpcodeEXA1, "SKNP", "X"  },
    { /* 0xFX07 */ 0xF007, 0xF0FF, &Chip8::OpcodeFX07, "LD", "X"  },
    { /* 0xFX0A */ 0xF00A, 0xF0FF, &Chip8::OpcodeFX0A, "LD", "X"  },
    { /* 0xFX15 */ 0xF015, 0xF0FF, &Chip8::OpcodeFX15, "LDTimer", "X"  },
    { /* 0xFX18 */ 0xF018, 0xF0FF, &Chip8::OpcodeFX18, "LDSound", "X"  },
    { /* 0xFX1E */ 0xF01E, 0xF0FF, &Chip8::OpcodeFX1E, "ADD", "X"  },
    { /* 0xFX29 */ 0xF029, 0xF0FF, &Chip8::OpcodeFX29, "LD", "X"  },
    { /* 0xFX33 */ 0xF033, 0xF0FF, &Chip8::OpcodeFX33, "LD", "X"  },
    { /* 0xFX55 */ 0xF055, 0xF0FF, &Chip8::OpcodeFX55, "LD", "X"  },
    { /* 0xFX65 */ 0xF065, 0xF0FF, &Chip8::OpcodeFX65, "LD", "X"  }
  };
}

uint16_t Chip8::ArgNNN(uint16_t opcode) const {
  return opcode & 0x0fff;
}

uint16_t Chip8::ArgNN(uint16_t opcode) const {
  return opcode & 0x00ff;
}

uint16_t Chip8::ArgN(uint16_t opcode) const {
  return opcode & 0x000f;
}

uint16_t Chip8::ArgX(uint16_t opcode) const {
  return (opcode & 0x0f00) >> 8;
}

uint16_t Chip8::ArgY(uint16_t opcode) const {
  return (opcode & 0x00f0) >> 4;
}

void Chip8::Opcode0NNN(uint16_t opcode) {
  // TODO(gynvael): This is probably not implemented correctly.
  Opcode2NNN(opcode);
  //printf("(pc=%.4x: opcode0NNN not implemented, but used\n", pc);
}

void Chip8::Opcode00E0(uint16_t /*opcode*/) {
  memset(&fb[0], 0, fb.size());
  RedrawScreen();
}

void Chip8::Opcode00EE(uint16_t /*opcode*/) {
  if (call_stack.empty()) {
    printf("(pc=%.4x: stack empty, but return used?\n", pc);
    return;
  }
  pc = call_stack.top();

  call_stack.pop();
}

void Chip8::Opcode1NNN(uint16_t opcode) {
  pc = ArgNNN(opcode);
}


void Chip8::Opcode2NNN(uint16_t opcode) {
  call_stack.push(pc);
  pc = ArgNNN(opcode);
  // TODO(gynvael): Perhaps add a call_stack limit.
}


void Chip8::Opcode3XNN(uint16_t opcode) {
  if (v[ArgX(opcode)] == ArgNN(opcode)) {
    pc += 2;
  }
}

void Chip8::Opcode4XNN(uint16_t opcode) {
  if (v[ArgX(opcode)] != ArgNN(opcode)) {
    pc += 2;
  }
}

void Chip8::Opcode5XY0(uint16_t opcode) {
  if (v[ArgX(opcode)] == v[ArgY(opcode)]) {
    pc += 2;
  }
}

void Chip8::Opcode6XNN(uint16_t opcode) {
  v[ArgX(opcode)] = ArgNN(opcode);
}

void Chip8::Opcode7XNN(uint16_t opcode) {
  v[ArgX(opcode)] += ArgNN(opcode);
}


void Chip8::Opcode8XY0(uint16_t opcode) {
  v[ArgX(opcode)] = v[ArgY(opcode)];
}


void Chip8::Opcode8XY1(uint16_t opcode) {
  v[ArgX(opcode)] |= v[ArgY(opcode)];
}


void Chip8::Opcode8XY2(uint16_t opcode) {
  v[ArgX(opcode)] &= v[ArgY(opcode)];
}

void Chip8::Opcode8XY3(uint16_t opcode) {
  v[ArgX(opcode)] ^= v[ArgY(opcode)];
}

void Chip8::Opcode8XY4(uint16_t opcode) {
  uint16_t res = (uint16_t)v[ArgX(opcode)] + (uint16_t)v[ArgY(opcode)];
  v[ArgX(opcode)] = (uint8_t)res;
  v[0xf] = (res >= 0x100);
}

void Chip8::Opcode8XY5(uint16_t opcode) {
  int16_t res = (int16_t)v[ArgX(opcode)] - (int16_t)v[ArgY(opcode)];
  v[ArgX(opcode)] = (uint8_t)res;
  v[0xf] = (res >= 0);
}

void Chip8::Opcode8XY6(uint16_t opcode) {
  uint8_t lsb = v[ArgY(opcode)] & 1;
  uint8_t res = v[ArgY(opcode)] >> 1;
  v[ArgY(opcode)] = res;
  v[ArgX(opcode)] = res;
  v[0xf] = lsb;
}

void Chip8::Opcode8XY7(uint16_t opcode) {
  int16_t res = (int16_t)v[ArgY(opcode)] - (int16_t)v[ArgX(opcode)];
  v[ArgX(opcode)] = (uint8_t)res;
  v[0xf] = (res >= 0);
}

void Chip8::Opcode8XYE(uint16_t opcode) {
  uint8_t msb = v[ArgY(opcode)] >> 7;
  uint8_t res = v[ArgY(opcode)] << 1;
  v[ArgY(opcode)] = res;
  v[ArgX(opcode)] = res;
  v[0xf] = msb;
}

void Chip8::Opcode9XY0(uint16_t opcode) {
  if (v[ArgX(opcode)] != v[ArgY(opcode)]) {
    pc += 2;
  }
}

void Chip8::OpcodeANNN(uint16_t opcode) {
  i = ArgNNN(opcode);
}


void Chip8::OpcodeBNNN(uint16_t opcode) {
  pc = (v[0] + ArgNNN(opcode)) & 0xfff;
}


void Chip8::OpcodeCXNN(uint16_t opcode) {
  v[ArgX(opcode)] = rand() & ArgNN(opcode);
}

void Chip8::OpcodeDXYN(uint16_t opcode) {
  uint8_t x = v[ArgX(opcode)] % 64;  // Not wrap around?
  uint8_t y = v[ArgY(opcode)] % 32;  // TODO(gynvael)
  uint8_t n = ArgN(opcode);
  bool flipped = false;

  for (int j = 0; j < n; j++, y++) {
    uint8_t px = mem.at(i + j);
    for (int k = 0; k < 8; k++) {
      uint8_t bit = ((px >> (7 - k)) & 1);

      if (bit && fb[x + k + y * 64]) {
        flipped |= true;
      }

      fb[x + k + y * 64] ^= bit;
    }
  }

  v[0xf] = flipped;

  RedrawScreen();
}

void Chip8::OpcodeEX9E(uint16_t opcode) {
  int idx = v[ArgX(opcode)];
  bool pressed = false;
  if (idx < 0x10) {
    pressed = key_pressed[idx];
  }

  if (pressed) {
    pc += 2;
  }
}

void Chip8::OpcodeEXA1(uint16_t opcode) {
  int idx = v[ArgX(opcode)];
  bool pressed = false;
  if (idx < 0x10) {
    pressed = key_pressed[idx];
  }

  if (!pressed) {
    pc += 2;
  }
}

void Chip8::OpcodeFX07(uint16_t opcode) {
  v[ArgX(opcode)] = delay_timer;
}

void Chip8::OpcodeFX0A(uint16_t opcode) {
  int k;
  // TODO(gynvael): Handle this race condition in a sane way.
  while ((k = last_key_pressed) == -1) {
    SDL_Delay(5);
  }

  v[ArgX(opcode)] = k;
}

void Chip8::OpcodeFX15(uint16_t opcode) {
  delay_timer = v[ArgX(opcode)];
}


void Chip8::OpcodeFX18(uint16_t opcode) {
  sound_timer = v[ArgX(opcode)];
}


void Chip8::OpcodeFX1E(uint16_t opcode) {
  i = (i + v[ArgX(opcode)]) & 0xfff;
}


void Chip8::OpcodeFX29(uint16_t /*opcode*/) {
  // TODO(gynvael): Add font support.
   i = 0;
}

void Chip8::OpcodeFX33(uint16_t opcode) {
  uint16_t bcd = v[ArgX(opcode)];
  mem.at(i + 0) = bcd / 100;
  mem.at(i + 1) = (bcd / 10) % 10;
  mem.at(i + 2) = bcd % 10;
}

void Chip8::OpcodeFX55(uint16_t opcode) {
  int last_reg = ArgX(opcode);
  for (int j = 0; j <= last_reg; j++, i++) {
    mem.at(i) = v[j];
  }
}

void Chip8::OpcodeFX65(uint16_t opcode) {
  int last_reg = ArgX(opcode);
  for (int j = 0; j <= last_reg; j++, i++) {
    v[j] = mem.at(i);
  }
}

Chip8::Chip8() {
  debug_breakpoints_mutex = SDL_CreateMutex();
  debug_break_execution = true;

  fb.resize(64 * 32);
  mem.resize(4096);
  InitializeOpcodeTable();
  Reset();
}

bool Chip8::ReadMemoryImage(const char *fname) {
  std::unique_ptr<FILE, FileDeleter> f;
  f.reset(fopen(fname, "rb"));
    if (f == nullptr) {
    return false;
  }

  return fread(&mem[0] + 512, 1, 4096 - 512, f.get()) > 0;
}

void Chip8::SetScreenBuffer(uint8_t *buf, uint32_t w, uint8_t h) {
  screen = buf;
  screen_w = w;
  screen_h = h;
}

void Chip8::DrawBigPixel(int x, int y, uint8_t color) {
  if (x < 0 || x >= 64 || y < 0 || y >= 32) {
    return;
  }

  for (int k = y * PIXEL_SIZE; k < (y + 1) * PIXEL_SIZE; k++) {
    for (int j = x * PIXEL_SIZE; j < (x + 1) * PIXEL_SIZE; j++) {
      screen[(k * screen_w + j) * 4 + 0] = color;
      screen[(k * screen_w + j) * 4 + 1] = color;
      screen[(k * screen_w + j) * 4 + 2] = color;
      screen[(k * screen_w + j) * 4 + 3] = color;
    }
  }
}

void Chip8::RedrawScreen() {
  if (screen == nullptr) {
    return;
  }

  // Bug spotted by Dawid S!
  for (int y = 0; y < 32; y++) {
    for (int x = 0; x < 64; x++) {
      DrawBigPixel(x, y, fb[x + y * 64] * 0xff);
    }
  }
}

void Chip8::Reset() {
  memset(&mem[0], 0, mem.size());

  for (int i = 0; i < 16; i++) {
    v[i] = 0;
  }

  this->i = 0;

  pc = 0x200;

  delay_timer = 0;
  sound_timer = 0;

  last_key_pressed = -1;
  for (int i = 0; i < 0x10; i++) {
    key_pressed[i] = false;
  }
}

void Chip8::MainLoop() {
  uint32_t last_ticks = SDL_GetTicks();

  for (;;) {
    if (SDL_AtomicGet(&the_end) != 0) {
      break;
    }

    // Handle timers.
    uint32_t now = SDL_GetTicks();
    if (now - last_ticks > 16) {
      uint32_t diff = now - last_ticks;
      uint32_t timer_ticks = diff / 16;

      delay_timer = std::max(0, (int)delay_timer - (int)timer_ticks);
      sound_timer = std::max(0, (int)sound_timer - (int)timer_ticks);

      last_ticks = now - diff % 16;  // Take into account "unused time".
    }

    // Execute the instruction.
    uint16_t opcode;
    if (pc + 1 >= 4096) {
      printf("error: pc out of bound (%.4x)\n", pc);
      return;
    }

    SDL_LockMutex(debug_breakpoints_mutex);
    if (debug_breakpoints.find((int)pc) !=
        debug_breakpoints.end()) {
      puts("Breakpoint Hit!");
      debug_break_execution = true;
    }
    SDL_UnlockMutex(debug_breakpoints_mutex);

    while (debug_break_execution) {
      SDL_Delay(10);

      if (SDL_AtomicGet(&the_end) != 0) {
        return;
      }
    }

    opcode = mem.at(pc) << 8;  // Big Endian
    opcode |= mem.at(pc + 1);
    pc += 2;

    for (const auto& entry : opcode_table) {
      if ((opcode & entry.mask) == entry.opcode) {
        auto handler = entry.handler;
        (this->*handler)(opcode);
        break;
      }
    }

    SDL_Delay(1);  // TODO(gynvael): Remove to allow the VM to run at full speed.
  }
}

int VMThreadFunc(void *vm_obj) {
  Chip8 *vm = (Chip8*)vm_obj;
  vm->MainLoop();
  return 0;
}

void DebugCmdBreakpoint(
    const char */*cmd*/, const std::vector<std::string>& args, Chip8 *vm) {
  if (args.size() != 1) {
    printf("Error: Wrong argument count, expected 1 argument (address)\n");
    return;
  }

  int break_pc;

  if (sscanf(args[0].c_str(), "%x", &break_pc) != 1) {
    printf("Error: Wrong argument format; should be address.\n");
    return;
  }

  SDL_LockMutex(vm->debug_breakpoints_mutex);
  vm->debug_breakpoints.insert(break_pc);
  SDL_UnlockMutex(vm->debug_breakpoints_mutex);
  printf("Breakpoint at %x set!\n", break_pc);
}

void DebugCmdQuit(
    const char* /*cmd*/, const std::vector<std::string>& /*args*/, Chip8 *vm) {
  SDL_AtomicSet(&vm->the_end, 1);
}

void DebugCmdRun(
    const char* /*cmd*/, const std::vector<std::string>& /*args*/, Chip8 *vm) {
  vm->debug_break_execution = false;
}

void DebugCmdRegisters(
    const char* /*cmd*/, const std::vector<std::string>& /*args*/, Chip8 *vm) {
  for (int i = 0; i < 16; i++) {
    char reg_name[8]{};
    sprintf(reg_name, "V%i", i);
    printf("%3s: %.2x    ", reg_name, vm->v[i]);
    if (i % 4 == 3) {
      putchar('\n');
    }
  }
  printf("  I: %.4x\n", vm->i);
  printf(" PC: %.4x\n", vm->pc);
}

void DebugCmdReadMemory(
    const char* /*cmd*/, const std::vector<std::string>& args, Chip8 *vm) {
  if (args.size() != 3) {
    puts("usage: x <type> <address_hex> <count_hex/dec>");
    puts("types: b (byte), w (word)");
    return;
  }

  if (args[0] != "b" && args[0] != "w") {
    puts("error: incorrect type");
    return;
  }

  unsigned int addr;
  if (sscanf(args[1].c_str(), "%x", &addr) != 1 ||
      addr >= vm->mem.size()) {
    puts("error: incorrect address");
    return;
  }

  int count;
  if (sscanf(args[2].c_str(), "%i", &count) != 1 ||
      count < 0 ||
      (unsigned)count > vm->mem.size() ||
      addr + count > vm->mem.size()) {
    puts("error: incorrect count");
    return;
  }

  if (args[0] == "b") {
    enum class ByteHexStates {
      STATE_START_OF_LINE,  // Print out the address.
      STATE_BYTES_1,        // Up to 8 bytes.
      STATE_MIDDLE_SEP,     // Middle separator.
      STATE_BYTES_2,        // Up to 8 bytes.
      STATE_END_SEP,        // End separator.
      STATE_CHARS,          // Printable characters.
      STATE_NEW_LINE
    } state = ByteHexStates::STATE_START_OF_LINE;

    int i = 0;  // STATE_BYTES_1, STATE_BYTES_2
    unsigned int addr_hex = addr;   // STATE_BYTES_1, STATE_BYTES_2
    unsigned int addr_char = addr;  // STATE_CHARS

    unsigned int end_addr = addr + (unsigned int)count;

    bool done = false;

    while (!done) {
      switch (state) {
        case ByteHexStates::STATE_START_OF_LINE:
          printf("%.4x:", addr_hex);
          state = ByteHexStates::STATE_BYTES_1;
          i = 0;
          continue;

        case ByteHexStates::STATE_BYTES_2:
        case ByteHexStates::STATE_BYTES_1:
          if (addr_hex < end_addr) {
            printf(" %.2x", vm->mem.at(addr_hex));
            addr_hex++;
          } else {
            printf("   ");
          }

          i++;
          if (i == 8) {
            if (state == ByteHexStates::STATE_BYTES_1) {
              state = ByteHexStates::STATE_MIDDLE_SEP;
            } else {
              state = ByteHexStates::STATE_END_SEP;
            }
          }
          continue;

        case ByteHexStates::STATE_MIDDLE_SEP:
          putchar(' ');
          i = 0;
          state = ByteHexStates::STATE_BYTES_2;
          continue;

        case ByteHexStates::STATE_END_SEP:
          printf(" | ");
          i = 0;
          state = ByteHexStates::STATE_CHARS;
          continue;

        case ByteHexStates::STATE_CHARS:
          if (addr_char < end_addr) {
            uint8_t b = vm->mem.at(addr_char);
            if (isprint(b)) {
              putchar((int)b);
            } else {
              putchar('.');
            }
            addr_char++;
          } else {
            putchar(' ');
          }

          i++;
          if (i == 16) {
            state = ByteHexStates::STATE_NEW_LINE;
          }
          continue;

        case ByteHexStates::STATE_NEW_LINE:
          putchar('\n');
          if (addr_hex >= end_addr && addr_char >= end_addr) {
            done = true;
            continue;
          }
          i = 0;
          state = ByteHexStates::STATE_START_OF_LINE;
          continue;
      }
    }

    return;
  }

  if (args[0] == "w") {
    int i;
    for(i = 0; i < count; i ++) {

      if((i % 8) == 0) {
        printf("%.4x:", addr + i * 2);
      }

      uint8_t b0 = vm->mem.at(addr + i * 2);
      uint8_t b1 = vm->mem.at(addr + i * 2 + 1);
      uint16_t w = (b0 << 8) | b1;

      printf(" %.4x", w);

      if(i + 1 == count || ((i + 1) % 8) == 0) {
        putchar('\n');
      }
    }
  }
}

void DebuggerDisasm(Chip8 *vm, uint16_t addr, uint16_t opcode) {
  for (const auto& entry : vm->opcode_table) {
    if ((opcode & entry.mask) == entry.opcode) {
      printf("%.4x: %s ", addr, entry.mnemonic.c_str());

      if (entry.args.empty()) {
        return;
      }

      if (entry.args == "NNN") {
        if ((opcode & 0xf000) == 0xa000) {
          printf("I, ");
        } else if ((opcode & 0xf000) == 0xb000) {
          printf("PC, ");
        }
        printf("0x%.3x\n", vm->ArgNNN(opcode));
        return;
      }

      if (entry.args == "XNN") {
        printf("V%i, 0x%.2x\n",
          vm->ArgX(opcode), vm->ArgNN(opcode));
        return;
      }

      if (entry.args == "XY") {
        printf("V%i, V%i\n",
          vm->ArgX(opcode), vm->ArgY(opcode));
        return;
      }

      if (entry.args == "XYN") {
        printf("V%i, V%i, 0x%x\n",
          vm->ArgX(opcode),
          vm->ArgY(opcode),
          vm->ArgN(opcode));
        return;
      }

      if (entry.args == "X") {
        printf("V%i\n", vm->ArgX(opcode));
        return;
      }

      printf("???\n");
      return;
    }
  }

  printf("%.4x: ???\n", addr);
}

void DebugCmdDisassemble(
    const char* /*cmd*/, const std::vector<std::string>& args, Chip8 *vm) {

  if (args.size() != 1 && args.size() != 2) {
    puts("usage: disas <address_hex> [count_hex/dec]");
    return;
  }

  unsigned int addr;
  if (sscanf(args[0].c_str(), "%x", &addr) != 1 ||
      addr >= vm->mem.size()) {
    puts("error: incorrect address");
    return;
  }

  int count = 10;
  if (args.size() == 2) {
    if (sscanf(args[1].c_str(), "%i", &count) != 1) {
      puts("error: incorrect count");
      return;
    }
  }

  for (int i = 0; i < count && addr + 1 < vm->mem.size(); i++, addr+=2) {
    uint8_t b0 = vm->mem.at(addr);
    uint8_t b1 = vm->mem.at(addr + 1);
    uint16_t w = (b0 << 8) | b1;
    DebuggerDisasm(vm, addr, w);
  }
}

int DebugThreadFunc(void *vm_obj) {
  Chip8 *vm = (Chip8*)vm_obj;

  std::unordered_map<
      std::string,
      std::function<
          void(const char*, const std::vector<std::string>&, Chip8*)>> debug_cmds = {
    { "b", DebugCmdBreakpoint },
    { "break", DebugCmdBreakpoint },
    { "q", DebugCmdQuit },
    { "quit", DebugCmdQuit },
    { "exit", DebugCmdQuit },
    { "bye", DebugCmdQuit },
    { "run", DebugCmdRun },
    { "start", DebugCmdRun },
    { "go", DebugCmdRun },
    { "g", DebugCmdRun },
    { "r", DebugCmdRegisters },
    { "reg", DebugCmdRegisters },
    { "regs", DebugCmdRegisters },
    { "registers", DebugCmdRegisters },
    { "x", DebugCmdReadMemory },
    { "mem", DebugCmdReadMemory },
    { "memory", DebugCmdReadMemory },
    { "dis", DebugCmdDisassemble },
    { "disas", DebugCmdDisassemble },
    { "disasm", DebugCmdDisassemble },
    { "disassemble", DebugCmdDisassemble }
  };

  for (;;) {
    if (SDL_AtomicGet(&vm->the_end) != 0) {
      break;
    }

    printf("chip8dbg> ");
    fflush(stdout);
    char line[2048]{};
    if (scanf(" %2047[^\n]", line) != 1) {
      continue;
    }

    char *p = line;

    char cmd[2048]{};
    int cmd_size{};
    sscanf(p, "%2047s%n", cmd, &cmd_size);
    p += cmd_size;

    std::vector<std::string> args;
    for (;;) {
      char arg[2048]{};
      int arg_size{};
      if (sscanf(p, " %2047s%n", arg, &arg_size) != 1) {
        break;
      }

      args.emplace_back(std::string(arg));

      p += arg_size;
    }

    const auto func = debug_cmds.find(cmd);
    if (func == debug_cmds.end()) {
      printf("Command \"%s\" not found.\n", cmd);
      continue;
    }

    func->second(cmd, args, vm);
  }

  puts("Bye.");
  return 0;
}


int TranslateCodeToIndex(SDL_Keycode key) {
  switch (key) {
    case SDLK_0: return 0;
    case SDLK_1: return 1;
    case SDLK_2: return 2;
    case SDLK_3: return 3;
    case SDLK_4: return 4;
    case SDLK_5: return 5;
    case SDLK_6: return 6;
    case SDLK_7: return 7;
    case SDLK_8: return 8;
    case SDLK_9: return 9;
    case SDLK_a: return 10;
    case SDLK_b: return 11;
    case SDLK_c: return 12;
    case SDLK_d: return 13;
    case SDLK_e: return 14;
    case SDLK_f: return 15;

    case SDLK_KP_0: return 0;
    case SDLK_KP_1: return 1;
    case SDLK_KP_2: return 2;
    case SDLK_KP_3: return 3;
    case SDLK_KP_4: return 4;
    case SDLK_KP_5: return 5;
    case SDLK_KP_6: return 6;
    case SDLK_KP_7: return 7;
    case SDLK_KP_8: return 8;
    case SDLK_KP_9: return 9;

    case SDLK_DOWN: return 8;
    case SDLK_UP: return 2;
    case SDLK_LEFT: return 4;
    case SDLK_RIGHT: return 6;
  }

  return -1;
}

int main(int argc, char **argv) {
  if (argc != 2) {
    puts("usage: chip8 <filename>");
    return 1;
  }

  auto vm = std::make_unique<Chip8>();
  if (!vm->ReadMemoryImage(argv[1])) {
    puts("failed to read RAM image");
    return 2;
  }

  // http://www.willusher.io/sdl2%20tutorials/2013/08/17/lesson-1-hello-world
  if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER | SDL_INIT_EVENTS) != 0) {
    puts("SDL failed");
    return 3;
  }

  SDL_Window *win = SDL_CreateWindow(
    "CHIP8", SDL_WINDOWPOS_CENTERED, /*SDL_WINDOWPOS_CENTERED*/ 1200 + 200,
    64 * PIXEL_SIZE, 32 * PIXEL_SIZE, SDL_WINDOW_SHOWN);
  if (win == nullptr) {
    puts("SDL failed");
    SDL_Quit();
    return 4;
  }

  SDL_Renderer *ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
  if (ren == nullptr){
    puts("SDL failed");
    SDL_DestroyWindow(win);
    SDL_Quit();
    return 1;
  }

  SDL_Surface *surface = SDL_GetWindowSurface(win);

  SDL_Thread *th = SDL_CreateThread(VMThreadFunc, "vm thread", vm.get());
  SDL_Thread *debug_th = SDL_CreateThread(
      DebugThreadFunc, "debugger thread", vm.get());

  vm->SetScreenBuffer((uint8_t*)surface->pixels, surface->w, surface->h);

  SDL_Event e;
  bool the_end = false;
  while (!the_end && SDL_AtomicGet(&vm->the_end) == 0) {
    while (SDL_PollEvent(&e)) {
      if (e.type == SDL_QUIT) {
        the_end = true;
        break;
      }

      if (e.type == SDL_KEYDOWN || e.type == SDL_KEYUP) {
        int idx = TranslateCodeToIndex(e.key.keysym.sym);
        if (idx != -1) {
          vm->key_pressed[idx] = e.key.state == SDL_PRESSED;

          if (e.key.state == SDL_PRESSED) {
            vm->last_key_pressed = idx;
          } else {
            bool all_keys_are_released = true;
            for (int i = 0; i < 16; i++) {
              if (vm->key_pressed[i]) {
                all_keys_are_released = false;
                break;
              }
            }

            if (all_keys_are_released) {
              vm->last_key_pressed = -1;
            }
          }
        }
      }

    }
    SDL_UpdateWindowSurface(win);
  }

  SDL_AtomicSet(&vm->the_end, 1);
  SDL_WaitThread(th, nullptr);
  SDL_WaitThread(debug_th, nullptr);

  SDL_DestroyRenderer(ren);
  SDL_DestroyWindow(win);
  SDL_Quit();
  return 0;
}
