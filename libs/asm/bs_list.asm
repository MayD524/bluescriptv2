
section .text
; this relies on malloc
;%include "libs/asm/posix.asm"

%define __BS_LIST_END__ 0xFFFFFFF

bs_makeList:
    ; size in rax
    push rax
    call bs_malloc
    ; set the end marker
    pop rdi
    mov dword [rax+rdi*8], __BS_LIST_END__
    ret

bs_length:
    ; list in rax
    mov rdi, 0
    push rax
    .loop:
        inc rdi 
        inc rax
        mov rsi, [rax]
        cmp rsi, __BS_LIST_END__
        jne .loop
    pop rax
    mov rax, rdi
    ret

bs_get:
    ; list in rax
    ; index in rdi
    ; return value in rax
    mov rsi, [rax+rdi*8]
    mov rax, rsi
    ret

bs_insert:
    ; ptr in rax
    ; val in rdi
    ; index in rsi
    mov [rax+rsi*8], rdi
    ret

bs_remove:
    ; ptr in rax
    ; index in rsi
    push rax
    call bs_length
    cmp rax, rsi
    jge .remove_end
    pop rax
    mov dword [rax+rsi*8], 0
    ret
    .remove_end:
    ret