
./a.out:     file format elf64-x86-64


Disassembly of section .text:

0000000000401000 <print>:
  401000:	50                   	push   %rax
  401001:	bb 00 00 00 00       	mov    $0x0,%ebx

0000000000401006 <print_loop>:
  401006:	48 ff c0             	inc    %rax
  401009:	48 ff c3             	inc    %rbx
  40100c:	8a 08                	mov    (%rax),%cl
  40100e:	80 f9 00             	cmp    $0x0,%cl
  401011:	75 f3                	jne    401006 <print_loop>
  401013:	b8 01 00 00 00       	mov    $0x1,%eax
  401018:	bf 01 00 00 00       	mov    $0x1,%edi
  40101d:	5e                   	pop    %rsi
  40101e:	48 89 da             	mov    %rbx,%rdx
  401021:	0f 05                	syscall 
  401023:	c3                   	retq   

0000000000401024 <input>:
  401024:	b8 00 00 00 00       	mov    $0x0,%eax
  401029:	bf 00 00 00 00       	mov    $0x0,%edi
  40102e:	0f 05                	syscall 
  401030:	90                   	nop
  401031:	90                   	nop
  401032:	90                   	nop
  401033:	90                   	nop
  401034:	c3                   	retq   

0000000000401035 <_start>:
  401035:	48 b8 00 20 40 00 00 	movabs $0x402000,%rax
  40103c:	00 00 00 
  40103f:	e8 bc ff ff ff       	callq  401000 <print>
  401044:	48 be 10 20 40 00 00 	movabs $0x402010,%rsi
  40104b:	00 00 00 
  40104e:	ba 10 00 00 00       	mov    $0x10,%edx
  401053:	e8 cc ff ff ff       	callq  401024 <input>
  401058:	48 b8 10 20 40 00 00 	movabs $0x402010,%rax
  40105f:	00 00 00 
  401062:	e8 99 ff ff ff       	callq  401000 <print>
  401067:	b8 3c 00 00 00       	mov    $0x3c,%eax
  40106c:	bf 01 00 00 00       	mov    $0x1,%edi
  401071:	0f 05                	syscall 

Disassembly of section .data:

0000000000402000 <msg>:
  402000:	57                   	push   %rdi
  402001:	68 6f 20 61 72       	pushq  $0x7261206f
  402006:	65 20 79 6f          	and    %bh,%gs:0x6f(%rcx)
  40200a:	75 3f                	jne    40204b <_end+0x2b>
  40200c:	0a 00                	or     (%rax),%al

Disassembly of section .bss:

0000000000402010 <name>:
	...
