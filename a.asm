global _start: ; the start we expect
%include "libs/bs_stdlib.asm"

section .text
_start:
pop rax
mov [argc], rax
pop rax
mov [argv], rax


mov rax, 5
mov [main_b], rax

mov rax, [main_a+1*8]
call bluescript2_numeric_print

mov rax, [main_a + 1*8]
add rax, 10
mov [main_a + 1*8], rax

mov rax, [main_a+1*8]
call bluescript2_numeric_print

mov rcx, [main_b]
mov rax, [main_a + rcx*8]
add rax, 100
mov [main_a + rcx*8], rax

mov rcx, [main_b]
mov rax, [main_a + rcx*8]
mov rbx, 2
mul rbx

mov [main_a + rcx*8], rax

mov rax, [main_b]
mov rax, [main_a+rax*8]
call bluescript2_numeric_print

mov rax, 60
mov rdi, 0
syscall

ret

println:
mov [println_strToPrint], rax

mov rax, [println_strToPrint]
call bluescript2_generic_print

lea rax, [newLine]
call bluescript2_generic_print

ret

section .rodata
newLine db "", 10

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

main_b resw 4 ; stores 64-bit int
println_strToPrint resb 4 ; stores char

section .data
;--- for recursion ---
recursiveDepth db 0
;--- other ---

main_a dq 0,1,2,3,0,0,0,0,0,0
