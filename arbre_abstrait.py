"""
Affiche une chaine de caractère avec une certaine identation
"""
def afficher(s,indent=0):
    print(" "*indent+s)

class Program:
    def __init__(self,listeInstructions, listeFunctions=None):
        self.listeInstructions = listeInstructions
        self.listeFunctions = listeFunctions
    def afficher(self,indent=0):
        afficher("<program>",indent)
        if self.listeFunctions:
            self.listeFunctions.afficher(indent+1)
        self.listeInstructions.afficher(indent + 1)
        afficher("</program>",indent)

class Instructions:
    def __init__(self, instructions = None):
        self.instructions = instructions if instructions else []
    def afficher(self,indent=0):
        afficher("<instructions>",indent)
        for instruction in self.instructions:
            instruction.afficher(indent+1)
        afficher("</instructions>",indent)

class Functions:
    def __init__(self):
        self.functions = []
    def afficher(self, indent=0):
        afficher("<functions>", indent)
        for function in self.functions:
            function.afficher(indent + 1)
        afficher("</functions>", indent)
    def append(self, expr):
        self.functions.append(expr)


class Function:
    def __init__(self,fct,args=None):
        self.fct = fct
        self.args = args
    def afficher(self,indent=0):
        afficher(f"<function name=\"{self.fct}\"{('' if self.args else '/')}>",indent)
        if self.args:
            self.args.afficher(indent+1)
            afficher("</function>",indent)

class Return:
    def __init__(self,exp):
        self.exp = exp
    def afficher(self,indent=0):
        afficher(f"<return>",indent)
        self.exp.afficher(indent+1)
        afficher("</return>",indent)

class Args:
    def __init__(self):
        self.listArgs = []
    def afficher(self, indent=0):
        afficher(f"<arguments>", indent)
        for arg in self.listArgs:
            arg.afficher(indent + 1)
        afficher("</arguments>", indent)
    def append(self, expr):
        self.listArgs.append(expr)

class Declaration:
    def __init__(self,type,name,value=None):
        self.type = type
        self.name = name
        self.value = value
    def afficher(self,indent=0):
        afficher(f"<declaration name=\"{self.name}\" type=\"{self.type}\"{('' if self.value else '/')}>", indent)
        if self.value:
            self.value.afficher(indent+1)
            afficher("</declaration>",indent)

class DeclarationFunction:
    def __init__(self, type, name, instructions, declarationArgs=None):
        self.type = type
        self.name = name
        self.instructions = instructions
        self.declarationArgs = declarationArgs
    def afficher(self, indent=0):
        afficher(f"<func_declaration name=\"{self.name}\" type=\"{self.type}\">", indent)
        if self.declarationArgs:
            self.declarationArgs.afficher(indent + 1)
        self.instructions.afficher(indent + 1)
        afficher("</func_declaration>", indent)
    def append(self, expr):
        self.declarationArgs.append(expr)

class ArgsDeclaration:
    def __init__(self):
        self.declarations = []
    def afficher(self, indent=0):
        afficher(f"<args_declaration>", indent)
        for i in range(len(self.declarations)):
            self.declarations[i].afficher(indent + 1)
        afficher("</args_declaration>", indent)
    def append(self, expr):
        self.declarations.append(expr)


class Assignment:
    def __init__(self,variable,value):
        self.variable = variable
        self.value = value
    def afficher(self,indent=0):
        afficher(f"<assignment name=\"{self.variable}\">",indent)
        self.value.afficher(indent+1)
        afficher("</assignment>",indent)

class Operation:
    def __init__(self,op,exp1,exp2=None):
        self.exp1 = exp1
        self.op = op
        self.exp2 = exp2
    def afficher(self,indent=0):
        afficher(f"<operation operator=\"{self.op}\">",indent)
        self.exp1.afficher(indent+1)
        if self.exp2:
            self.exp2.afficher(indent+1)
        afficher("</operation>",indent)

class While:
    def __init__(self,cond,instructions):
        self.cond = cond
        self.instructions = instructions
    def afficher(self,indent=0):
        afficher(f"<while>",indent)
        self.cond.afficher(indent+1)
        self.instructions.afficher(indent+1)
        afficher("</while>",indent)

class If:
    def __init__(self,cond,instructions, elseInstruction = None):
        self.cond = cond
        self.instructions = instructions
        self.elseInstruction = elseInstruction
    def afficher(self,indent=0):
        afficher(f"<if>",indent)
        self.cond.afficher(indent+1)
        self.instructions.afficher(indent+1)
        if self.elseInstruction:
            self.elseInstruction.afficher(indent+1)
        afficher("</if>",indent)

class Else:
    def __init__(self,instructions):
        self.instructions = instructions
    def afficher(self,indent=0):
        afficher(f"<else>",indent)
        self.instructions.afficher(indent+1)
        afficher("</else>",indent)

class Integer:
    def __init__(self,valeur):
        self.valeur = valeur
    def afficher(self,indent=0):
        afficher(f"<integer value=\"{str(self.valeur)}\"/>",indent)

class Variable:
    def __init__(self,valeur):
        self.valeur = valeur
    def afficher(self,indent=0):
        afficher(f"<variable value=\"{str(self.valeur)}\"/>",indent)

class Boolean:
    def __init__(self,valeur):
        self.valeur = valeur
    def afficher(self,indent=0):
        afficher(f"<boolean value=\"{str(self.valeur)}\"/>",indent)
