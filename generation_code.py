import sys
from analyse_lexicale import FloLexer
from analyse_syntaxique import FloParser
import arbre_abstrait
from table_des_symboles import TableSymboles

num_etiquette_courante = -1  # Permet de donner des noms différents à toutes les étiquettes (en les appelant e0, e1,e2,...)

afficher_table = False
afficher_code = False

tableSymboles = TableSymboles()

"""
affiche une erreur sur la sortie stderr et quitte le programme
"""

def erreur(s):
    print("Erreur:", s, file=sys.stderr)
    exit(1)


"""
Un print qui ne fonctionne que si la variable.flo afficher_table vaut Vrai.
(permet de choisir si on affiche le code assembleur ou la table des symboles)
"""


def printifm(*args, **kwargs):
    if afficher_code:
        print(*args, **kwargs)


"""
Un print qui ne fonctionne que si la variable.flo afficher_table vaut Vrai.
(permet de choisir si on affiche le code assembleur ou la table des symboles)
"""


def printift(*args, **kwargs):
    if afficher_table:
        print(*args, **kwargs)


def typeStr(type):
    return type.__name__

"""
Fonction locale, permet d'afficher un commentaire dans le code arm.
"""


def arm_comment(comment):
    if comment != "":
        printifm(
            "\t\t @ " + comment
        )  # le point virgule indique le début d'un commentaire en ARM. Les tabulations sont là pour faire jolie.
    else:
        printifm("")


"""
Affiche une instruction ARM sur une ligne
Par convention, les derniers opérandes sont nuls si l'opération a moins de 3 arguments.
"""


def arm_instruction(opcode, op1="", op2="", op3="", comment=""):
    if op2 == "":
        printifm("\t" + opcode + "\t" + op1 + "\t\t", end="")
    elif op3 == "":
        printifm("\t" + opcode + "\t" + op1 + ",\t" + op2 + "\t", end="")
    else:
        printifm("\t" + opcode + "\t" + op1 + ",\t" + op2 + ",\t" + op3, end="")
    arm_comment(comment)


"""
Retourne le nom d'une nouvelle étiquette
"""


def arm_nouvelle_etiquette():
    global num_etiquette_courante
    num_etiquette_courante += 1
    return ".e" + str(num_etiquette_courante)


"""
Affiche le code arm correspondant à tout un programme
"""


def gen_programme(programme):
    header = """
.global __aeabi_idiv
.global __aeabi_idivmod
.boolean_or:
    mov r0, #1
	bx lr
.boolean_not:
    mov r0, #0
	bx lr
.LC0:
	.ascii	"%d\\000"
	.align	2
.LC1:
	.ascii	"%d\\012\\000"
	.text
	.align	2
	.global	main"""
    printifm(header)

    if programme.listeFunctions:
        for function in programme.listeFunctions.functions:
            tableSymboles.add(function)
        printift(tableSymboles)

        arm_comment("functions")
        for function in programme.listeFunctions.functions:
            gen_def_fonction(function)

    printifm("main:")
    arm_instruction("push", "{fp,lr}", "", "", "")
    arm_instruction("add", "fp", "sp", "#4", "")

    gen_listeInstructions(programme.listeInstructions)

    arm_instruction("mov", "r0", "#0", "", "")
    arm_instruction("pop", "{fp, pc}", "", "", "")

def gen_def_fonction(f):
    printifm(f"_{f.name}:")
    arm_instruction("push", "{lr}")
    gen_listeInstructions(f.instructions, f.name)

"""
Affiche le code arm correspondant à une suite d'instructions
"""


def gen_listeInstructions(listeInstructions, function=None):
    for instruction in listeInstructions.instructions:
        gen_instruction(instruction, function)


"""
Affiche le code arm correspondant à une instruction
"""
def gen_instruction(instruction, function=None):
    if type(instruction) == arbre_abstrait.Function:
        if instruction.fct == "lire":
            gen_lire()
            return arbre_abstrait.Integer
        elif instruction.fct == "ecrire":
            gen_ecrire(instruction)
        elif tableSymboles.has(instruction.fct):
            arm_instruction("bl", f"_{instruction.fct}")
            return tableSymboles.returnType(instruction.fct)
    elif type(instruction) in [arbre_abstrait.While, arbre_abstrait.If]:
        gen_block_operation(instruction)
    elif type(instruction) == arbre_abstrait.Return:
        if not function:
            erreur("Return keyword is only valid inside a function")
        returnType = gen_expression(instruction.exp)
        expectedType = tableSymboles.returnType(function)
        if returnType != expectedType:
            erreur(f"Incorrect return type expected {typeStr(expectedType)} got {typeStr(returnType)}")
        arm_instruction("pop", "{r2}")
        arm_instruction("pop", "{pc}", comment="return")
    else:
        erreur("génération type instruction non implémenté " + typeStr(type(instruction)))
    return None


"""
Affiche le code arm correspondant au fait d'envoyer la valeur entière d'une expression sur la sortie standard
"""
def gen_ecrire(ecrire):
    gen_expression(
        ecrire.args.listArgs[0]
    )  # on calcule et empile la valeur d'expression
    arm_instruction(
        "pop", "{r1}", "", "", ""
    )  # on dépile la valeur d'expression sur r1
    arm_instruction("ldr", "r0", "=.LC1", "", "")
    arm_instruction(
        "bl", "printf", "", "", ""
    )  # on envoie la valeur de r1 sur la sortie standard


"""
Affiche le code arm correspondant au fait de mettre en pause le programme, et permet à l’utilisateur d’entrée au clavier une chaîne 
de caractère qui est interprétée comme un entier.
"""
def gen_lire():
    arm_instruction("ldr", "r0", "=.LC0", "", "Charge l’adresse de la chaîne de format pour scanf dans r0")
    arm_instruction("sub", "sp", "sp", "#4", "Réserve de l’espace sur la pile pour stocker l’entier lu (on fait sp = sp -4)")
    arm_instruction("movs", "r1" , "sp", "", "Copie l’adresse de cet espace dans r1")
    arm_instruction("bl", "scanf", "", "", "Lance scanf pour lire l’entier et le stocker à l’adresse spécifiée par r1")
    arm_instruction("pop", "{r2}", "", "", "empiler input dans r2")

def gen_block_operation(instruction):
    endTrue = arm_nouvelle_etiquette()
    ifFalse = arm_nouvelle_etiquette()
    
    if type(instruction) == arbre_abstrait.While:
        arm_instruction(f"{endTrue}:", comment="true condition jump")
    gen_expression(instruction.cond)
    arm_instruction("pop", "{r0}")
    arm_instruction("cmp", "r0", "#1")
    arm_instruction("bNE", ifFalse, comment="condition is false")
    gen_listeInstructions(instruction.instructions)
    arm_instruction("b", endTrue)
    arm_instruction(f"{ifFalse}:", comment="false condition jump")
    if type(instruction) == arbre_abstrait.If:
        if instruction.elseInstruction:
            gen_listeInstructions(instruction.elseInstruction.instructions)
        arm_instruction(f"{endTrue}:", comment="true condition jump")

"""
Affiche le code arm pour calculer et empiler la valeur d'une expression
"""
def gen_expression(expression):
    if type(expression) == arbre_abstrait.Function:
        instType = gen_instruction(expression)
        arm_instruction("push", "{r2}", "", "", "")
        return instType
    elif type(expression) == arbre_abstrait.Operation:
        return gen_operation(expression)  # on calcule et empile la valeur de l'opération
    elif type(expression) == arbre_abstrait.Integer:
        arm_instruction("mov", "r1", "#" + str(expression.valeur), "", "")
        # on met sur la pile la valeur entière
        arm_instruction("push", "{r1}", "", "", "")
        # on met sur la pile la valeur entière
    elif type(expression) == arbre_abstrait.Boolean:
        arm_instruction("mov", "r1", "#" + str(1 if expression.valeur else 0), "", "")
        arm_instruction("push", "{r1}", "", "", "")
    else:
        erreur("type d'expression inconnu " + typeStr(type(expression)))
    return type(expression)


"""
Affiche le code arm pour calculer l'opération et la mettre en haut de la pile
"""


def gen_operation(operation):
    op = operation.op

    type1 = gen_expression(operation.exp1)  # on calcule et empile la valeur de exp1

    if operation.exp2:
        type2 = gen_expression(operation.exp2)  # on calcule et empile la valeur de exp2
        if type1 != type2:
            erreur(f"Types incompatibles {typeStr(type1)} != {typeStr(type2)}")
        arm_instruction("pop", "{r1}", "", "", "dépile exp2 dans r1")

    arm_instruction("pop", "{r0}", "", "", "dépile exp1 dans r0")

    comparisons = {
        "==": "EQ",
        "!=": "NE",
        "<=": "LE",
        ">=": "GE",
        "<": "LT",
        ">": "GT"
    }
    if type1 == arbre_abstrait.Integer and gen_operation_integer(op):
        True # do nothing
    elif type1 == arbre_abstrait.Boolean and gen_operation_boolean(op):
        True # do nothing
    elif op in comparisons.keys():
        labelTrue = arm_nouvelle_etiquette()
        labelFalse = arm_nouvelle_etiquette()

        arm_instruction("cmp", "r0", "r1")
        arm_instruction(f"b{comparisons[op]}", labelTrue)
        arm_instruction("mov", "r0", "#0")
        arm_instruction("b", labelFalse)
        arm_instruction(f"{labelTrue}:")
        arm_instruction("mov", "r0", "#1")
        arm_instruction(f"{labelFalse}:")
    else:
        erreur(f'operateur "{op}" non implémenté pour le type {typeStr(type1)}')
    arm_instruction("push", "{r0}", "", "", "empile le résultat")
    return type1

def gen_operation_integer(op):
    code = {
        "+": "add",
        "*": "mul"
    }  # Un dictionnaire qui associe à chaque opérateur sa fonction arm
    # Voir: https://developer.arm.com/documentation/dui0497/a/the-cortex-m0-instruction-set/instruction-set-summary?lang=en

    if op in code.keys():
        arm_instruction(
            code[op],
            "r0",
            "r1",
            "r0",
            "effectue l'opération r0" + op + "r1 et met le résultat dans r0",
        )
    elif op == "-":
        arm_instruction(
            "sub",
            "r0",
            "r0",
            "r1",
            "effectue l'opération r0" + op + "r1 et met le résultat dans r0",
        )
    elif op == "/":
        arm_instruction("bl", "__aeabi_idiv")
    elif op == "%":
        arm_instruction("bl", "__aeabi_idivmod")
        arm_instruction("mov", "r0", "r1")
    else:
        return False
    return True

def gen_operation_boolean(op):
    if op == "et":
        arm_instruction(
            "mul",
            "r0",
            "r1",
            "r0",
            "effectue l'opération r0" + op + "r1 et met le résultat dans r0",
        )
    elif op == "ou":
        arm_instruction("add", "r0", "r1", "r0")
        arm_instruction("cmp", "r0", "#2")
        arm_instruction("blEQ", ".boolean_or")
    elif op == "non":
        arm_instruction("add", "r0", "#1")
        arm_instruction("cmp", "r0", "#2")
        arm_instruction("blEQ", ".boolean_not")
    else:
        return False
    return True

if __name__ == "__main__":
    afficher_arm = True
    lexer = FloLexer()
    parser = FloParser()
    if len(sys.argv) < 3 or sys.argv[1] not in ["-arm", "-table"]:
        print("usage: python3 generation_code.py -arm|-table NOM_FICHIER_SOURCE.flo")
        exit(1)
    if sys.argv[1] == "-arm":
        afficher_code = True
    else:
        afficher_table = True
    with open(sys.argv[2], "r") as f:
        data = f.read()
        try:
            arbre = parser.parse(lexer.tokenize(data))
            gen_programme(arbre)
        except EOFError:
            exit(1)