global _start
%include "libs/asm/bs_stdlib.asm"
%include "libs/asm/posix.asm"
%include "libs/asm/bs_fstream.asm"
%include "libs/asm/bs_string.asm"
section .text
_start: call main
mov rax, 60
xor rdi, rdi
syscall
main:
mov [main_argc], rdi
mov [main_argv], rsi
<<<<<<< HEAD
mov rax, 10
mov [main_h], rax
mov rax, [main_h]
add rax, 1
mov [main_h], rax
mov rax, [main_h]
mov rbx, 2
mul rbx
mov [main_h], rax
mov rax, [main_h]
call stdout_in
mov rax, 0
=======
call testNamespace.test
mov rax, 0
ret
testNamespace.test:
lea rax, [bs_str0]
call println
>>>>>>> 0ec40a4edd9181816edc33e27e5ba2853e8d7d83
ret
setCursorPos:
mov [setCursorPos_x], rax
mov [setCursorPos_y], rdi
lea rax, [bs_str3]
call stdout
mov rax, [setCursorPos_y]
call stdout_i
lea rax, [bs_str4]
call stdout
mov rax, [setCursorPos_x]
call stdout_i
lea rax, [bs_str5]
call stdout
ret
stderr:
mov [stderr_msg], rax
mov [stderr_eno], rdi
mov rax, [stderr_msg]
mov rdi, 2
call bluescript2_unix_print
mov rax, [stderr_eno]
mov rdx, 0
cmp rax, rdx
je .bs_logic_end5
mov rax, [stderr_eno]
call exit
.bs_logic_end5:
mov rax, [warno]
add rax, 1
mov [warno], rax
mov rax, [warno]
mov rdx, 2
cmp rax, rdx
jle .bs_logic_end7
mov rax, 1
call exit
.bs_logic_end7:
ret
ret
raise:
mov [raise_msg], rax
mov rax, [raise_msg]
mov rdi, 1
call stderr
ret
stdout:
mov [stdout_msg], rax
mov rax, [stdout_msg]
mov rdi, [STDOUT]
call bluescript2_unix_print
ret
atoi:
mov [atoi_intStr], rax
mov rax, [atoi_intStr]
call bs_atoi
mov [atoi_in], rax
mov rax, [atoi_in]
ret
sprompt:
mov [sprompt_prmpt], rax
mov [sprompt_msgSize], rdi
mov rax, [sprompt_prmpt]
call print
mov rax, [sprompt_msgSize]
call bluescript2_string_input
mov [sprompt_theString], rax
mov rax, [sprompt_theString]
ret
prompt:
mov [prompt_prmpt], rax
mov rax, [prompt_prmpt]
mov rdi, [stdinBuffSize]
call sprompt
mov [prompt_inp], rax
mov rax, [prompt_inp]
ret
print:
mov [print_msg], rax
mov rax, [print_msg]
call stdout
ret
stdout_i:
mov [stdout_i_msg], rax
mov rax, [stdout_i_msg]
call bluescript2_numeric_print
ret
stdout_in:
mov [stdout_in_i], rax
mov rax, [stdout_in_i]
call stdout_i
lea rax, [bs_str20]
call stdout
ret
exit:
mov [exit_eno], rax
mov rax, [exit_eno]
call bs_exit
ret
pwarn:
mov [pwarn_err], rax
mov rax, [pwarn_err]
call print
ret
section .rodata
STDOUT dq 1
section .bss
digitSpace resb 100
digitSpacePos resb 8
main_argc resw 4
main_argv resw 10
main_h resw 4
setCursorPos_x resw 4
setCursorPos_y resw 4
stderr_msg resw 4
stderr_eno resw 4
raise_msg resw 4
stdout_msg resw 4
atoi_intStr resw 4
atoi_in resw 4
sprompt_prmpt resw 4
sprompt_msgSize resw 4
sprompt_theString resw 4
prompt_prmpt resw 4
prompt_inp resw 4
print_msg resw 4
stdout_i_msg resw 4
stdout_in_i resw 4
exit_eno resw 4
pwarn_err resw 4
section .data
<<<<<<< HEAD
bs_str3: db 27,91, 0
bs_str4: db 59, 0
bs_str5: db 72, 0
bs_str20: db 10, 0
bs_str21: db 34,27,49,98,27,91,50,74,34, 0
=======
bs_str0: db 116,101,115,116, 0
bs_str1: db 27,91, 0
bs_str2: db 59, 0
bs_str3: db 72, 0
bs_str18: db 10, 0
bs_str19: db 34,27,49,98,27,91,50,74,34, 0
bs_str20: db 34,112,111,115,105,120,34, 0
>>>>>>> 0ec40a4edd9181816edc33e27e5ba2853e8d7d83
stdinBuffSize dq 1024
warno dq 0