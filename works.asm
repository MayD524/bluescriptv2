
; ------------ boring string manipulation stuff ------------
global _start: ; the start we expect
%include "libs/bs_stdlib.asm"

section .text
test:
; move the value of rax into the variable test_arg
mov rdi, test_arg
call bluescript2_string_copy


mov rax, test_arg
call bluescript2_generic_print

ret
_start:
lea rax, [bs_str5]
call test ; 0

mov rax, 60
mov rdi, 0
syscall

ret

section .bss
;--- for printing numbers ---
digitSpace resb 100
digitSpacePos resb 8

test_arg resb 100 ; stores char

section .data
bs_str5: db "hello world", 0xa, 0 ; 2
bs_int1: db 10

; ------------ number test ------------

global _start: ; the start we expect
%include "libs/bs_stdlib.asm"

section .text
_start:

; init the variables
mov rax, 0x0a
mov rbx, 0x0a
mov [bs_int_test], rax
mov [bs_int_test2], rbx

mov rax, [bs_int_test]
add rax, [bs_int_test2]
mov [bs_int_test], rax
call bluescript2_numeric_print ; this results in 20 :o yay

mov rax, [bs_test]
add rax, [bs_test2]
mov [bs_test], rax
call bluescript2_numeric_print ; this results in not 20 (why? 🤷‍♂️)

mov rax, bs_str12
call bluescript2_generic_print

mov rax, 60
mov rdi, 0
syscall

ret

; note use .bss for all dynamic memory 
; who woulda thunk it?
section .bss
;--- for printing numbers ---
digitSpace resb 100
digitSpacePos resb 8

;; change ints to this
bs_int_test resb 8
bs_int_test2 resb 8

section .data
bs_str12: db "hello world", 0xa, 0 ; 2
bs_test2: db 10
bs_test : db 10

; ----------- string test ------------

global _start: ; the start we expect
%include "libs/asm/bs_stdlib.asm"
%include "libs/asm/bs_string.asm"

section .text
_start:
pop rax
mov [argc], rax
pop rax
mov [argv], rax

push rax
mov rax, [bs_str0]; get ptr to str
mov [main_test], rax
pop rax

mov rax, [main_test] ; 3
call strlen ; 3
mov [main_ln], rax

mov rax, [main_ln]
call bluescript2_numeric_print

mov rax, 60
mov rdi, 0
syscall
ret

strlen:
mov [strlen_lnstr], rax

mov rax, strlen_lnstr
call bs_string_strlen
mov [strlen_ln], rax

mov rax, [strlen_ln] ; return value in rax
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

main_test resb 12 ; stores char
main_ln resw 4 ; stores 64-bit int
println_strToPrint resb 4 ; stores char
strlen_lnstr resb 4 ; stores char
strlen_ln resw 4 ; stores 64-bit int

section .data
;--- for recursion ---
recursiveDepth db 0
;--- other ---

bs_str0: db "hello world", 0
