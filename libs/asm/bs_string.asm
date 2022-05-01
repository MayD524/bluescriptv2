
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

    bs_concat:
        ; string1 in rax
        ; string2 in rdi
        ; join string1 and string2
        ; returns joined string

        ; get length of string1
        mov rbx, 0
        .strlenloop:
            inc rax
            inc rbx
            mov cl, [rax]
            cmp cl, 0
            jne .strlenloop
        
        ; get length of string2
        mov rcx, 0
        .strlenloop2:
            inc rdi
            inc rcx
            mov cl, [rdi]
            cmp cl, 0
            jne .strlenloop2
        

        ; allocate space for new string

        ; get the new size
        mov r8, rbx
        add r8, rcx
        add r8, 1 ; add 1 for null terminator

        mov rax, r8
        call bs_malloc
        mov rsi, rax ; save new string address in rsi
            
        ; copy string1 to new string
        .strcpyloop:
            mov cl, [rax]
            mov [rsi], cl
            inc rax
            inc rsi
            cmp cl, 0
            jne .strcpyloop
        
        ; copy string2 to new string
        .strcpyloop2:
            mov cl, [rdi]
            mov [rsi], cl
            inc rdi
            inc rsi
            cmp cl, 0
            jne .strcpyloop2
        
        mov dword [rsi], 0 ; null terminate new string

        ; return new string
        mov rax, rsi
        ret
