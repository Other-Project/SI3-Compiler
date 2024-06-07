import sys
import arbre_abstrait
from prettytable import PrettyTable, SINGLE_BORDER


types = {
    "entier": arbre_abstrait.Integer,
    "booleen": arbre_abstrait.Boolean,
    "vide": None,
}

print_builtins = False


def log(s):
    print("Table des symboles:", s, file=sys.stderr)

def erreur(s):
    print("Erreur:", s, file=sys.stderr)
    exit(1)

def typeStr(type):
    return "|".join(type) if isinstance(type, list) else type

class TableSymboles:
    def __init__(self):
        self._builtins = {
            "lire": {"type": "entier", "args": []},
            "ecrire": {"type": "vide", "args": [["entier", "booleen"]]},
        }
        self._symbols = {}

    def add(self, declaration):
        def retrieveArgs():
            args = []
            if declaration.declarationArgs:
                for decl in declaration.declarationArgs.declarations:
                    if decl.type not in types.keys():
                        erreur(f"invalid type {decl.type}")
                    args.append(decl.type)
            return args

        if type(declaration) not in [
            arbre_abstrait.DeclarationFunction,
            arbre_abstrait.Declaration,
        ]:
            return
        if declaration.type not in types.keys():
            erreur(f"invalid type {declaration.type}")
        if self.has(declaration.name):
            erreur(f"Name already used {declaration.name}")
        self._symbols[declaration.name] = {
            "type": declaration.type,
            "args": retrieveArgs(),
        }

    def returnType(self, name):
        symbol = self._symbols[name] or self._builtins[name]
        if not symbol:
            erreur(f"Symbol {name} not found")
        return types[symbol["type"]]

    def checkArgsType(self, name, args):
        symbol = self._symbols[name] or self._builtins[name]
        if not symbol:
            erreur(f"Symbol {name} not found")
        argsTypes = symbol["args"]
        if len(argsTypes) != len(args):
            erreur(f"Incorrect number of arguments, expected {len(argsTypes)} got {len(args)}")
        for type, arg in zip(argsTypes, args):
            argTypes = type if isinstance(type, list) else [type]
            if arg not in [types[t] for t in argTypes]:
                self.erreur(f"Incorrect argument type, expected {typeStr(type)} got {arg}")

    def has(self, name):
        return name in self._symbols

    def _getRow(self, name, value):
        args = value["args"]
        return [name, value["type"], f"{len(args)}*4={len(args)*4}", ", ".join([typeStr(arg) for arg in args])]

    def __str__(self) -> str:
        table = PrettyTable()
        table.set_style(SINGLE_BORDER)
        table.field_names = ["Name", "Type", "Memory", "Args"]
        if print_builtins:
            for name, value in self._builtins.items():
                table.add_row(self._getRow(name, value))
            table._dividers[-1] = True
        for name, value in self._symbols.items():
            table.add_row(self._getRow(name, value))
        return str(table)
