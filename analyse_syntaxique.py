import sys
from sly import Parser
from analyse_lexicale import FloLexer
import arbre_abstrait


class FloParser(Parser):
    # On récupère la liste des lexèmes de l'analyse lexicale
    tokens = FloLexer.tokens

    # Règles gramaticales et actions associées

    debugfile = 'parser.out'

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

    @_('IDENTIFIANT "(" expr ")"')
    def instruction(self, p):
        return arbre_abstrait.Function(p.IDENTIFIANT, p.expr)  # p.expr = p[2]

    @_('TYPE IDENTIFIANT "=" expr')
    def instruction(self, p):
        return p.expr

    @_(
        'expr "+" produit',
        'expr "-" produit',
    )
    def expr(self, p):
        return arbre_abstrait.Operation(p[1], p[0], p[2])
    
    @_('produit')
    def expr(self, p):
        return p.produit
    
    @_('factor')
    def produit(self, p):
        return p.factor
    
    @_('produit "*" factor')
    def produit(self, p):
        return arbre_abstrait.Operation('*', p[0], p[2])
    
    @_('produit "/" factor')
    def produit(self, p):
        return arbre_abstrait.Operation('/', p[0], p[2])
    
    @_('produit "%" factor')
    def produit(self, p):
        return arbre_abstrait.Operation('%', p[0], p[2])

    @_('"(" expr ")"')
    def factor(self, p):
        return p.expr
    
    @_("INTEGER")
    def factor(self, p):
        return arbre_abstrait.Integer(p.INTEGER)

    @_("boolean")
    def expr(self, p):
        return p.boolean

    @_("BOOLEAN")
    def boolean(self, p):
        return arbre_abstrait.Boolean(p.BOOLEAN)

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
