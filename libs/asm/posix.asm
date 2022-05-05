section .text
%define SYS_EXIT 60

bs_asmExit:
    mov rdi, rax
    mov rax, SYS_EXIT
    syscall
    ret