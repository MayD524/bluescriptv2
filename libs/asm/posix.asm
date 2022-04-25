section .text
%define SYS_EXIT 60

extern malloc

bs_malloc:
    ; rax = size
    
    mov rdi, rax
    call malloc
    test rax, rax
    jz .bs_malloc_end
    ret

    .bs_malloc_end:
    mov rax, 0
    ret

bs_asmExit:
    mov rdi, rax
    mov rax, SYS_EXIT
    syscall
    ret