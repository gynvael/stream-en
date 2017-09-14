[bits 64]
[org 0x4a0584]

push rax
push rdi
push rsi
push rdx
push rcx

mov rdi, 0x400000  ; 0xabcd1234
mov rsi, 0xa1000
mov rdx, 7  ; RWX
mov rax, 10
syscall

mov rdi, 0x4003b0
mov rsi, rdi
mov rcx, 0xa01d4

cld
decrypt:
  lodsb
  xor al, 0xa5
  stosb
  loop decrypt

pop rcx
pop rdx
pop rsi
pop rdi
pop rax

push 0x4009D0
ret

