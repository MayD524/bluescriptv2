
from pprint import pprint
import os
import sys
from urllib.request import HTTPPasswordMgrWithDefaultRealm

TOKEN_TYPES = [
    "BS_STRING_TOKEN_AHOY", 
    "BS_VARIABLE_TOKEN", 
    "BS_INT_TOKEN", 
    "BS_FLOAT_TOKEN", 
    "BS_FUNCTION_TOKEN",
    "BS_STRUCT_TOKEN",
]


class llvm_compiler:
    def __init__(self, package, output):
        self.package = package
        self.output = output
        self.filePtr = 0
        self.global_token_id = 0
        
        self.package["variables"]["main_argc"] = ["int", "argc", True, -1]
        self.package["variables"]["main_argv"] = ["int", "argv", True, -1]
        
        self.compiled_code:str = ""
        
        
        self.inLogic = False
        self.logicEndLabel = []
        
        self.currentFunction = ""
        self.currentLineNo = 0
        
        self.totalMemory = 0
        
    def bsTypeToLLVM(self, bsType):
        if bsType == "int":
            return "i32"
        elif bsType == "float":
            return "double"
        elif bsType == "string":
            return "i8*"
        elif bsType == "void":
            return "void"
        elif bsType == "bool":
            return "i1"
        elif bsType == "struct":
            return "i8*"
        else:
            return "i8*"
        
    def getExt(self, varname:str) -> str|bool:
        if varname in self.package["variables"]:
            return "variables"
        elif varname in self.package["constants"]:
            return "constants"
        elif varname in self.package["globals"]:
            return "globals"
        elif varname in self.package["arrays"]:
            return "arrays"
        elif varname in self.package["structs"]:
            return "structs"
        return False
        
    def compileLine(self, block, line):
        expectedIndent = len(self.logicEndLabel) - 1 if len(self.logicEndLabel) > 0 else 0
        
        check = set(line)
        if check == {13}:
            return False
        
        if line[expectedIndent] != 13 and self.inLogic:
            if any(x == 13 for x in line[:expectedIndent]):
                cnt = line[:expectedIndent].count(13)
                for i in range(cnt):
                    self.compiled_code += "br label %" + self.logicEndLabel[-1] + "\n"
                    self.logicEndLabel.pop()
            else:
                for i in range(len(self.logicEndLabel)):
                    self.compiled_code += "br label %" + self.logicEndLabel[-1] + "\n"
                self.logicEndLabel.clear()
                
            self.inLogic = False if len(self.logicEndLabel) == 0 else True
            
        if line[expectedIndent] == 13:
            line = line[expectedIndent:]
            
        hasReturned = False
        needReturnValue = False
        returnVarName = ""
        token_no = 0
        
        while token_no < len(line):
            token = line[token_no]
            
            if token == "BS_STRING_TOKEN_AHOY":
                ## create a string constant
                self.compiled_code += f"%str{self.global_token_id} = private unnamed_addr constant [{len(line[token_no+1])} x i8] c\"{line[token_no+1]}\"\n"
        
            elif token == "BS_VARIABLE_TOKEN":
                varName = line[token_no+1]
                
                ext = self.getExt(varName)
                if not ext: raise Exception(f"Variable {varName} not found")
                
                if len(line) > token_no+2:
                    assert len(line) != token_no+3, f"line {block}:{self.currentLineNo} has no value for variable {varName}, {line}"
                    inc = 3
                    mode = line[token_no+2]
                    dType = line[token_no+3]
                    
                    if dType == "BS_FUNCTION_TOKEN":
                        ## function call
                        needReturnValue = True
                        returnVarName = varName
                        if line[token_no+4] in self.package["blocks"]: ## it's a bs function
                            self.package[ext][varName] = [self.package["blocks"][line[token_no+4]]["retType"], "funcReturn"]
                        else:
                            self.package[ext][varName] = ["int", "funcReturn"]
                        token_no += 1
                        continue
                    
                    value = "NULL"
                    if len(line) > token_no+4:
                        value = line[token_no+4]
                        inc = 4
                        
                    if ext == "constants":
                        raise Exception(f"{block}:{self.currentLineNo} >> Cannot assign to constant {varName}")
                        
                    match mode:
                        case 12: ## assign
                            if ext == "variables" or ext == "globals":
                                self.compiled_code += f"%{varName} = alloca {self.bsTypeToLLVM(self.package[ext][varName][0])}\n"
                                self.compiled_code += f"store {self.bsTypeToLLVM(self.package[ext][varName][0])} {value}, {self.bsTypeToLLVM(self.package[ext][varName][0])} %{varName}\n"
                        case 10: ## add
                            self.compiled_code += f"%{varName} = add {self.bsTypeToLLVM(self.package[ext][varName][0])} {value}, {self.bsTypeToLLVM(self.package[ext][varName][0])} %{varName}\n"
                            
                        case 9: ## sub
                            self.compiled_code += f"%{varName} = sub {self.bsTypeToLLVM(self.package[ext][varName][0])} {value}, {self.bsTypeToLLVM(self.package[ext][varName][0])} %{varName}\n"
                        
                        case 8: ## mul
                            self.compiled_code += f"%{varName} = mul {self.bsTypeToLLVM(self.package[ext][varName][0])} {value}, {self.bsTypeToLLVM(self.package[ext][varName][0])} %{varName}\n"
                        
                        case 11: ## div
                            self.compiled_code += f"%{varName} = sdiv {self.bsTypeToLLVM(self.package[ext][varName][0])} {value}, {self.bsTypeToLLVM(self.package[ext][varName][0])} %{varName}\n"
                        
                token_no += inc
    
            elif token == "BS_FUNCTION_TOKEN":
                nextFun = line[token_no+1]
                loc_args = line[token_no+2:]
                loc_argc = len(loc_args)
                
                assert nextFun in self.package["live_blocks"], f"{block}:{self.currentLineNo} >> Function {nextFun} not found"

                self.compiled_code += f"%{nextFun} = call {self.bsTypeToLLVM(self.package['blocks'][nextFun]['retType'])} @{nextFun}("
                for i in range(loc_argc):
                    self.compiled_code += f"{self.bsTypeToLLVM(self.package['blocks'][nextFun]['args'][i][0])} %{loc_args[i]}"
                    if i != loc_argc-1:
                        self.compiled_code += ", "
                self.compiled_code += ")\n"
                if needReturnValue:
                    self.compiled_code += f"%{returnVarName} = load {self.bsTypeToLLVM(self.package['blocks'][nextFun]['retType'])}, {self.bsTypeToLLVM(self.package['blocks'][nextFun]['retType'])} %{nextFun}\n"
                token_no += 1
                
            elif isinstance(token, int):
                match token:
                    case 0: ## if
                        ## check if the condition is false
                        self.compiled_code += f"%cond{self.cond_id} = icmp eq i32 0, {line[token_no+1]}\n"
            
            token_no += 1
    def compile(self):
        
        for block in self.package["blocks"]:
            self.currentFunction = block
            hasReturned = False
            requireReturn = False if self.package["blocks"][block]["retType"] == "void" else True
        
            self.compiled_code += f"define {self.bsTypeToLLVM(self.package['blocks'][block]['retType'])} @{block}("
            
            if block == "main":
                self.compiled_code += "i32 %argc, i8** %argv"
            
            elif self.package["blocks"][block]["args"][0] != "void":
                args = self.package["blocks"][block]["tokens"][0]
                args = [arg for arg in args if arg != "BS_VARIABLE_TOKEN"]
                
                if len(args) > self.package["blocks"][block]["argc"]:
                    print(f"Error: Too many arguments for function {block}, expected {self.package['blocks'][block]['argc']}")
                    exit(1)
                elif len(args) < self.package["blocks"][block]["argc"]:
                    print(f"Error: Too few arguments for function {block}, expected {self.package['blocks'][block]['argc']}")
                    exit(1)
                    
                for i in range(len(args)):
                    self.compiled_code += f"{self.bsTypeToLLVM(self.package['blocks'][block]['args'][i])} %arg{args[i]}"
                    
            self.compiled_code += ") {\n"
            for line_no, line in enumerate(self.package["blocks"][block]["tokens"]):
                self.currentLineNo = line_no
                if not hasReturned:
                    hasReturned = self.compileLine(block, line)
                    continue
                self.compileLine(block, line)
                
            if self.inLogic:
                for decl in self.logicEndLabel:
                    ## create a label for the end of the logic
                    self.compiled_code += f"br label %{decl}\n"
                    
                self.inLogic = False
                self.logicEndLabel.clear()
                
            if requireReturn and not hasReturned and block != "main":
                print(f"Error: Function {block} does not return a value")
                exit(1)
            
            elif block == "main":
                self.compiled_code += "ret i32 0\n"
                
            elif not requireReturn and not hasReturned:
                self.compiled_code += "ret void\n"
                
            self.compiled_code += "}\n"
        print("-----------------------------------------------------")
        print("----                Done Compiling               ----")
        print("-----------------------------------------------------")
        
        with open(self.output, "w+") as f:
            f.write(self.compiled_code)
            