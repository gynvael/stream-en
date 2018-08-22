#include <cstdio>
#include <cstdlib>
#include <unordered_map>
#include <assert.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <unistd.h>
#include <errno.h>
#include "debuggee.h"

static void HandleException(int pid) {
  struct user u{};
  ptrace(PTRACE_GETREGS, pid, 0, &u);

  // UD2 is 0f 0b
  long ret = ptrace(PTRACE_PEEKDATA, pid, (void*)u.regs.rip, 0);
  unsigned char buf[2] = {
      (unsigned char)(ret & 0xff),
      (unsigned char)((ret >> 8) & 0xff)
  };

  if (buf[0] == 0x0f && buf[1] == 0x0b) {
    long long a = (long long)(int)u.regs.rdi;
    long long b = (long long)(int)u.regs.rsi;
    u.regs.rax = (int)(a + b);
    u.regs.rip += 2;
    ptrace(PTRACE_SETREGS, pid, 0, &u);
  }
}

int Debugger() {
  puts("Debugger");

  // 1. Start the process and debug it
  int pid = fork();

  if (pid == 0) {
    // Child.
    ptrace(PTRACE_TRACEME, 0, 0, 0);
    return Debuggee();
  }

  // Parent.
  printf("Child PID: %i\n", pid);

  // 2. Debugger event loop
  bool the_end = false;
  while (!the_end) {
    int status = 0;
    int ret = waitpid(pid, &status, 0);

    //printf("ret: %i, status: %i\n", ret, status);

    if (WIFEXITED(status)) {
      puts("Child exited");
      the_end = true;
    } else if (WIFSIGNALED(status)) {
      int s = WTERMSIG(status);
      //printf("Child has signaled: %i\n", s);
      the_end = true;
    } else if (WIFSTOPPED(status)) {
      int s = WSTOPSIG(status);
      //printf("Child has stopped: %i\n", s);
      if (s == SIGILL) {
        HandleException(pid);
      }
    }

    ptrace(PTRACE_CONT, pid, 0, 0);
  }

  return 0;
}

