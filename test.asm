global main:
%include "libs/asm/bs_stdlib.asm"
%include "libs/asm/posix.asm"
%include "libs/asm/bs_fstream.asm"
%include "libs/asm/bs_string.asm"
section .text
main:
mov [main_argc], rdi
mov [main_argv], rsi
call termSize
mov [main_tmSize], rax
mov rax, [main_tmSize]
mov rdi, 0
call bsat
mov [main_x], rax
mov rax, [main_tmSize]
mov rdi, 1
call bsat
mov [main_y], rax
mov rax, [main_x]
call stdout_i
lea rax, [bs_str6]
call stdout
mov rax, [main_y]
call stdout_i
lea rax, [bs_str7]
call stdout
mov rax, 60
mov rdi, 0
syscall
ret
bsat:
mov [bsat_pr], rax
mov [bsat_index], rdi
mov rax, [bsat_pr]
mov rdi, [bsat_index]
call bs_at
mov [bsat_x], rax
mov rax, [bsat_x]
ret
termSize:
call bs_termSize
mov [termSize_dt], rax
mov rax, [termSize_dt]
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
je .bs_logic_end17
mov rax, [stderr_eno]
call exit
.bs_logic_end17:
mov rax, [warno]
add rax, 1
mov [warno], rax
mov rax, [warno]
mov rdx, 2
cmp rax, rdx
jle .bs_logic_end20
mov rax, 1
call exit
.bs_logic_end20:
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
jge .bs_logic_end44
mov rax, [fileExists_rx]
call close
mov rax, 1
ret
.bs_logic_end44:
mov rax, 0
ret
pwarn:
mov [pwarn_err], rax
mov rax, [pwarn_err]
call print
ret
section .rodata
STDOUT dd 1
SYS_open dd 2
SYS_close dd 3
O_RDONLY dd 0
section .bss
digitSpace resb 100
digitSpacePos resb 8
main_argc resw 4
main_argv resw 10
main_tmSize resw 4
main_x resw 4
main_y resw 4
bsat_pr resw 4
bsat_index resw 4
bsat_x resw 4
termSize_dt resw 4
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
exit_eno resw 4
open_pth resw 4
open_mode resw 4
open_sysc resw 4
close_fd resw 4
close_sysc resw 4
fileExists_pth resw 4
fileExists_rx resw 4
pwarn_err resw 4
section .data
bs_str6: db 10, 0
bs_str7: db 10, 0
stdinBuffSize dd 1024
warno dd 0