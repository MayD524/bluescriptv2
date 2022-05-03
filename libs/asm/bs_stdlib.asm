section .bss
    dummy resb 1

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

bs_clearStdin:
    .core:
    xor rax, rax
    mov rdi, 0
    mov rsi, dummy
    mov rdx, 1
    syscall
    cmp byte[rsi], 10
    jne .core
    ret

bs_random:
    ; max in rax
    mov rbx, rax
    rdtsc
    xor rdx, rdx
    div rbx
    mov rax, rdx
    ret

bs_sleepy:
    ; seconds in rax
    ; nanoseconds in rdi
    push rbp

    mov rbp, rsp
    push rdi
    push rax

    mov rax, 35
    mov rdi, rsp
    mov rsi, 0
    syscall
    
    mov rsp, rbp
    pop rbp
    ret

bluescript2_string_input:
    ; return the string inputted by the user
    ; size in rax
    push rax        ; save size
    call bs_malloc  ; make a buffer for the string
    pop rdx         ; size in rdx

    mov rsi, rax    ; string buffer
    xor rax, rax    ; 0 for sys_read
    mov rdi, 0      ; stdin
    syscall

    cmp rax, rdx    ; check if there are any extra characters
    jl .done
    
    push rsi        ; save string buffer
    call bs_clearStdin ; so we don't get more input than we asked for
    pop rsi         ; string buffer
    
    .done:
    mov rax, rsi
    ret

bs_termSize:
    mov rax, 2
    call bs_malloc
    mov rdx, rax
    
    mov rax, 16
    mov rdi, 1
    mov rsi, 0x5413
    syscall

    mov rax, rdx
    ret

bs_at:
    ; rax = ptr
    ; rdi = index
    ; return the value at the index

    cmp rdi, 0
    jg .nonzero
    mov rax, [rax+0*8]
    ret
    .nonzero:
    mov rax, [rax+rdi*2]
    ret

bs_itoa:
    ; rax = int 
    ; rax = new character
    ; rdi = buffer
    push rax
    mov rax, 1
    call bs_malloc
    pop rdx
    mov [rax], rdx
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