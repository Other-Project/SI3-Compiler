import sys
from analyse_lexicale import FloLexer
from analyse_syntaxique import FloParser
import arbre_abstrait

num_etiquette_courante = -1 #Permet de donner des noms différents à toutes les étiquettes (en les appelant e0, e1,e2,...)

afficher_table = False
afficher_code = False

"""
affiche une erreur sur la sortie stderr et quitte le programme
"""

def erreur(s):
	print("Erreur:",s,file=sys.stderr)
	exit(1)
	
"""
Un print qui ne fonctionne que si la variable afficher_table vaut Vrai.
(permet de choisir si on affiche le code assembleur ou la table des symboles)
"""
def printifm(*args,**kwargs):
	if afficher_code:
		print(*args,**kwargs)

"""
Un print qui ne fonctionne que si la variable afficher_table vaut Vrai.
(permet de choisir si on affiche le code assembleur ou la table des symboles)
"""
def printift(*args,**kwargs):
	if afficher_table:
		print(*args,**kwargs)

"""
Fonction locale, permet d'afficher un commentaire dans le code arm.
"""
def arm_comment(comment):
	if comment != "":
		printifm("\t\t @ "+comment)#le point virgule indique le début d'un commentaire en ARM. Les tabulations sont là pour faire jolie.
	else:
		printifm("")  
"""
Affiche une instruction ARM sur une ligne
Par convention, les derniers opérandes sont nuls si l'opération a moins de 3 arguments.
"""
def arm_instruction(opcode, op1="", op2="", op3="", comment=""):
	if op2 == "":
		printifm("\t"+opcode+"\t"+op1+"\t\t",end="")
	elif op3 =="":
		printifm("\t"+opcode+"\t"+op1+",\t"+op2+"\t",end="")
	else:
		printifm("\t"+opcode+"\t"+op1+",\t"+op2+",\t"+op3,end="")
	arm_comment(comment)


"""
Retourne le nom d'une nouvelle étiquette
"""
def arm_nouvelle_etiquette():
	num_etiquette_courante+=1
	return "e"+str(num_etiquette_courante)

"""
Affiche le code arm correspondant à tout un programme
"""
def gen_programme(programme):
	header=""".LC0:
	.ascii	"%d\\000"
	.align	2
.LC1:
	.ascii	"%d\\012\\000"
	.text
	.align	2
	.global	main"""
	printifm(header)
	

	
	printifm('main:')
	arm_instruction("push", "{fp,lr}", "", "", "")
	arm_instruction("add", "fp","sp", "#4", "")
	gen_listeInstructions(programme.listeInstructions)
	arm_instruction("mov", "r0", "#0", "", "")
	arm_instruction("pop", "{fp, pc}","","","")

"""
Affiche le code arm correspondant à une suite d'instructions
"""
def gen_listeInstructions(listeInstructions):
	for instruction in listeInstructions.instructions:
		gen_instruction(instruction)

"""
Affiche le code arm correspondant à une instruction
"""
def gen_instruction(instruction):
	if type(instruction) == arbre_abstrait.Ecrire:
		gen_ecrire(instruction)
	else:
		erreur("génération type instruction non implémenté "+str(type(instruction)))

"""
Affiche le code arm correspondant au fait d'envoyer la valeur entière d'une expression sur la sortie standard
"""	
def gen_ecrire(ecrire):
	gen_expression(ecrire.exp) #on calcule et empile la valeur d'expression
	arm_instruction("pop", "{r1}", "", "", "") #on dépile la valeur d'expression sur r1
	arm_instruction("ldr", "r0", "=.LC1", "", "")
	arm_instruction("bl", "printf", "", "", "") #on envoie la valeur de r1 sur la sortie standard
	
"""
Affiche le code arm pour calculer et empiler la valeur d'une expression
"""
def gen_expression(expression):
	if type(expression) == arbre_abstrait.Operation:
		gen_operation(expression) #on calcule et empile la valeur de l'opération
	elif type(expression) == arbre_abstrait.Entier:
      		arm_instruction("mov", "r1", "#"+str(expression.valeur), "", "") ; #on met sur la pile la valeur entière
      		arm_instruction("push", "{r1}", "", "", "") ; #on met sur la pile la valeur entière			
	else:
		erreur("type d'expression inconnu"+str(type(expression)))


"""
Affiche le code arm pour calculer l'opération et la mettre en haut de la pile
"""
def gen_operation(operation):
	op = operation.op
		
	gen_expression(operation.exp1) #on calcule et empile la valeur de exp1
	gen_expression(operation.exp2) #on calcule et empile la valeur de exp2
	
	arm_instruction("pop", "{r1}", "", "", "dépile exp2 dans r1")
	arm_instruction("pop", "{r0}", "", "", "dépile exp1 dans r0")
	
	code = {"+":"add","*":"mul"} #Un dictionnaire qui associe à chaque opérateur sa fonction arm
	#Voir: https://developer.arm.com/documentation/dui0497/a/the-cortex-m0-instruction-set/instruction-set-summary?lang=en
	if op in ['+','*']:
		arm_instruction(code[op], "r0", "r1", "r0", "effectue l'opération r0" +op+"r1 et met le résultat dans r0" )
	else:
		erreur("operateur \""+op+"\" non implémenté")
	arm_instruction("push",  "{r0}" , "", "", "empile le résultat");


if __name__ == "__main__":
	afficher_arm = True
	lexer = FloLexer()
	parser = FloParser()
	if len(sys.argv) < 3 or sys.argv[1] not in ["-arm","-table"]:
		print("usage: python3 generation_code.py -arm|-table NOM_FICHIER_SOURCE.flo")
		exit(1)
	if sys.argv[1]  == "-arm":
		afficher_code = True
	else:
		afficher_tableSymboles = True
	with open(sys.argv[2],"r") as f:
		data = f.read()
		try:
			arbre = parser.parse(lexer.tokenize(data))
			gen_programme(arbre)
		except EOFError:
			exit(1)
