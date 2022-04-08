global _start: ; the start we expect
%include "libs/bs_stdlib.asm"


section .text
recursionTest:
mov [recursionTest_x], rax
mov [recursionTest_r], rbx

mov rax, [recursionTest_x]
push rax
add rax, [recursionTest_r]
mov [recursionTest_x], rax
pop rax

mov rax, [recursionTest_x]
call bluescript2_numeric_print

mov rax, [recursionTest_x]
mov rdx, 1000
cmp rax, rdx
jle bs_logic_end3

mov rax, [recursionTest_x] ; return value in rax
ret

bs_logic_end3:

mov rax, [recursionTest_x] ; 3
mov rbx, [recursionTest_r] ; 3
call recursionTest ; 3
mov [recursionTest_a], rax

mov rax, [recursionTest_a] ; return value in rax
ret

_start:
pop rax
mov [argc], rax
pop rax
mov [argv], rax

mov rax, rax

mov rax, 0

mov rdi, 0

div rdi

mov rax, 0 ; 3
mov rbx, 1 ; 3
call recursionTest ; 3
mov [main_r], rax

mov rax, [main_r]
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

recursionTest_x resw 4 ; stores 64-bit int
recursionTest_r resw 4 ; stores 64-bit int
recursionTest_a resw 4 ; stores 64-bit int
main_r resw 4 ; stores 64-bit int

section .data
;--- for recursion ---
recursiveDepth db 0
;--- other ---

bs_str12: db "mov rax, rax", 0
bs_str15: db "mov rax, 0", 0
bs_str18: db "mov rdi, 0", 0
bs_str21: db "div rdi", 0
