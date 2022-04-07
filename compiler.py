from pprint import isrecursive, pprint
import os


IS_DEBUG = True

name = "posix" if IS_DEBUG else os.name

if name == "nt":
    raise NotImplementedError("Windows is not supported")
elif name == "posix":
    ## currently only tested on linux
    sys_exit   = lambda code : f"mov rax, 60\nmov rdi, {code}\nsyscall\n" if code.isnumeric() else f"mov rax, 60\nmov rdi, [{code}]\nsyscall\n"
    
    def print_str() -> str:
        return """
            bluescript2_generic_print:          \n
                ; print string (unsized)\n
                ; rax = string\n
                push rax\n
                mov  rbx, 0\n
                generic_print_loop:\n
                    inc rax\n
                    inc rbx\n
                    mov cl, [rax]\n
                    cmp cl, 0\n
                    jne generic_print_loop\n
                mov rax, 1\n
                mov rid, 1\n
                pop rsi\n
                mov rdx, rbx\n
                syscall\n
                ret\n
        """
    
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
    
    FUNCTION_MAIN_NAME = "_start:"
    
    pass

JMP_MODES = {
    14 : "jl",
    15 : "jg",
    16 : "jge",
    17 : "jle",
    18 : "je",
    19 : "jne"
}

REGISTERS = [
    "rax",
    "rbx",
    "rcx",
    "rdx",
    "rsi",
    "r8",
    "r9",
    "r10",
    "r11",
    "r12",
    "r13",
    "r14",
    "r15"
    "rdi", ## use rdi last as it is used in bluescript2_string_copy
]

class compiler:
    def __init__(self, packagedData:dict[str, dict]) -> None:
        self.package = packagedData
        self.filePtr = 0
        self.global_token_id = 0

        self.compiledASM:dict[str,list[str]] = {
            ".text":   [],  ## code
            ".rodata": [],  ## read-only data
            ".bss":    [
                ";--- for printing numbers ---\ndigitSpace resb 100\ndigitSpacePos resb 8\n;--- recursion ---\nrecursiveStack resw 100\n;--- other ---\n"],  ## uninitialized data
            ".data":   [
                ";--- for recursion ---\nrecursiveDepth db 0\n;--- other ---\n",
            ]   ## initialized data
        }
        
        ## for logic control (so we can do our checks)
        self.inLogicDecl:bool          = False
        self.logicEndLabel:str|None    = None
        
        self.totalMemory = 0
    
    def allocSpace(self, name:str, dtype:str, size:int=4) -> None:
        if dtype == "int":
            self.compiledASM[".bss"].append(f"{name} resw {size} ; stores {size*16}-bit int")
        elif dtype == "str":
            self.compiledASM[".bss"].append(f"{name} resb {size} ; stores char")

    def typeOf(self, token:str) -> str:
        if token in self.package["constants"]:
            return self.package["constants"][token][0]
        elif token in self.package["variables"]:
            return self.package["variables"][token][0]
        elif token.isnumeric():
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
    
    def isVariable(self, name:str) -> bool:
        return name in self.package["variables"] or name in self.package["constants"]

    def allocStr(self, value:str, useName:str=None) -> str:
        """
            value (str) : the value of the string

            ret   (str) : the string id
        """
        bs_str = f"bs_str{self.global_token_id}: db " if useName is None else f"{useName}: db "
        if "\\n" in value:
            bs_str += "\"" + value.replace("\\n","") + "\", 0xa"
        else:
            bs_str += "\"" + value + "\""
        
        self.compiledASM[".data"].append(f"{bs_str}, 0")

    def checkVariableOperations(self, varName:str, value:str) -> None:
        if varName not in self.package["variables"]:
            raise Exception(f"variable {varName} not found")
        elif varName in self.package["constants"]:
            raise Exception(f"variable {varName} is constant")
        elif self.package["variables"][varName][0] != "int":
            raise Exception(f"variable {varName} is not an integer, but a {self.package['variables'][varName][0]}")
        elif self.typeOf(value) != "int":
            raise Exception(f"variable '{value}' is not an integer, but a {self.typeOf(value)}")
    
    def compile_blockLine(self, name:str, line:list[str]) -> bool:
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
                
                if len(line) > token_no+2:
                    incToken = 3
                    mode     = line[token_no+2]
                    dType    = line[token_no+3]
                    print(dType)
                    if dType == "BS_FUNCTION_TOKEN" or dType == "BS_GENERIC_FUNCTION_TOKEN":
                        ## call a function and store the result in a variable
                        needReturnValue = True
                        returnVarName   = varName
                        self.package["variables"][varName] = [self.package["blocks"][line[token_no + 4]]["retType"], "funcReturn"]
                        self.allocSpace(varName, self.package["variables"][varName][0])
                        token_no +=1 
                        continue
                    value = "NULL"
                    if len(line) > token_no+4:
                        value    = line[token_no + 4]
                        incToken = 4
                    token_no += incToken
                    match mode:
                        case 12: ## assign
                            if dType != "BS_STRING_TOKEN_AHOY":
                                size = 4 ## default store a 32bit value 
                                self.package["variables"][varName] = [self.typeOf(value), value, False] if len(self.package["variables"][varName]) != 3 else self.package["variables"][varName]
                                if self.isVariable(value):
                                    value = f"[{value}]"
                                if '[' in varName and ']' in varName:
                                    varName, size = varName.split('[')
                                    size = int(size.replace(']',''))
                                if not self.package["variables"][varName][2]:
                                    self.compiledASM[".bss"].append(f"{varName} resw {size}")
                                self.compiledASM[".text"].append(f"push rax\nmov rax, {value}\nmov [{varName}], rax\npop rax")
                                self.package["variables"][varName][2] = True ## the variable has been declared
                            else:
                                self.package["variables"][varName] = [self.typeOf(value), value, False]
                                self.compiledASM[".text"].append(f"push rax\nmov rax, bs_str{self.global_token_id}\nmov [{varName}], rax\npop rax")
                                if not self.package["variables"][varName][2]:
                                    self.allocSpace(varName, "str", len(value) + 1)
                                self.allocStr(value)
                                self.package["variables"][varName][2] = True if len(self.package["variables"][varName]) != 3 else self.package["variables"][varName] ## the variable has been declared
                                
                        case 10: ## add
                            print(f"add = {varName} {mode} {dType} {value}")
                            self.checkVariableOperations(varName, value)
                            
                            ## we can add to a variable
                            self.compiledASM['.text'].append(f"mov rax, [{varName}]")
                            value = value if not self.isVariable(value) else f"[{value}]"
                            self.compiledASM[".text"].append(f"push rax\nadd rax, {value}\nmov [{varName}], rax\npop rax")
                        
                        case 8: ## mul
                            print(f"mul = {varName} {mode} {dType} {value}")
                            self.checkVariableOperations(varName, value)
                            
                            self.compiledASM[".text"].append("push rax\npush rbx\n")
                            ## we can multiply to a variable
                            self.compiledASM['.text'].append(f"mov rax, [{varName}]\n")
                            value = value if not self.isVariable(value) else f"[{value}]"
                            self.compiledASM[".text"].append(f"mov rbx, {value}\nmul rbx\n")
                            self.compiledASM[".text"].append(f"mov [{varName}], rax\npop rbx\npop rax\n")
                    
                        case 11: ## div
                            print(f"div = {varName} {mode} {dType} {value}")
                            self.compiledASM[".text"].append("push rax\npush rcx\npush rdx\n") ## free the registers we're going to use
                            self.checkVariableOperations(varName, value)
                            
                            value = value if not self.isVariable(value) else f"[{value}]"
                            self.compiledASM[".text"].append(f"mov rdx, 0\nmov rax, [{varName}]\nmov rcx, {value}\ndiv rcx\nmov [{varName}], rax\npop rdx\npop rcx\npop rax")
                        case 9: ## sub
                            print(f"sub = {varName} {mode} {dType} {value}")
                            self.checkVariableOperations(varName, value)
                            self.compiledASM[".text"].append("push rax\npush rbx\n")
                            
                            value = value if not self.isVariable(value) else f"[{value}]"
                            self.compiledASM[".text"].append(f"mov rax, [{varName}]\nmov rbx, {value}\nsub rax, rbx\nmov [{varName}], rax\npop rbx\npop rax")
                            
                #    ## .bss gen
                #    self.allocSpace(varName, self.typeOf(varName))
            elif token == "BS_FUNCTION_TOKEN":
                nextFun = line[token_no+1]
                loc_args = line[token_no+2:]
                #loc_args = [x for x in loc_args if x not in ["BS_STRING_TOKEN_AHOY", "BS_VARIABLE_TOKEN", "BS_INT_TOKEN", "BS_FLOAT_TOKEN", "BS_FUNCTION_TOKEN", "BS_GENERIC_FUNCTION_TOKEN"]]
                loc_argc = len(loc_args)
                if nextFun not in self.package["livingFunctions"]:
                    raise Exception(f"function {nextFun} not found")
                
                functionData = self.package["blocks"][nextFun]
                isrecursive = nextFun == name
                
                if isrecursive:
                    ## move all local variables to the stack
                    for var in functionData["local_variables"]:
                        self.compiledASM[".text"].append(f"mov rax, [{var}]")
                        self.compiledASM[".text"].append(f"push rax")
                
                if functionData["args"][0] == "void":
                    self.compiledASM[".text"].append(f"call {nextFun} ; {token_no}")
                    if isrecursive:
                        self.compiledASM[".text"].append(f"mov rbx, rax")
                        for var in functionData["local_variables"][::-1]:
                            self.compiledASM[".text"].append(f"pop rax")
                            self.compiledASM[".text"].append(f"mov [{var}], rax")
                        self.compiledASM[".text"].append(f"mov rax, rbx")
                    if needReturnValue:
                        self.compiledASM[".text"].append(f"mov [{returnVarName}], rax")
                        returnVarName   = ""
                        needReturnValue = False
                    break
                if functionData["argc"] != loc_argc // 2:
                    raise Exception(f"function {nextFun} takes {functionData['argc']} arguments, but {loc_argc} were given")
                ## check if all arguments are of the same type
                regIndex = 0
                arg_ptr = 0
                while arg_ptr < loc_argc:
                    argType  = loc_args[arg_ptr]
                    argValue = loc_args[arg_ptr+1]
                    if self.typeOf(argValue) != functionData["args"][arg_ptr-arg_ptr//2]:
                        raise Exception(f"function {nextFun} takes {functionData['args'][arg_ptr-arg_ptr//2]} as argument {arg_ptr}, but {self.typeOf(loc_args[arg_ptr])} was given")
                    
                    if argType   == "BS_STRING_TOKEN_AHOY":
                        self.compiledASM[".data"].append(f"bs_str{self.global_token_id}: db \"{argValue}\", 0xa")
                        self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, [bs_str{self.global_token_id}] ; {token_no}")
                    elif argType == "BS_VARIABLE_TOKEN": ## TODO: Check if variable is string or int
                        self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, [{argValue}] ; {token_no}")
                    elif argType == "BS_INT_TOKEN":
                        self.compiledASM[".text"].append(f"mov {REGISTERS[regIndex]}, {argValue} ; {token_no}")
                    arg_ptr  += 2
                    regIndex += 1
                self.compiledASM[".text"].append(f"call {nextFun} ; {token_no}")

                if isrecursive:
                    self.compiledASM[".text"].append(f"mov rbx, rax")
                    for var in functionData["local_variables"][::-1]:
                        self.compiledASM[".text"].append(f"pop rax")
                        self.compiledASM[".text"].append(f"mov [{var}], rax")
                    self.compiledASM[".text"].append(f"mov rax, rbx")
                if needReturnValue:
                    self.compiledASM[".text"].append(f"mov [{returnVarName}], rax")
                    needReturnValue = False
                    returnVarName   = ""
                break
            elif token == "BS_GENERIC_FUNCTION_TOKEN":
                funcName = line[token_no+1]
                if funcName == "print":
                    if len(line) < token_no+4:
                        raise Exception(f"'print' function can only take one argument")
                    if line[token_no+2] =="BS_STRING_TOKEN_AHOY":
                        self.compiledASM[".text"].append(f"mov rax, bs_str{self.global_token_id+2}")
                    elif line[token_no+2] == "BS_INT_TOKEN":
                        self.compiledASM[".text"].append(f"mov rax, {line[token_no+3]}")
                    elif line[token_no+2] == "BS_VARIABLE_TOKEN":
                        if line[token_no+3] in self.package["variables"]:
                            self.compiledASM[".text"].append(f"mov rax, [{line[token_no+3]}]")
                        elif line[token_no+3] in self.package["constants"]:
                            self.compiledASM[".text"].append(f"lea rax, [{line[token_no+3]}]")
                        else:
                            raise Exception("Unknown variable")
                    incBy = 0
                    ## change to variable so we don't have to mess with types later
                    if line[token_no+2] == "BS_VARIABLE_TOKEN":
                        line[token_no+2] = "BS_STRING_TOKEN_AHOY" if self.typeOf(line[token_no+3]) == "str" else "BS_INT_TOKEN"
                        incBy = 3
                    if line[token_no+2] == "BS_STRING_TOKEN_AHOY":
                        self.compiledASM[".text"].append(f"call bluescript2_generic_print")
                    elif line[token_no+2] == "BS_INT_TOKEN":
                        self.compiledASM[".text"].append("call bluescript2_numeric_print")
                    
                    token_no += incBy
                    
            elif isinstance(token, int):
                match token:
                    case 0: ## if:
                        self.logicEndLabel = f"bs_logic_end{self.global_token_id}"
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
                            self.allocStr(cmp1)
                            cmp1 = f"[bs_str{self.global_token_id}]"

                        if self.isVariable(cmp2):
                            cmp2 = f"[{cmp2}]"
                        elif self.typeOf(cmp2) == "str":
                            self.allocStr(cmp2)
                            cmp2 = f"[bs_str{self.global_token_id}]"
                        
                        
                        ## move cmp1 to rax and cmp2 to rdx
                        self.compiledASM[".text"].append(f"mov rax, {cmp1}\nmov rdx, {cmp2}")
                        self.compiledASM[".text"].append(f"cmp rax, rdx\n{mode} {self.logicEndLabel}")
                        self.inLogicDecl   = True
                        self.logicEndLabel = f"bs_logic_end{self.global_token_id}"
                    ## TODO: else statements (maybe?)
                    #case 1: ## else:
                    #    self.logicEndLabel = f"bs_logic_end{self.global_token_id}"
                    
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
                            continue
                        
                        if token_no + 1 > len(line):
                            raise Exception(f"return must have a value")
                        
                        retValue = line[token_no+2]
                        
                        if (retType == "int" and not retValue.isnumeric()) and (retType != self.typeOf(retValue)):
                            raise Exception(f"return value must be an integer")
                        
                        if name == "main":
                            self.compiledASM[".text"].append(sys_exit(retValue))
                        else:
                            if retValue not in self.package["constants"] or retValue not in self.package["variables"]:
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
            
            if self.package["blocks"][block]["args"][0] != "void":
                args = self.package["blocks"][block]["tokens"][0]
                args = [arg for arg in args if arg != "BS_VARIABLE_TOKEN"]
                ## remove BS_VARIABLE_TOKEN from args
                print(f"args: {args} {self.package['blocks'][block]['args']}")
                print(f"argc: {len(args)} {self.package['blocks'][block]['argc']}")
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
                            self.allocSpace(arg, dtype, int(size))
                        else:
                            raise Exception(f"size of '{size}' is not a number")
                    else:
                        self.allocSpace(arg, dtype)
                    self.package["variables"][arg] = [dtype, "function_argument"]
                    ## TODO: rework this (so we don't have string issues)
                    self.compiledASM[".text"].append(f"mov [{arg}], {REGISTERS[regIndex]}")
                    regIndex += 1
            
            for line in self.package["blocks"][block]["tokens"]:
                if not hasReturned:
                    hasReturned = self.compile_blockLine(block, line)
                    continue
                self.compile_blockLine(block, line)
            if requireReturn and not hasReturned:
                raise Exception(f"{block} must return a value")
            elif not requireReturn and not hasReturned:
                self.compiledASM[".text"].append("ret")
    
    def compileConstants(self) -> None:
        for constant in self.package["constants"]:
            self.package['constants'][constant][1] = self.package['constants'][constant][1] if not self.isVariable(self.package['constants'][constant][1]) else f"[{self.package['constants'][constant][1]}]"
            ## check if there is a newline in the string
            if "\\n" in self.package['constants'][constant][1]:
                self.package['constants'][constant][1] = self.package['constants'][constant][1].replace("\\n", "")
                self.package['constants'][constant][1] += ", 10" if self.package['constants'][constant][1] != "" else "10"
            self.compiledASM[".rodata"].append(f"{constant} db {self.package['constants'][constant][1]}")
    
    def compile(self) -> None:
        self.compileBlock()
        self.compileConstants()

        print("\n\n----- Variables -----")
        pprint(self.package["variables"])
        print("\n\n------ Compiled ASM ------")
        pprint(self.compiledASM)
        
        ## now to join the sections
        compiled = f"global {FUNCTION_MAIN_NAME} ; the start we expect\n%include \"libs/bs_stdlib.asm\"\n\n"
        for section in self.compiledASM:
            if self.compiledASM[section] != []:
                compiled += f"\nsection {section}\n"
                compiled += "\n".join(self.compiledASM[section])
                compiled += "\n"
                
        with open("test.asm", "w+") as writer:
            writer.write(compiled)
            
        print("\n\n------ Compiled Assembly ------")
        print("compiled to: test.asm")
        print("nasm -felf64 test.asm && ld test.o && ./a.out")