
section .text
    bs_string_isString:
        ; string in rax
        ; returns 1 if string is a string
        .strloop:
            inc rax
            
            mov cl, [rax]
            cmp cl, 32
            jge .isStr
            cmp cl, 126
            jle .isStr

            cmp cl, 0
            jne .strloop

            mov rax, 0
            ret

        .isStr:
            mov rax, 1
            ret

    bs_string_strlen:
        ; string in rax
        ; returns length of string
        mov rbx, 0
        .strlenloop:
            inc rax
            inc rbx
            mov cl, [rax]
            cmp cl, 0
            jne .strlenloop

        mov rax, rbx
        ret

    bs_string_isNumber:
        ; string in rax
        ; returns 1 if string is a number
        .numloop:
            inc rax

            mov cl, [rax]
            cmp cl, 48
            jge .isNum
            cmp cl, 57
            jle .isNum

            cmp cl, 0
            jne .numloop

            mov rax, 0
            ret
        
        .isNum:
            mov rax, 1
            ret
            
    bs_string_cmp:
        ; string1 in rax
        ; string2 in rdx
        ; returns 1 if string1 is equal to string2
        ; returns 0 if string1 is not equal to string2

        .strcmp:
            inc rax
            inc rdx

            mov cl, [rax]
            mov ch, [rdx]
            cmp cl, ch
            jne .strcmpend

            ; the strings should be the same to here
            cmp cl, 0
            jne .strcmp

            mov rax, 1
            ret

        .strcmpend:
            mov rax, 0
            ret
