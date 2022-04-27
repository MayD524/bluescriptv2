global main: ; the start we expect
%include "libs/asm/bs_stdlib.asm"
%include "libs/asm/posix.asm"
%include "libs/asm/bs_fstream.asm"
%include "libs/asm/float.asm"
%include "libs/asm/bs_math.asm"
%include "libs/asm/bs_string.asm"


section .text
main:
pop rax
mov [argc], rax
pop rax
mov [argv], rax

mov rax, 50
mov [main_x], rax

mov rax, 25
mov [main_y], rax

mov rax, [main_x] ; 3
mov rdi, [main_y] ; 3
call gcd ; 3
mov [main_gc], rax

mov rax, [main_gc] ; 0
call stdout_i ; 0

lea rax, [bs_str4] ; 0
call stdout ; 0

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
je .bs_logic_end6

mov rax, [stderr_eno] ; 0
call exit ; 0

.bs_logic_end6:

mov rax, [warno]
add rax, 1
mov [warno], rax

mov rax, [warno]
mov rdx, 2
cmp rax, rdx
jl .bs_logic_end9

mov rax, 1 ; 0
call exit ; 0

.bs_logic_end9:

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
lea rax, [bs_str11] ; 0
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
jle .bs_logic_end26

mov rax, [fileExists_rx] ; 0
call close ; 0

mov rax, 1 ; return value in rax
ret

.bs_logic_end26:

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
jne .bs_logic_end34

lea rax, [bs_str36] ; 0
call pwarn ; 0

mov rax, 1 ; return value in rax
ret

.bs_logic_end34:

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
bsfloat:
mov [bsfloat_whole], rax
mov [bsfloat_decimal], rdi
call bs_makeFloat
mov [bsfloat_pr], rax

mov rax, [bsfloat_pr]
mov rdi, [bsfloat_whole]
mov rsi, [bsfloat_decimal]
call bs_fiSet

mov rax, [bsfloat_pr] ; return value in rax
ret

fimul:
mov [fimul_pr], rax
mov [fimul_val], rdi
mov rax, [fimul_pr]
mov rdi, [fimul_val]
call bs_fiMul
mov [fimul_pr], rax

mov rax, [fimul_pr] ; return value in rax
ret

fiadd:
mov [fiadd_pr], rax
mov [fiadd_val], rdi
mov rax, [fiadd_pr]
mov rdi, [fiadd_val]
call bs_fiAdd
mov [fiadd_pr], rax

mov rax, [fiadd_pr] ; return value in rax
ret

fisub:
mov [fisub_pr], rax
mov [fisub_val], rdi
mov rax, [fisub_pr]
mov rdi, [fisub_val]
call bs_fiSub
mov [fisub_pr], rax

mov rax, [fisub_pr] ; return value in rax
ret

stdout_f:
mov [stdout_f_pr], rax
mov rax, [stdout_f_pr]
call bs_stdoutf

ret
pow:
mov [pow_base], rax
mov [pow_pwr], rdi
mov rax, [pow_pwr]
mov rdx, 0
cmp rax, rdx
jne .bs_logic_end60

mov rax, 1 ; return value in rax
ret

.bs_logic_end60:

mov rax, [pow_pwr]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end64

mov rax, [pow_base] ; return value in rax
ret

.bs_logic_end64:

mov rax, [pow_pwr]
mov rdx, 2
cmp rax, rdx
jne .bs_logic_end68

mov rax, [pow_base]
mov rbx, [pow_base]
mul rbx

mov [pow_base], rax

mov rax, [pow_base] ; return value in rax
ret

.bs_logic_end68:

mov rax, [pow_pwr]
mov rax, [pow_pwr]
mov rbx, 1
sub rax, rbx
mov [pow_pwr], rax

mov rax, [pow_base]
mov [pow_save], rax

lea rax, [bs_str75] ; 0
call stdout ; 0

.pow_bsDo_225:

mov rax, [pow_base]
mov rbx, [pow_save]
mul rbx

mov [pow_base], rax

mov rax, [pow_pwr]
mov rax, [pow_pwr]
mov rbx, 1
sub rax, rbx
mov [pow_pwr], rax

mov rax, [pow_pwr]
mov rdx, 0
cmp rax, rdx
je .bs_logic_end80

jmp .pow_bsDo_225

.bs_logic_end80:

mov rax, [pow_base] ; return value in rax
ret

mod:
mov [mod_dividend], rax
mov [mod_divisor], rdi
mov rax, [mod_divisor]
mov rdx, 0
cmp rax, rdx
jne .bs_logic_end87

lea rax, [bs_str89] ; 0
call print ; 0

mov rax, 1 ; return value in rax
ret

.bs_logic_end87:

mov rax, [mod_dividend]
mov rdi, [mod_divisor]
call bs_modulus
mov [mod_re], rax

mov rax, [mod_re] ; return value in rax
ret

gcd:
mov [gcd_x], rax
mov [gcd_y], rdi
mov rax, [gcd_x]
mov rdx, 0
cmp rax, rdx
jg .bs_logic_end95

mov rax, 0 ; return value in rax
ret

.bs_logic_end95:

mov rax, [gcd_y]
mov rdx, 0
cmp rax, rdx
jg .bs_logic_end99

mov rax, 0 ; return value in rax
ret

.bs_logic_end99:

.gcd_gcdTop:

mov rax, [gcd_y]
mov [gcd_tmp], rax

mov rax, [gcd_x] ; 3
mov rdi, [gcd_y] ; 3
call mod ; 3
mov [gcd_y], rax

mov rax, [gcd_tmp]
mov [gcd_x], rax

mov rax, [gcd_y]
mov rdx, 0
cmp rax, rdx
je .bs_logic_end110

jmp .gcd_gcdTop

.bs_logic_end110:

mov rax, [gcd_x] ; return value in rax
ret

strlen:
mov [strlen_lnstr], rax
lea rax, [bs_str117] ; 0
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

main_x resw 4 ; stores 64-bit int
main_y resw 4 ; stores 64-bit int
main_gc resw 4 ; stores 64-bit int
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
bsfloat_whole resw 4 ; stores 64-bit int
bsfloat_decimal resw 4 ; stores 64-bit int
bsfloat_pr resw 4 ; stores 64-bit int
fimul_pr resw 4 ; stores 64-bit int
fimul_val resw 4 ; stores 64-bit int
fiadd_pr resw 4 ; stores 64-bit int
fiadd_val resw 4 ; stores 64-bit int
fisub_pr resw 4 ; stores 64-bit int
fisub_val resw 4 ; stores 64-bit int
stdout_f_pr resw 4 ; stores 64-bit int
pow_base resw 4 ; stores 64-bit int
pow_pwr resw 4 ; stores 64-bit int
pow_save resw 4 ; stores 64-bit int
mod_dividend resw 4 ; stores 64-bit int
mod_divisor resw 4 ; stores 64-bit int
mod_re resw 4 ; stores 64-bit int
gcd_x resw 4 ; stores 64-bit int
gcd_y resw 4 ; stores 64-bit int
gcd_tmp resw 4 ; stores 64-bit int
strlen_lnstr resw 4 ; stores char
itos_iStr resw 4 ; stores 64-bit int
itos_s resw 4 ; stores char
pow_bsDo_225 resw 4 ; stores char
gcd_gcdTop resw 4 ; stores char
itos_bs_string_itos resw 4 ; stores char

section .data
;--- for recursion ---
recursiveDepth db 0
;--- other ---

bs_str4: db "", 0xa, 0
bs_str11: db "Not implemented", 0xa, 0
bs_str36: db "file already exists", 0
bs_str75: db "", 0xa, 0
bs_str89: db "Division by zero", 0xa, 0
bs_str117: db "strlen: not implemented", 0xa, 0
errno dd 0
warno dd 0
