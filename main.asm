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
getTestStruct:
mov rax, 1
mov [getTestStruct_a.a], rax
mov rax, 10
mov [getTestStruct_a.b], rax
mov rax, [getTestStruct_a]
ret
main:
mov [main_argc], rdi
mov [main_argv], rsi
call getTestStruct
mov [main_s], rax
mov rax, [main_s.a]
call stdout_in
mov rax, [main_s.b]
call stdout_in
mov rax, 0
ret
mov rax, 0
ret
setCursorPos:
mov [setCursorPos_x], rax
mov [setCursorPos_y], rdi
lea rax, [bs_str9]
call stdout
mov rax, [setCursorPos_y]
call stdout_i
lea rax, [bs_str10]
call stdout
mov rax, [setCursorPos_x]
call stdout_i
lea rax, [bs_str11]
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
je .bs_logic_end11
mov rax, [stderr_eno]
call exit
.bs_logic_end11:
mov rax, [warno]
add rax, 1
mov [warno], rax
mov rax, [warno]
mov rdx, 2
cmp rax, rdx
jle .bs_logic_end13
mov rax, 1
call exit
.bs_logic_end13:
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
call stdout
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
lea rax, [bs_str26]
call stdout
ret
exit:
mov [exit_eno], rax
mov rax, [exit_eno]
call bs_exit
ret
open:
mov [open_pth], rax
mov [open_mode], rdi
mov rax, [SYS_open]
mov rdi, [open_pth]
mov rsi, [open_mode]
call bs_open
mov [open_sysc], rax
mov rax, [open_sysc]
ret
close:
mov [close_fd], rax
mov rax, [SYS_close]
mov rdi, [close_fd]
call bs_close
mov [close_sysc], rax
mov rax, [close_sysc]
ret
fileExists:
mov [fileExists_pth], rax
mov rax, [fileExists_pth]
mov rdi, [O_RDONLY]
call open
mov [fileExists_rx], rax
mov rax, [fileExists_rx]
mov rdx, 100
cmp rax, rdx
jge .bs_logic_end36
mov rax, [fileExists_rx]
call close
mov rax, 1
ret
.bs_logic_end36:
mov rax, 0
ret
pwarn:
mov [pwarn_err], rax
mov rax, [pwarn_err]
call print
ret
section .rodata
STDOUT dq 1
SYS_open dq 2
SYS_close dq 3
O_RDONLY dq 0
section .bss
digitSpace resb 100
digitSpacePos resb 8
main_argc resw 4
main_argv resw 10
getTestStruct_a:
.a resw 4
.b resw 4
main_s resw 4
setCursorPos_x resw 2
setCursorPos_y resw 2
stderr_msg resw 2
stderr_eno resw 2
raise_msg resw 2
stdout_msg resw 2
atoi_intStr resw 2
atoi_in resw 2
sprompt_prmpt resw 2
sprompt_msgSize resw 2
sprompt_theString resw 2
prompt_prmpt resw 2
prompt_inp resw 2
print_msg resw 2
stdout_i_msg resw 2
stdout_in_i resw 2
exit_eno resw 2
open_pth resw 2
open_mode resw 2
open_sysc resw 2
close_fd resw 2
close_sysc resw 2
fileExists_pth resw 2
fileExists_rx resw 2
pwarn_err resw 2
section .data
bs_str9: db 27,91, 0
bs_str10: db 59, 0
bs_str11: db 72, 0
bs_str26: db 10, 0
bs_str42: db 34,27,49,98,27,91,50,74,34, 0
bs_str43: db 34,112,111,115,105,120,34, 0
stdinBuffSize dq 1024
warno dq 0