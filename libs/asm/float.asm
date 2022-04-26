section .text
%define __BS_FLOAT_HEAD__ 0xfc

bs_makeFloat:
    mov rax, 3 ; 16-bit float
    call bs_malloc
    ; stores ptr to float in rax
    ; set the first 8 bits of the float to
    mov dword [rax+0*8], __BS_FLOAT_HEAD__
    ret

bs_isFloat:
    ; check if the first byte is 0xfc
    mov rcx, [rax+0*8]
    cmp rcx, __BS_FLOAT_HEAD__
    jne .bs_isNotFloat
    ; if it is, return 1
    mov rax, 1
    ret
    .bs_isNotFloat:
    ; if it isn't, return 0
    mov rax, 0
    ret

bs_fcheck:
    ; int | float in rax
    ; int | float in rdi
    mov rbx, 0
    push rax

    call bs_isFloat
    mov r8, rax

    mov rax, rdi
    call bs_isFloat
    mov r9, rax
    pop rax

    cmp r8, 1
    jne .r8NotFloat
    add rbx, 1
    
    cmp r9,  1
    jne .r9NotFloat
    add rbx, 1 
    ; both are floats
    mov rax, rbx
    ret
    
    .r8NotFloat:
    cmp r9, 1
    jne .r9NotFloat
    add rbx,1 

    .r9NotFloat:
    mov rax, rbx
    ret


bs_fAdd:
    ; int | float in rax
    ; int | float in rdi
    push rax
    push rdi
    call bs_fcheck
    call stdout_i
    pop rdi
    pop rax
    ret
