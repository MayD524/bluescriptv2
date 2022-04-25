;; https://stackoverflow.com/questions/48672864/how-to-use-malloc-and-free-in-64-bit-nasm
section .text
%include "libs/asm/bs_stdlib.asm"
%include "libs/asm/posix.asm"
global main

main:
    mov rax, 8000
    call bs_malloc

    mov dword [rax+0], 0
    mov dword [rax+8], 10
    mov dword [rax+8*2], 11
    mov rdi, rax
    mov rax, [rdi]
    call bluescript2_numeric_print

    mov rax, 60
    xor rdi, rdi
    syscall
    ret

section .bss
;--- for printing numbers ---
digitSpace resb 100
digitSpacePos resb 8