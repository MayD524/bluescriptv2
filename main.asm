global _start
%include "libs/asm/bs_stdlib.asm"
%include "libs/asm/bs_os.asm"
%include "libs/asm/bs_list.asm"
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
mov rax, 0
mov rdi, 10
call generator
mov [main_x], rax
lea rax, [bs_str4]
mov rdi, 24
call sprompt
mov [main_y], rax
lea rax, [bs_str5]
call print
mov rax, [main_y]
call println
mov rax, 0
ret
mov rax, 0
ret
setCursorPos:
mov [setCursorPos_x], rax
mov [setCursorPos_y], rdi
lea rax, [bs_str7]
call stdout
mov rax, [setCursorPos_y]
call stdout_i
lea rax, [bs_str8]
call stdout
mov rax, [setCursorPos_x]
call stdout_i
lea rax, [bs_str9]
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
je .bs_logic_end9
mov rax, [stderr_eno]
call exit
.bs_logic_end9:
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
println:
mov [println_msg], rax
mov rax, [println_msg]
call stdout
lea rax, [bs_str28]
call stdout
ret
exit:
mov [exit_eno], rax
mov rax, [exit_eno]
call bs_exit
ret
List:
mov [List_size], rax
mov rax, [List_size]
call bs_makeList
mov [List_pr], rax
mov rax, [List_pr]
ret
li_insert:
mov [li_insert_pr], rax
mov [li_insert_value], rdi
mov [li_insert_index], rsi
mov rax, [li_insert_pr]
call li_size
mov [li_insert_size], rax
mov rax, [li_insert_index]
mov rdx, [li_insert_size]
cmp rax, rdx
jle .bs_logic_end34
lea rax, [bs_str37]
call raise
ret
.bs_logic_end34:
mov rax, [li_insert_pr]
mov rdi, [li_insert_index]
call li_get
mov [li_insert_x], rax
mov rax, [li_insert_x]
mov rdx, [BS_ENDOF_LIST]
cmp rax, rdx
jne .bs_logic_end40
ret
.bs_logic_end40:
mov rax, [li_insert_pr]
mov rdi, [li_insert_value]
mov rsi, [li_insert_index]
call bs_insert
ret
li_get:
mov [li_get_pr], rax
mov [li_get_index], rdi
mov rax, [li_get_pr]
call li_size
mov [li_get_sz], rax
mov rax, [li_get_index]
mov rdx, [li_get_sz]
cmp rax, rdx
jl .bs_logic_end45
ret
.bs_logic_end45:
mov rax, [li_get_pr]
mov rdi, [li_get_index]
call bs_get
mov [li_get_got], rax
mov rax, [li_get_got]
ret
li_size:
mov [li_size_pr], rax
mov rax, [li_size_pr]
call bs_length
mov [li_size_sz], rax
mov rax, [li_size_sz]
mov rdx, 0
mov rax, [li_size_sz]
mov rcx, 8
div rcx
mov [li_size_sz], rax
mov rax, [li_size_sz]
ret
generator:
mov [generator_start], rax
mov [generator_max], rdi
mov rax, [generator_max]
mov [generator_dif], rax
mov rax, [generator_dif]
mov rax, [generator_dif]
mov rbx, [generator_start]
sub rax, rbx
mov [generator_dif], rax
mov rax, [generator_dif]
call List
mov [generator_newLi], rax
mov rax, 0
mov [generator_index], rax
mov rax, [generator_start]
mov [generator_value], rax
.generator_bsDo_336:
mov rax, [generator_newLi]
mov rdi, [generator_value]
mov rsi, [generator_index]
call li_insert
mov rax, [generator_index]
add rax, 1
mov [generator_index], rax
mov rax, [generator_value]
add rax, 1
mov [generator_value], rax
mov rax, [generator_index]
mov rdx, [generator_dif]
cmp rax, rdx
jg .bs_logic_end70
jmp .generator_bsDo_336
.bs_logic_end70:
mov rax, [generator_newLi]
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
jge .bs_logic_end88
mov rax, [fileExists_rx]
call close
mov rax, 1
ret
.bs_logic_end88:
mov rax, 0
ret
pwarn:
mov [pwarn_err], rax
mov rax, [pwarn_err]
call print
ret
section .rodata
bs_str48 dd "BS_ENDOF_LIST", 0
STDOUT dq 1
BS_ENDOF_LIST dq 0xFFFF
SYS_open dq 2
SYS_close dq 3
O_RDONLY dq 0
section .bss
digitSpace resb 100
digitSpacePos resb 8
main_argc resw 4
main_argv resw 10
main_x resw 4
main_y resw 4
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
println_msg resw 4
exit_eno resw 4
List_size resw 4
List_pr resw 4
li_insert_pr resw 4
li_insert_value resw 4
li_insert_index resw 4
li_insert_size resw 4
li_insert_x resw 4
li_get_pr resw 4
li_get_index resw 4
li_get_sz resw 4
li_get_got resw 4
li_size_pr resw 4
li_size_sz resw 4
generator_start resw 4
generator_max resw 4
generator_dif resw 4
generator_newLi resw 4
generator_index resw 4
generator_value resw 4
open_pth resw 4
open_mode resw 4
open_sysc resw 4
close_fd resw 4
close_sysc resw 4
fileExists_pth resw 4
fileExists_rx resw 4
pwarn_err resw 4
section .data
bs_str4: db 72,101,108,108,111,44,32,119,104,97,116,32,105,115,32,121,111,117,114,32,110,97,109,101,63,32, 0
bs_str5: db 72,101,108,108,111,44,32, 0
bs_str7: db 27,91, 0
bs_str8: db 59, 0
bs_str9: db 72, 0
bs_str28: db 10, 0
bs_str37: db 108,105,95,105,110,115,101,114,116,58,32,105,110,100,101,120,32,111,117,116,32,111,102,32,114,97,110,103,101,10, 0
bs_str96: db 34,27,49,98,27,91,50,74,34, 0
bs_str97: db 34,112,111,115,105,120,34, 0
stdinBuffSize dq 1024
warno dq 0