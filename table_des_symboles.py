import sys
import arbre_abstrait
from prettytable import PrettyTable

class TableSymboles:
    def __init__(self):
        self.typeIdentifier = {}

    def log(s):
        print("Table des symboles:", s, file=sys.stderr)

    def erreur(s):
        print("Erreur:", s, file=sys.stderr)
        exit(1)

    def add(self, declaration):
        if (type(declaration) in [arbre_abstrait.DeclarationFunction, arbre_abstrait.Declaration]):
            #self.erreur(f"{type(declaration)} n'est pas implementé pour la table des symboles")
            self.typeIdentifier[declaration.name] = declaration.type

    def __str__(self) -> str:
        table = PrettyTable()
        table.field_names = ["Name", "Type"]
        table.add_rows(self.typeIdentifier.items())
        return str(table)

    
