@.str = private unnamed_addr constant [13 x i8] c"hello world!\00"
declare i32 puts(i8* nocapture) nounwind
define i32 @main(i32 %argc, i8** %argv) {
%main_x = getelementptr [13 x i8]* @.str, i64 0, i64 0
ret i32 0
}
