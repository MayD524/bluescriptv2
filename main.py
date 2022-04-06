import compiler
import parse
import os


def bs_main(fileName:str) -> None:
    with open(fileName, "r") as f:
        data = f.readlines()
    ps = parse.parser(fileName, data, [fileName])
    ps.pre_parse()
    ps.blockify()
    cs = compiler.compiler(ps.package())
    cs.compile()

if __name__ == "__main__":
    test_file = "syntax.bs"
    bs_main(test_file)