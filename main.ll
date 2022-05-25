; Copied directly from the documentation
; Declare the string constant as a global constant.
@.str = private unnamed_addr constant [13 x i8] c"hello world\0A\00"

; External declaration of the puts function
declare i32 @puts(i8* nocapture) nounwind

; Definition of main function
define i32 @main() { ; i32()*
    ; Convert [13 x i8]* to i8  *...
    %1 = bitcast [13 x i8]* @.str to i8*

    ; Call puts function to write out the string to stdout.
    call i32 @puts(i8* %1) nounwind
    ret i32 0
}
