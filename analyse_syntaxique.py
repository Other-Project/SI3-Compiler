import sys
from sly import Parser
from analyse_lexicale import FloLexer
import arbre_abstrait


class FloParser(Parser):
    # On récupère la liste des lexèmes de l'analyse lexicale
    tokens = FloLexer.tokens

    # Règles gramaticales et actions associées

    debugfile = 'parser.out'

    @_("listeInstructions")
    def prog(self, p):
        return arbre_abstrait.Program(p[0])

    @_("instruction")
    def listeInstructions(self, p):
        l = arbre_abstrait.Instructions()
        l.instructions.append(p[0])
        return l

    @_("instruction listeInstructions")
    def listeInstructions(self, p):
        p[1].instructions.insert(0, p[0])
        return p[1]

    @_('expr ";"')
    def instruction(self, p):
        return p.expr

    @_('IDENTIFIANT "(" expr ")"')
    def expr(self, p):
        return arbre_abstrait.Function(p.IDENTIFIANT, p.expr)  # p.expr = p[2]

    @_(
        'expr "+" expr',
        'expr "-" expr',
        'expr "*" expr',
        'expr "/" expr',
        'expr "%" expr',
    )
    def expr(self, p):
        return arbre_abstrait.Operation(p[1], p[0], p[2])

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr  # ou p[1]

    @_("INTEGER")
    def expr(self, p):
        return arbre_abstrait.Integer(p.INTEGER)

    @_("BOOLEAN")
    def expr(self, p):
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
