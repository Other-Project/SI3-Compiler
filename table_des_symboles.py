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
        self._function = None

    def add(self, declaration:arbre_abstrait.Declaration|arbre_abstrait.DeclarationFunction):
        if declaration.type not in types.keys():
            gen_code.erreur(f"invalid type {declaration.type}")
        if any(self.has(declaration.name)):
            gen_code.erreur(f"Name already used {declaration.name}")

        if type(declaration) == arbre_abstrait.DeclarationFunction:
            self._symbols[declaration.name] = {"args": ([decl.type for decl in declaration.declarationArgs.declarations] if declaration.declarationArgs else [])}
        elif type(declaration) == arbre_abstrait.Declaration:
            self._symbols[declaration.name] = {
                "address": self._address,
                "depth": self._depth,
            }
            self._address -= 4
        else:
            gen_code.erreur(f"Unknown declaration type {type(declaration).__name__}")
        self._symbols[declaration.name]["type"] = declaration.type

    def remove(self, symbol: str):
        if symbol not in self._symbols:
            gen_code.erreur(f"Symbol {symbol} not found")
        if "args" in self._symbols[symbol]:
            gen_code.erreur(f"Cannot remove, it's a function")
        self._symbols.pop(symbol)
        self._address += 4

    def enterFunction(self, function: arbre_abstrait.DeclarationFunction):
        self.enterBlock(False)
        self._function = function.name
        self._address += self.memory(self._function)
        if function.declarationArgs:
            for decl in function.declarationArgs.declarations:
                self.add(decl)
        gen_code.printift(f"Entered '{function.name}'\n{self}")

    def quitFunction(self):
        removed = self.quitBlock(False)
        gen_code.printift(f"Quitted '{self._function}'\n{self}")
        self._address -= self.memory(self._function)
        self._function = None
        return removed

    def enterBlock(self, print=True):
        self._depth += 1
        if print:
            gen_code.printift(f"Entering depth {self._depth}\n{self}")

    def quitBlock(self, print=True):
        if print:
            gen_code.printift(f"Quitting depth {self._depth}\n{self}")
        toRemove = list(filter(lambda symbol: self._symbols[symbol].get("depth", 0) >= self._depth, self._symbols))
        for symbol in toRemove:
            self.remove(symbol)
        if print:
            gen_code.printift(f"Quitted depth {self._depth}\n{self}")
        self._depth -= 1
        return toRemove

    def getFunction(self):
        return self._function

    def _get_symbol(self, name: str):
        symbol = self._symbols.get(name, self._builtins.get(name, None))
        if not symbol:
            gen_code.erreur(f"Symbol {name} not found")
        return symbol

    def returnType(self, name: str):
        return types[self._get_symbol(name)["type"]]

    def checkArgsType(self, name: str, args):
        argsTypes = self._get_symbol(name)["args"]
        if len(argsTypes) != len(args):
            gen_code.erreur(f"Incorrect number of arguments, expected {len(argsTypes)} got {len(args)}")
        for type, arg in zip(argsTypes, args):
            argTypes = type if isinstance(type, list) else [type]
            if arg not in [types[t] for t in argTypes]:
                gen_code.erreur(f"Incorrect argument type, expected {gen_code.typeStr(type)} got {gen_code.typeStr(arg)}")

    def address(self, name: str):
        symbol = self._get_symbol(name)
        if "args" in symbol:
            gen_code.erreur(f"{name} is a function")
        return symbol["address"]

    def memory(self, name: str):
        symbol = self._get_symbol(name)
        if "args" not in symbol:
            gen_code.erreur(f"{name} isn't a function")
        return len(symbol["args"]) * 4

    def has(self, name: str):
        return (name in self._symbols, name in self._builtins)

    def _getRow(self, name: str, value):
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
