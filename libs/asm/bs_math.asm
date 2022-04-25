
bs_modulus:
    ; rax = dividend
    ; rdi = divisor
    ; return rax % rdi
    xor rdx, rdx 
    div rdi ; divide rax by rdi
    mov rax, rdx
    ret

