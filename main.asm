global main:
%include "libs/asm/bs_stdlib.asm"
%include "libs/asm/posix.asm"
%include "libs/asm/bs_fstream.asm"
%include "libs/asm/bs_list.asm"
%include "libs/asm/bs_math.asm"
%include "libs/asm/bs_string.asm"
section .text
preamble:
call clearScreen
lea rax, [bs_str0]
call stdout
lea rax, [bs_str1]
call stdout
mov rax, 1
mov rdi, 4
call setColor
lea rax, [bs_str2]
call stdout
call termReset
lea rax, [bs_str3]
call stdout
call PAUSE
call clearScreen
ret
gameLoop:
mov [gameLoop_pCount], rax
mov rax, 0
mov [gameLoop_totalOccupiedCells], rax
mov rax, 0
mov [gameLoop_isRunning], rax
mov rax, 0
mov [gameLoop_turn], rax
.gameLoop_bsDo_25:
call clearScreen
call drawCells
lea rax, [bs_str9]
call stdout
mov rax, [gameLoop_turn]
mov rdx, 0
cmp rax, rdx
jne .bs_logic_end9
lea rax, [bs_str12]
call stdout
.bs_logic_end9:
mov rax, [gameLoop_turn]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end12
lea rax, [bs_str15]
call stdout
.bs_logic_end12:
mov rax, [gameLoop_turn]
mov [gameLoop_tmp], rax
mov rax, [gameLoop_tmp]
add rax, [gameLoop_pCount]
mov [gameLoop_tmp], rax
mov rax, [gameLoop_tmp]
mov rdx, 2
cmp rax, rdx
jne .bs_logic_end17
.gameLoop_cpuTryAgain:
mov rax, 0
mov rdi, 9
call randint
mov [gameLoop_choice], rax
mov rax, [gameLoop_choice]
mov rdi, 2
call updateCell
mov [gameLoop_rVal], rax
mov rax, [gameLoop_rVal]
mov rdx, 0
cmp rax, rdx
je .bs_logic_end30
jmp .gameLoop_cpuTryAgain
.bs_logic_end30:
jmp .gameLoop_cpuTurnEnd
.bs_logic_end17:
mov rax, 0
mov [gameLoop_validChoice], rax
.gameLoop_bsDo_48:
call termReset
lea rax, [bs_str46]
call iprompt
mov [gameLoop_choice], rax
mov rax, [gameLoop_choice]
mov rdx, 1
cmp rax, rdx
jge .bs_logic_end46
mov rax, 1
mov rdi, 1
call setColor
lea rax, [bs_str50]
call stdout
jmp .gameLoop_bsDo_48
.bs_logic_end46:
mov rax, [gameLoop_choice]
mov rdx, 9
cmp rax, rdx
jle .bs_logic_end54
mov rax, 1
mov rdi, 1
call setColor
lea rax, [bs_str58]
call stdout
jmp .gameLoop_bsDo_48
.bs_logic_end54:
mov rax, [gameLoop_choice]
mov rax, [gameLoop_choice]
mov rbx, 1
sub rax, rbx
mov [gameLoop_choice], rax
mov rax, 1
mov [gameLoop_validChoice], rax
mov rax, [gameLoop_validChoice]
mov rdx, 0
cmp rax, rdx
jne .bs_logic_end67
jmp .gameLoop_bsDo_48
.bs_logic_end67:
mov rax, [gameLoop_turn]
mov [gameLoop_cVal], rax
mov rax, [gameLoop_cVal]
add rax, 1
mov [gameLoop_cVal], rax
mov rax, [gameLoop_choice]
mov rdi, [gameLoop_cVal]
call updateCell
mov [gameLoop_retVal], rax
mov rax, [gameLoop_retVal]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end77
mov rax, 1
mov rdi, 1
call setColor
lea rax, [bs_str81]
call stdout
call termReset
jmp .gameLoop_bsDo_25
.bs_logic_end77:
.gameLoop_cpuTurnEnd:
mov rax, [gameLoop_turn]
add rax, 1
mov [gameLoop_turn], rax
mov rax, [gameLoop_turn]
mov rdx, 2
cmp rax, rdx
jne .bs_logic_end90
mov rax, 0
mov [gameLoop_turn], rax
.bs_logic_end90:
mov rax, 1
mov rdi, 5
call setColor
lea rax, [bs_str97]
call stdout
lea rax, [bs_str98]
call stdout
call termReset
mov rax, [gameLoop_totalOccupiedCells]
add rax, 1
mov [gameLoop_totalOccupiedCells], rax
mov rax, [gameLoop_totalOccupiedCells]
call checkWin
mov [gameLoop_isRunning], rax
mov rax, [gameLoop_isRunning]
mov rdx, 0
cmp rax, rdx
jne .bs_logic_end101
jmp .gameLoop_bsDo_25
.bs_logic_end101:
call clearScreen
call drawCells
lea rax, [bs_str107]
call stdout
mov rax, [gameLoop_isRunning]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end107
lea rax, [bs_str110]
call stdout
.bs_logic_end107:
mov rax, [gameLoop_isRunning]
mov rdx, 2
cmp rax, rdx
jne .bs_logic_end110
lea rax, [bs_str113]
call stdout
.bs_logic_end110:
mov rax, [gameLoop_isRunning]
mov rdx, 3
cmp rax, rdx
jne .bs_logic_end113
lea rax, [bs_str116]
call stdout
.bs_logic_end113:
lea rax, [bs_str117]
call stdout
ret
playerCount:
call termReset
.playerCount_TryAgain:
lea rax, [bs_str122]
call iprompt
mov [playerCount_total], rax
mov rax, [playerCount_total]
mov rdx, 1
cmp rax, rdx
jge .bs_logic_end122
mov rax, 1
mov rdi, 1
call setColor
lea rax, [bs_str126]
call stdout
jmp .playerCount_TryAgain
.bs_logic_end122:
mov rax, [playerCount_total]
mov rdx, 2
cmp rax, rdx
jle .bs_logic_end130
mov rax, 1
mov rdi, 1
call setColor
lea rax, [bs_str134]
call stdout
jmp .playerCount_TryAgain
.bs_logic_end130:
mov rax, [playerCount_total]
ret
main:
mov [main_argc], rdi
mov [main_argv], rsi
call clearScreen
call preamble
call playerCount
mov [main_total], rax
mov rax, [main_total]
mov rdx, 2
cmp rax, rdx
jne .bs_logic_end142
mov rax, 0
mov [main_total], rax
.bs_logic_end142:
call init
mov rax, [main_total]
call gameLoop
mov rax, 60
mov rdi, 0
syscall
ret
randint:
mov [randint_min], rax
mov [randint_max], rdi
mov rax, [randint_max]
add rax, 1
mov [randint_max], rax
mov rax, [randint_max]
call bs_random
mov [randint_num], rax
mov rax, [randint_num]
mov rdx, [randint_min]
cmp rax, rdx
jge .bs_logic_end151
mov rax, [randint_num]
add rax, [randint_min]
mov [randint_num], rax
.bs_logic_end151:
mov rax, [randint_num]
ret
setColor:
mov [setColor_modif], rax
mov [setColor_color], rdi
mov rax, [setColor_color]
mov rdx, 0
cmp rax, rdx
jge .bs_logic_end157
lea rax, [bs_str160]
call raise
.bs_logic_end157:
mov rax, [setColor_color]
mov rdx, 8
cmp rax, rdx
jle .bs_logic_end160
lea rax, [bs_str163]
call raise
.bs_logic_end160:
mov rax, [setColor_color]
add rax, 30
mov [setColor_color], rax
lea rax, [bs_str164]
call stdout
mov rax, [setColor_modif]
call stdout_i
lea rax, [bs_str165]
call stdout
mov rax, [setColor_color]
call stdout_i
lea rax, [bs_str166]
call stdout
ret
termReset:
lea rax, [bs_str167]
call stdout
ret
setCursorPos:
mov [setCursorPos_x], rax
mov [setCursorPos_y], rdi
lea rax, [bs_str168]
call stdout
mov rax, [setCursorPos_y]
call stdout_i
lea rax, [bs_str169]
call stdout
mov rax, [setCursorPos_x]
call stdout_i
lea rax, [bs_str170]
call stdout
ret
stderr:
mov [stderr_msg], rax
mov [stderr_eno], rdi
mov rax, [stderr_msg]
mov rdi, 2
call bluescript2_unix_print
mov rax, [stderr_eno]
mov rdx, 0
cmp rax, rdx
je .bs_logic_end170
mov rax, [stderr_eno]
call exit
.bs_logic_end170:
mov rax, [warno]
add rax, 1
mov [warno], rax
mov rax, [warno]
mov rdx, 2
cmp rax, rdx
jle .bs_logic_end174
mov rax, 1
call exit
.bs_logic_end174:
ret
ret
PAUSE:
lea rax, [bs_str179]
call prompt
mov [PAUSE_x], rax
ret
raise:
mov [raise_msg], rax
mov rax, [raise_msg]
mov rdi, 1
call stderr
ret
stdout:
mov [stdout_msg], rax
mov rax, [stdout_msg]
mov rdi, [STDOUT]
call bluescript2_unix_print
ret
clearScreen:
lea rax, [bs_str180]
call stdout
mov rax, 0
mov rdi, 0
call setCursorPos
ret
atoi:
mov [atoi_intStr], rax
mov rax, [atoi_intStr]
call bs_atoi
mov [atoi_in], rax
mov rax, [atoi_in]
ret
sprompt:
mov [sprompt_prmpt], rax
mov [sprompt_msgSize], rdi
mov rax, [sprompt_prmpt]
call stdout
mov rax, [sprompt_msgSize]
call bluescript2_string_input
mov [sprompt_theString], rax
mov rax, [sprompt_theString]
ret
prompt:
mov [prompt_prmpt], rax
mov rax, [prompt_prmpt]
mov rdi, [stdinBuffSize]
call sprompt
mov [prompt_inp], rax
mov rax, [prompt_inp]
ret
iprompt:
mov [iprompt_prmpt], rax
mov rax, [iprompt_prmpt]
mov rdi, 4
call sprompt
mov [iprompt_dt], rax
mov rax, [iprompt_dt]
call atoi
mov [iprompt_dti], rax
mov rax, [iprompt_dti]
ret
print:
mov [print_msg], rax
mov rax, [print_msg]
call stdout
ret
stdout_i:
mov [stdout_i_msg], rax
mov rax, [stdout_i_msg]
call bluescript2_numeric_print
ret
exit:
mov [exit_eno], rax
mov rax, [exit_eno]
call bs_exit
ret
displayCell:
mov [displayCell_cellID], rax
mov rax, [gameState]
mov rdi, [displayCell_cellID]
call li_get
mov [displayCell_cell], rax
mov rax, [displayCell_cell]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end200
lea rax, [bs_str203]
call stdout
ret
.bs_logic_end200:
mov rax, [displayCell_cell]
mov rdx, 2
cmp rax, rdx
jne .bs_logic_end204
lea rax, [bs_str207]
call stdout
ret
.bs_logic_end204:
lea rax, [bs_str208]
call stdout
ret
drawCells:
mov rax, 0
mov [drawCells_cellID], rax
mov rax, 0
mov rdi, 0
call setCursorPos
.drawCells_bsDo_356:
mov rax, [drawCells_cellID]
call displayCell
mov rax, [drawCells_cellID]
add rax, 1
mov [drawCells_cellID], rax
mov rax, [drawCells_cellID]
mov rdi, 3
call mod
mov [drawCells_newRow], rax
mov rax, [drawCells_newRow]
mov rdx, 0
cmp rax, rdx
jne .bs_logic_end215
lea rax, [bs_str218]
call stdout
.bs_logic_end215:
mov rax, [drawCells_cellID]
mov rdx, 9
cmp rax, rdx
jge .bs_logic_end218
jmp .drawCells_bsDo_356
.bs_logic_end218:
ret
checkLine:
mov [checkLine_line], rax
mov rax, [checkLine_line]
mov [checkLine_i], rax
mov rax, [checkLine_i]
mov rbx, 3
mul rbx
mov [checkLine_i], rax
mov rax, 0
mov [checkLine_x], rax
mov rax, 0
mov [checkLine_xCount], rax
mov rax, 0
mov [checkLine_oCount], rax
.checkLine_bsDo_373:
mov rax, [gameState]
mov rdi, [checkLine_i]
call li_get
mov [checkLine_cell], rax
mov rax, [checkLine_cell]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end234
mov rax, [checkLine_xCount]
add rax, 1
mov [checkLine_xCount], rax
.bs_logic_end234:
mov rax, [checkLine_cell]
mov rdx, 2
cmp rax, rdx
jne .bs_logic_end238
mov rax, [checkLine_oCount]
add rax, 1
mov [checkLine_oCount], rax
.bs_logic_end238:
mov rax, [checkLine_i]
add rax, 1
mov [checkLine_i], rax
mov rax, [checkLine_x]
add rax, 1
mov [checkLine_x], rax
mov rax, [checkLine_x]
mov rdx, 3
cmp rax, rdx
jge .bs_logic_end244
jmp .checkLine_bsDo_373
.bs_logic_end244:
mov rax, [checkLine_xCount]
mov rdx, 3
cmp rax, rdx
jne .bs_logic_end250
mov rax, 1
ret
.bs_logic_end250:
mov rax, [checkLine_oCount]
mov rdx, 3
cmp rax, rdx
jne .bs_logic_end255
mov rax, 2
ret
.bs_logic_end255:
mov rax, 0
ret
checkDiagonals:
mov rax, [gameState]
mov rdi, 4
call li_get
mov [checkDiagonals_center], rax
mov rax, [checkDiagonals_center]
mov rdx, 2
cmp rax, rdx
jle .bs_logic_end264
mov rax, 0
ret
.bs_logic_end264:
mov rax, [checkDiagonals_center]
mov rdx, 0
cmp rax, rdx
jne .bs_logic_end269
mov rax, 0
ret
.bs_logic_end269:
mov rax, [gameState]
mov rdi, 0
call li_get
mov [checkDiagonals_topLeft], rax
mov rax, [gameState]
mov rdi, 8
call li_get
mov [checkDiagonals_bottomRight], rax
mov rax, [checkDiagonals_topLeft]
mov rdx, [checkDiagonals_center]
cmp rax, rdx
jne .bs_logic_end278
mov rax, [checkDiagonals_bottomRight]
mov rdx, [checkDiagonals_center]
cmp rax, rdx
jne .bs_logic_end281
mov rax, [checkDiagonals_center]
ret
.bs_logic_end278:
.bs_logic_end281:
mov rax, [gameState]
mov rdi, 2
call li_get
mov [checkDiagonals_topRight], rax
mov rax, [gameState]
mov rdi, 6
call li_get
mov [checkDiagonals_bottomLeft], rax
mov rax, [checkDiagonals_topRight]
mov rdx, [checkDiagonals_center]
cmp rax, rdx
jne .bs_logic_end290
mov rax, [checkDiagonals_bottomLeft]
mov rdx, [checkDiagonals_center]
cmp rax, rdx
jne .bs_logic_end293
mov rax, [checkDiagonals_center]
ret
.bs_logic_end290:
.bs_logic_end293:
mov rax, 0
ret
checkCol:
mov [checkCol_col], rax
mov rax, [checkCol_col]
mov [checkCol_i], rax
mov rax, 0
mov [checkCol_x], rax
mov rax, 0
mov [checkCol_xCount], rax
mov rax, 0
mov [checkCol_oCount], rax
.checkCol_bsDo_423:
mov rax, [gameState]
mov rdi, [checkCol_i]
call li_get
mov [checkCol_cell], rax
mov rax, [checkCol_cell]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end309
mov rax, [checkCol_xCount]
add rax, 1
mov [checkCol_xCount], rax
.bs_logic_end309:
mov rax, [checkCol_cell]
mov rdx, 2
cmp rax, rdx
jne .bs_logic_end313
mov rax, [checkCol_oCount]
add rax, 1
mov [checkCol_oCount], rax
.bs_logic_end313:
mov rax, [checkCol_i]
add rax, 3
mov [checkCol_i], rax
mov rax, [checkCol_x]
add rax, 1
mov [checkCol_x], rax
mov rax, [checkCol_x]
mov rdx, 3
cmp rax, rdx
jge .bs_logic_end319
jmp .checkCol_bsDo_423
.bs_logic_end319:
mov rax, [checkCol_xCount]
mov rdx, 3
cmp rax, rdx
jne .bs_logic_end325
mov rax, 1
ret
.bs_logic_end325:
mov rax, [checkCol_oCount]
mov rdx, 3
cmp rax, rdx
jne .bs_logic_end330
mov rax, 2
ret
.bs_logic_end330:
mov rax, 0
ret
checkWin:
mov [checkWin_totalOccupiedCells], rax
mov rax, 0
mov [checkWin_i], rax
.checkWin_bsDo_443:
mov rax, [checkWin_i]
call checkLine
mov [checkWin_winner], rax
mov rax, [checkWin_winner]
mov rdx, 0
cmp rax, rdx
je .bs_logic_end343
mov rax, [checkWin_winner]
ret
.bs_logic_end343:
mov rax, [checkWin_i]
call checkCol
mov [checkWin_winner], rax
mov rax, [checkWin_winner]
mov rdx, 0
cmp rax, rdx
je .bs_logic_end350
mov rax, [checkWin_winner]
ret
.bs_logic_end350:
mov rax, [checkWin_i]
add rax, 1
mov [checkWin_i], rax
mov rax, [checkWin_i]
mov rdx, 3
cmp rax, rdx
jge .bs_logic_end356
jmp .checkWin_bsDo_443
.bs_logic_end356:
call checkDiagonals
mov [checkWin_diag], rax
mov rax, [checkWin_diag]
mov rdx, 0
cmp rax, rdx
je .bs_logic_end364
mov rax, [checkWin_diag]
ret
.bs_logic_end364:
mov rax, [checkWin_totalOccupiedCells]
mov rdx, 9
cmp rax, rdx
jl .bs_logic_end369
mov rax, 3
ret
.bs_logic_end369:
mov rax, 0
ret
updateCell:
mov [updateCell_cellID], rax
mov [updateCell_newVal], rdi
mov rax, [gameState]
call li_size
mov [updateCell_sz], rax
mov rax, [updateCell_cellID]
mov rdx, [updateCell_sz]
cmp rax, rdx
jl .bs_logic_end378
mov rax, 1
ret
.bs_logic_end378:
mov rax, [gameState]
mov rdi, [updateCell_cellID]
call li_get
mov [updateCell_cVal], rax
mov rax, [updateCell_cVal]
mov rdx, 1
cmp rax, rdx
jne .bs_logic_end385
mov rax, 1
ret
.bs_logic_end385:
mov rax, [updateCell_cVal]
mov rdx, 2
cmp rax, rdx
jne .bs_logic_end390
mov rax, 1
ret
.bs_logic_end390:
mov rax, [gameState]
mov rdi, [updateCell_newVal]
mov rsi, [updateCell_cellID]
call li_insert
mov rax, 0
ret
init:
mov rax, 9
call List
mov [init_liPtr], rax
mov rax, [gameState]
add rax, [init_liPtr]
mov [gameState], rax
ret
open:
mov [open_pth], rax
mov [open_mode], rdi
mov rax, [SYS_open]
mov rdi, [open_pth]
mov rsi, [open_mode]
call bs_open
mov [open_sysc], rax
mov rax, [open_sysc]
ret
close:
mov [close_fd], rax
mov rax, [SYS_close]
mov rdi, [close_fd]
call bs_close
mov [close_sysc], rax
mov rax, [close_sysc]
ret
fileExists:
mov [fileExists_pth], rax
mov rax, [fileExists_pth]
mov rdi, [O_RDONLY]
call open
mov [fileExists_rx], rax
mov rax, [fileExists_rx]
mov rdx, 100
cmp rax, rdx
jge .bs_logic_end410
mov rax, [fileExists_rx]
call close
mov rax, 1
ret
.bs_logic_end410:
mov rax, 0
ret
pwarn:
mov [pwarn_err], rax
mov rax, [pwarn_err]
call print
ret
List:
mov [List_size], rax
mov rax, [List_size]
call bs_makeList
mov [List_pr], rax
mov rax, [List_pr]
ret
li_insert:
mov [li_insert_pr], rax
mov [li_insert_value], rdi
mov [li_insert_index], rsi
mov rax, [li_insert_pr]
call li_size
mov [li_insert_size], rax
mov rax, [li_insert_index]
mov rdx, [li_insert_size]
cmp rax, rdx
jle .bs_logic_end424
lea rax, [bs_str427]
call raise
ret
.bs_logic_end424:
mov rax, [li_insert_pr]
mov rdi, [li_insert_index]
call li_get
mov [li_insert_x], rax
mov rax, [li_insert_x]
mov rdx, [BS_ENDOF_LIST]
cmp rax, rdx
jne .bs_logic_end430
ret
.bs_logic_end430:
mov rax, [li_insert_pr]
mov rdi, [li_insert_value]
mov rsi, [li_insert_index]
call bs_insert
ret
li_get:
mov [li_get_pr], rax
mov [li_get_index], rdi
mov rax, [li_get_pr]
call li_size
mov [li_get_sz], rax
mov rax, [li_get_index]
mov rdx, [li_get_sz]
cmp rax, rdx
jl .bs_logic_end435
ret
.bs_logic_end435:
mov rax, [li_get_pr]
mov rdi, [li_get_index]
call bs_get
mov [li_get_got], rax
mov rax, [li_get_got]
ret
li_size:
mov [li_size_pr], rax
mov rax, [li_size_pr]
call bs_length
mov [li_size_sz], rax
mov rax, [li_size_sz]
mov rdx, 0
mov rax, [li_size_sz]
mov rcx, 8
div rcx
mov [li_size_sz], rax
mov rax, [li_size_sz]
ret
mod:
mov [mod_dividend], rax
mov [mod_divisor], rdi
mov rax, [mod_divisor]
mov rdx, 0
cmp rax, rdx
jne .bs_logic_end449
lea rax, [bs_str452]
call print
mov rax, 1
ret
.bs_logic_end449:
mov rax, [mod_dividend]
mov rdi, [mod_divisor]
call bs_modulus
mov [mod_re], rax
mov rax, [mod_re]
ret
section .rodata
bs_str438 dd "BS_ENDOF_LIST", 0
STDOUT dd 1
SYS_open dd 2
SYS_close dd 3
O_RDONLY dd 0
BS_ENDOF_LIST dd 0xFFFF
section .bss
digitSpace resb 100
digitSpacePos resb 8
main_argc resw 4
main_argv resw 10
gameLoop_pCount resw 4
gameLoop_totalOccupiedCells resw 4
gameLoop_isRunning resw 4
gameLoop_turn resw 4
gameLoop_tmp resw 4
gameLoop_choice resw 4
gameLoop_rVal resw 4
gameLoop_validChoice resw 4
gameLoop_cVal resw 4
gameLoop_retVal resw 4
playerCount_total resw 4
main_total resw 4
randint_min resw 4
randint_max resw 4
randint_num resw 4
setColor_modif resw 4
setColor_color resw 4
setCursorPos_x resw 4
setCursorPos_y resw 4
stderr_msg resw 4
stderr_eno resw 4
PAUSE_x resw 4
raise_msg resw 4
stdout_msg resw 4
atoi_intStr resw 4
atoi_in resw 4
sprompt_prmpt resw 4
sprompt_msgSize resw 4
sprompt_theString resw 4
prompt_prmpt resw 4
prompt_inp resw 4
iprompt_prmpt resw 4
iprompt_dt resw 4
iprompt_dti resw 4
print_msg resw 4
stdout_i_msg resw 4
exit_eno resw 4
displayCell_cellID resw 4
displayCell_cell resw 4
drawCells_cellID resw 4
drawCells_newRow resw 4
checkLine_line resw 4
checkLine_i resw 4
checkLine_x resw 4
checkLine_xCount resw 4
checkLine_oCount resw 4
checkLine_cell resw 4
checkDiagonals_center resw 4
checkDiagonals_topLeft resw 4
checkDiagonals_bottomRight resw 4
checkDiagonals_topRight resw 4
checkDiagonals_bottomLeft resw 4
checkCol_col resw 4
checkCol_i resw 4
checkCol_x resw 4
checkCol_xCount resw 4
checkCol_oCount resw 4
checkCol_cell resw 4
checkWin_totalOccupiedCells resw 4
checkWin_i resw 4
checkWin_winner resw 4
checkWin_diag resw 4
updateCell_cellID resw 4
updateCell_newVal resw 4
updateCell_sz resw 4
updateCell_cVal resw 4
init_liPtr resw 4
open_pth resw 4
open_mode resw 4
open_sysc resw 4
close_fd resw 4
close_sysc resw 4
fileExists_pth resw 4
fileExists_rx resw 4
pwarn_err resw 4
List_size resw 4
List_pr resw 4
li_insert_pr resw 4
li_insert_value resw 4
li_insert_index resw 4
li_insert_size resw 4
li_insert_x resw 4
li_get_pr resw 4
li_get_index resw 4
li_get_sz resw 4
li_get_got resw 4
li_size_pr resw 4
li_size_sz resw 4
mod_dividend resw 4
mod_divisor resw 4
mod_re resw 4
section .data
bs_str0: db 87,101,108,99,111,109,101,32,116,111,32,116,104,101,32,103,97,109,101,33,10, 0
bs_str1: db 84,104,105,115,32,105,115,32,97,32,116,105,99,32,116,97,99,32,116,111,101,32,103,97,109,101,44,32,119,114,105,116,116,101,110,32,105,110,32, 0
bs_str2: db 66,108,117,101,83,99,114,105,112,116,46,10, 0
bs_str3: db 65,117,116,104,111,114,58,32,77,97,121,32,68,114,97,115,107,111,118,105,99,115,10, 0
bs_str9: db 80,108,97,121,101,114,32, 0
bs_str12: db 88,32,116,117,114,110,33,10, 0
bs_str15: db 79,32,116,117,114,110,33,10, 0
bs_str46: db 80,108,97,121,101,114,32,115,101,108,101,99,116,58,32, 0
bs_str50: db 73,110,118,97,108,105,100,32,99,104,111,105,99,101,33,10, 0
bs_str58: db 73,110,118,97,108,105,100,32,99,104,111,105,99,101,33,10, 0
bs_str81: db 73,110,118,97,108,105,100,32,105,110,112,117,116,33,32,115,112,97,99,101,32,105,115,32,111,99,99,117,112,105,101,100,46,10, 0
bs_str97: db 27,91,50,75, 0
bs_str98: db 78,101,120,116,32,116,117,114,110,33,10, 0
bs_str107: db 71,97,109,101,32,111,118,101,114,33,10, 0
bs_str110: db 80,108,97,121,101,114,32,88,32,119,105,110,115,33,10, 0
bs_str113: db 80,108,97,121,101,114,32,79,32,119,105,110,115,33,10, 0
bs_str116: db 68,114,97,119,33,10, 0
bs_str117: db 10, 0
bs_str122: db 72,111,119,32,109,97,110,121,32,112,108,97,121,101,114,115,63,32,49,32,111,114,32,50,58,32, 0
bs_str126: db 73,110,118,97,108,105,100,32,105,110,112,117,116,33,10, 0
bs_str134: db 73,110,118,97,108,105,100,32,105,110,112,117,116,33,10, 0
bs_str160: db 99,111,108,111,114,32,109,117,115,116,32,98,101,32,62,61,32,48, 0
bs_str163: db 99,111,108,111,114,32,109,117,115,116,32,98,101,32,60,61,32,56, 0
bs_str164: db 27,91, 0
bs_str165: db 59, 0
bs_str166: db 109, 0
bs_str167: db 27,91,48,109, 0
bs_str168: db 27,91, 0
bs_str169: db 59, 0
bs_str170: db 72, 0
bs_str179: db 80,114,101,115,115,32,101,110,116,101,114,32,116,111,32,99,111,110,116,105,110,117,101,46,46,46, 0
bs_str180: db 27,49,98,27,91,50,74, 0
bs_str203: db 88, 0
bs_str207: db 79, 0
bs_str208: db 45, 0
bs_str218: db 10, 0
bs_str427: db 108,105,95,105,110,115,101,114,116,58,32,105,110,100,101,120,32,111,117,116,32,111,102,32,114,97,110,103,101,10, 0
bs_str452: db 68,105,118,105,115,105,111,110,32,98,121,32,122,101,114,111,10, 0
bs_str459: db 34,27,49,98,27,91,50,74,34, 0
bs_str460: db 34,112,111,115,105,120,34, 0
stdinBuffSize dd 1024
warno dd 0
gameState dd 0