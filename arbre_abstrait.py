"""
Affiche une chaine de caractère avec une certaine identation
"""
def afficher(s,indent=0):
	print(" "*indent+s)
	
class Program:
	def __init__(self,listeInstructions):
		self.listeInstructions = listeInstructions
	def afficher(self,indent=0):
		afficher("<program>",indent)
		self.listeInstructions.afficher(indent+1)
		afficher("</program>",indent)

class Instructions:
	def __init__(self):
		self.instructions = []
	def afficher(self,indent=0):
		afficher("<instructions>",indent)
		for instruction in self.instructions:
			instruction.afficher(indent+1)
		afficher("</instructions>",indent)
			
class Function:
	def __init__(self,fct,exp):
		self.fct = fct
		self.exp = exp
	def afficher(self,indent=0):
		afficher(f"<function name=\"{self.fct}\">",indent)
		self.exp.afficher(indent+1)
		afficher("</function>",indent)

class Args:
	def __init__(self):
		self.listArgs = []
	def afficher(self, indent=0):
		afficher(f"<arguments>", indent)
		for i in range(len(self.listArgs)):
			self.listArgs[i].afficher(indent + 1)
		afficher("</arguments>", indent)
	def append(self, expr):
		self.listArgs.append(expr)

		
class Operation:
	def __init__(self,op,exp1,exp2):
		self.exp1 = exp1
		self.op = op
		self.exp2 = exp2
	def afficher(self,indent=0):
		afficher(f"<operation operator=\"{self.op}\">",indent)
		self.exp1.afficher(indent+1)
		self.exp2.afficher(indent+1)
		afficher("</operation>",indent)

class Integer:
	def __init__(self,valeur):
		self.valeur = valeur
	def afficher(self,indent=0):
		afficher(f"<integer value=\"{str(self.valeur)}\" />",indent)

class Variable:
	def __init__(self,valeur):
		self.valeur = valeur
	def afficher(self,indent=0):
		afficher(f"<variable value=\"{str(self.valeur)}\" />",indent)

class Boolean:
	def __init__(self,valeur):
		self.valeur = valeur
	def afficher(self,indent=0):
		afficher(f"<boolean value=\"{str(self.valeur)}\" />",indent)
