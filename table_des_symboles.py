import sys
import arbre_abstrait
from prettytable import PrettyTable, SINGLE_BORDER

if __name__ == "__main__":
	print("Call generation_code.py instead")
	exit(1)

import __main__ as gen_code


types = {
    "entier": arbre_abstrait.Integer,
    "booleen": arbre_abstrait.Boolean,
    "vide": None,
}


class TableSymboles:
    def __init__(self):
        self._builtins = {
            "lire": {"type": "entier", "args": []},
            "ecrire": {"type": "vide", "args": [["entier", "booleen"]]},
        }
        self._symbols = {}
        self._address = 0
        self._depth = 0

    def add(self, declaration):
        if declaration.type not in types.keys():
            erreur(f"invalid type {declaration.type}")
        if self.has(declaration.name)[0]:
            erreur(f"Name already used {declaration.name}")

        if type(declaration) == arbre_abstrait.DeclarationFunction:
            self._symbols[declaration.name] = {
                "args": (
                    [decl.type for decl in declaration.declarationArgs.declarations]
                    if declaration.declarationArgs
                    else []
                )
            }
        elif type(declaration) == arbre_abstrait.Declaration:
            self._address += 4
            self._symbols[declaration.name] = {
                "address": self._address,
                "depth": self._depth,
            }
        else:
            erreur(f"Unknown declaration type {type(declaration).__name__}")
        self._symbols[declaration.name]["type"] = declaration.type

    def remove(self, symbol):
        if symbol not in self._symbols:
            erreur(f"Symbol {symbol} not found")
        if "args" in self._symbols[symbol]:
            erreur(f"Cannot remove, it's a function")
        self._symbols.pop(symbol)
        self._address -= 4

    def enterFunction(self, function):
        self._depth += 1
        if function.declarationArgs:
            for decl in function.declarationArgs.declarations:
                self.add(decl)
        gen_code.printift(f"Entered '{function.name}'\n{self}")

    def quitFunction(self, function):
        for symbol in list(
            filter(
                lambda symbol: self._symbols[symbol].get("depth", 0) >= self._depth,
                self._symbols,
            )
        ):
            self.remove(symbol)
        self._depth -= 1
        gen_code.printift(f"Quitted '{function.name}'\n{self}")

    def returnType(self, name):
        symbol = self._symbols.get(name, self._builtins.get(name, None))
        if not symbol:
            erreur(f"Symbol {name} not found")
        return types[symbol["type"]]

    def checkArgsType(self, name, args):
        symbol = self._symbols.get(name, self._builtins.get(name, None))
        if not symbol:
            erreur(f"Symbol {name} not found")
        argsTypes = symbol["args"]
        if len(argsTypes) != len(args):
            erreur(
                f"Incorrect number of arguments, expected {len(argsTypes)} got {len(args)}"
            )
        for type, arg in zip(argsTypes, args):
            argTypes = type if isinstance(type, list) else [type]
            if arg not in [types[t] for t in argTypes]:
                erreur(f"Incorrect argument type, expected {gen_code.typeStr(type)} got {arg}")

    def address(self, name):
        symbol = self._symbols.get(name, self._builtins.get(name, None))
        if not symbol:
            erreur(f"Symbol {name} not found")
        if "args" in symbol:
            erreur(f"{name} is a function")
        return symbol["address"]

    def has(self, name):
        return (name in self._symbols, name in self._builtins)

    def _getRow(self, name, value):
        args = value.get("args", None)
        return [
            name,
            value["type"],
            f"{len(args)}*4={len(args)*4}" if args else "/",
            ", ".join([gen_code.typeStr(arg) for arg in args]) if args else "/",
            value.get("address", "/"),
            value.get("depth", "/"),
        ]

    def __str__(self) -> str:
        table = PrettyTable()
        table.set_style(SINGLE_BORDER)
        table.field_names = ["Name", "Type", "Memory", "Args", "Address", "Depth"]
        if gen_code.print_builtins:
            for name, value in self._builtins.items():
                table.add_row(self._getRow(name, value))
            table._dividers[-1] = True
        for name, value in self._symbols.items():
            table.add_row(self._getRow(name, value))
        return str(table)
