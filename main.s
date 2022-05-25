	.def	 @feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 1
	.def	 WinMain;
	.scl	2;
	.type	32;
	.endef
	.text
	.globl	WinMain
	.align	16, 0x90
WinMain:                                  # @main
# BB#0:
	pushl	%eax
	movl	$L_.str, (%esp)
	calll	_puts
	xorl	%eax, %eax
	popl	%edx
	ret

	.section	.rdata,"r"
L_.str:                                 # @.str
	.asciz	"hello world\n"


