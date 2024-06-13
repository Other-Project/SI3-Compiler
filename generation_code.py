import argparse
import sys
import textwrap
from analyse_lexicale import FloLexer
from analyse_syntaxique import FloParser
import arbre_abstrait
from table_des_symboles import TableSymboles

num_etiquette_courante = -1  # Permet de donner des noms différents à toutes les étiquettes (en les appelant e0, e1,e2,...)

afficher_table = False
print_builtins = False
output = None

tableSymboles = TableSymboles()


def erreur(s, line=None):
    """affiche une erreur sur la sortie stderr et quitte le programme"""
    print(f"Error (l{line}):" if line else "Error:", s, file=sys.stderr)
    exit(1)


def printifm(*args, **kwargs):
    """
    Un print qui ne fonctionne que si la variable.flo afficher_table vaut Vrai.
    (permet de choisir si on affiche le code assembleur ou la table des symboles)
    """
    if output:
        print(*args, **kwargs, file=output)


def printift(*args, **kwargs):
    """
    Un print qui ne fonctionne que si la variable.flo afficher_table vaut Vrai.
    (permet de choisir si on affiche le code assembleur ou la table des symboles)
    """
    if afficher_table:
        print(*args, **kwargs)


def typeStr(t):
    """Converti un type en une chaîne de caractères"""
    if isinstance(t, type):
        return t.__name__
    elif isinstance(t, list):
        return "|".join([typeStr(_t) for _t in t])
    elif isinstance(t, str):
        return t
    else:
        return str(t)


def arm_comment(comment):
    """Fonction locale, permet d'afficher un commentaire dans le code arm."""
    if comment != "":
        printifm("\t\t @ " + comment)  # le point virgule indique le début d'un commentaire en ARM. Les tabulations sont là pour faire jolie.
    else:
        printifm("")


def arm_instruction(opcode, op1="", op2="", op3="", comment=""):
    """
    Affiche une instruction ARM sur une ligne
    Par convention, les derniers opérandes sont nuls si l'opération a moins de 3 arguments.
    """
    if op2 == "":
        printifm("\t" + opcode + "\t" + op1 + "\t\t", end="")
    elif op3 == "":
        printifm("\t" + opcode + "\t" + op1 + ",\t" + op2 + "\t", end="")
    else:
        printifm("\t" + opcode + "\t" + op1 + ",\t" + op2 + ",\t" + op3, end="")
    arm_comment(comment)


def arm_nouvelle_etiquette():
    """
    Retourne le nom d'une nouvelle étiquette
    """
    global num_etiquette_courante
    num_etiquette_courante += 1
    return ".e" + str(num_etiquette_courante)


def gen_programme(programme: arbre_abstrait.Program):
    """
    Affiche le code arm correspondant à tout un programme
    """

    header = textwrap.dedent(
        """\
        .global __aeabi_idiv
        .global __aeabi_idivmod
        .boolean_or:
        	mov r0,	#1
        	bx lr
        .boolean_not:
        	mov r0,	#0
        	bx lr
        .LC0:
        	.ascii	"%d\\000"
        	.align	2
        .LC1:
        	.ascii	"%d\\012\\000"
        	.text
        	.align	2
        	.global	main
        """
    )
    printifm(header)

    if programme.listeFunctions:
        for function in programme.listeFunctions.functions:
            tableSymboles.add(function)
        printift(tableSymboles)

        arm_comment("functions")
        for function in programme.listeFunctions.functions:
            gen_def_fonction(function)

    printifm("main:")
    arm_instruction("push", "{fp,lr}")
    arm_instruction("add", "fp", "sp", "#4")

    gen_listeInstructions(programme.listeInstructions)

    arm_instruction("mov", "r0", "#0")
    arm_instruction("pop", "{fp, pc}")


def gen_def_fonction(f: arbre_abstrait.DeclarationFunction):
    tableSymboles.enterFunction(f)
    printifm(f"_{f.name}:")
    arm_instruction("push", "{fp,lr}")
    arm_instruction("add", "fp", "sp", "#4")
    gen_listeInstructions(f.instructions, False)
    tableSymboles.quitFunction()


def gen_listeInstructions(listeInstructions: arbre_abstrait.Instructions, deallocate=True):
    """Affiche le code arm correspondant à une suite d'instructions"""
    tableSymboles.enterBlock(deallocate)
    for instruction in listeInstructions.instructions:
        gen_instruction(instruction)
    removed = tableSymboles.quitBlock(deallocate)
    if deallocate:
        arm_instruction("add", "sp", f"#{len(removed)*4}")


def gen_instruction(instruction):
    """Affiche le code arm correspondant à une instruction"""
    if type(instruction) == arbre_abstrait.Function:
        return gen_function(instruction)
    elif type(instruction) in [arbre_abstrait.While, arbre_abstrait.If]:
        gen_block_operation(instruction)
    elif type(instruction) == arbre_abstrait.Return:
        gen_return(instruction)
    elif type(instruction) == arbre_abstrait.Declaration:
        gen_def_variable(instruction)
    elif type(instruction) == arbre_abstrait.Assignment:
        gen_assign_variable(instruction)
    else:
        erreur("génération type instruction non implémenté " + typeStr(type(instruction)))
    return None


def gen_function(instruction):
    inProgram, inBuiltins = tableSymboles.has(instruction.fct)
    if not inProgram and not inBuiltins:
        erreur(f"Unknown function {instruction.fct}")
    else:
        args = instruction.args.listArgs if instruction.args else []
        argsType = [gen_expression(arg) for arg in args]
        tableSymboles.checkArgsType(instruction.fct, argsType)
        if inProgram:
            arm_instruction("bl", f"_{instruction.fct}")
            arm_instruction("add", "sp", f"#{tableSymboles.memory(instruction.fct)}")
        else:
            if instruction.fct == "lire":
                gen_lire()
            elif instruction.fct == "ecrire":
                gen_ecrire(instruction)
            else:
                erreur(f"Builtin function not found {instruction.fct}")
    return tableSymboles.returnType(instruction.fct)


def gen_return(instruction):
    function = tableSymboles.getFunction()
    if not function:
        erreur("Return keyword is only valid inside a function")
    returnType = gen_expression(instruction.exp)
    expectedType = tableSymboles.returnType(function)
    if returnType != expectedType:
        erreur(f"Incorrect return type expected {typeStr(expectedType)} got {typeStr(returnType)}")
    arm_instruction("pop", "{r2}", comment="Return value")
    removed = list(filter(lambda symbol: tableSymboles._symbols[symbol].get("depth", 0) >= tableSymboles._depth, tableSymboles._symbols))
    arm_instruction("add", "sp", f"#{len(removed)*4}")
    arm_instruction("pop", "{fp, pc}")


def gen_ecrire(ecrire):
    """Affiche le code arm correspondant au fait d'envoyer la valeur entière d'une expression sur la sortie standard"""
    arm_instruction("pop", "{r1}")  # on dépile la valeur d'expression sur r1
    arm_instruction("ldr", "r0", "=.LC1")
    arm_instruction("bl", "printf")  # on envoie la valeur de r1 sur la sortie standard


def gen_lire():
    """
    Affiche le code arm correspondant au fait de mettre en pause le programme, et permet à l’utilisateur d’entrée au clavier une chaîne
    de caractère qui est interprétée comme un entier.
    """
    arm_instruction("ldr", "r0", "=.LC0", comment="Charge l’adresse de la chaîne de format pour scanf dans r0")
    arm_instruction("sub", "sp", "sp", "#4", comment="Réserve de l’espace sur la pile pour stocker l’entier lu (on fait sp = sp -4)")
    arm_instruction("movs", "r1", "sp", comment="Copie l’adresse de cet espace dans r1")
    arm_instruction("bl", "scanf", comment="Lance scanf pour lire l’entier et le stocker à l’adresse spécifiée par r1")
    arm_instruction("pop", "{r2}", comment="Dépiler l'input dans r2")


def gen_block_operation(instruction: arbre_abstrait.While | arbre_abstrait.If):
    endTrue = arm_nouvelle_etiquette()
    ifFalse = arm_nouvelle_etiquette()

    if type(instruction) == arbre_abstrait.While:
        arm_instruction(f"{endTrue}:", comment="true condition jump")
    conditionType = gen_expression(instruction.cond)
    if conditionType != arbre_abstrait.Boolean:
        erreur(f"Wrong condition type, expected {typeStr(arbre_abstrait.Boolean)}, got {typeStr(conditionType)}")
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


def gen_def_variable(instruction: arbre_abstrait.Declaration):
    tableSymboles.add(instruction)
    declaredType = tableSymboles.returnType(instruction.name)
    if instruction.value:
        valType = gen_expression(instruction.value)
        if valType != declaredType:
            erreur(f"Type mismatch, declared {typeStr(declaredType)}, assigned {typeStr(valType)}")
    else:
        arm_instruction("mov", "r2", f"#{declaredType.DEFAULT_VALUE}", comment="Default value")
        arm_instruction("push", "{r2}", comment=f"Assign newly declared variable {instruction.name}")


def get_memory_accessor(address):
    if address > 0:
        return f"[fp, #{address}]"
    return f"[fp, #{-8 + address}]"
    """spAddress = tableSymboles._address
    return f"[sp, #{(address - spAddress)}]"""


def gen_assign_variable(instruction: arbre_abstrait.Assignment):
    inProgram, _ = tableSymboles.has(instruction.variable)
    if not inProgram:
        erreur(f"Unknown variable {instruction.variable}")
    valueType = gen_expression(instruction.value)
    expectedType = tableSymboles.returnType(instruction.variable)
    if valueType != expectedType:
        erreur(f"Invalid assignment, expected type {typeStr(expectedType)}, got {typeStr(valueType)}")
    offset = tableSymboles.address(instruction.variable)
    arm_instruction("pop", "{r2}")
    arm_instruction("str", "r2", get_memory_accessor(offset), comment=f"Assign {instruction.variable}")
    return tableSymboles.returnType(instruction.variable)


def gen_expression(expression):
    """Affiche le code arm pour calculer et empiler la valeur d'une expression"""
    if type(expression) == arbre_abstrait.Function:
        instType = gen_instruction(expression)
        arm_instruction("push", "{r2}")
        return instType
    elif type(expression) == arbre_abstrait.Operation:
        return gen_operation(expression)
    elif type(expression) == arbre_abstrait.Variable:
        return gen_variable(expression)
    elif type(expression) == arbre_abstrait.Integer:
        arm_instruction("mov", "r1", "#" + str(expression.valeur))
        arm_instruction("push", "{r1}")
    elif type(expression) == arbre_abstrait.Boolean:
        arm_instruction("mov", "r1", "#" + str(1 if expression.valeur else 0))
        arm_instruction("push", "{r1}")
    else:
        erreur("type d'expression inconnu " + typeStr(type(expression)))
    return type(expression)


def gen_variable(variable):
    inProgram, _ = tableSymboles.has(variable.valeur)
    if not inProgram:
        erreur(f"Unknown variable {variable.valeur}")
    offset = tableSymboles.address(variable.valeur)
    arm_instruction("ldr", "r2", get_memory_accessor(offset), comment=f"Retrieve {variable.valeur}")
    arm_instruction("push", "{r2}", comment=f"Stack {variable.valeur}")
    return tableSymboles.returnType(variable.valeur)


def gen_operation(operation):
    """Affiche le code arm pour calculer l'opération et la mettre en haut de la pile"""
    op = operation.op

    type1 = gen_expression(operation.exp1)  # on calcule et empile la valeur de exp1

    if operation.exp2:
        type2 = gen_expression(operation.exp2)  # on calcule et empile la valeur de exp2
        if type1 != type2:
            erreur(f"Types incompatibles {typeStr(type1)} != {typeStr(type2)}")
        arm_instruction("pop", "{r1}", comment="dépile exp2 dans r1")

    arm_instruction("pop", "{r0}", comment="dépile exp1 dans r0")

    comparisons = {"==": "EQ", "!=": "NE", "<=": "LE", ">=": "GE", "<": "LT", ">": "GT"}
    if type1 == arbre_abstrait.Integer and gen_operation_integer(op):
        True  # do nothing
    elif type1 == arbre_abstrait.Boolean and gen_operation_boolean(op):
        True  # do nothing
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
        type1 = arbre_abstrait.Boolean
    else:
        erreur(f'operateur "{op}" non implémenté pour le type {typeStr(type1)}')
    arm_instruction("push", "{r0}", comment="empile le résultat")
    return type1


def gen_operation_integer(op):
    code = {
        "+": "add",
        "*": "mul",
    }  # Un dictionnaire qui associe à chaque opérateur sa fonction arm
    # Voir: https://developer.arm.com/documentation/dui0497/a/the-cortex-m0-instruction-set/instruction-set-summary?lang=en

    if op in code.keys():
        arm_instruction(code[op], "r0", "r1", "r0", comment=f"effectue l'opération r0 {op} r1 et met le résultat dans r0")
    elif op == "-":
        arm_instruction("sub", "r0", "r0", "r1", comment=f"effectue l'opération r0 {op} r1 et met le résultat dans r0")
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
        arm_instruction("mul", "r0", "r1", "r0", comment=f"effectue l'opération r0 {op} r1 et met le résultat dans r0")
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
    argParser = argparse.ArgumentParser(description="Generate assembly code from flo script", formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))
    argParser.add_argument("filename")
    argParser.add_argument("-o", "--output", action="store", help="Destination file")
    argParser.add_argument("-arm", "--arm", action="store_true", help="Generate ARM assembly")
    argParser.add_argument("-t", "-table", "--table", action="store_true", help="Display the symbol table")
    argParser.add_argument("--builtins", action="store_true", help="Display builtins in the symbol tables")
    args = argParser.parse_args()
    afficher_table = args.table
    print_builtins = args.builtins

    lexer = FloLexer()
    parser = FloParser()
    with open(args.filename, "r") as f:
        if args.arm:
            output = open(args.output, "w") if args.output else sys.stdout
        data = f.read()

        try:
            arbre = parser.parse(lexer.tokenize(data))
            gen_programme(arbre)
        except EOFError:
            exit(1)
        finally:
            if output:
                output.close()
