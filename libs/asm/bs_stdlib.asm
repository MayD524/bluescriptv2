
section .data
    bs_negative db "-"

section .text

; why does x64 have to remove pusha and popa :cring:
%macro mpusha 0
    push rax
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push rbp
%endmacro

%macro mpopa 0
    pop rbp
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    pop rax
%endmacro

bluescript2_string_input:
    ; return the string inputted by the user
    ; size in rax
    push rax ; save size
    call bs_malloc
    pop rdx
    mov rsi, rax
    xor rax, rax
    mov rdi, 0
    syscall
    mov rax, rsi
    ret

bs_atoi:
    ; rax = ptr to string
    ; rax = return value
    xor rbx, rbx

    .nextDigit:
        movzx rsi, byte[rax]
        inc rax      ; get next char
        sub rsi, '0' ; convert to int
        imul rbx, 10 ; multiply by 10 to get the next digit
        add rbx, rsi ; rbx = rbx * 10 + rsi

        cmp byte[rax], 10 ; remove \n if it exists
        jne .checkEnd
        inc rax
        .checkEnd:
        cmp byte[rax], 0
        jne .nextDigit
    mov rax, rbx
    ret


bluescript2_unix_print:
    ; string in rax
    ; file descriptor in rdi
    push rax
    xor rbx, rbx

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

bs_exit:
    ; exit code in rax
    mov rdi, rax
    mov rax, 60
    syscall

bluescript2_numeric_print:
    ; number is in rax
    ; use newLine = 1 to print newline
    ; print the number
    ; check if the number is negative
    mov rcx, digitSpace
    cmp rax, 0
    jge .isPos
    neg rax
    
    mpusha
    mov rax, bs_negative
    call bluescript2_unix_print
    mpopa

    .isPos:
    
    xor rbx, rbx ; zero out rbx
    mov rdi, 1
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