import sys
import arbre_abstrait
from prettytable import PrettyTable


types = {
	"entier": arbre_abstrait.Integer,
	"booleen": arbre_abstrait.Boolean
}

class TableSymboles:
    def __init__(self):
        self.typeIdentifier = {}

    def log(s):
        print("Table des symboles:", s, file=sys.stderr)

    def erreur(s):
        print("Erreur:", s, file=sys.stderr)
        exit(1)

    def add(self, declaration):
        if type(declaration) not in [arbre_abstrait.DeclarationFunction, arbre_abstrait.Declaration]:
            return
        if declaration.type not in types.keys():
            erreur(f"invalid type {declaration.type}")
        if self.has(declaration.name):
            erreur(f"Name already used {declaration.name}")
        self.typeIdentifier[declaration.name] = declaration.type

    def get(self, name):
        return types[self.typeIdentifier[name]]

    def has(self, name):
        return name in self.typeIdentifier

    def __str__(self) -> str:
        table = PrettyTable()
        table.field_names = ["Name", "Type"]
        table.add_rows(self.typeIdentifier.items())
        return str(table)
