#include <cstdio>
#include <stdint.h>
#include <memory>
#include <cstdlib>
#include <SDL2/SDL.h>
#undef main

const int PIXEL_SIZE = 16;  // Pixels.

class Chip8 {
 public:
  bool ReadMemoryImage(const char *fname);
  void Reset();
  void MainLoop();  // Can be run in a separate thread.

  uint8_t mem[4096]{};
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

bool Chip8::ReadMemoryImage(const char *fname) {
  std::unique_ptr<FILE, FileDeleter> f;
  f.reset(fopen(fname, "rb"));
    if (f == nullptr) {
    return false;
  }

  return fread(mem + 512, 1, 4096 - 512, f.get()) > 0;
}

void Chip8::Reset() {
  memset(mem, 0, sizeof(mem));

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
  vm->Reset();
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


  uint8_t *px = (uint8_t*)surface->pixels;
  px[256 * surface->pitch + 512 * 4] = 0xff;

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
