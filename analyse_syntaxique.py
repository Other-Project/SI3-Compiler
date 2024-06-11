import sys
from sly import Parser
from analyse_lexicale import FloLexer
import arbre_abstrait


class FloParser(Parser):

    if __name__ == "__main__":
        debugfile = "parser.out"

    # On récupère la liste des lexèmes de l'analyse lexicale
    tokens = FloLexer.tokens

    # Règles gramaticales et actions associées

    @_("instructions")
    def prog(self, p):
        return arbre_abstrait.Program(p.instructions)

    @_("functions instructions")
    def prog(self, p):
        return arbre_abstrait.Program(p.instructions, p.functions)

    @_('IF "(" expr ")" "{" instructions "}" condition_else')
    def condition(self, p):
        return arbre_abstrait.If(p.expr, p.instructions, p.condition_else)

    @_("")
    def condition_else(self, p):
        pass

    @_("ELSE condition")
    def condition_else(self, p):
        return arbre_abstrait.Else(arbre_abstrait.Instructions([p.condition]))

    @_('ELSE "{" instructions "}"')
    def condition_else(self, p):
        return arbre_abstrait.Else(p.instructions)

    @_('WHILE "(" expr ")" "{" instructions "}"')
    def while_loop(self, p):
        return arbre_abstrait.While(p.expr, p.instructions)

    @_("condition", "while_loop")
    def block_operator(self, p):
        return p[0]

    @_('instruction ";" instructions')
    def instructions(self, p):
        p.instructions.instructions.insert(0, p.instruction)
        return p.instructions

    @_("block_operator instructions")
    def instructions(self, p):
        p.instructions.instructions.insert(0, p.block_operator)
        return p.instructions

    @_("")
    def instructions(self, p):
        return arbre_abstrait.Instructions()

    @_("function")
    def variable(self, p):
        return p.function

    @_("function")
    def instruction(self, p):
        return p.function

    @_("declarationFunction")
    def functions(self, p):
        l = arbre_abstrait.Functions()
        l.functions.insert(0, p.declarationFunction)
        return l

    @_("functions declarationFunction")
    def functions(self, p):
        p.functions.append(p.declarationFunction)
        return p.functions

    @_('IDENTIFIANT "(" args ")"')
    def function(self, p):
        return arbre_abstrait.Function(p.IDENTIFIANT, p.args)

    @_('TYPE IDENTIFIANT "(" declarationArgs ")" "{" instructions "}"')
    def declarationFunction(self, p):
        return arbre_abstrait.DeclarationFunction(p.TYPE, p.IDENTIFIANT, p.instructions, p.declarationArgs)

    @_("")
    def args(self, p):
        pass

    @_("expr")
    def args(self, p):
        a = arbre_abstrait.Args()
        a.listArgs.append(p.expr)
        return a

    @_('expr "," args')
    def args(self, p):
        p.args.listArgs.insert(0, p.expr)
        return p.args

    @_('TYPE IDENTIFIANT "," declarationArgs')
    def declarationArgs(self, p):
        declaration = arbre_abstrait.Declaration(p.TYPE, p.IDENTIFIANT)
        p.declarationArgs.declarations.insert(0, declaration)
        return p.declarationArgs

    @_("TYPE IDENTIFIANT")
    def declarationArgs(self, p):
        a = arbre_abstrait.ArgsDeclaration()
        declaration = arbre_abstrait.Declaration(p.TYPE, p.IDENTIFIANT)
        a.declarations.append(declaration)
        return a

    @_("")
    def declarationArgs(self, p):
        pass

    @_('TYPE IDENTIFIANT "=" expr')
    def instruction(self, p):
        return arbre_abstrait.Declaration(p.TYPE, p.IDENTIFIANT, p.expr)

    @_("TYPE IDENTIFIANT")
    def instruction(self, p):
        return arbre_abstrait.Declaration(p.TYPE, p.IDENTIFIANT)

    @_('IDENTIFIANT "=" expr')
    def instruction(self, p):
        return arbre_abstrait.Assignment(p.IDENTIFIANT, p.expr)

    @_("RETURN expr")
    def instruction(self, p):
        return arbre_abstrait.Return(p.expr)

    @_("somme")
    def boolean(self, p):
        return p.somme

    @_('somme "+" produit', 'somme "-" produit')
    def somme(self, p):
        return arbre_abstrait.Operation(p[1], p[0], p[2])

    @_("produit")
    def somme(self, p):
        return p.produit

    @_("factor")
    def produit(self, p):
        return p.factor

    @_('"-" factor')
    def produit(self, p):
        return arbre_abstrait.Operation("*", arbre_abstrait.Integer(-1), p.factor)

    @_('produit "*" factor', 'produit "/" factor', 'produit "%" factor')
    def produit(self, p):
        return arbre_abstrait.Operation(p[1], p[0], p[2])

    @_("variable")
    def factor(self, p):
        return p.variable

    @_("IDENTIFIANT")
    def variable(self, p):
        return arbre_abstrait.Variable(p.IDENTIFIANT)

    @_('"(" expr ")"')
    def factor(self, p):
        return p.expr

    @_("INTEGER")
    def factor(self, p):
        return arbre_abstrait.Integer(p.INTEGER)

    @_("b_or")
    def expr(self, p):
        return p.b_or

    @_(
        'somme "<" somme',
        'somme ">" somme',
        "somme EQ somme",
        "somme LE somme",
        "somme GE somme",
        "somme NE somme",
        "boolean_value EQ boolean_value",
        "boolean_value NE boolean_value",
    )
    def boolean(self, p):
        return arbre_abstrait.Operation(p[1], p[0], p[2])

    @_("boolean_value")
    def boolean(self, p):
        return p.boolean_value

    @_("BOOLEAN")
    def boolean_value(self, p):
        return arbre_abstrait.Boolean(p.BOOLEAN)

    @_("b_and OR b_or")
    def b_or(self, p):
        return arbre_abstrait.Operation(p[1], p[0], p[2])

    @_("b_and")
    def b_or(self, p):
        return p.b_and

    @_("b_not AND b_and")
    def b_and(self, p):
        return arbre_abstrait.Operation(p[1], p[0], p[2])

    @_("b_not")
    def b_and(self, p):
        return p.b_not

    @_("NOT boolean")
    def b_not(self, p):
        return arbre_abstrait.Operation(p.NOT, p.boolean)

    @_("boolean")
    def b_not(self, p):
        return p.boolean

    def error(self, p):
        print("Erreur de syntaxe", p, file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    lexer = FloLexer()
    parser = FloParser()
    if len(sys.argv) < 2:
        print("usage: python3 analyse_syntaxique.py NOM_FICHIER_SOURCE.flo")
    else:
        with open(sys.argv[1], "r") as f:
            data = f.read()
            try:
                arbre = parser.parse(lexer.tokenize(data))
                arbre.afficher()
            except EOFError:
                exit(1)
