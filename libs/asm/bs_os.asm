
%define MAX_PATH 260

bs_getCwd:
    mov rax, MAX_PATH
    call bs_malloc
    mov rdi, rax
    mov rax, 79
    mov rsi, MAX_PATH
    syscall 
    mov rax, rdi
    ret
