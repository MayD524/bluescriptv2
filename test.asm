global _start: ; the start we expect
%include "libs/bs_stdlib.asm"


section .text
_start:
pop rax
mov [argc], rax
pop rax
mov [argv], rax

mov rax, 10
mov [main_c], rax

mov rax, [main_c]
call bluescript2_numeric_print


mov rax, [main_a+0*8]
mov [main_b], rax

mov rax, [main_b]
add rax, [main_c]
mov [main_b], rax


mov rax, [main_a+0*8]
call bluescript2_numeric_print

mov rax, 60
mov rdi, 0
syscall

ret


section .bss
;--- for printing numbers ---
digitSpace resb 100
digitSpacePos resb 8
;--- recursion ---
recursiveStack resw 100
;--- args ---
argc resw 4
argv resw 10
;--- other ---

main_c resw 4 ; stores 64-bit int
main_b resw 4 ; stores 64-bit int

section .data
;--- for recursion ---
recursiveDepth db 0
;--- other ---

main_a dq 1,2
main_a dq main_b
