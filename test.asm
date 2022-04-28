global main:
%include "libs/asm/bs_stdlib.asm"
%include "libs/asm/posix.asm"
%include "libs/asm/bs_fstream.asm"
%include "libs/asm/bs_string.asm"
%include "libs/asm/bs_list.asm"
section .text
main:
mov [main_argc], rdi
mov [main_argv], rsi
mov rax, [main_argc]
call stdout_i
lea rax, [bs_str0]
call stdout
mov rax, 60
mov rdi, 0
syscall
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
je .bs_logic_end2
mov rax, [stderr_eno]
call exit
.bs_logic_end2:
mov rax, [warno]
add rax, 1
mov [warno], rax
mov rax, [warno]
mov rdx, 2
cmp rax, rdx
jle .bs_logic_end5
mov rax, 1
call exit
.bs_logic_end5:
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
mov [exit_exitCode], rax
mov rax, [exit_exitCode]
call bs_asmExit
ret
println:
mov [println_strToPrint], rax
mov rax, [println_strToPrint]
call print
mov rax, [newLine]
call print
ret
write:
mov [write_pth], rax
mov [write_data], rdi
lea rax, [bs_str7]
mov rdi, 1
call stderr
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
mayloc:
mov [mayloc_size], rax
mov rax, 0
mov [mayloc_new_ptr], rax
mov rax, [mayloc_size]
mov rdi, [mayloc_new_ptr]
call bs_malloc
mov rax, [mayloc_new_ptr]
ret
read:
mov [read_pth], rax
mov rax, [read_pth]
call print
mov rax, 0
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
jge .bs_logic_end22
mov rax, [fileExists_rx]
call close
mov rax, 1
ret
.bs_logic_end22:
mov rax, 0
ret
makeFile:
mov [makeFile_pth], rax
mov rax, [makeFile_pth]
call fileExists
mov [makeFile_exists], rax
mov rax, [makeFile_exists]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end30
lea rax, [bs_str32]
call pwarn
mov rax, 1
ret
.bs_logic_end30:
mov rax, [O_WRONLY]
mov [makeFile_mode], rax
mov rax, [makeFile_mode]
add rax, [O_CREAT]
mov [makeFile_mode], rax
mov rax, [makeFile_pth]
mov rdi, [makeFile_mode]
call open
mov [makeFile_rx], rax
mov rax, 0
ret
pwarn:
mov [pwarn_err], rax
mov rax, [pwarn_err]
call print
ret
perr:
mov [perr_msg], rax
mov rax, [perr_msg]
call pwarn
mov rax, [FAILED_EXIT]
call exit
ret
Set:
mov [Set_size], rax
mov rax, [Set_size]
call List
mov [Set_pr], rax
mov rax, [Set_pr]
ret
set.insert:
mov [set.insert_pr], rax
mov [set.insert_value], rdi
mov [set.insert_index], rsi
mov rax, [set.insert_pr]
mov rdi, [set.insert_value]
call li_contains
mov [set.insert_exists], rax
mov rax, [set.insert_exists]
mov rdx, [true]
cmp rax, rdx
jne .bs_logic_end46
ret
.bs_logic_end46:
mov rax, [set.insert_pr]
mov rdi, [set.insert_value]
mov rsi, [set.insert_index]
call li_insert
ret
set.remove:
mov [set.remove_pr], rax
mov [set.remove_value], rdi
mov rax, [set.remove_pr]
mov rdi, [set.remove_value]
call li_contains
mov [set.remove_exists], rax
mov rax, [set.remove_exists]
mov rdx, [true]
cmp rax, rdx
jne .bs_logic_end50
mov rax, [set.remove_pr]
mov rdi, [set.remove_value]
call li_remove
.bs_logic_end50:
ret
set.contains:
mov [set.contains_pr], rax
mov [set.contains_value], rdi
mov rax, [set.contains_pr]
mov rdi, [set.contains_value]
call li_contains
mov [set.contains_exists], rax
mov rax, [set.contains_exists]
ret
set.size:
mov [set.size_pr], rax
mov rax, [set.size_pr]
call li_size
mov [set.size_size], rax
mov rax, [set.size_size]
ret
set.get:
mov [set.get_pr], rax
mov [set.get_index], rdi
mov rax, [set.get_pr]
mov rdi, [set.get_index]
call li_get
mov [set.get_value], rax
mov rax, [set.get_value]
ret
set.set:
mov [set.set_pr], rax
mov [set.set_value], rdi
mov [set.set_index], rsi
mov rax, [set.set_pr]
mov rdi, [set.set_value]
mov rsi, [set.set_index]
call li_insert
ret
strlen:
mov [strlen_lnstr], rax
lea rax, [bs_str64]
mov rdi, 1
call stderr
mov rax, 1
ret
itos:
mov [itos_iStr], rax
mov rax, [itos_bs_string_itos]
mov [itos_s], rax
mov rax, [itos_s]
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
jle .bs_logic_end77
lea rax, [bs_str79]
mov rdi, 0
call stderr
ret
.bs_logic_end77:
mov rax, [li_insert_pr]
mov rdi, [li_insert_index]
call li_get
mov [li_insert_x], rax
mov rax, [li_insert_x]
mov rdx, [BS_ENDOF_LIST]
cmp rax, rdx
jne .bs_logic_end81
ret
.bs_logic_end81:
mov rax, [li_insert_pr]
mov rdi, [li_insert_value]
mov rsi, [li_insert_index]
call bs_insert
ret
li_contains:
mov [li_contains_pr], rax
mov [li_contains_value], rdi
mov rax, [li_contains_pr]
call li_size
mov [li_contains_size], rax
mov rax, 0
mov [li_contains_index], rax
.li_contains_bsDo_277:
mov rax, [li_contains_pr]
mov rdi, [li_contains_index]
call li_get
mov [li_contains_x], rax
mov rax, [li_contains_x]
mov rdx, [li_contains_value]
cmp rax, rdx
jne .bs_logic_end91
ret
.bs_logic_end91:
mov rax, [li_contains_index]
add rax, 1
mov [li_contains_index], rax
mov rax, [li_contains_index]
mov rdx, [li_contains_size]
cmp rax, rdx
jge .bs_logic_end96
jmp .li_contains_bsDo_277
.bs_logic_end96:
ret
li_get:
mov [li_get_pr], rax
mov [li_get_index], rdi
mov rax, [li_get_pr]
mov rdi, [li_get_index]
call bs_get
mov [li_get_got], rax
mov rax, [li_get_got]
ret
li_remove:
mov [li_remove_pr], rax
mov [li_remove_index], rdi
mov rax, [li_remove_pr]
mov rdi, [li_remove_index]
call bs_remove
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
section .rodata
bs_str93 dd "true", 0
true dd 1
false dd 0
STDOUT dd 1
newLine dd "", 10
FAILED_EXIT dd 1
SYS_open dd 2
SYS_close dd 3
O_RDONLY dd 0
O_WRONLY dd 1
O_CREAT dd 64
BS_ENDOF_LIST dd 0xfffffff
section .bss
digitSpace resb 100
digitSpacePos resb 8
main_argc resw 4
main_argv resw 10
stderr_msg resw 4
stderr_eno resw 4
raise_msg resw 4
stdout_msg resw 4
print_msg resw 4
stdout_i_msg resw 4
exit_exitCode resw 4
println_strToPrint resw 4
write_pth resw 4
write_data resw 4
open_pth resw 4
open_mode resw 4
open_sysc resw 4
close_fd resw 4
close_sysc resw 4
mayloc_size resw 4
mayloc_new_ptr resw 4
read_pth resw 4
fileExists_pth resw 4
fileExists_rx resw 4
makeFile_pth resw 4
makeFile_exists resw 4
makeFile_mode resw 4
makeFile_rx resw 4
pwarn_err resw 4
perr_msg resw 4
Set_size resw 4
Set_pr resw 4
set.insert_pr resw 4
set.insert_value resw 4
set.insert_index resw 4
set.insert_exists resw 4
set.remove_pr resw 4
set.remove_value resw 4
set.remove_exists resw 4
set.contains_pr resw 4
set.contains_value resw 4
set.contains_exists resw 4
set.size_pr resw 4
set.size_size resw 4
set.get_pr resw 4
set.get_index resw 4
set.get_value resw 4
set.set_pr resw 4
set.set_value resw 4
set.set_index resw 4
strlen_lnstr resw 4
itos_iStr resw 4
itos_s resw 4
List_size resw 4
List_pr resw 4
li_insert_pr resw 4
li_insert_value resw 4
li_insert_index resw 4
li_insert_size resw 4
li_insert_x resw 4
li_contains_pr resw 4
li_contains_value resw 4
li_contains_size resw 4
li_contains_index resw 4
li_contains_x resw 4
li_get_pr resw 4
li_get_index resw 4
li_get_got resw 4
li_remove_pr resw 4
li_remove_index resw 4
li_size_pr resw 4
li_size_sz resw 4
itos_bs_string_itos resw 4
li_contains_bsDo_277 resw 4
section .data
recursiveDepth db 0
bs_str0: db "", 0xa, 0
bs_str7: db "Not implemented", 0xa, 0
bs_str32: db "file already exists", 0
bs_str64: db "strlen: not implemented", 0xa, 0
bs_str79: db "index out of range", 0xa, 0
warno dd 0