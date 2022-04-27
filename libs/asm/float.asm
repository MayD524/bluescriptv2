section .data
    bsFloatDecimalPoint: db ".", 0

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

bs_fSize:
    ; float in rax 
    mov rbx, [rax+1*8]
    mov rcx, [rax+2*8]
    mov r8, 1
    .szLoop:
        mov rax, 10
        imul r8, rax
        cmp rcx, r8
        jg .szLoop
    mov rax, r8
    ret

bs_fiMul:
    ; float in rax
    ; int in rdi
    ; [rax+1*8] is the whole number
    ; [rax+2*8] is the decimal
    mov rbx, [rax+1*8]
    mov rcx, [rax+2*8]

    ; get length of decimal ([rax+2*8])
    push rax
    push rcx
    call bs_fSize
    mov r8, rax
    pop rcx
    pop rax

    imul rbx, rdi
    imul rcx, rdi

    ; if rcx is greater than 100/100, then we need to add 1 to rbx
    .checkCarry:
        cmp rcx, r8
        jb .noAdd
        add rbx, 1
        sub rcx, r8
        jmp .checkCarry

    .noAdd:
    mov [rax+1*8], rbx
    mov [rax+2*8], rcx
    ret


bs_fiAdd:
    ; float in rax
    ; int | float in rdi
    add [rax+1*8], rdi
    ret

bs_stdoutf:
    ; float in rax
    mov r8, [rax+1*8]
    mov r9, [rax+2*8]
    ; remove the negative sign from r9
    
    mov rax, r8
    call stdout_i

    mov rax, bsFloatDecimalPoint
    call stdout

    mov rax, r9
    call stdout_i

    mov rax, newLine
    call stdout

    ret
