#include <cstdio>
#include <stdint.h>
#include <memory>
#include <cstdlib>
#include <vector>
#include <SDL2/SDL.h>

#undef main

const int PIXEL_SIZE = 16;  // Pixels.

class Chip8 {
 private:
  struct OpcodeTableEntry {
    uint16_t opcode;
    uint16_t mask;
    void (Chip8::*handler)(uint16_t);
  };

  std::vector<OpcodeTableEntry> opcode_table;

  uint8_t *screen{};
  uint32_t screen_w{}, screen_h{};

  void InitializeOpcodeTable();

  uint16_t ArgNNN(uint16_t opcode) const;
  uint16_t ArgNN(uint16_t opcode) const;
  uint16_t ArgN(uint16_t opcode) const;
  uint16_t ArgX(uint16_t opcode) const;
  uint16_t ArgY(uint16_t opcode) const;

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

  std::vector<uint8_t> fb;
  std::vector<uint8_t> mem;
  uint8_t v[16]{};
  uint16_t i{};
  uint16_t pc{};

  SDL_atomic_t the_end{};
};

// https://dev.krzaq.cc/post/you-dont-need-a-stateful-deleter-in-your-unique_ptr-usually/
struct FileDeleter {
  void operator()(FILE* ptr) const {
    fclose(ptr);
  }
};

void Chip8::InitializeOpcodeTable() {
  opcode_table = std::vector<OpcodeTableEntry>{
    { /* 0x0NNN */ 0x0000, 0xF000, &Chip8::Opcode0NNN },
    { /* 0x00E0 */ 0x00E0, 0xFFFF, &Chip8::Opcode00E0 },
    { /* 0x00EE */ 0x00EE, 0xFFFF, &Chip8::Opcode00EE },
    { /* 0x1NNN */ 0x1000, 0xF000, &Chip8::Opcode1NNN },
    { /* 0x2NNN */ 0x2000, 0xF000, &Chip8::Opcode2NNN },
    { /* 0x3XNN */ 0x3000, 0xF000, &Chip8::Opcode3XNN },
    { /* 0x4XNN */ 0x4000, 0xF000, &Chip8::Opcode4XNN },
    { /* 0x5XY0 */ 0x5000, 0xF00F, &Chip8::Opcode5XY0 },
    { /* 0x6XNN */ 0x6000, 0xF000, &Chip8::Opcode6XNN },
    { /* 0x7XNN */ 0x7000, 0xF000, &Chip8::Opcode7XNN },
    { /* 0x8XY0 */ 0x8000, 0xF00F, &Chip8::Opcode8XY0 },
    { /* 0x8XY1 */ 0x8001, 0xF00F, &Chip8::Opcode8XY1 },
    { /* 0x8XY2 */ 0x8002, 0xF00F, &Chip8::Opcode8XY2 },
    { /* 0x8XY3 */ 0x8003, 0xF00F, &Chip8::Opcode8XY3 },
    { /* 0x8XY4 */ 0x8004, 0xF00F, &Chip8::Opcode8XY4 },
    { /* 0x8XY5 */ 0x8005, 0xF00F, &Chip8::Opcode8XY5 },
    { /* 0x8XY6 */ 0x8006, 0xF00F, &Chip8::Opcode8XY6 },
    { /* 0x8XY7 */ 0x8007, 0xF00F, &Chip8::Opcode8XY7 },
    { /* 0x8XYE */ 0x800E, 0xF00F, &Chip8::Opcode8XYE },
    { /* 0x9XY0 */ 0x9000, 0xF00F, &Chip8::Opcode9XY0 },
    { /* 0xANNN */ 0xA000, 0xF000, &Chip8::OpcodeANNN },
    { /* 0xBNNN */ 0xB000, 0xF000, &Chip8::OpcodeBNNN },
    { /* 0xCXNN */ 0xC000, 0xF000, &Chip8::OpcodeCXNN },
    { /* 0xDXYN */ 0xD000, 0xF000, &Chip8::OpcodeDXYN },
    { /* 0xEX9E */ 0xE09E, 0xF0FF, &Chip8::OpcodeEX9E },
    { /* 0xEXA1 */ 0xE0A1, 0xF0FF, &Chip8::OpcodeEXA1 },
    { /* 0xFX07 */ 0xF007, 0xF0FF, &Chip8::OpcodeFX07 },
    { /* 0xFX0A */ 0xF00A, 0xF0FF, &Chip8::OpcodeFX0A },
    { /* 0xFX15 */ 0xF015, 0xF0FF, &Chip8::OpcodeFX15 },
    { /* 0xFX18 */ 0xF018, 0xF0FF, &Chip8::OpcodeFX18 },
    { /* 0xFX1E */ 0xF01E, 0xF0FF, &Chip8::OpcodeFX1E },
    { /* 0xFX29 */ 0xF029, 0xF0FF, &Chip8::OpcodeFX29 },
    { /* 0xFX33 */ 0xF033, 0xF0FF, &Chip8::OpcodeFX33 },
    { /* 0xFX55 */ 0xF055, 0xF0FF, &Chip8::OpcodeFX55 },
    { /* 0xFX65 */ 0xF065, 0xF0FF, &Chip8::OpcodeFX65 }
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
}

void Chip8::Opcode00E0(uint16_t opcode) {
  memset(&fb[0], 0, fb.size());
  RedrawScreen();
}

void Chip8::Opcode00EE(uint16_t opcode) {
}

void Chip8::Opcode1NNN(uint16_t opcode) {
  pc = ArgNNN(opcode);
}


void Chip8::Opcode2NNN(uint16_t opcode) {
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
      uint8_t bit = ((px >> k) & 1);

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
}


void Chip8::OpcodeEXA1(uint16_t opcode) {
}


void Chip8::OpcodeFX07(uint16_t opcode) {
}


void Chip8::OpcodeFX0A(uint16_t opcode) {
}


void Chip8::OpcodeFX15(uint16_t opcode) {
}


void Chip8::OpcodeFX18(uint16_t opcode) {
}


void Chip8::OpcodeFX1E(uint16_t opcode) {
  i = (i + v[ArgX(opcode)]) & 0xfff;
}


void Chip8::OpcodeFX29(uint16_t opcode) {
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

  for (int y = 0; y < 32; y++) {
    for (int x = 0; y < 64; y++) {
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

  // TODO(gynvael): add timer initialization.
}

void Chip8::MainLoop() {




  for (;;) {
    if (SDL_AtomicGet(&the_end) != 0) {
      break;
    }



    SDL_Delay(1);  // TODO(gynvael): Remove to allow the VM to run at full speed.
  }
}

int VMThreadFunc(void *vm_obj) {
  Chip8 *vm = (Chip8*)vm_obj;
  vm->MainLoop();
  return 0;
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
    "CHIP8", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
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

  vm->SetScreenBuffer((uint8_t*)surface->pixels, surface->w, surface->h);

  SDL_Event e;
  bool the_end = false;
  while (!the_end) {
    while (SDL_PollEvent(&e)) {
      if (e.type == SDL_QUIT) {
        the_end = true;
        break;
      }
    }
    SDL_UpdateWindowSurface(win);
  }

  SDL_AtomicSet(&vm->the_end, 1);
  SDL_WaitThread(th, nullptr);

  SDL_DestroyRenderer(ren);
  SDL_DestroyWindow(win);
  SDL_Quit();
  return 0;
}
