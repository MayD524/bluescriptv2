section .text
%define SYS_EXIT 60

extern malloc
extern free

bs_malloc:
    ; rax = size
    mov rdi, rax
    xor rax, rax
    call malloc
    test rax, rax
    jz .bs_malloc_end
    ret

    .bs_malloc_end:
    mov rax, 0
    ret

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