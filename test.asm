global _start: ; the start we expect
%include "libs/bs_stdlib.asm"


section .text
test:
mov [a], rax
mov [b], rbx
mov [c], rcx

mov rax, [a]
push rax
add rax, [b]
mov [a], rax
pop rax

push rax
push rbx

mov rax, [a]

mov rbx, [c]
mul rbx

mov [a], rax
pop rbx
pop rax


mov rax, [a]
call bluescript2_numeric_print

lea rax, [a] ; 0
lea rbx, [b] ; 0
lea rcx, [c] ; 0
call test ; 0

mov rax, 1 ; return value in rax
ret

_start:
mov rax, 1 ; 3
mov rbx, 2 ; 3
mov rcx, 3 ; 3
call test ; 3
mov [hello], rax

mov rax, [hello]
call bluescript2_numeric_print

mov rax, 60
mov rdi, 0
syscall

ret


section .rodata
km db 10

section .bss
;--- for printing numbers ---
digitSpace resb 100
digitSpacePos resb 8

a resw 4 ; stores 64-bit int
b resw 4 ; stores 64-bit int
c resw 4 ; stores 64-bit int
hello resw 4 ; stores 64-bit int
