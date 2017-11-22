all:
	nasm keycheck.vasm
	objcopy --input binary --output pe-x86-64 --binary-architecture i386:x86-64 \
	  keycheck keycheck.o
	g++ -Wall -Wextra app.cc keycheck.o -o app.exe -O3

