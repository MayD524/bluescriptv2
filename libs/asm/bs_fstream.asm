section .text
; file manipulations

; open a file
extern _open

bs_open:
    ; path = rax
    ; mode = rdi
    mov rsi, rdi
    mov rdi, rax
    mov rax, 3
    mov rdx, 0
    syscall 
    ret

bs_close:
    ; fd = rax
    mov rdi, rax
    mov rax, 4
    syscall
    ret

bs_write:
    ; fd = rax
    ; buf = rdi
    ; len = rsi
    mov rdi, rax
    mov rsi, rdi
    mov rax, 1
    syscall
    ret

bs_fileSize:
    ; fd = rax
    mov rdi, rax
    mov rsi, 0
    mov rdx, 2
    mov rax, 8
    syscall
    ; size in rax
    ret

bs_read:
    ; fd = rax
    ; count = rdi
    sub rsp, rsi
    mov rdi, rax
    mov rsi, rsp
    mov rax, 0
    syscall
    ; read in rax
    mov rax, rsp
    pop rsp

    ret