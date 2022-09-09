@.str = private unnamed_addr constant [13 x i8] c"hello world\0A\00"

declare i32 @puts(ptr nocapture) nounwind

define i32 @main() {
    call i32 @puts(ptr @.str)
    ret i32 0
}

!0 = !{i32 42, null, !"string"}
!foo = !{!0}