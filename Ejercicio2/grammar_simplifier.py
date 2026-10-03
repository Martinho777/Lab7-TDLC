#!/usr/bin/env python3
"""Simplificación de gramáticas libres de contexto: eliminación de ε-producciones.

Formato aceptado por línea:
    S -> 0A0 | 1B1 | BB

No terminales: una letra mayúscula individual (A-Z).
Terminales: una letra minúscula o un dígito individual (a-z, 0-9).
También se acepta ε como producción vacía.
"""

from __future__ import annotations

import argparse
import itertools
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

EPSILON = "ε"
ARROW = "→"
NONTERMINAL = re.compile(r"^[A-Z]$")
SYMBOL = re.compile(r"^[A-Z a-z0-9]+$")
LINE_PATTERN = re.compile(
    r"^\s*[A-Z]\s*(?:→|->)\s*(?:ε|[A-Za-z0-9]+)"
    r"(?:\s*\|\s*(?:ε|[A-Za-z0-9]+))*\s*$"
)


@dataclass
class Grammar:
    start: str
    productions: dict[str, list[str]] = field(default_factory=dict)

    @property
    def nonterminals(self) -> set[str]:
        return set(self.productions)

    def copy(self) -> "Grammar":
        return Grammar(self.start, {key: list(value) for key, value in self.productions.items()})


def validate_line(line: str, line_number: int) -> None:
    """Detiene la ejecución si una línea no cumple la convención del laboratorio."""
    if not LINE_PATTERN.fullmatch(line):
        raise ValueError(
            f"Línea {line_number} inválida: {line!r}. "
            "Use el formato 'A -> cuerpo | cuerpo', con ε para vacío."
        )


def parse_grammar(path: Path) -> Grammar:
    productions: dict[str, list[str]] = {}
    start: str | None = None

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"No se pudo leer el archivo {path}: {error}") from error

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        validate_line(line, line_number)
        left, right = re.split(r"→|->", line, maxsplit=1)
        left = left.strip()
        alternatives = [part.strip() for part in right.split("|")]
        productions.setdefault(left, [])
        for alternative in alternatives:
            body = "" if alternative == EPSILON else alternative
            if body not in productions[left]:
                productions[left].append(body)
        start = start or left

    if not productions:
        raise ValueError(f"El archivo {path} no contiene producciones.")
    return Grammar(start=start or "S", productions=productions)


def nullable_symbols(grammar: Grammar) -> set[str]:
    nullable: set[str] = set()
    changed = True
    while changed:
        changed = False
        for left, bodies in grammar.productions.items():
            if left in nullable:
                continue
            for body in bodies:
                if body == "" or all(symbol in nullable for symbol in body if NONTERMINAL.fullmatch(symbol)):
                    # Una producción solo es anulable si todos sus símbolos son
                    # no terminales anulables; terminales/dígitos no pueden omitirse.
                    if body == "" or all(
                        NONTERMINAL.fullmatch(symbol) and symbol in nullable for symbol in body
                    ):
                        nullable.add(left)
                        changed = True
                        break
    return nullable


def combinations_without_nullable(body: str, nullable: set[str]) -> list[str]:
    positions = [index for index, symbol in enumerate(body) if symbol in nullable]
    results: set[str] = set()
    for mask in itertools.product((False, True), repeat=len(positions)):
        omitted = {position for position, remove in zip(positions, mask) if remove}
        candidate = "".join(symbol for index, symbol in enumerate(body) if index not in omitted)
        results.add(candidate)
    return sorted(results, key=lambda value: (len(value), value))


def eliminate_epsilon(grammar: Grammar, verbose: bool = True) -> Grammar:
    nullable = nullable_symbols(grammar)
    if verbose:
        print(f"Símbolos anulables: {{{', '.join(sorted(nullable)) or 'ninguno'}}}")

    start = grammar.start
    result_start = start
    if start in nullable:
        result_start = fresh_symbol("S0", grammar.nonterminals)
        if verbose:
            print(f"El símbolo inicial {start} es anulable; se crea {result_start} -> {start} | ε")

    result: dict[str, list[str]] = {result_start: [start] if result_start != start else []}
    for left, bodies in grammar.productions.items():
        result.setdefault(left, [])
        for body in bodies:
            if body == "":
                continue
            generated = combinations_without_nullable(body, nullable)
            if verbose and len(generated) > 1:
                print(f"  {left} -> {body}: {len(generated)} combinaciones (2^{sum(symbol in nullable for symbol in body)})")
                print(f"    {', '.join(format_body(item) for item in generated)}")
            for candidate in generated:
                if candidate != "" and candidate not in result[left]:
                    result[left].append(candidate)

    if result_start != start:
        result[result_start].append("")
    return Grammar(result_start, {left: bodies for left, bodies in result.items() if bodies})


def fresh_symbol(preferred: str, used: set[str]) -> str:
    candidate = preferred
    counter = 0
    while candidate in used:
        counter += 1
        candidate = f"{preferred}{counter}"
    return candidate


def format_body(body: str) -> str:
    return body if body else EPSILON


def format_grammar(grammar: Grammar) -> str:
    return "\n".join(
        f"{left} {ARROW} {' | '.join(format_body(body) for body in bodies)}"
        for left, bodies in grammar.productions.items()
    )


def process_file(path: Path) -> None:
    print("=" * 72)
    print(f"Archivo: {path}")
    grammar = parse_grammar(path)
    print("\nGramática cargada:")
    print(format_grammar(grammar))
    print("\n--- Eliminación de producciones-ε ---")
    simplified = eliminate_epsilon(grammar)
    print("\nGramática resultante:")
    print(format_grammar(simplified))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Archivos de gramáticas a procesar")
    args = parser.parse_args()
    try:
        for path in args.files:
            process_file(path)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
