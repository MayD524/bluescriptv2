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
pickRandomChar:
mov rax, [MIN_CHAR]
mov rdi, [MAX_CHAR]
call randint
mov [pickRandomChar_retChar], rax
mov rax, [pickRandomChar_retChar]
ret
main:
mov [main_argc], rdi
mov [main_argv], rsi
mov rax, 0
mov [main_uSize], rax
.main_lengthTryAgain:
lea rax, [bs_str10]
call iprompt
mov [main_uSize], rax
mov rax, [main_uSize]
mov rdx, [MIN_LEN]
cmp rax, rdx
jge .bs_logic_end10
mov rax, 1
mov rdi, 1
call setColor
lea rax, [bs_str12]
call print
call termReset
jmp .main_lengthTryAgain
.bs_logic_end10:
mov rax, [main_uSize]
mov rdx, [MAX_LEN]
cmp rax, rdx
jle .bs_logic_end16
mov rax, 1
mov rdi, 1
call setColor
lea rax, [bs_str18]
call print
call termReset
jmp .main_lengthTryAgain
.bs_logic_end16:
mov rax, 0
mov [main_last], rax
mov rax, 0
mov [main_i], rax
lea rax, [bs_str24]
call print
.main_bsDo_31:
.main_doAgain:
call pickRandomChar
mov [main_chr], rax
mov rax, [main_chr]
mov rdx, [main_last]
cmp rax, rdx
jne .bs_logic_end32
jmp .main_doAgain
.bs_logic_end32:
mov rax, [main_chr]
call putc
mov rax, [main_chr]
mov [main_last], rax
mov rax, [main_i]
add rax, 1
mov [main_i], rax
mov rax, [main_i]
mov rdx, [main_uSize]
cmp rax, rdx
jge .bs_logic_end40
jmp .main_bsDo_31
.bs_logic_end40:
lea rax, [bs_str43]
call print
mov rax, 0
ret
mov rax, 0
ret
randint:
mov [randint_min], rax
mov [randint_max], rdi
mov rax, [randint_max]
call bs_random
mov [randint_num], rax
mov rax, [randint_num]
mov rdx, [randint_min]
cmp rax, rdx
jge .bs_logic_end47
mov rax, [randint_num]
add rax, [randint_min]
mov [randint_num], rax
.bs_logic_end47:
mov rax, [randint_num]
ret
setColor:
mov [setColor_modif], rax
mov [setColor_color], rdi
mov rax, [setColor_color]
mov rdx, 0
cmp rax, rdx
jge .bs_logic_end51
lea rax, [bs_str52]
call raise
.bs_logic_end51:
mov rax, [setColor_color]
mov rdx, 8
cmp rax, rdx
jle .bs_logic_end52
lea rax, [bs_str53]
call raise
.bs_logic_end52:
mov rax, [setColor_color]
add rax, 30
mov [setColor_color], rax
lea rax, [bs_str54]
call stdout
mov rax, [setColor_modif]
call stdout_i
lea rax, [bs_str55]
call stdout
mov rax, [setColor_color]
call stdout_i
lea rax, [bs_str56]
call stdout
ret
termReset:
lea rax, [bs_str57]
call stdout
ret
setCursorPos:
mov [setCursorPos_x], rax
mov [setCursorPos_y], rdi
lea rax, [bs_str58]
call stdout
mov rax, [setCursorPos_y]
call stdout_i
lea rax, [bs_str59]
call stdout
mov rax, [setCursorPos_x]
call stdout_i
lea rax, [bs_str60]
call stdout
ret
putc:
mov [putc_ch], rax
mov rax, [putc_ch]
mov rdi, [STDOUT]
call bluescript2_putChar
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
je .bs_logic_end60
mov rax, [stderr_eno]
call exit
.bs_logic_end60:
mov rax, [warno]
add rax, 1
mov [warno], rax
mov rax, [warno]
mov rdx, 2
cmp rax, rdx
jle .bs_logic_end62
mov rax, 1
call exit
.bs_logic_end62:
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
iprompt:
mov [iprompt_prmpt], rax
mov rax, [iprompt_prmpt]
mov rdi, 4
call sprompt
mov [iprompt_dt], rax
mov rax, [iprompt_dt]
call atoi
mov [iprompt_dti], rax
mov rax, [iprompt_dti]
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
pwarn:
mov [pwarn_err], rax
mov rax, [pwarn_err]
call print
ret
section .rodata
MIN_CHAR dq '!'
MAX_CHAR dq '~'
MIN_LEN dq 8
MAX_LEN dq 64
STDOUT dq 1
section .bss
digitSpace resb 100
digitSpacePos resb 8
main_argc resw 4
main_argv resw 10
pickRandomChar_retChar resw 4
main_uSize resw 4
main_last resw 4
main_i resw 4
main_chr resw 4
randint_min resw 4
randint_max resw 4
randint_num resw 4
setColor_modif resw 4
setColor_color resw 4
setCursorPos_x resw 4
setCursorPos_y resw 4
putc_ch resw 4
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
iprompt_prmpt resw 4
iprompt_dt resw 4
iprompt_dti resw 4
print_msg resw 4
stdout_i_msg resw 4
exit_eno resw 4
pwarn_err resw 4
section .data
bs_str10: db 69,110,116,101,114,32,97,32,108,101,110,103,116,104,32,111,102,32,56,32,116,111,32,54,52,58,32, 0
bs_str12: db 80,97,115,115,119,111,114,100,32,109,117,115,116,32,98,101,32,97,116,32,108,101,97,115,116,32,56,32,99,104,97,114,97,99,116,101,114,115,32,108,111,110,103,46,10, 0
bs_str18: db 80,97,115,115,119,111,114,100,32,109,117,115,116,32,98,101,32,108,101,115,115,32,116,104,97,110,32,54,52,32,99,104,97,114,97,99,116,101,114,115,32,108,111,110,103,46,10, 0
bs_str24: db 89,111,117,114,32,112,97,115,115,119,111,114,100,32,105,115,58,32, 0
bs_str43: db 10, 0
bs_str52: db 99,111,108,111,114,32,109,117,115,116,32,98,101,32,62,61,32,48, 0
bs_str53: db 99,111,108,111,114,32,109,117,115,116,32,98,101,32,60,61,32,56, 0
bs_str54: db 27,91, 0
bs_str55: db 59, 0
bs_str56: db 109, 0
bs_str57: db 27,91,48,109, 0
bs_str58: db 27,91, 0
bs_str59: db 59, 0
bs_str60: db 72, 0
bs_str81: db 34,27,49,98,27,91,50,74,34, 0
bs_str82: db 34,112,111,115,105,120,34, 0
stdinBuffSize dq 1024
warno dq 0