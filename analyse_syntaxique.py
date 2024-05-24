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

    @_('instruction ";"')
    def instructions(self, p):
        l = arbre_abstrait.Instructions()
        l.instructions.append(p.instruction)
        return l

    @_('instruction ";" instructions')
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
        return p.expr

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

    @_("boolean")
    def expr(self, p):
        return p.boolean

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
#
#    @_("expr")
#    def args(self, p):
 #       return arbre_abstrait.Args(p.expr)

   # @_("args, expr")
  #  def args(self,p):
    #    p.args.append(p.expr)
     #   return arbre_abstrait.Args(p.args)

#    @_('IN "(" expr ")" ')
 #   def function_name(self,p):
  #      return arbre_abstrait.Function(p.function_name, p.expr)

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
