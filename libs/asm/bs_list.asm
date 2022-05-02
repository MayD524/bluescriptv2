
section .text
; this relies on malloc
;%include "libs/asm/posix.asm"

%define __BS_LIST_END__ 0xFFFF

bs_makeList:
    ; size in rax
    push rax
    call bs_malloc
    ; set the end marker
    pop rdi
    imul rdi, 8
    mov dword [rax+rdi], __BS_LIST_END__
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
    imul rdi, 8
    mov rsi, [rax+rdi]
    mov rax, rsi
    ret

bs_insert:
    ; ptr in rax
    ; val in rdi
    ; index in rsi
    imul rsi, 8
    mov [rax+rsi], rdi
    ret

bs_remove:
    ; ptr in rax
    ; index in rdi
    push rax
    call bs_length
    cmp rax, rdi
    jge .remove_end
    pop rax
    imul rdi, 8
    mov dword [rax+rdi], 0
    ret
    .remove_end:
    ret