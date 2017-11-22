%define vr0 0
%define vr1 1
%define vr2 2
%define vr3 3
%define vr4 4
%define vr5 5
%define vr6 6
%define vr7 7

%macro vxor 2
  db 0x00, %1, %2
%endmacro

%macro vand 2
  db 0x01, %1, %2
%endmacro

%macro vor 2
  db 0x02, %1, %2
%endmacro

%macro vmovi 2
  db 0x10, %1
  dd %2
%endmacro

%macro vmov 2
  db 0x11, %1, %2
%endmacro

%macro vend 0
  db 0xff
%endmacro


