section .data
    bsFloatDecimalPoint: db "."

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
    mov rcx, [rax*0+8]
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
    ; float in rax
    ; float in rdi
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
    ; float in rax
    ; float in rdi
    push rax
    push rdi
    call bs_fcheck
    call stdout_i
    pop rdi
    pop rax
    ret

bs_fiSet:
    ; float in rax
    ; int in rdi
    ; int in rsi
    mov [rax+1*8], rdi
    mov [rax+2*8], rsi
    ret

bs_fiMul:
    push rax
    call bs_isFloat
    mov r8, rax
    pop rax
    cmp r8, 1
    jne .notFloat
    imul [rax+1*8], rdi

    .notFloat:
    mov rax, 1
    ret

bs_fiAdd:
    ; float in rax
    ; int | float in rdi
    push rax
    call bs_isFloat
    mov r8, rax
    pop rax
    cmp r8, 1
    jne .notFloat

    add [rax+1*8], rdi
    ret

    .notFloat:
    mov rax, 1
    ret

bs_stdoutf:
    ; float in rax
    mov r8, [rax+1*8]
    mov r9, [rax+2*8]

    mov rax, r8
    call stdout_i

    mov rax, bsFloatDecimalPoint
    call stdout

    mov rax, r9
    call stdout_i
    ret
