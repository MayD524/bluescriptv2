
from pprint import pprint
import sys
import os

IS_DEBUG = True
os_name = os.name


TOKEN_TYPES = [
    "BS_STRING_TOKEN_AHOY", 
    "BS_VARIABLE_TOKEN", 
    "BS_INT_TOKEN", 
    "BS_FLOAT_TOKEN", 
    "BS_FUNCTION_TOKEN",
    "BS_STRUCT_TOKEN",
]

DEBUG = False

ESCAPE_CHARACTERS = {
    "n" : 0xa,
    "x" : 0x1b,
    "t" : 0x9,
    "b" : 0x7,
    "d" : 0x8,
    "r" : 0xd,
    "v" : 0xb
}

class c_compiler:
    def __init__(self, packagedData: dict[str,dict], outFile:str="a.c") -> None:
        self.outFile = outFile
        self.package = packagedData
        self.filePtr = 0
        self.global_token_id = 0


        self.package["variables"]["main_argc"] = ["int", "argc", True, -1]
        self.package["variables"]["main_argv"] = ["int", "argv", True, -1]

        self.compiledC: str = ""

        self.inLogicDecl:bool                = False
        self.logicEndLabel:list[str]         = []

        self.currentFunName:str = None
        self.currentLineNo:int  = 0

    def compile(self) -> None:
        pprint(self.package)