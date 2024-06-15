# Flo compilator

<p align=center>
  <span>Project realized by <a href="https://github.com/deliasTheo">Théo Delias</a>, <a href="https://github.com/AlbanFALCOZ">Alban Falcoz</a>, <a href="https://github.com/06Games">Evan Galli</a> and <a href="https://github.com/theoLassauniere">Théo Lassauniere</a> <br/>as part of the <b>Languages, Compilation, Automata</b> course.</span>
</p>

## The project

The aim of this project is to compile FLO code (detailed below) into ARMv7 assembly code.

## The structure

* Lexical analysis: breaks down the code into lexemes
* Syntax analysis: generates an abstract tree of the code
* Code generation: transforms the abstract tree into the corresponding assembly code

## The FLO langage

The Flo programming language is a statically typed imperative language designed by [Florian Bridoux](https://webusers.i3s.unice.fr/~bridoux/).

Data types:
* `entier` (integer)
* `booleen` (boolean)

Operators:
* Algebraic: `+`, `-`, `*`, `/`, `%`
* Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
* Logical: `et` (and), `ou` (or), `non` (not)

Built-in functions:
* `vide ecrire(entier|booleen valeur)` (write)
* `entier lire()` (read)

Functions:
* Functions always return a value: no void (`vide`) except for the built-in function `ecrire`

Control flow:
* `si` (if), `sinon si` (else if), `sinon` (else)
* `tantque` (while)

## Limitations

* There is no check for the presence of a return in the functions. This is a bit complex to do, as it requires to check that there is a return in all cases. Simply checking that the last instruction in the function is a return is not enough.  
* It would have been interesting to add an optimisation phase at the end. This would have eliminated, for example, pushes followed immediately by pops, variables declared but not used (or only used in one direction), and useless operations such as +0, -0, *1 or /1.
* Read, write, divide and modulo are implemented via the libc functions, it would have been better to program them directly in asm.

## Usage

```
usage: generation_code.py [-h] [-o OUTPUT] [-arm] [-t] [--builtins] filename

Generate assembly code from flo script

positional arguments:
  filename

options:
  -h, --help                  Show this help message and exit
  -o OUTPUT, --output OUTPUT  Destination file
  -arm, --arm                 Generate ARM assembly
  -t, -table, --table         Display the symbol table
  --builtins                  Display builtins in the symbol table
```
