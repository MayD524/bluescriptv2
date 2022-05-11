
from pprint import pprint
import os
import sys

IS_DEBUG = True
os_name = "posix" if IS_DEBUG else os.name

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

JMP_MODES = {
    14 : "jle",
    15 : "jge",
    16 : "jg",
    17 : "jl",
    18 : "je",
    19 : "jne"
}

## this is a good order for linux
REGISTERS = [
    "rax",
    "rdi",
    "rsi",
    "rdx",
    "rbx",
    "rcx",
    "r8",
    "r9",
    "r10",
    "r11",
    "r12",
    "r13",
    "r14",
    "r15"
]

class compiler:
    def __init__(self, packagedData:dict[str, dict], outFile:str="test.asm") -> None:
        self.outFile = outFile
        self.package = packagedData
        self.filePtr = 0
        self.global_token_id = 0
        
        self.package["variables"]["main_argc"] = ["int", "argc", True, -1]
        self.package["variables"]["main_argv"] = ["int", "argv", True, -1]

        self.compiledASM:dict[str,list[str]] = {
            ".text":   [],  ## code
            ".rodata": [],  ## read-only data
            ".bss":    [
                ";--- for printing numbers ---\ndigitSpace resb 100\ndigitSpacePos resb 8\nmain_argc resw 4\nmain_argv resw 10\n"],  ## uninitialized data
            ".data":   [
            ]
        }
        
        ## for logic control (so we can do our checks)
        self.inLogicDecl:bool                = False
        self.logicEndLabel:list[str]         = []

        ## switch name : [cases]
        self.switchCaseStack:dict[str,list[str]] = {}
        
        self.currentFunName:str = None
        self.currentLineNo:int  = 0
        
        self.totalMemory = 0
    
    def tokenToType(self, token:str) -> str:
        assert token in TOKEN_TYPES, f"{self.currentFunName}:{self.currentLineNo} >> {token} is not a valid token"
        match token:
            case "BS_STRING_TOKEN_AHOY":
                return "str"
            case "BS_VARIABLE_TOKEN":
                return "int"
            case "BS_INT_TOKEN":
                return "int"
            case _:
                assert False, f"{self.currentFunName}:{self.currentLineNo} >> {token} is not a valid token"
    
    def isAlloced(self, name:str) -> bool:
        if "." in name:
            ## TODO: Don't blindly assume
            return True ## we assume it's a struct
        for bss in self.compiledASM[".bss"]:
            if any(name == x for x in bss.split(" ")):
                return True
        for data in self.compiledASM[".data"]:
            if any(name == x for x in data.split(" ")):
                return True
        return False
    
    def allocSpace(self, name:str, dtype:str, size:int=4) -> None:
        if name in self.package["globals"]: return
        if name in self.package["arrays"]: return
        if self.isAlloced(name): return
        
        if size == 2:
            ## check if length is defined (self.package[ext][name][3])
            if "$" in name:
                ext = self.getExtention(name)
                cpy = self.package[ext][name].copy()
                ## remove name from package
                del self.package[ext][name]
                name, size = name.split("$")
                cpy[2], cpy[3] = True, size
                self.package[ext][name] = cpy
                self.compiledASM[".bss"].append(f"{name} resw {size}")
                return 
        elif size != 2:
            self.compiledASM[".bss"].append(f"{name} resw {size}")
            return
        if dtype == "int" or dtype == "BS_INT_TOKEN" and name not in self.package["arrays"]:
            self.compiledASM[".bss"].append(f"{name} resw 2 ; stores {2*16}-bit int")
        elif dtype == "short":
            self.compiledASM[".bss"].append(f"{name} resw 1 ; stores {1*16}-bit int")
        elif dtype == "long":
            self.compiledASM[".bss"].append(f"{name} resw 4 ; stores {4*16}-bit int")
        elif dtype == "str" or dtype == "BS_STRING_TOKEN_AHOY":
            self.compiledASM[".bss"].append(f"{name} resw {size} ; stores char")

    def getVarName(self, cblock:str, varName:str) -> str:
        if varName in self.package["constants"] or varName in self.package["arrays"] or varName in self.package["globals"]:
            ## all are unaffected by local scope
            return varName
        return f"{cblock}_{varName}"
    
    def getOffset(self, varName:str=None, size:str=None, cBlock:str=None) -> int:
        if varName is not None:
            if not '[' in varName and not ']' in varName:
                return -1
            offset = varName.split("[")[1].replace("]", "")
            if offset.isnumeric():
                return int(offset)
            return self.getVarName(cBlock, offset)
        
        assert size is not None, "Size must be not None if varName is None"
        if size.isnumeric():
            return int(size)
        return self.getVarName(cBlock, size)

    def typeOf(self, token:str) -> str:
        ext = self.getExtention(token)
        if ext != False:
            if isinstance(self.package[ext][token], str):
                self.package[ext][token] = [self.package[ext][token], "unknown" if self.package[ext][token] == "str" else "0"]
            tpy = self.package[ext][token][0]
            if tpy in ["float", "ptr", "int"]:
                return "int"
            elif tpy in TOKEN_TYPES:
                return self.tokenToType(tpy)
            return tpy
        elif token.isnumeric() or (token[0] == "-" and token[1:].isnumeric()):
            return "int"
        elif "." in token and token.replace(".", "").isnumeric():
            return "float"
        else:
            return "str"
        
    def getVarValue(self, varName:str) -> str:
        if varName in self.package["variables"]:
            return self.package["variables"][varName][1]
        elif varName in self.package["constants"]:
            return self.package["constants"][varName][1]
        else:
            raise Exception(f"variable {varName} not found")
    
    def getExtention(self, name:str) -> str|bool:
        """
            returns parent group which contains the name
            else returns False
        """
        if name in self.package["constants"]:
            return "constants"
        elif name in self.package["variables"]:
            return "variables"
        elif name in self.package["globals"]:
            return "globals"
        elif name in self.package["arrays"]:
            return "arrays"
        else:
            return False
    
    def isVariable(self, name:str) -> bool:
        if name.isnumeric(): return False
        ext = self.getExtention(name)
        if ext in ["variables", "constants", "globals", "arrays"]:
            return True
        return False
    
    def strExists(self, data:str) -> str|None:
        for ext in self.compiledASM[".data"]:
            if data in ext:
                return ext.split(":",1)[0]

        return None

    def allocStr(self, value:str, useName:str=None) -> str:
        """
            value (str) : the value of the string

            ret   (str) : the string id
        """
        if ( name := self.strExists(value)) is not None:
            return name
            
        if useName and self.strExists(useName) is not None:
            return useName
        elif useName is None and self.strExists(f"bs_str{self.global_token_id}") is not None:
            self.global_token_id += 1
        bs_str = f"bs_str{self.global_token_id}: db " if useName is None else f"{useName}: db "
        
        endStr = ""
        skip = False
        ## find all escape characters
        for i, char in enumerate(value):
            if skip: skip = False; continue
            
            if char == "\\":
                nxt = value[i+1]
                skip = True
                code = ESCAPE_CHARACTERS[nxt]
                endStr += f",{code}"
                continue
                        
            endStr += "," + str(ord(char))

        if endStr[0] == ',':
            endStr = endStr[1:]
        bs_str += endStr
        
        if f"bs_str{self.global_token_id}" not in self.compiledASM[".data"]:
            self.compiledASM[".data"].append(f"{bs_str}, 0")
        return f"bs_str{self.global_token_id}"

    def checkVariableOperations(self, varName:str, value:str) -> None:
        ext = self.getExtention(varName)
        
        if not ext:
            raise Exception(f"{self.currentFunName}:{self.currentLineNo+1} variable {varName} not found")
        elif ext == "constants":
            raise Exception(f"{self.currentFunName}:{self.currentLineNo+1} variable {varName} is constant")
        elif self.typeOf(varName) != "int":
            raise Exception(f"{self.currentFunName}:{self.currentLineNo+1} variable {varName} is not an integer, but a {self.typeOf(varName)}")
        elif self.typeOf(value) != "int":
            raise Exception(f"{self.currentFunName}:{self.currentLineNo+1} variable '{value}' is not an integer, but a {self.typeOf(value)}")
    
    def compile_blockLine(self, name:str, line:list[str], lineNo:int=0) -> bool:
        expectedIndent = len(self.logicEndLabel) - 1 if len(self.logicEndLabel) > 0 else 0
        
        ## check if the line is just the number '13'
        check = set(line)
        if check == {13}:
            return False
        
        if line[expectedIndent] != 13 and self.inLogicDecl:
            ## self.compiledASM[".text"].append(f"{self.logicEndLabel[-1]}:\n")
            ## check if any are 13
            if any(x == 13 for x in line[:expectedIndent]):
                cnt = line[:expectedIndent].count(13)
                for i in range(cnt):
                    ## add the label 
                    self.compiledASM[".text"].append(f"{self.logicEndLabel[-1]}:\n")
                    self.logicEndLabel.pop()
            else:
                for end in self.logicEndLabel:
                    self.compiledASM[".text"].append(f"{end}:\n")
                self.logicEndLabel.clear()
                
            self.inLogicDecl = False if len(self.logicEndLabel) == 0 else True
        if line[expectedIndent] == 13:
            line = line[expectedIndent:]
        hasReturned     = False
        needReturnValue = False ## for declaring variables that require a return value
        returnVarName   = ""
        token_no        = 0
        while token_no < len(line):
            token = line[token_no]
            
            if token == "BS_STRING_TOKEN_AHOY":
                self.allocStr(line[token_no+1])

            elif token == "BS_VARIABLE_TOKEN":
                varName = line[token_no+1]
                
                ext = self.getExtention(varName if '[' not in varName else varName.split("[")[0])
                if not ext: raise Exception(f"variable {varName} not found")
                if len(line) > token_no+2:
                    assert len(line) != token_no+3, f"line {name}:{lineNo} has no value for variable {varName}, {line}"
                    incToken = 3
                    mode     = line[token_no+2]
                    dType    = line[token_no+3]
                    if dType == "BS_FUNCTION_TOKEN":
                        ## call a function and store the result in a variable
                        needReturnValue = True
                        returnVarName   = varName
                        if line[token_no+4] in self.package["blocks"]:
                            self.package[ext][varName] = [self.package["blocks"][line[token_no + 4]]["retType"], "funcReturn"]
                        else:
                            self.package[ext][varName] = ["int", "funcReturn"]
                        if len(self.package[ext][varName]) <= 2 or not self.package[ext][varName][2]:
                            self.allocSpace(varName, self.package[ext][varName][0])
                        token_no +=1 
                        continue
                    value = "NULL"
                    if len(line) > token_no+4:
                        value    = line[token_no + 4]
                        incToken = 4
                    
                    if mode == 12: ## assign
                        
                        size = -1
                        atIndex = False
                        if '[' in varName and ']' in varName :
                            varName, size = varName.split("[")
                            vardatacopy = self.package[ext][varName]
                            ## delete the variable
                            del self.package[ext][varName]
                            size = size.replace(']', '')
                            if not self.isVariable(f"{name}_{size}"):
                                assert size.isnumeric(), "size is not a number"
                                size = int(size)
                            self.package[ext][varName] = vardatacopy
                            self.package[ext][varName][0] = dType
                        
                        elif "@" in varName:
                            varName, size = varName.split("@")
                            atIndex = True
                            vardatacopy = self.package[ext][varName]
                            del self.package[ext][varName]
                            self.package[ext][varName] = vardatacopy
                            self.package[ext][varName][0] = dType
                            
                        if dType == "BS_STRUCT_TOKEN":
                            assert value in self.package["structs"], f"{name}:{lineNo} struct {value} not found"
                            dt = self.package["structs"][value]
                            
                            self.compiledASM[".bss"].append(f"{varName}:")
                            structSize = 0
                            for x in dt:
                                x = x.strip()
                                subType, subName = x.split(" ",1)
                                if " " in subName:
                                    subName, size = subName.split(" ",1)
                                else:
                                    size = 4 if subType == "int" else 32
                                structSize += int(size)
                                self.compiledASM[".bss"].append(f".{subName} resw {size}")
                                self.package["variables"][f"{varName}.{subName}"] = [subType, "unknown"]
                            self.compiledASM[".rodata"].append(f"{varName}.len dq {structSize}")
                            self.package["variables"][f"{varName}.len"] = ["int", f"{structSize}"]
                            
                        elif dType != "BS_STRING_TOKEN_AHOY":
                            vsize = -1 if '[' not in value and ']' not in value else int(value.split('[')[1].replace(']',''))
                            if vsize != -1:
                                value = value.split('[')[0].replace(']','')
                                dType = self.typeOf(value)
                            self.package[ext][varName] = [self.typeOf(value), value if ext != "arrays" else self.package[ext][varName][1], False, size] if len(self.package[ext][varName]) == 2 else self.package[ext][varName]
                            if self.isVariable(value) and not "@" in value:
                                value = f"[{value}]" if vsize == -1 else f"[{value}+{vsize}*8]"
                            
                            elif "@" in value and self.isVariable(value.split('@')[0]):
                                value, vsize = value.split('@')
                                value = f"[{value}+{vsize}]"
                            #dType = self.typeOf(value.replace("[", "").replace("]", ""))
                            
                            if not self.package[ext][varName][2]:
                                if size != -1 and not atIndex and ext != "arrays": ## make an array
                                    dt = [x for x in line[token_no+3:] if x not in TOKEN_TYPES]
                                    dt = len(dt) if isinstance(dt, str) or isinstance(dt, list) else dt
                                    
                                    if dt < size:
                                        for _ in range(size - dt):
                                            dt.append(0)
                                    data = ','.join([str(x) for x in dt])
                                    self.compiledASM[".data"].append(f"{varName} dq {data}")
                                elif atIndex:
                                    self.compiledASM['.text'].append(f"mov rax, {value}")
                                    self.compiledASM['.text'].append(f"mov [{varName}+{size}], rax")
                                else:
                                    if vsize != -1:
                                        if '+' in value:
                                            dType = self.typeOf(value if '+' not in value else value.split('+')[0].replace("[", ''))
                                        else:
                                            dType = self.typeOf(value.replace("[", '').replace("]", ''))
                                        tmpName = varName if "$" not in varName else varName.split("$")[0]
                                        self.compiledASM[".text"].append(f"mov rax, {value}\nmov [{tmpName}], rax")
                                    else:
                                        tmpName = varName if "$" not in varName else varName.split("$")[0]
                                        self.compiledASM[".text"].append(f"mov rax, {value}")
                                        self.compiledASM[".text"].append(f'mov [{tmpName}], rax')
                                    
                                    if len(self.package[ext][varName]) < 2 or not self.package[ext][varName][2]:
                                        self.allocSpace(varName, dType)
                                        if "$" in varName:
                                            varName, size = varName.split("$")
                                    self.package[ext][varName][0] = dType
                                    self.package[ext][varName][2] = True
                                    self.package[ext][varName][1] = value if ext != "arrays" else self.package[ext][varName][1]
                                    self.package[ext][varName][3] = size
                                    token_no += incToken
                                    continue
                            
                            else:
                                if size != -1:
                                    if f"{name}_{size}" in self.package["variables"]:
                                        size = f"{name}_{size}"
                                    varName = f"{varName}+{size}*8" if not atIndex else f"{varName}+{size}"
                                self.compiledASM[".text"].append(f"mov rax, {value}")
                                self.compiledASM[".text"].append(f'mov [{varName}], rax')
                                token_no += 1
                                continue
                            if size == -1:
                                self.compiledASM[".text"].append(f"push rax\nmov rax, {value}\nmov [{varName}], rax\npop rax")
                            self.package[ext][varName][2] = True ## the variable has been declared
                            self.package[ext][varName][3] = size
                            self.package[ext][varName][0] = dType#'int' if dType == "BS_INT_TOKEN" else "str"
                        else:
                            self.package[ext][varName] = ["str", value, False, len(value)]
                            if not self.package[ext][varName][2]:
                                if size == -1 and not self.package[ext][varName][2]:
                                    self.allocSpace(varName, "str", len(value) + 1)
                                else:
                                    data = ','.join([str(i) for i in range(size)])
                                    self.compiledASM[".data"].append(f"{varName} dq {data}")
                                    self.package[ext][varName][3] = size
                            strName = self.allocStr(value)
                            self.compiledASM[".text"].append(f"push rax\nlea rax, [{strName}]; get ptr to str\nmov [{varName}], rax\npop rax")
                            self.package[ext][varName][2] = True if len(self.package[ext][varName]) != 3 else self.package[ext][varName] ## the variable has been declared
                            self.package[ext][varName][1] = value if ext != "arrays" else self.package[ext][varName][1]
                            self.package[ext][varName][3] = size
                        token_no += incToken
                        continue ## skip the rest of the code
                    
                    match mode: ## for math
                        case 10: ## add
                            voffset = self.getOffset(varName)
                            if voffset != -1:
                                varName = varName.split('[')[0]

                            if isinstance(voffset, str):
                                self.compiledASM[".text"].append(f"mov rcx, [{voffset}]")
                                voffset = "rcx"
                            self.checkVariableOperations(varName, value)

                            ## we can add to a variable
                            self.compiledASM['.text'].append(f"mov rax, [{varName}]" if voffset == -1 else f"mov rax, [{varName} + {voffset}*8]")
                            value = value if not self.isVariable(value) else f"[{value}]"
                            varName = f"[{varName}]" if voffset == -1 else f"[{varName} + {voffset}*8]"
                            self.compiledASM[".text"].append(f"add rax, {value}\nmov {varName}, rax")
                        
                        case 8: ## mul
                            voffset = self.getOffset(varName)
                            if voffset != -1:
                                varName = varName.split('[')[0]

                            if isinstance(voffset, str):
                                self.compiledASM[".text"].append(f"mov rcx, [{voffset}]")
                                voffset = "rcx"

                            self.checkVariableOperations(varName, value)

                            ## we can add to a variable
                            self.compiledASM['.text'].append(f"mov rax, [{varName}]" if voffset == -1 else f"mov rax, [{varName} + {voffset}*8]")
                            value = value if not self.isVariable(value) else f"[{value}]"
                            varName = f"[{varName}]" if voffset == -1 else f"[{varName} + {voffset}*8]"
                            self.compiledASM[".text"].append(f"mov rbx, {value}\nmul rbx\n")
                            self.compiledASM[".text"].append(f"mov {varName}, rax")
                    
                        case 11: ## div
                            voffset = self.getOffset(varName)
                            if voffset != -1:
                                varName = varName.split('[')[0]

                            if isinstance(voffset, str):
                                self.compiledASM[".text"].append(f"mov r10, [{voffset}]")
                                voffset = "r10"
                            self.checkVariableOperations(varName, value)
                            
                            ## we can add to a variable
                            self.compiledASM['.text'].append(f"mov rax, [{varName}]" if voffset == -1 else f"mov rax, [{varName} + {voffset}*8]")
                            value = value if not self.isVariable(value) else f"[{value}]"
                            varName = f"[{varName}]" if voffset == -1 else f"[{varName} + {voffset}*8]"
                            self.compiledASM[".text"].append(f"mov rdx, 0\nmov rax, {varName}\nmov rcx, {value}\ndiv rcx\nmov {varName}, rax")
                        
                        case 9: ## sub
                            voffset = self.getOffset(varName)
                            if voffset != -1:
                                varName = varName.split('[')[0]
                            
                            if isinstance(voffset, str):
                                self.compiledASM[".text"].append(f"mov rcx, [{voffset}]")
                                voffset = "rcx"
                            
                            self.checkVariableOperations(varName, value)
                            
                            ## we can add to a variable
                            self.compiledASM['.text'].append(f"mov rax, [{varName}]" if voffset == -1 else f"mov rax, [{varName} + {voffset}*8]")
                            value = value if not self.isVariable(value) else f"[{value}]"
                            varName = f"[{varName}]" if voffset == -1 else f"[{varName} + {voffset}*8]"
                            self.compiledASM[".text"].append(f"mov rax, {varName}\nmov rbx, {value}\nsub rax, rbx\nmov {varName}, rax")
                    
                    token_no += incToken
                #    ## .bss gen
                #    self.allocSpace(varName, self.typeOf(varName))
                
            elif token == "BS_FUNCTION_TOKEN":
                nextFun = line[token_no+1]
                loc_args = line[token_no+2:]
                #loc_args = [x for x in loc_args if x not in TOKEN_TYPES]
                loc_argc = len(loc_args)
                if nextFun not in self.package["livingFunctions"]:
                    raise Exception(f"function {nextFun} not found")
                
                if nextFun not in self.package["blocks"]:
                    ## raw call to functions
                    ## move the arguments to the correct registers
                    loc_args = [arg for arg in loc_args if arg not in TOKEN_TYPES]
                    ## because c is stupid and wants to use rdi for the first argument not rax :/ 
                    regIndex = 0 if nextFun not in self.package['externs'] else 1
                    for arg in loc_args:
                        #self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, {arg}")
                        arg = arg if not self.isVariable(arg) else f"[{arg}]"
                        if regIndex == 1 and os_name == "nt":
                            self.compiledASM[".text"].append(f"mov rax, {arg}\n push rax")
                        else:
                            self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, {arg}")
                        regIndex += 1
                    self.compiledASM['.text'].append(f"call {nextFun}")
                    
                    if needReturnValue:
                        self.package[self.getExtention(returnVarName)][returnVarName][0] = self.package["blocks"][name]["retType"]
                        if os_name == "nt" and regIndex == 1:
                            self.compiledASM[".text"].append(f"pop rax")
                        self.compiledASM[".text"].append(f"mov [{returnVarName}], rax")
                        needReturnValue = False
                        returnVarName   = ""
                        
                    break
                
                functionData = self.package["blocks"][nextFun]
                
                if functionData["args"][0] == "void":
                    self.compiledASM[".text"].append(f"call {nextFun} ; {token_no}")
                    if needReturnValue:
                        self.compiledASM[".text"].append(f"mov [{returnVarName}], rax")
                        returnVarName   = ""
                        needReturnValue = False
                    break
                
                if functionData["argc"] != loc_argc // 2:
                    raise Exception(f"{name}:{lineNo} >> function {nextFun} takes {functionData['argc']} arguments, but {loc_argc//2} were given")
                
                ## check if all arguments are of the same type
                regIndex = 0
                arg_ptr = 0
                
                while arg_ptr < loc_argc:
                    argType  = loc_args[arg_ptr]
                    argValue = loc_args[arg_ptr+1]

                    if argValue in TOKEN_TYPES and argType not in TOKEN_TYPES:
                        argValue, argType = argType, argValue
                    
                    funcArgType = functionData["args"][arg_ptr-arg_ptr//2]
                    if "|" in funcArgType:
                        funcArgType = funcArgType.split("|")
                        tOf = self.typeOf(argValue)
                        if tOf in TOKEN_TYPES:
                            tOf = self.tokenToType(tOf)
                        assert tOf in funcArgType, f"{name}:{lineNo} >> argument {arg_ptr//2} of function {nextFun} is of type {' or '.join(funcArgType)}, but {tOf} was given"

                    elif funcArgType not in ["arg", "void"]:
                        if argValue not in self.package["livingFunctions"]:
                            tOf = self.typeOf(argValue)
                            if tOf in TOKEN_TYPES:
                                tOf = self.tokenToType(tOf)
                            if "&" in tOf:
                                tOf = "int"
                            assert tOf in funcArgType, f"{name}:{lineNo} >> argument {arg_ptr//2} of function {nextFun} is of type {funcArgType}, but {tOf} was given"
                            
                    if argType   == "BS_STRING_TOKEN_AHOY":
                        strName = self.allocStr(argValue)
                        self.compiledASM[".text"].append(f"lea {REGISTERS[regIndex]}, [{strName}] ; {token_no}")
                    elif argType == "BS_VARIABLE_TOKEN": 
                        size = -1
                        if '[' in argValue:
                            vname, size = argValue.split('[')
                            size = int(size.replace(']','')) if size.isnumeric() else size
                            if isinstance(size, str):
                                self.compiledASM[".text"].append(f"mov rax, [{vname}]" if functionData['args'][arg_ptr-arg_ptr//2] != "ptr" else f"mov rax, {vname}")
                                size = f"rax"

                            self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex+1]}, [{vname}] ; {token_no}")
                            argValue = f"{REGISTERS[regIndex+1]}+{size}" 
                        
                        self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, [{argValue}] ; {token_no}")
                    elif argType == "BS_INT_TOKEN":
                        self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, {argValue} ; {token_no}")
                    elif argType == "BS_FUNCTION_TOKEN":
                        self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, {argValue} ; {token_no}")
                    arg_ptr  += 2
                    regIndex += 1
                
                self.compiledASM[".text"].append(f"call {nextFun} ; {token_no}")
                
                rType = functionData["retType"]

                if needReturnValue:

                    if "&" in rType and rType in self.package["structs"]:
                        regIndex = 0
                        ## assign the struct values
                        rType = rType.replace("&", "")
                        struct = self.package["structs"][rType]
                        self.compiledASM[".bss"].append(f"{returnVarName}:")
                        ext = self.getExtention(returnVarName)
                        for field in struct["fields"]:
                            for typ, sname in field.split(" ", 2):
                                size = 2
                                if " " in sname:
                                    sname, size = sname.split(" ")
                                    
                                self.compiledASM[".bss"].append(f".{sname} resw {size}")
                                self.compiledASM[".text"].append(f"mov [{returnVarName}.{sname}], {REGISTERS[regIndex]}")
                                self.package[ext][f"{returnVarName}.{sname}"] = [typ, "struct_value", True, size]
                            regIndex += 1
                    self.package[ext][returnVarName][0] = 'int' if rType in self.package["structs"] else rType
                    needReturnValue = False
                    returnVarName   = ""
                break
            
            elif isinstance(token, int):
                match token:
                    case 0: ## if:
                        cmp1 = line[token_no+2]
                        nextArgs = 3
                        funcCalls = 0
                        mode = 0
                        if line[token_no+1] != "BS_FUNCTION_TOKEN":
                            mode = line[token_no+nextArgs]
                        else:
                            ## get the index of the first int type in line
                            for x in range(1, len(line)):
                                if isinstance(line[x], int):
                                    nextArgs = x
                                    mode = line[x]
                                    break
                            funcCalls += 1
                            args = line[3:nextArgs]
                            if args == []:
                                self.compiledASM[".text"].append(f"call {cmp1}")
                            else:
                                regIndex = 0 if cmp1 not in self.package["externs"] else 1
                                for arg in args:
                                    if arg in TOKEN_TYPES:
                                        continue
                                    if self.isVariable(arg):
                                        self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, [{arg}]")
                                    else:
                                        self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, {arg}")
                                    regIndex += 1
                                self.compiledASM[".text"].append(f"call {cmp1}")

                            self.compiledASM[".text"].append("push rax")
                        cmp2 = line[token_no+nextArgs+2]
                        
                        mode += 1 if mode % 2 == 0 else -1
                        
                        assert mode in JMP_MODES, f"{name}:{lineNo} >> invalid jump mode {mode}"
                        mode = JMP_MODES[mode]
                        
                        ## check if cmp1 is a variable or a string
                        if self.isVariable(cmp1):
                            cmp1 = f"[{cmp1}]"
                        elif self.typeOf(cmp1) == "str":
                            strName = self.allocStr(cmp1)
                            cmp1 = f"[{strName}]"
                        elif line[token_no+nextArgs] == "BS_FUNCTION_TOKEN":
                            ## func call
                            ## get the index of the first int type in line
                            for x in range(len(line)):
                                if isinstance(line[x], int):
                                    nextArgs = x
                                    break
                                funcCalls += 1
                                args = line[3:nextArgs]
                                if args == []:
                                    self.compiledASM[".text"].append(f"call {cmp1}")
                                else:
                                    regIndex = 0 if cmp1 not in self.package["externs"] else 1
                                    for arg in args:
                                        if arg in TOKEN_TYPES:
                                            continue
                                        if self.isVariable(arg):
                                            self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, [{arg}]")
                                        else:
                                            self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, {arg}")
                                        regIndex += 1
                                    self.compiledASM[".text"].append(f"call {cmp1}")
                                self.compiledASM[".text"].append("push rax")
                            
                        if self.isVariable(cmp2):
                            cmp2 = f"[{cmp2}]"
                            
                        elif self.typeOf(cmp2) == "str":
                            strName = self.allocStr(cmp2)
                            cmp2 = f"[{strName}]"

                        elif line[token_no+nextArgs+1] == "BS_FUNCTION_TOKEN":
                            ## func call
                            for x in range(len(line)):
                                if isinstance(line[x], int):
                                    nextArgs = x
                                    break
                                funcCalls += 2
                                args = line[token_no+4:len(line)]
                                if args == []:
                                    self.compiledASM[".text"].append(f"call {cmp2}")
                                else:
                                    regIndex = 0 if cmp2 not in self.package["externs"] else 1
                                    for arg in args:
                                        if arg in TOKEN_TYPES:
                                            continue
                                        if self.isVariable(arg):
                                            self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, [{arg}]")
                                        else:
                                            self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, {arg}")
                                        regIndex += 1
                                    self.compiledASM[".text"].append(f"call {cmp2}")
                                cmp2 = 'rax'
                        
                        self.logicEndLabel.append(f".bs_logic_end{self.global_token_id}")
                        self.inLogicDecl   = True
                        ## move cmp1 to rax and cmp2 to rdx
                        if funcCalls == 0:
                            self.compiledASM[".text"].append(f"mov rax, {cmp1}\nmov rdx, {cmp2}")
                        elif funcCalls == 1:
                            self.compiledASM[".text"].append(f"pop rax\nmov rdx, {cmp2}")
                        elif funcCalls % 2:
                            self.compiledASM[".text"].append(f"mov rdx, {cmp2}\nmov rax, {cmp1}")
                        elif funcCalls == 3:
                            self.compiledASM[".text"].append(f"mov rdx, {cmp2}\npop rax")
                        self.compiledASM[".text"].append(f"cmp rax, rdx\n{mode} {self.logicEndLabel[-1]}")
                        
                        return
                    
                    case 27: ## goto
                        gotoPoint = line[token_no+1]
                        if gotoPoint in TOKEN_TYPES:
                            gotoPoint = f"[{line[token_no+2].replace('&', '')}]"
                        elif gotoPoint.isalpha() or "bsDo_" in gotoPoint:
                            gotoPoint = f".{name}_{gotoPoint}"
                        self.compiledASM[".text"].append(f"jmp {gotoPoint}")
                    case 28: ## label
                        self.compiledASM[".text"].append(f".{line[token_no+2]}:")
                    
                    case 25: ## asm
                        ## allow for loading assembly code before runtime
                        if (token_no+2 > len(line)):
                            raise Exception(f"asm must have a value")
                        if not self.isVariable(line[token_no+2]):
                            asm = line[token_no+2].replace("\n", "")
                            self.compiledASM[".text"].append(asm)
                        else:
                            asm = "[{}]".format(line[token_no+2])
                            self.compiledASM[".text"][-1] += f"{asm}"

                    case 7: ## return/exit
                        ## check the return type
                        if (retType := self.package["blocks"][name]["retType"]) == "void":
                            ## no return value just exit the function
                            self.compiledASM[".text"].append("ret")
                            token_no += 1
                            continue
                        
                        if token_no + 1 > len(line):
                            raise Exception(f"return must have a value")
                        retValue = line[token_no+2]
                        #if (retType == "int" and not retValue.isnumeric()) and (retType != self.typeOf(retValue)):
                        #    raise Exception(f"The block {name} does not return {retType} but {self.typeOf(retValue)}.")
                        
                        #if name == "main":
                        #    self.compiledASM[".text"].append(f"mov rax, {retValue}\nret")
                        #else:
                        ext = self.getExtention(retValue)
                        if retValue not in self.package["constants"] or retValue not in self.package[ext]:
                            self.compiledASM[".text"].append(f"mov rax, {retValue if not self.isVariable(retValue) else f'[{retValue}]'} ; return value in rax")
                        else:
                            retValue = f"\"{retValue}\""
                            if "\\n" in retValue:
                                retValue.replace("\\n")
                                retvalue += ", 10"
                            self.compiledASM[".rodata"].append(f"bs_str{self.global_token_id} dd {retValue}, 0")
                            
                        #self.compiledASM[".text"].append(f"mov rax, {retValue} ; return value in rax")
                        self.compiledASM[".text"].append("ret")
                        token_no += 1
                        hasReturned = True
                    
                    case 29: ## switch
                        raise Exception(f"switch is not implemented yet")

                    case 30: ## case
                        raise Exception(f"case is not implemented yet")

                    case 31: ## syscall
                        args = [x for x in line[token_no+1:] if x not in TOKEN_TYPES]
                        assert len(args) != 0, f"{name}:{lineNo} >> syscall has no arguments"
                        assert len(args) < 9, f"{name}:{lineNo} >> syscall has too many arguments"

                        for i in range(len(args)):
                            if self.isVariable(args[i]):
                                args[i] = f"[{args[i]}]"
                            elif self.typeOf(args[i]) == "str":
                                strName = self.allocStr(args[i])
                                args[i] = f"[{strName}]"
                            self.compiledASM[".text"].append(f"mov {REGISTERS[i]}, {args[i]}")
                        self.compiledASM[".text"].append(f"syscall\npush rax")
                    
                    case 32: ## pop
                        if len(line) >= token_no + 2:
                            varname = line[token_no+2]
                            assert self.isVariable(varname), f"{name}:{lineNo} >> {varname} is not a variable"
                            self.compiledASM[".text"].append(f"pop rax")
                            self.compiledASM[".text"].append(f"mov [{varname}], rax")
                            self.allocSpace(varname, "int")
                            
                        else:
                            self.compiledASM[".text"].append("pop rax")

                    case 33: ## push
                        data = line[token_no+2]
                        if self.isVariable(data):
                            data = f"[{data}]"
                        self.compiledASM[".text"].append(f"mov rax, {data}")
                        self.compiledASM[".text"].append(f"push rax")

                    case _:
                        pass
                        #raise Exception(f"unrecognized token: {token}")
            
            token_no += 1
            self.global_token_id += 1
        self.compiledASM[".text"].append("")
        return hasReturned

    def compileBlock(self) -> None:
        for block in self.package["blocks"]:
            self.currentFunName = block
            hasReturned = False
            requireReturn = False if self.package["blocks"][block]["retType"] == "void" else True
            
            self.compiledASM[".text"].append(f"{block}:")
            if block == "main" and self.package["blocks"][block]["retType"] != "int":
                raise Exception("main function must return int")

            if block == "main" and os_name != 'nt':
                self.compiledASM[".text"].append(f"mov [main_argc], rdi\nmov [main_argv], rsi\n")

            elif self.package["blocks"][block]["args"][0] != "void":
                assert len(self.package["blocks"][block]["tokens"]) > 0, f"{block} has no tokens, this is most likely because you forgot to add an 'end' to the block."
                args = self.package["blocks"][block]["tokens"][0]
                args = [arg for arg in args if arg != "BS_VARIABLE_TOKEN"]
                ## remove BS_VARIABLE_TOKEN from args
                if len(args) > self.package["blocks"][block]["argc"]:
                    raise Exception(f"too many arguments for {block}")
                elif len(args) < self.package["blocks"][block]["argc"]:
                    raise Exception(f"not enough arguments for {block}")
                regIndex = 0
                for i in range(len(args)):
                    arg = args[i]
                    dtype = self.package["blocks"][block]["args"][i]

                    if '[' in arg and ']' in arg:
                        arg, size = arg.split("[")
                        size = size.replace("]", "")
                        if size.isnumeric():
                            data = ','.join([i for i in range(int(size))])
                            self.compiledASM[".data"].append(f"{arg} dw {data}")
                        else:
                            raise Exception(f"size of '{size}' is not a number")
                    else:
                        ## this allocates parameters for the function
                        typ = dtype.split("|")[0] if "|" in dtype else dtype
                        self.allocSpace(arg, typ)
                    self.package["variables"][arg] = [dtype, "function_argument"]
                    ## TODO: rework this (so we don't have string issues)
                    self.compiledASM[".text"].append(f"mov [{arg}], {REGISTERS[regIndex]}")
                    regIndex += 1
                self.package["blocks"][block]["tokens"].pop(0)
                
            for line_no, line in enumerate(self.package["blocks"][block]["tokens"]):
                self.currentLineNo = line_no
                if not hasReturned:
                    hasReturned = self.compile_blockLine(block, line, line_no)
                    continue
                self.compile_blockLine(block, line)
                
            if self.inLogicDecl:
                for decl in self.logicEndLabel:
                    self.compiledASM[".text"].append(f"{decl}:")
                self.logicEndLabel = []
                self.inLogicDecl = False
            
            if requireReturn and not hasReturned and block != "main":
                raise Exception(f"{block} must return a value")
            
            elif block == "main":
                self.compiledASM[".text"].append("mov rax, 0\n ret")
            
            elif not requireReturn and not hasReturned:
                self.compiledASM[".text"].append("ret")
    
    def compileArray(self) -> None:
        for array in self.package["arrays"]:
            data = ','.join(['0' for _ in range(int(self.package["arrays"][array][1]))])
            self.compiledASM[".data"].append(f"{array} dq {data}")
            
    def compileGlobals(self) -> None:
        for global_ in self.package["globals"]:
            dtype, value = self.package["globals"][global_][0], self.package["globals"][global_][1]
            if dtype == 'str':
                self.allocStr(self.pacakge["globals"][global_][1], global_)
                continue
            self.compiledASM[".data"].append(f"{global_} dq {value}")
            
    def compileConstants(self) -> None:
        for constant in self.package["constants"]:
            self.package['constants'][constant][1] = self.package['constants'][constant][1] if not self.isVariable(self.package['constants'][constant][1]) else f"[{self.package['constants'][constant][1]}]"
            ## check if there is a newline in the string
            if "\"" in self.package['constants'][constant][1]:
                val = self.package['constants'][constant][1]
                str = self.allocStr(val)
                self.compiledASM[".rodata"].append(f"{constant} db {str}")
            else:
                self.compiledASM[".rodata"].append(f"{constant} dq {self.package['constants'][constant][1]}")

    def removeFromSection(self, name:str, section:str) -> None:
        if not any(name in alloc for alloc in self.compiledASM[section]): return

        ## get index of name in .bss
        index = [i for i, alloc in enumerate(self.compiledASM[section]) if name in alloc]
        assert len(index) != 0, f"{name} is not in {section}"
        self.compiledASM[section].pop(index[0])
    
    def varIsUsed(self, varName:str) -> bool:
        for line in self.compiledASM[".text"]:
            if varName in line:
                return True
        return False
    
    def removeUnusedVariables(self) -> str:
        
        varLookups = ["constants", "globals", "arrays", "variables"]
        sections   = [".rodata"  , ".bss"   , ".data" , ".bss"]
        preserve   = ["main_argc", "main_argv", "digitSpace", "digitSpacePos"]
        for varLookup in varLookups:
            for section in sections:
                for var in self.package[varLookup]:
                    if var in preserve: continue
                    if not self.varIsUsed(var):
                        self.removeFromSection(var, section)
            
    def compile(self) -> str:
        
        if DEBUG: pprint(self.package["livingFunctions"])
        print("\n\n ---- Compiling... ----")
        self.compileBlock()
        self.compileConstants()
        self.compileArray()
        self.compileGlobals()

        if DEBUG:
            print("\n\n----- Variables -----")
            pprint(self.package["variables"])
            for var in self.package["variables"]:
                if var not in self.compiledASM['.bss']:
                    self.allocSpace(var, self.package["variables"][var][0])
        print("\n\n------ Compiled ASM ------")
        
        ## now to join the sections
        includes = '\n'.join([f'%include "{f}"' for f in self.package["includedFiles"] if f.endswith(".asm") or f.endswith('.s')])
        externs = '\n'.join([f'extern {f}' for f in self.package["externs"]])
        compiled = f"global _start ; the start we expect\n{includes}\n{externs}\n"
        self.removeUnusedVariables()
        self.compiledASM[".text"].insert(0, "_start: call main\n mov rax, 60\n xor rdi, rdi\n syscall")
        for section in self.compiledASM:
            if self.compiledASM[section] != []:
                compiled += f"\nsection {section}\n"
                compiled += "\n".join(self.compiledASM[section])
                compiled += "\n"
        
        tmp = compiled
        tmp = tmp.split("\n")
        index = 0
        while index < len(tmp):
            if ";" in tmp[index] and "--comment" not in sys.argv:
                tmp[index] = tmp[index].split(";", 1)[0]
            if tmp[index].strip() == "":
                tmp.pop(index)
            else:
                tmp[index] = tmp[index].strip()
                index += 1
        compiled = "\n".join(tmp)
        
        with open(self.outFile, "w+") as writer:
            writer.write(compiled)
        
        print("\n\n------ Compiled Assembly ------")
        print(f"compiled to: {self.outFile}")
        if os_name == "nt":
            print(f"nasm -fwin64 {self.outFile} && gcc {self.outFile.replace('.asm', '.obj')} -o {self.outFile.replace('.asm', '.exe')} && ./{self.outFile.replace('.asm', '.exe')}")
            return compiled
        print(f"nasm -felf64 {self.outFile} && ld {self.outFile.replace('.asm', '.o')} -o {self.outFile.replace('.asm', '.out')} && ./{self.outFile.replace('.asm', '.out')}")
        return compiled
