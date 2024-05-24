import sys
from sly import Parser
from analyse_lexicale import FloLexer
import arbre_abstrait


class FloParser(Parser):
    # On récupère la liste des lexèmes de l'analyse lexicale
    tokens = FloLexer.tokens

    # Règles gramaticales et actions associées

    debugfile = "parser.out"

    @_("instructions")
    def prog(self, p):
        return arbre_abstrait.Program(p.instructions)

    @_('IF "(" expr ")" "{" instructions "}"')
    def condition(self, p):
        return arbre_abstrait.If(p.expr, p.instructions)

    @_("condition")
    def condition_elseif(self, p):
        return p.condition

    @_("condition_elseif ELSE condition")
    def condition_elseif(self, p):
        p.condition_elseif.elseList.append(arbre_abstrait.Else(p.condition))
        return p.condition_elseif

    @_("condition_elseif")
    def condition_else(self, p):
        return p.condition_elseif

    @_('condition_elseif ELSE "{" instructions "}"')
    def condition_else(self, p):
        p.condition_elseif.elseList.append(arbre_abstrait.Else(p.instructions))
        return p.condition_elseif

    @_('instruction ";"')
    def instructions(self, p):
        l = arbre_abstrait.Instructions()
        l.instructions.insert(0, p.instruction)
        return l

    @_("condition_else")
    def instructions(self, p):
        l = arbre_abstrait.Instructions()
        l.instructions.insert(0, p.condition_else)
        return l

    @_('instruction ";" instructions')
    def instructions(self, p):
        p.instructions.instructions.insert(0, p.instruction)
        return p.instructions

    @_('condition_else ";" instructions')
    def instructions(self, p):
        p.instructions.instructions.insert(0, p.instruction)
        return p.instructions
		  
    @_('function')
    def instruction(self,p):
        return p.function

    @_('IDENTIFIANT "(" args ")"')
    def function(self, p):
        return arbre_abstrait.Function(p.IDENTIFIANT, p.args)

    @_('expr')
    def args(self,p):
        a = arbre_abstrait.Args()
        a.listArgs.append(p.expr)
        return a

    @_('expr "," args')
    def args(self,p):
        p.args.listArgs.insert(0,p.expr)
        return p.args

    @_('function')
    def args(self, p):
        return p.function

# mafonction(mafonction(5,3),2)
    @_('function "," args')
    def args(self,p):
        p.args.listArgs.insert(0,p.function)
        return p.args

    @_('TYPE IDENTIFIANT "=" expr')
    def instruction(self, p):
        return arbre_abstrait.Declaration(p.TYPE, p.IDENTIFIANT, p.expr)

    @_("TYPE IDENTIFIANT")
    def instruction(self, p):
        return arbre_abstrait.Declaration(p.TYPE, p.IDENTIFIANT)

    @_('IDENTIFIANT "=" expr')
    def instruction(self, p):
        return arbre_abstrait.Assignment(p.IDENTIFIANT, p.expr)

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
    )
    def boolean(self, p):
        return arbre_abstrait.Operation(p[1], p[0], p[2])

    @_("BOOLEAN")
    def boolean(self, p):
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
