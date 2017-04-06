#include <stdio.h>
#include <windows.h>

volatile DWORD *ptr;

bool FakeSyscall() {
  if (*ptr == 10) {
    if (*ptr == 5) {
      return true;
    }
  }

  return false;
}


DWORD WINAPI MyProc(LPVOID) {
  LARGE_INTEGER start, stop;

  QueryPerformanceCounter(&start);  

  int i = 0;
  while (i < 10000) {
    if (FakeSyscall()) {
      i++;
    }
  }
  QueryPerformanceCounter(&stop);

  LONGLONG delta = stop.QuadPart - start.QuadPart;
  printf("%I64u\n", delta);

  return 0;
}

#define COUNT 5000

BYTE arr[COUNT] = {};
LONGLONG delta[COUNT];

int main(void) {



  //DWORD tid = 0;

  //HANDLE hth = CreateThread(0, 0, MyProc, 0, 0, &tid);

  //*ptr = 5;

  

  for (int j = 0; j < COUNT; j++) {
    ptr = (DWORD*)&arr[j];

    LARGE_INTEGER start, stop;
    DWORD sum = 0;
    QueryPerformanceCounter(&start);  
    for (int i = 0; i < 1000 * 1000; i++) {
      sum += *ptr;
    }
    QueryPerformanceCounter(&stop);

    delta[j] = stop.QuadPart - start.QuadPart;
  }

  for (int j = 0; j < COUNT; j++) {
    printf("[%i] %I64u\n", j, delta[j]);  
  }    


  //CloseHandle(hth);



  return 0;
}


