from pprint import pprint

BS_GENERIC_TYPES = [
    #"char",
    "int",
    "void",
    "null",
#    "ptr"
    "float", ## TODO: Add support for float
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
    "ptr"   : 2,
    #"char"  : 5,
    "float" : 6,
    "return": 7,
    
    "*"     : 8,
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
    
    "&&"    : 19,
    "||"    : 20,
    "! "    : 21,
    
    "asm"   : 25,
    ";"     : 26,
    "goto"  : 27,
    "label" : 28,
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
        self.variables      : dict[str, list[str]] = {}
        self.constantValues : dict[str, list[str]] = {}
        self.arrays         : dict[str, list[str]] = {}
        self.globalVariables: dict[str, list[str]] = {}
        self.headers        : list[str] = []
        self.livingFunctions: list[str] = []
        self.externs        : list[str] = []
    
    def handleIncludes(self) -> None:
        ## find any line that starts with #include
        for line_no, line in enumerate(self.combined_data):
            if line.startswith("#include"):
                ## get the file name
                fileName = line.split(" ", 1)[1].strip()
                if fileName in self.included_files:
                    continue
                ## get the file data
                fileData = open(fileName, "r").readlines()
                ## add the file data to the combined data
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
                if filename in self.included_files:
                    continue
                self.included_files.append(filename)

                ## get the function names
                functionNames = open(filename, "r").readlines()
                
                for line in functionNames:
                    if line.startswith(";"):
                        continue
                    elif ":" in line and not "." in line:
                        
                        self.livingFunctions.append(line.strip().replace(":", ""))
            elif line.startswith("#extern"):
                line = line.split(" ", 1)[1].strip()
                self.externs.append(line)
                self.livingFunctions.append(line)
                
    def pre_parse(self) -> None:
        self.handleIncludes()
        inMultiLineComment = False
        
        ## remove single line comments
        ## TODO: check if string contains # or #**#
        line_no = 0
        
        while line_no < len(self.combined_data):
            line = self.combined_data[line_no]
            if BS_COMMENT_START in line:
                self.combined_data[line_no] = line.split(BS_COMMENT_START, 1)[0]
                inMultiLineComment = True
                
            elif inMultiLineComment:
                if BS_COMMENT_END in line:
                    inMultiLineComment = False
                    self.combined_data[line_no] = line.split(BS_COMMENT_END, 1)[0].strip()
                    continue
                self.combined_data[line_no] = ""
                
            elif ";" in line:
                ## break the line into lines
                lines = line.split(";")
                self.combined_data[line_no] = lines[0].strip()
                self.combined_data.insert(line_no + 1, lines[1].strip())
                
            line_no += 1
                
        
        self.combined_data = [line.split("#",1)[0].strip() for line in self.combined_data]
        ## remove empty lines
        self.combined_data = [line for line in self.combined_data if line != "" and line != "\n"]
        print("\n\n-- COMBINED DATA --")
        pprint(self.combined_data)
    
    def blockify(self) -> None:
        """
            Turn our source code into blocks
            easier for parsing later
        """
        lineNo = 0
        while lineNo < len(self.combined_data):
            line = self.combined_data[lineNo]
            if line.startswith("block"):
                _, blockName, argc = line.split(" ", 2)
                argc, retType = argc.split("->", 1)
                args = argc.split(" ")
                args = [arg.strip() for arg in args if arg != ""]
                argc = len(args)
                
            elif line.startswith("const"):
                _, dType, varName, value = line.split(" ", 3)
                self.constantValues[varName] = [dType, value]
                lineNo += 1
                continue 
            elif line.startswith("array"):
                _, dType, varName, size = line.split(" ", 3)
                self.arrays[varName] = [dType, size]
                lineNo += 1
                continue
            elif line.startswith("global"):
            
                _, dType, varName, value = line.split(" ", 3)
                self.globalVariables[varName] = [dType, value]
                lineNo += 1
                continue
            ## find the next end 
            next_end = self.combined_data[lineNo:].index("end")
            
            ## add the block
            self.blocks[blockName] = {
                "args": args,
                "argc": argc,
                "retType": retType.strip(),
                "local_variables": [],
                "lines": self.combined_data[lineNo+1:lineNo+next_end],
                "lineRange": (lineNo, lineNo+next_end)
            }
            self.livingFunctions.append(blockName)
            lineNo = lineNo + next_end + 1
                
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
        print("\n\n-- TOKENIZING --")
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
                        
                    if not inStr:
                        if token in BS_KEY_TOKENS:
                            tokens[token_no] = BS_KEY_TOKENS[token]
                        elif token in self.livingFunctions:
                            tokens.insert(token_no, "BS_FUNCTION_TOKEN")
                            skip = True
                        elif token.isnumeric() or token.startswith("0x") or token.startswith("0b") or token.startswith("0o") or (token.startswith('-') and token[1:].isnumeric()):
                            tokens.insert(token_no, "BS_INT_TOKEN")
                            skip = True
                        else:
                            #print(f"{block}:{token_no} - {token}")
                            tokens.insert(token_no, "BS_VARIABLE_TOKEN")
                            if token not in self.constantValues and token.split('[')[0] not in self.arrays and token not in self.globalVariables:
                                ## scope 
                                #token = token.split('[')[0] if '[' in token else token
                                self.variables[f"{blockName}_{token}"] = [self.typeOf(token, blockName), "unknown"]
                                ## replace token with the variable name
                                tokens[token_no+1] = f"{blockName}_{token}"
                                print(f"{tokens[token_no+1]}")
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
                        
                    
        pprint(self.blocks)
    
    def package(self) -> dict[str, dict]:
        return {
            "blocks": self.blocks,                   ## all block data
            "constants": self.constantValues,        ## all constant values
            "livingFunctions": self.livingFunctions, ## all functions
            "includedFiles": self.included_files,    ## all included files
            "arrays": self.arrays,                   ## all arrays
            "globals": self.globalVariables,         ## all globals
            "variables": self.variables,             ## all variables
            "coreFile": self.core_file,              ## the core filename
            "externs": self.externs                  ## all externs
        }