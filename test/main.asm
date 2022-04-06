; https://cs.lmu.edu/~ray/notes/nasmtutorial/
; https://www.youtube.com/watch?v=Fz7Ts9RN0o4
; nasm -felf64 main.asm && ld main.o && ./a.out
global    _start
section   .text

;
;   In division
;   rdx = remainder
;   rax = quotient
;


%macro exit 1
    mov   rax, 60
    mov   rdi, %1 
    syscall
%endmacro

print: 
    push rax
    mov  rbx, 0

    print_loop:
        inc rax
        inc rbx
        mov cl, [rax]
        cmp cl, 0
        jne print_loop
        
        mov rax, 1
        mov rdi, 1
        pop rsi 
        mov rdx, rbx
        syscall
    ret

print_number:
    ; number is in rax
    ; print the number

    mov rcx, digitSpace
    mov rbx, 10 
    mov [rcx], rbx
    inc rcx
    mov [digitSpacePos], rcx

    _printLoop: 
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
        jne _printLoop

    _printLoop2:
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
        jge _printLoop2
    ret

input:
    mov rax, 0
    mov rdi, 0
    syscall
    ret

_start:
    ; get the length of the string
    ;mov rax, msg
    mov rax, 123
    call print_number
    exit 1

section .data
    gen.error: db "An error has occurred", 10, 0
    msg: db "Who are you?", 10, 0

section .bss
    name resb 16

    ; for number printing
    digitSpace resb 100
    digitSpacePos resb 8