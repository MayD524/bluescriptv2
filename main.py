from c_compiler import c_compiler
import llvm_compiler
import compiler
import parse
import sys
import os

__version__ = "0.0.5 (style heaven)"
__os_name__ = "Windows" if os.name == "nt" else "Linux"

def bs_main(fileName:str, output:str) -> None:
    with open(fileName, "r") as f:
        data = f.readlines()
    compiler_type = data[0].strip()
    data = data[1:]
    ps = parse.parser(fileName, data, [fileName])
    ps.structFind()
    ps.pre_parse()
    ps.blockify()

    if compiler_type == "#use llvm":
        cs = llvm_compiler.llvm_compiler(ps.package(),output)
    elif compiler_type == "#use ez180":
        pass
    elif compiler_type == "#use c":
        cs = c_compiler(ps.package(), output)
    else:
        cs = compiler.compiler(ps.package(), output)
    cs.compile()

if __name__ == "__main__":
    DEBUG = False
    print(f"BlueScript Compiler: v{__version__} ({__os_name__}) by May Draskovics")
    if len(sys.argv) < 2:
        sys.tracebacklimit = 0
        print("Usage: bs <file> [output]")
        exit(1)

    print("Compiling...")
    
    filename = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "a.asm"
    bs_main(filename, output)
