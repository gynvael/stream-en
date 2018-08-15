#include <cstdio>
#include <cstdlib>
#include <windows.h>
#include <unordered_map>
#include <assert.h>

static void HandleException(
    const DEBUG_EVENT& ev,
    HANDLE ph,
    HANDLE th) {

  CONTEXT ctx{};
  ctx.ContextFlags = CONTEXT_CONTROL | CONTEXT_INTEGER;

  BOOL ret = GetThreadContext(th, &ctx);
  assert(ret);

  if ((ctx.Rip & 0xfffffffffff00000) !=
                 0x0000000000400000) {
    return;
  }

  // UD2 is 0f 0b
  BYTE buf[2]{};
  SIZE_T actually_read = 0;
  ret = ReadProcessMemory(
      ph, (void*)ctx.Rip, buf, 2, &actually_read);
  assert(ret);

  if (buf[0] == 0x0f && buf[1] == 0x0b) {
    long long a = (long long)(int)ctx.Rdx;
    long long b = (long long)(int)ctx.Rcx;
    ctx.Rax = (int)(a + b);
    ctx.Rip += 2;
    SetThreadContext(th, &ctx);
  }

  printf("RIP: %p\n", (void*)ctx.Rip);
}

int Debugger() {
  puts("Debugger");
  _putenv("YOUARETHESECOND=1");

  STARTUPINFO si{};
  si.cb = sizeof(si);
  PROCESS_INFORMATION pi{};

  BOOL ret = CreateProcess(
    "nano.exe", NULL,
    NULL, NULL,
    FALSE,
    DEBUG_PROCESS,
    NULL,
    NULL,
    &si, &pi);

  DEBUG_EVENT ev;
  std::unordered_map<DWORD, HANDLE> threads;

  threads[pi.dwThreadId] = pi.hThread;

  bool the_end = false;
  while (!the_end) {
    ret = WaitForDebugEvent(&ev, INFINITE);
    if (!ret) {
      printf("WaitForDebugEvent failed: %u\n", GetLastError());
      return 1;
    }

    switch (ev.dwDebugEventCode) {
      case EXCEPTION_DEBUG_EVENT:
        HandleException(ev, pi.hProcess, threads[ev.dwThreadId]);
        break;

      case EXIT_PROCESS_DEBUG_EVENT:
        the_end = true;
        break;

      case CREATE_THREAD_DEBUG_EVENT:
        threads[ev.dwThreadId] = ev.u.CreateThread.hThread;
        break;

      case EXIT_THREAD_DEBUG_EVENT:
        CloseHandle(threads[ev.dwThreadId]);
        threads.erase(ev.dwThreadId);
        break;

      case CREATE_PROCESS_DEBUG_EVENT:
        CloseHandle(ev.u.CreateProcessInfo.hFile);
        CloseHandle(ev.u.CreateProcessInfo.hProcess);
        CloseHandle(ev.u.CreateProcessInfo.hThread);
        break;

      case LOAD_DLL_DEBUG_EVENT:
      case UNLOAD_DLL_DEBUG_EVENT:
        break;

      default:
        printf("Ev: %u\n", ev.dwDebugEventCode);
        break;
    }

    ContinueDebugEvent(
      ev.dwProcessId, ev.dwThreadId, DBG_CONTINUE);
  }



  CloseHandle(pi.hThread);
  CloseHandle(pi.hProcess);


  return 0;
}

