from pprint import pprint
import os
from sys import argv
IS_DEBUG = True
name = "posix" if IS_DEBUG else os.name

if name == "nt":
    raise NotImplementedError("Windows is not supported")
elif name == "posix":
    ## currently only tested on linux
    sys_exit   = lambda code : f"mov rax, 60\nmov rdi, {code}\nsyscall\n" if code.isnumeric() else f"mov rax, 60\nmov rdi, [{code}]\nsyscall\n"
    
    def input_str() -> str:
        return """
            bluescript2_generic_input:  \n
                ; rsi = buffer          \n
                ; rdx = buffer size     \n
                mov rax, 0              \n
                mov rdi, 0              \n  
                syscall                 \n
                ret                     \n
        """
    
    FUNCTION_MAIN_NAME = "main:"
    
    pass

TOKEN_TYPES = [
    "BS_STRING_TOKEN_AHOY", 
    "BS_VARIABLE_TOKEN", 
    "BS_INT_TOKEN", 
    "BS_FLOAT_TOKEN", 
    "BS_FUNCTION_TOKEN"
]

## TODO: file this!!!
## small issue: only je/jne works correctly :,(
JMP_MODES = {
    14 : "jl",
    15 : "jle",
    16 : "jg",
    17 : "jge",
    18 : "je",
    19 : "jne"
}

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

        self.compiledASM:dict[str,list[str]] = {
            ".text":   [],  ## code
            ".rodata": [],  ## read-only data
            ".bss":    [
                ";--- for printing numbers ---\ndigitSpace resb 100\ndigitSpacePos resb 8\n;--- recursion ---\nrecursiveStack resw 100\n;--- args ---\nargc resw 4\nargv resw 10\n;--- other ---\n"],  ## uninitialized data
            ".data":   [
                ";--- for recursion ---\nrecursiveDepth db 0\n;--- other ---\n",
            ]   ## initialized data
        }
        
        ## for logic control (so we can do our checks)
        self.inLogicDecl:bool          = False
        self.logicEndLabel:str|None    = None
        
        self.totalMemory = 0
    
    def isAlloced(self, name:str) -> bool:
        for bss in self.compiledASM[".bss"]:
            if name in bss:
                return True
        return False
    
    def allocSpace(self, name:str, dtype:str, size:int=4) -> None:
        if name in self.package["arrays"]: return
        if self.isAlloced(name): return
        
        if dtype == "int" or dtype == "BS_INT_TOKEN" and name not in self.package["arrays"]:
            self.compiledASM[".bss"].append(f"{name} resw {size} ; stores {size*16}-bit int")
        elif dtype == "ptr":
            self.compiledASM[".bss"].append(f"{name} resb {size} ; stores {size*8}-bit ptr")
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
            return self.package[ext][token][0]
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
        return True if self.getExtention(name) is not False else False
    
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
            
        bs_str = f"bs_str{self.global_token_id}: db " if useName is None else f"{useName}: db "
        if "\\n" in value:
            bs_str += "\"" + value.replace("\\n","") + "\", 0xa"
        else:
            bs_str += "\"" + value + "\""
        

        self.compiledASM[".data"].append(f"{bs_str}, 0")
        return f"bs_str{self.global_token_id}"

    def checkVariableOperations(self, varName:str, value:str) -> None:
        print(f"{varName} = {value}")
        ext = self.getExtention(varName)
        
        if not ext:
            raise Exception(f"variable {varName} not found")
        elif ext == "constants":
            raise Exception(f"variable {varName} is constant")
        elif self.typeOf(varName) != "int":
            
            raise Exception(f"variable {varName} is not an integer, but a {self.typeOf(varName)}")
        elif self.typeOf(value) != "int":
            raise Exception(f"variable '{value}' is not an integer, but a {self.typeOf(value)}")
    
    def compile_blockLine(self, name:str, line:list[str], lineNo:int=0) -> bool:
        if line[0] != 13 and self.inLogicDecl:
            self.inLogicDecl = False
            self.compiledASM[".text"].append(f"{self.logicEndLabel}:\n")
        elif line[0] == 13:
            line = line[1:]
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
                        print(f"assigning {value} to {varName}")
                        size = -1
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
                        if dType != "BS_STRING_TOKEN_AHOY":
                            #pprint(self.package[ext])
                            vsize = -1 if '[' not in value and ']' not in value else int(value.split('[')[1].replace(']',''))
                            if vsize != -1:
                                value = value.split('[')[0].replace(']','')
                                dType = self.typeOf(value)
                            #print(self.package[ext][varName])
                            self.package[ext][varName] = [self.typeOf(value), value if ext != "arrays" else self.package[ext][varName][1], False, size] if len(self.package[ext][varName]) == 2 else self.package[ext][varName]
                            print(self.package[ext][varName])
                            if self.isVariable(value):
                                value = f"[{value}]" if vsize == -1 else f"[{value}+{vsize}*8]"
                            dType = self.typeOf(value.replace("[", "").replace("]", ""))
                            if not self.package[ext][varName][2]:
                                if size != -1 and ext != "arrays": ## make an array
                                    dt = [x for x in line[token_no+3:] if x not in TOKEN_TYPES]
                                    dt = len(dt) if isinstance(dt, str) or isinstance(dt, list) else dt
                                    print(size)
                                    print(line)
                                    
                                    if dt < size:
                                        for _ in range(size - dt):
                                            dt.append(0)
                                    data = ','.join([str(x) for x in dt])
                                    self.compiledASM[".data"].append(f"{varName} dq {data}")
                                else:
                                    if vsize != -1:
                                        if '+' in value:
                                            dType = self.typeOf(value if '+' not in value else value.split('+')[0].replace("[", ''))
                                        else:
                                            dType = self.typeOf(value.replace("[", '').replace("]", ''))
                                        self.compiledASM[".text"].append(f"mov rax, {value}\nmov [{varName}], rax")
                                    else:
                                        self.compiledASM[".text"].append(f"mov rax, {value}")
                                        self.compiledASM[".text"].append(f'mov [{varName}], rax')
                                    
                                    if len(self.package[ext][varName]) < 2 or not self.package[ext][varName][2]:
                                        self.allocSpace(varName, dType)
                                    
                                    self.package[ext][varName][0] = dType
                                    self.package[ext][varName][2] = True
                                    self.package[ext][varName][1] = value if ext != "arrays" else self.package[ext][varName][1]
                                    print(self.package[ext][varName])
                                    self.package[ext][varName][3] = size
                                    token_no += incToken
                                    continue
                            else:
                                if size != -1:
                                    if f"{name}_{size}" in self.package["variables"]:
                                        size = f"{name}_{size}"
                                    varName = f"{varName}+{size}*8"
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
                            self.package[ext][varName] = [self.typeOf(value), value, False, len(value)]
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
                            print(f"add = {varName} {mode} {dType} {value}")
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
                            print(f"mul = {varName} {mode} {dType} {value}")
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
                            print(f"div = {varName} {mode} {dType} {value}")
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
                            print(f"sub = {varName} {mode} {dType} {value}")
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
                        self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, {arg}" if not self.isVariable(arg) else f"mov {REGISTERS[regIndex]}, [{arg}]")
                        regIndex += 1
                    self.compiledASM['.text'].append(f"call {nextFun}")
                    if needReturnValue:
                        self.package[self.getExtention(returnVarName)][returnVarName] = self.package["blocks"][name]["retType"]
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
                    
                    if self.typeOf(argValue) != functionData["args"][arg_ptr-arg_ptr//2] and functionData["args"][arg_ptr-arg_ptr//2] not in ["any", "ptr", "void"] :
                        print(line)
                        raise Exception(f"function {nextFun} takes {functionData['args'][arg_ptr-arg_ptr//2]} as argument {arg_ptr}, but got {self.typeOf(argValue)}. variable: '{argValue}'")
                    
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
                    arg_ptr  += 2
                    regIndex += 1
                self.compiledASM[".text"].append(f"call {nextFun} ; {token_no}")
                
                if needReturnValue:
                    self.compiledASM[".text"].append(f"mov [{returnVarName}], rax")
                    needReturnValue = False
                    returnVarName   = ""
                break
            
            elif isinstance(token, int):
                match token:
                    case 0: ## if:
                        self.logicEndLabel = f".bs_logic_end{self.global_token_id}"
                        cmp1 = line[token_no+2]
                        mode = line[token_no+3]
                        cmp2 = line[token_no+5]
                        
                        mode += 1 if mode % 2 == 0 else -1
                        
                        if mode not in JMP_MODES:
                            raise Exception(f"unknown jump mode '{mode}' (this is a compiler error sorry for lack of detail :/)")
                        mode = JMP_MODES[mode]
                        
                        ## check if cmp1 is a variable or a string
                        if self.isVariable(cmp1):
                            cmp1 = f"[{cmp1}]"
                        elif self.typeOf(cmp1) == "str":
                            strName = self.allocStr(cmp1)
                            cmp1 = f"[{strName}]"

                        if self.isVariable(cmp2):
                            cmp2 = f"[{cmp2}]"
                        elif self.typeOf(cmp2) == "str":
                            strName = self.allocStr(cmp2)
                            cmp2 = f"[{strName}]"
                        
                        
                        ## move cmp1 to rax and cmp2 to rdx
                        self.compiledASM[".text"].append(f"mov rax, {cmp1}\nmov rdx, {cmp2}")
                        self.compiledASM[".text"].append(f"cmp rax, rdx\n{mode} {self.logicEndLabel}")
                        self.inLogicDecl   = True
                        self.logicEndLabel = f".bs_logic_end{self.global_token_id}"
                    ## TODO: else statements (maybe?)
                    #case 1: ## else:
                    #    self.logicEndLabel = f"bs_logic_end{self.global_token_id}"
                    
                    case 27: ## goto
                        self.compiledASM[".text"].append(f"jmp .{line[token_no+2]}")
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
                        #print(f"{name}:{lineNo} >> return type: {line}")
                        retValue = line[token_no+2]
                        #if (retType == "int" and not retValue.isnumeric()) and (retType != self.typeOf(retValue)):
                        #    raise Exception(f"The block {name} does not return {retType} but {self.typeOf(retValue)}.")
                        
                        if name == "main":
                            self.compiledASM[".text"].append(sys_exit(retValue))
                        else:
                            if retValue not in self.package["constants"] or retValue not in self.package[ext]:
                                self.compiledASM[".text"].append(f"mov rax, {retValue if not self.isVariable(retValue) else f'[{retValue}]'} ; return value in rax")
                            else:
                                retValue = f"\"{retValue}\""
                                if "\\n" in retValue:
                                    retValue.replace("\\n")
                                    retvalue += ", 10"
                                self.compiledASM[".rodata"].append(f"bs_str{self.global_token_id}: .ascii {retValue}, 0")
                                
                            #self.compiledASM[".text"].append(f"mov rax, {retValue} ; return value in rax")
                        self.compiledASM[".text"].append("ret")
                        token_no += 1
                        hasReturned = True
                    
                    case _:
                        pass
                        #raise Exception(f"unrecognized token: {token}")
            
            token_no += 1
            self.global_token_id += 1
        self.compiledASM[".text"].append("")
        return hasReturned

    def compileBlock(self) -> None:
        for block in self.package["blocks"]:
            hasReturned = False
            requireReturn = False if self.package["blocks"][block]["retType"] == "void" else True
            
            self.compiledASM[".text"].append(f"{block}:" if block != "main" else FUNCTION_MAIN_NAME)
            if block == "main" and self.package["blocks"][block]["retType"] != "int":
                raise Exception("main function must return int")
            
            if block == "main":
                self.compiledASM[".text"].append(f"pop rax\nmov [argc], rax\npop rax\nmov [argv], rax\n")

            elif self.package["blocks"][block]["args"][0] != "void":
                
                args = self.package["blocks"][block]["tokens"][0]
                args = [arg for arg in args if arg != "BS_VARIABLE_TOKEN"]
                ## remove BS_VARIABLE_TOKEN from args
                #print(f"args: {args} {self.package['blocks'][block]['args']}")
                #print(f"argc: {len(args)} {self.package['blocks'][block]['argc']}")
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
                        self.allocSpace(arg, dtype)
                    self.package["variables"][arg] = [dtype, "function_argument"]
                    ## TODO: rework this (so we don't have string issues)
                    self.compiledASM[".text"].append(f"mov [{arg}], {REGISTERS[regIndex]}")
                    regIndex += 1
                self.package["blocks"][block]["tokens"].pop(0)
                
            for line_no, line in enumerate(self.package["blocks"][block]["tokens"]):
                if not hasReturned:
                    hasReturned = self.compile_blockLine(block, line, line_no)
                    continue
                self.compile_blockLine(block, line)
            if requireReturn and not hasReturned:
                raise Exception(f"{block} must return a value")
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
                self.pacakge["globals"][global_][1] = self.package["globals"][global_][1].replace("\\n", ", 10")
            self.compiledASM[".data"].append(f"{global_} dd {value}")
            
    def compileConstants(self) -> None:
        for constant in self.package["constants"]:
            self.package['constants'][constant][1] = self.package['constants'][constant][1] if not self.isVariable(self.package['constants'][constant][1]) else f"[{self.package['constants'][constant][1]}]"
            ## check if there is a newline in the string
            if "\\n" in self.package['constants'][constant][1]:
                self.package['constants'][constant][1] = self.package['constants'][constant][1].replace("\\n", "")
                self.package['constants'][constant][1] += ", 10" if self.package['constants'][constant][1] != "" else "10"
            
            self.compiledASM[".rodata"].append(f"{constant} dd {self.package['constants'][constant][1]}")
    
    def compile(self) -> None:
        #print("\n\n ---- PACKAGE ----")
        #pprint(self.package)
        print("\n\n ---- Compiling... ----")
        self.compileBlock()
        self.compileConstants()
        self.compileArray()
        self.compileGlobals()

        print("\n\n----- Variables -----")
        pprint(self.package["variables"])
        for var in self.package["variables"]:
            if var not in self.compiledASM['.bss']:
                self.allocSpace(var, self.package["variables"][var][0])
        print("\n\n------ Compiled ASM ------")
        pprint(self.compiledASM)
        
        
        ## now to join the sections
        includes = '\n'.join([f'%include "{f}"' for f in self.package["includedFiles"] if f.endswith(".asm") or f.endswith('.s')])
        externs = '\n'.join([f'extern {f}' for f in self.package["externs"]])
        compiled = f"global {FUNCTION_MAIN_NAME} ; the start we expect\n{includes}\n{externs}\n"
        #self.compiledASM[".data"] = list(set(self.compiledASM[".data"]))
        #self.compiledASM[".bss"] = list(set(self.compiledASM[".bss"]))
        for section in self.compiledASM:
            if self.compiledASM[section] != []:
                compiled += f"\nsection {section}\n"
                compiled += "\n".join(self.compiledASM[section])
                compiled += "\n"
                
        with open(self.outFile, "w+") as writer:
            writer.write(compiled)
        
        print("\n\n------ Compiled Assembly ------")
        print(f"compiled to: {self.outFile}")
        print(f"nasm -felf64 {self.outFile} && gcc -no-pie {self.outFile.replace('.asm', '.o')} -o {self.outFile.replace('.asm', '.out')} && ./{self.outFile.replace('.asm', '.out')}")