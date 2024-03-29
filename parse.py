import os
from pprint import pprint

DEBUG = False

BS_GENERIC_TYPES = [
    "str"
    "int",
    "void"
]

BS_MATH_OPERS = [
    "+",
    "-",
    "&",
    "/",
    '='
]

GENERAL_OPERATORS = [
    "==",
    "!=",
    ">",
    "<",
    ">=",
    "<=",
    "->",
]

BS_NAMESPACEABLE_TOKENS = [
    "block",
    "struct",
    "const",
    "array",
]

BS_TOKEN_TYPES = [
    ## these are the only tokens that require special handling
    "BS_FUNCTION_TOKEN",
    "BS_VARIABLE_TOKEN",
]

BS_KEY_TOKENS = {
    "if"    : 0,
    "else"  : 1,
    "int"   : 2,
    "void"  : 3,
    #"ptr"   : 2,
    #"char"  : 5,
    "float" : 6,
    "return": 7,
    
    "*="     : 8,
    "-="     : 9,
    "+="     : 10,
    "/="     : 11,
    
    "&"     : 8,
    "-"     : 9,
    "+"     : 10,
    "/"     : 11,
    "="     : 12,
    "|"     : 13,
    
    "<"     : 14,
    ">"     : 15,
    ">="    : 16,
    "<="    : 17,
    "=="    : 18,
    "!="    : 19,
    
    "asm"   : 25,
    ";"     : 26,
    "goto"  : 27,
    "label" : 28,
    "switch": 29,
    "case"  : 30,
    "syscall": 31,
    "pop"   : 32,
    "push"  : 33,
    
    
    "namespace" : -1,
}

BS_COMMENT_CHAR = "#"
BS_COMMENT_START = BS_COMMENT_CHAR + "*"
BS_COMMENT_END   = "*" + BS_COMMENT_CHAR

class parser:
    def __init__(self,
                    core_file:str,
                    combined_data:list[str],
                    included_files:list[str]) -> None:
        self.core_file      = core_file
        self.combined_data  = combined_data
        self.included_files = included_files
        
        self.blocks:dict[str, dict] = {}
        """
        these get defined in .data
            var_name : {
                value,
                type,
                size
            }
        """
        
        self.currentNameSpace = ""
        
        ## list of structs
        self.structs        : dict[str, dict[str]] = {}
        
        self.variables      : dict[str, list[str]] = {}
        self.constantValues : dict[str, list[str]] = {}
        self.arrays         : dict[str, list[str]] = {}
        self.globalVariables: dict[str, list[str]] = {}
        self.headers        : list[str] = []
        self.livingFunctions: list[str] = []
        self.externs        : list[str] = []
        self.calledFuncs    : list[str] = ["main"]
    
    def handleIncludes(self) -> None:
        ## find any line that starts with #include
        for line_no, line in enumerate(self.combined_data):
            if line.startswith("#include"):
                ## get the file name
                fileName = line.split(" ", 1)[1].strip()
                #if "std." in fileName:
                    ## get current files path
                #    fileName = fileName.replace("std.", str(Path(__file__).parent.absolute()) + "/libs/") 
                if fileName in self.included_files:
                    continue
                ## get the file data
                fileData = open(fileName, "r").readlines()
                ## add the file data to the combined data
                self.combined_data.append("namespace")
                self.combined_data.extend(fileData)
                ## remove the line that included the file
                self.combined_data.pop(line_no)
                ## recursively call this function on the new data
                self.handleIncludes()
                self.included_files.append(fileName)
                break

            ## allow for using assembly includes
            elif line.startswith("#use"):
                filename = line.split(" ", 1)[1].strip()
                #if "std." in filename:
                #    filename = filename.replace("std.", str(Path(__file__).parent.absolute()) + "/libs/") 
                if filename in self.included_files:
                    continue
                self.included_files.append(filename)

                ## get the function names
                if not os.path.exists(filename):
                    ## assume stdlib 
                    continue
                functionNames = open(filename, "r").readlines()
                
                for line in functionNames:
                    if line.startswith(";"):
                        continue
                    elif ":" in line and not line.startswith('.'):
                        self.livingFunctions.append(line.strip().replace(":", ""))
                        
            elif line.startswith("#extern"):
                line = line.split(" ", 1)[1].strip()
                self.externs.append(line)
                self.livingFunctions.append(line)
                
            ## TODOOO: exports

    def structFind(self) -> None:
        
        lineNo = 0
        structName  = None
        structStart = 0
        structData  = []
        
        while lineNo < len(self.combined_data):
            line = self.combined_data[lineNo]
            if not line.startswith("struct"):
                lineNo += 1
                continue
            if line.startswith("struct"):
                assert structName is None, f"{lineNo} >> struct is already being defined!"
                assert structName not in self.structs, f"{lineNo} >> struct is already defined!"
                structStart = lineNo
                structName = line.split(" ", 1)[1]
            
            elif structName != None and line == "end":
                self.structs[structName] = structData.copy()
                structName = None
                structData.clear()
                self.combined_data = self.combined_data[:structStart] + self.combined_data[lineNo+1:]
                
            elif structName != None:
                dtype,vname = line.split(" ", 1)
                dtype = self.setType(dtype)
                line = f"{dtype} {vname}"
                structData.append(line)
            
            lineNo += 1

    def parseMath(self, line:str) -> list[str]:
        op_out  = []
        num_out = []
        buff    = []
        for c in line:
            if c in BS_MATH_OPERS:
                num_out.append(''.join(buff))
                buff = []
                op_out.append(c)
            else:
                buff.append(c)
        num_out.append(''.join(buff))
        return num_out, op_out

    def pre_parse(self) -> None:
        self.handleIncludes()
        inMultiLineComment = False
        
        ## remove single line comments
        line_no = 0
        
        whileCheck   = False
        whileBlkName = []
        
        ## remove comments and empty lines
        self.combined_data = [line.split("#",1)[0].strip() for line in self.combined_data]
        self.combined_data = [line for line in self.combined_data if line != "" and line != "\n"]

        while line_no < len(self.combined_data):
            line = self.combined_data[line_no].strip()
            ## Handle comments & multi-line comments
            if BS_COMMENT_START in line:
                self.combined_data[line_no] = line.split(BS_COMMENT_START, 1)[0]
                inMultiLineComment = True
                
            elif inMultiLineComment:
                print("here")
                if BS_COMMENT_END in line:
                    inMultiLineComment = False
                    self.combined_data[line_no] = line.split(BS_COMMENT_END, 1)[0].strip()
                    continue
                self.combined_data[line_no] = ""
                
            ## split lines (allows for single line operations)
            elif ";" in line:
                ## break the line into lines
                ## check if the ';' is in a string
                if '"' in line:
                    ## find the next '"'
                    start = line.find('"')
                    end_quote = line.find('"', start + 1)
                    if end_quote == -1:
                        raise Exception(f"Error: Unclosed string on line {line_no + 1}")
                    ## check if the ';' is in the string
                    if line.find(';') in range(start, end_quote):
                        line_no += 1
                        continue ## do not split the line
                    
                lines = line.split(";")
                self.combined_data[line_no] = lines[0].strip()
                self.combined_data.insert(line_no + 1, lines[1].strip())
                
            elif line == "do":
                line = f"label bsDo_{line_no}"
                whileCheck = True
                whileBlkName.append(f"bsDo_{line_no}")
                self.combined_data[line_no] = line
            
            elif line.startswith("while"):
                assert whileCheck, "While without do"
                
                logic = line.split("while", 1)[1].strip()            
                
                self.combined_data[line_no] = f"if {logic}"
                self.combined_data.insert(line_no + 1, f"| goto {whileBlkName[-1]}")
                
                whileBlkName.pop()
                if len(whileBlkName) == 0:
                    whileCheck = False
            
            elif "continue" in line:
                if "\"" in line:
                    strStart = line.find('"')
                    strEnd = line.find('"', strStart + 1)
                    ctn = line.find("continue")
                    if ctn in range(strStart, strEnd): ## continue in string
                        line_no += 1
                        continue
                assert whileCheck, "Continue without while"
                gotoCMD = f"goto {whileBlkName[-1]}"
                gotoCMD = "| " + gotoCMD if "|" in line else gotoCMD
                self.combined_data[line_no] = gotoCMD

            ## split line by operators (+,-,*,/,=,==,!=,>,<,>=,<=)
            elif any(op in line for op in BS_MATH_OPERS) and not any(op in line for op in GENERAL_OPERATORS):
                nums, ops = self.parseMath(line)
                current = line_no
                setTo = ''
                for i in range(0, len(nums)):
                    if i == len(ops):
                        break
                    a, b = nums[i], nums[i+1]
                    a, b = a.strip(), b.strip()
                    if ops[i] == "=":
                        setTo = a
                    if a.isnumeric():
                        a = setTo if setTo != '' else a

                    if current == line_no:
                        self.combined_data[current] = f"{a} {ops[i]} {b}".strip()
                    else:
                        self.combined_data.insert(current, f"{a} {ops[i]} {b}".strip())
                    current += 1
                line_no = current - 1
            
            elif "namespace" in line:
                self.currentNameSpace = line.split("namespace", 1)[1].strip()
                self.combined_data[line_no] = ""
                
            ## handle namespacing
            elif any (tp in line for tp in BS_NAMESPACEABLE_TOKENS) and self.currentNameSpace != '':
                tokenName, linedata = line.split(" ", 1)
                linedata = self.currentNameSpace + "." + linedata
                self.combined_data[line_no] = f"{tokenName} {linedata}"

            line_no += 1
        
        if DEBUG:
            print("\n\n-- COMBINED DATA --")
            pprint(self.combined_data)
    
    def setType(self, typeName:str) -> str:
        if typeName == "ptr":
            return "int"
        elif typeName == "byte":
            return "int"
        elif typeName == "bool":
            return "int"
        elif typeName == "char":
            return "int"
        elif typeName == "int":
            return "int"
        elif typeName in self.structs:
            return "int" ## ptr to struct
        return typeName
    
    def blockify(self) -> None:
        """
            Turn our source code into blocks
            easier for parsing later
        """
        lineNo = 0
        while lineNo < len(self.combined_data):         
            line = self.combined_data[lineNo]
            useSquiggly = False
            if line == "":
                lineNo += 1
                continue
            if line.startswith("block"):
                if "{" in line:
                    line = line.replace("{", "")
                    useSquiggly = True
                _, blockName = line.split(" ", 1)
                if " " in blockName:
                    blockName, argc = blockName.split(" ", 1)
                else:
                    argc = "void -> void"
                if "->" in argc:
                    argc, retType = argc.split("->", 1)
                else:
                    retType = "void"
                    argc = argc.strip()
                args = argc.split(" ")
                
                for i in range(len(args)):
                    args[i] = args[i].replace(",", "").strip()
                    if args[i] == "":
                        args.pop(i)
                    elif "|" in args[i]:
                        args[i] = "|".join([self.setType(x) for x in args[i].split("|")])
                    elif "&" not in args[i]:
                        args[i] = self.setType(args[i])
                    else:
                        args[i] = args[i].replace("&", "")
                    
                if len(args) == 0:
                    args.append("void")
                argc = len(args)
                
            elif line.startswith("const"):
                _, dType, varName, value = line.split(" ", 3)
                self.constantValues[varName] = [self.setType(dType), value]
                lineNo += 1
                continue 
            
            elif line.startswith("array"):
                _, dType, varName, size = line.split(" ", 3)
                self.arrays[varName] = [self.setType(dType), size]
                lineNo += 1
                continue
            
            elif line.startswith("global"):
                _, dType, varName, value = line.split(" ", 3)
                self.globalVariables[varName] = [self.setType(dType), value]
                lineNo += 1
                continue
            
            #assert blockName not in self.blocks, f"Block {blockName} already exists! {lineNo}"
            next_end = self.combined_data[lineNo:].index("end" if not useSquiggly else "}")
            retType = self.setType(retType.strip()) 
            ## add the block
            if blockName not in self.blocks:
                self.blocks[blockName] = {
                    "args": args,
                    "argc": argc,
                    "retType": retType,
                    "local_variables": [],
                    "lines": self.combined_data[lineNo+1:lineNo+next_end],
                    "lineRange": (lineNo, lineNo+next_end)
                }
                self.livingFunctions.append(blockName)
            lineNo = lineNo + next_end + 1
            
        if DEBUG:
            print("\n\n-- BLOCKS --")
            pprint(self.blocks)
            
            print("\n\n-- CONSTANTS --")
            pprint(self.constantValues)
            
            print("\n\n-- ARRAYS --")
            pprint(self.arrays)
            
            print("\n\n-- GLOBALS --")
            pprint(self.globalVariables)
        
        self.tokenizeBlocks()
        
    def typeOf(self, token:str, blockName:str) -> str:
        if token in BS_KEY_TOKENS:
            return "keyword"
        
        elif token.isnumeric() or token.startswith("0x") or token.startswith("0b") or token.startswith("0o") or (token.startswith('-') and token[1:].isnumeric()):
            return "int"
        
        ## check if it's a variable
        elif f"{blockName}_{token}" in self.variables:
            return self.variables[f"{blockName}_{token}"][0]
        
        elif token in self.constantValues:
            return self.constantValues[token][0]
        
        elif token in self.arrays:
            return self.arrays[token][0]
        
        elif token in self.globalVariables:
            return self.globalVariables[token][0]

        ## check if it's a float
        elif "." in token and token.replace(".", "").isnumeric():
            return "float"
        
        else:
            return "str"
    
    def tokenizeBlocks(self) -> None:
        """
            Tokenize the blocks
            and add them to the blocks
        """
        if DEBUG: print("\n\n-- TOKENIZING --")
        for blockName, block in self.blocks.items():
            block["tokens"] = []
            for line in block["lines"]:
                tokens = line.split(" ")
                tokens = [token.strip() for token in tokens if token != ""]
                
                strStart = 0
                inStr    = False
                skip     = False
                for token_no, token in enumerate(tokens):
                    if skip:
                        skip = False
                        continue
                    ## check if we are in a string
                    if token.startswith("\"") or token.endswith("\""):
                        inStr = not inStr
                        if token.startswith("\"") and token.replace("\"", "").strip() != "":
                            strStart = token_no
                            token = token[1:]
                        if token.endswith("\""):
                            token[:-1]
                            inStr = False
                        if not inStr:
                            ## join the string 
                            tokens[strStart] = " ".join(tokens[strStart:token_no+1]).replace("\"", "")
                            tokens = tokens[:strStart+1] + tokens[token_no+1:]
                            ## co-pilot decided to say ahoy \o.o/ Mwahahaha \o.o/ <- co-pilot
                            tokens.insert(strStart, "BS_STRING_TOKEN_AHOY")
                        else:
                            strStart = token_no
                        
                        continue
                    
                    elif token.startswith("'"): ## char (convert to int)
                        ## remove the '
                        token = str(ord(token[1:-1]))
                        tokens[token_no] = token
                    
                    if not inStr:
                        
                        if token in BS_KEY_TOKENS:
                            tokens[token_no] = BS_KEY_TOKENS[token]
                            
                            ## is a goto
                            if token == "goto":
                                skip = True if "&" not in tokens[token_no+1] else False 
                        elif token in self.livingFunctions:
                            tokens.insert(token_no, "BS_FUNCTION_TOKEN")
                            self.calledFuncs.append(token)
                            skip = True
                        elif token.isnumeric() or token.startswith("0x") or token.startswith("0b") or token.startswith("0o") or (token.startswith('-') and token[1:].isnumeric()):
                            tokens.insert(token_no, "BS_INT_TOKEN")
                            skip = True
                        elif "&" in token and token.replace("&", "") in self.livingFunctions:
                            tokens.insert(token_no, "BS_INT_TOKEN")
                            token = token.replace("&", "")
                            tokens[token_no+1] = token
                            self.calledFuncs.append(token)
                            skip = True
                        elif token in self.structs:
                            tokens.insert(token_no, "BS_STRUCT_TOKEN")
                            skip = True
                        else:
                            tokens.insert(token_no, "BS_VARIABLE_TOKEN")
                            if token not in self.constantValues and token.split('[')[0] not in self.arrays and token not in self.globalVariables:
                                ## scope 
                                #token = token.split('[')[0] if '[' in token else token
                                self.variables[f"{blockName}_{token}"] = [self.typeOf(token, blockName), "unknown"]
                                ## replace token with the variable name
                                tokens[token_no+1] = f"{blockName}_{token}"
                                if DEBUG: print(f"{tokens[token_no+1]}")
                                if f"{blockName}_{token}" not in self.blocks[blockName]["local_variables"]:
                                    self.blocks[blockName]["local_variables"].append(f"{blockName}_{token}")
                            skip = True
                    ## split tokens by token types
                    
                newTokens = [[]]
                for t2 in tokens[::-1]:
                    if token in BS_TOKEN_TYPES:
                        newTokens[-1].append(t2)
                        newTokens.append([])
                        
                    else:
                        newTokens[-1].append(t2)
                for tok in newTokens:
                    self.blocks[blockName]["tokens"].append(tok[::-1])
                        
                    
        if DEBUG: pprint(self.blocks)
    
    def package(self) -> dict[str, dict]:
        cp = self.blocks.copy()
        for block in self.blocks:
            if block not in self.calledFuncs:
                cp.pop(block)
        self.blocks = cp
        return {
            "blocks": self.blocks,                   ## all block data
            "constants": self.constantValues,        ## all constant values
            "livingFunctions": self.livingFunctions, ## all functions
            "includedFiles": self.included_files,    ## all included files
            "arrays": self.arrays,                   ## all arrays
            "globals": self.globalVariables,         ## all globals
            "variables": self.variables,             ## all variables
            "coreFile": self.core_file,              ## the core filename
            "externs": self.externs,                 ## all externs
            "structs": self.structs                  ## all structs
        }
