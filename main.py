import compiler
import parse
import sys
import os

__version__ = "0.0.5 (style heaven)"
__os_name__ = "Windows" if os.name == "nt" else "Linux"

def bs_main(fileName:str, output:str) -> None:
    with open(fileName, "r") as f:
        data = f.readlines()
    ps = parse.parser(fileName, data, [fileName])
    ps.pre_parse()
    ps.blockify()
    cs = compiler.compiler(ps.package(),output)
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
