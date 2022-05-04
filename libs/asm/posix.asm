section .text
%define SYS_EXIT 60

extern free

bs_free:
    mov rdi, rax
    xor rax, rax
    call bs_free
    ret

bs_asmExit:
    mov rdi, rax
    mov rax, SYS_EXIT
    syscall
    ret