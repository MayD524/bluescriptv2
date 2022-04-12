%define sys_brk 0x1000

bluescript2_generic_print: 
    ; string in rax
    push rax
    mov  rbx, 0

    .print_loop:
        inc rax
        inc rbx
        mov cl, [rax]
        cmp cl, 0
        jne .print_loop
        
        mov rax, 1
        mov rdi, 1
        pop rsi 
        mov rdx, rbx
        syscall
    ret

bluescript2_numeric_print:
    ; number is in rax
    ; print the number

    mov rcx, digitSpace
    mov rbx, 10 
    mov [rcx], rbx
    inc rcx
    mov [digitSpacePos], rcx

    ._printLoop: 
        mov rdx, 0  ; stops rdx from being concatenated
        mov rbx, 10
        div rbx
        push rax
        add rdx, 48

        mov rcx, [digitSpacePos]
        mov [rcx], dl ; load the character
        inc rcx 
        mov [digitSpacePos], rcx

        pop rax
        cmp rax, 0
        jne ._printLoop

    ._printLoop2:
        ; print the number in reverse
        mov rcx, [digitSpacePos]
        
        ; the printing
        mov rax, 1
        mov rdi, 1
        mov rsi, rcx
        mov rdx, 1
        syscall 

        ; load the next character
        mov rcx, [digitSpacePos]
        dec rcx
        mov [digitSpacePos], rcx

        ; check if we are at the end
        cmp rcx, digitSpace
        jge ._printLoop2
    ret

bluescript2_string_copy:
    ; string in rax
    ; destination in rdi
    ; copy till null byte

    ._copyLoop:
        mov cl, [rax]
        cmp cl, 0
        je ._copyLoopEnd
        mov [rdi], cl
        inc rdi
        inc rax
        jmp ._copyLoop
    
    ._copyLoopEnd:
    ret

bluescript2_string_cmp:
    ; string in rax
    ; string to compare with in rdi
    ; returns 0 if equal, 1 if not equal
    ._cmpLoop:
        mov cl, [rax]
        mov dl, [rdi]
        cmp cl, dl
        jne .notEqual
        inc rax
        inc rdi
        jmp ._cmpLoop
    
    .areEqual:
        mov rax, 0
        ret

    .notEqual:
        mov rax, 1
        ret


bluescript2_atoi:
    ; string in rax
    ; returns the number
    ; if the string is not a number, returns 0