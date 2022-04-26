global main: ; the start we expect
%include "libs/asm/bs_stdlib.asm"
%include "libs/asm/posix.asm"
%include "libs/asm/bs_fstream.asm"
%include "libs/asm/bs_string.asm"


section .text
recursive:
mov [recursive_cur], rax
mov rax, [recursive_cur] ; 0
call stdout_i ; 0

mov rax, [recursive_cur]
add rax, 1
mov [recursive_cur], rax

mov rax, [recursive_cur]
mov rdx, 10
cmp rax, rdx
jne .bs_logic_end1

ret

.bs_logic_end1:

mov rax, [recursive_cur] ; 0
call recursive ; 0

ret
main:
pop rax
mov [argc], rax
pop rax
mov [argv], rax

mov rax, 0
mov [main_i], rax

.main_hi:

mov rax, [main_i]
add rax, 1
mov [main_i], rax

mov rax, [main_i] ; 0
call stdout_i ; 0

mov rax, [main_i]
mov rdx, 10
cmp rax, rdx
je .bs_logic_end8

jmp .main_hi

.bs_logic_end8:

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
je .bs_logic_end15

mov rax, [stderr_eno] ; 0
call exit ; 0

.bs_logic_end15:

mov rax, [warno]
add rax, 1
mov [warno], rax

mov rax, [warno]
mov rdx, 2
cmp rax, rdx
jl .bs_logic_end18

mov rax, 1 ; 0
call exit ; 0

.bs_logic_end18:

ret

ret
stdout:
mov [stdout_msg], rax
mov rax, [stdout_msg]
mov rdi, [STDOUT]
call bluescript2_unix_print

ret
print:
mov [print_msg], rax
mov rax, [print_msg] ; 0
call stdout ; 0

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
mov rax, [println_strToPrint] ; 0
call print ; 0

mov rax, [newLine] ; 0
call print ; 0

ret
write:
mov [write_pth], rax
mov [write_data], rdi
lea rax, [bs_str20] ; 0
mov rdi, 1 ; 0
call stderr ; 0

ret
open:
mov [open_pth], rax
mov [open_mode], rdi
mov rax, [SYS_open]
mov rdi, [open_pth]
mov rsi, [open_mode]
call bs_open
mov [open_sysc], rax

mov rax, [open_sysc] ; return value in rax
ret

close:
mov [close_fd], rax
mov rax, [SYS_close]
mov rdi, [close_fd]
call bs_close
mov [close_sysc], rax

mov rax, [close_sysc] ; return value in rax
ret

mayloc:
mov [mayloc_size], rax
mov rax, 0
mov [mayloc_new_ptr], rax

mov rax, [mayloc_size]
mov rdi, [mayloc_new_ptr]
call bs_malloc

mov rax, [mayloc_new_ptr] ; return value in rax
ret

read:
mov [read_pth], rax
mov rax, [read_pth] ; 0
call print ; 0

mov rax, 0 ; return value in rax
ret

fileExists:
mov [fileExists_pth], rax
mov rax, [fileExists_pth] ; 3
mov rdi, [O_RDONLY] ; 3
call open ; 3
mov [fileExists_rx], rax

mov rax, [fileExists_rx]
mov rdx, 100
cmp rax, rdx
jle .bs_logic_end35

mov rax, [fileExists_rx] ; 0
call close ; 0

mov rax, 1 ; return value in rax
ret

.bs_logic_end35:

mov rax, 0 ; return value in rax
ret

makeFile:
mov [makeFile_pth], rax
mov rax, [makeFile_pth] ; 3
call fileExists ; 3
mov [makeFile_exists], rax

mov rax, [makeFile_exists]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end43

lea rax, [bs_str45] ; 0
call pwarn ; 0

mov rax, 1 ; return value in rax
ret

.bs_logic_end43:

mov rax, [O_WRONLY]
mov [makeFile_mode], rax

mov rax, [makeFile_mode]
add rax, [O_CREAT]
mov [makeFile_mode], rax

mov rax, [makeFile_pth] ; 3
mov rdi, [makeFile_mode] ; 3
call open ; 3
mov [makeFile_rx], rax

mov rax, 0 ; return value in rax
ret

pwarn:
mov [pwarn_err], rax
mov rax, [pwarn_err] ; 0
call print ; 0

ret
perr:
mov [perr_msg], rax
mov rax, [perr_msg] ; 0
call pwarn ; 0

mov rax, [FAILED_EXIT] ; 0
call exit ; 0

ret
strlen:
mov [strlen_lnstr], rax
lea rax, [bs_str53] ; 0
mov rdi, 1 ; 0
call stderr ; 0

mov rax, 1 ; return value in rax
ret

itos:
mov [itos_iStr], rax
mov rax, [itos_bs_string_itos]
mov [itos_s], rax

mov rax, [itos_s] ; return value in rax
ret


section .rodata
NULL dd 0
STDIN dd  0
STDOUT dd 1
STDERR dd 2
newLine dd "", 10
os_name dd "posix"
SUCCESS_EXIT dd 0
FAILED_EXIT dd 1
SYS_read dd 0
SYS_write dd 1
SYS_open dd 2
SYS_close dd 3
SYS_exit dd 60
O_RDONLY dd 0
O_WRONLY dd 1
O_RDWR dd 2
O_CREAT dd 64
O_APPEND dd 1024
O_DIRECTORY dd 65536

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

recursive_cur resw 4 ; stores 64-bit int
main_i resw 4 ; stores 64-bit int
stderr_msg resw 4 ; stores char
stderr_eno resw 4 ; stores 64-bit int
stdout_msg resw 4 ; stores char
print_msg resw 4 ; stores char
stdout_i_msg resw 4 ; stores 64-bit int
exit_exitCode resw 4 ; stores 64-bit int
println_strToPrint resw 4 ; stores char
write_pth resw 4 ; stores char
write_data resw 4 ; stores char
open_pth resw 4 ; stores char
open_mode resw 4 ; stores 64-bit int
open_sysc resw 4 ; stores 64-bit int
close_fd resw 4 ; stores 64-bit int
close_sysc resw 4 ; stores 64-bit int
mayloc_size resw 4 ; stores 64-bit int
mayloc_new_ptr resw 4 ; stores 64-bit int
read_pth resw 4 ; stores char
fileExists_pth resw 4 ; stores char
fileExists_rx resw 4 ; stores 64-bit int
makeFile_pth resw 4 ; stores char
makeFile_exists resw 4 ; stores 64-bit int
makeFile_mode resw 4 ; stores 64-bit int
makeFile_rx resw 4 ; stores 64-bit int
pwarn_err resw 4 ; stores char
perr_msg resw 4 ; stores char
strlen_lnstr resw 4 ; stores char
itos_iStr resw 4 ; stores 64-bit int
itos_s resw 4 ; stores char
main_hi resw 4 ; stores char
itos_bs_string_itos resw 4 ; stores char

section .data
;--- for recursion ---
recursiveDepth db 0
;--- other ---

bs_str20: db "Not implemented", 0xa, 0
bs_str45: db "file already exists", 0
bs_str53: db "strlen: not implemented", 0xa, 0
errno dd 0
warno dd 0
