#!/usr/bin/env python3
"""R.1 link-preparation address-provenance lint for candidate BCEX/BCRG.

Require referenced callable targets and descriptor boundaries to be
source-declared assembler ENTRY labels, with address-valued fields emitted
as linker relocations A(SYMBOL), not raw aligned numeric fullwords.
This does not replace independent inspection of IEWL MAP/XREF or provide
runtime memory protection against arbitrary externally supplied bytes.
"""
from __future__ import annotations
import re

REF = re.compile(r'A\(([A-Z][A-Z0-9]{0,7})\)')
FVAL = re.compile(r"F'(-?\d+)'")


def exported_names(source: str) -> set[str]:
    names = set()
    for line in source.splitlines():
        match = re.fullmatch(r'\s+ENTRY\s+([A-Z][A-Z0-9,]*)\s*',line)
        if match:
            names.update(match.group(1).split(','))
    return names


def extern_names(source: str) -> set[str]:
    names = set()
    for line in source.splitlines():
        match = re.fullmatch(r'\s+EXTRN\s+([A-Z][A-Z0-9,]*)\s*',line)
        if match:
            names.update(match.group(1).split(','))
    return names


def check(registry: str, descriptor: str, extras: list[str],
          *, allow_untrusted_fixture: bool=False) -> dict:
    # Registry must always be a real linker-relocated descriptor array.
    trusted = exported_names(descriptor)
    for source in extras:
        trusted.update(exported_names(source))
    boundaries = list(re.findall(r'^\s+DC\s+(A\([^\n]+\))\s*$',
                                 registry, re.M))
    if not boundaries:
        raise ValueError('BCPLREG has no relocated descriptor span')
    regextern = extern_names(registry)
    for line in boundaries:
        addresses = REF.findall(line)
        if len(addresses)!=2 or line.count('A(')!=2:
            raise ValueError('BCPLREG extent needs two A(SYMBOL) references')
        for symbol in addresses:
            if symbol not in regextern or symbol not in trusted:
                raise ValueError(f'BCPLREG extent untrusted: {symbol}')
    # A deliberately wrong magic is still allowed to reach the existing
    # negative MVS validation (diagnostic 1005).
    # The 6-field descriptor record has finalizer in its fourth word.
    finalizers=[]
    for src in [descriptor,*extras]:
        source_extern=extern_names(src)
        for line in src.splitlines():
            fields=re.match(r'^\s+DC\s+(F\'[0-9]+\',F\'[0-9]+\',F\'[0-9]+\',(.+),F\'[0-9]+\',F\'[0-9]+\')\s*$',line)
            if not fields:
                continue
            final=fields.group(2)
            if final == "F'0'":
                continue
            names=REF.fullmatch(final)
            if not names:
                if allow_untrusted_fixture:
                    continue
                raise ValueError(f'BCEX finalizer lacks A(SYMBOL): {final}')
            symbol=names.group(1)
            if symbol not in source_extern or symbol not in trusted:
                raise ValueError(f'BCEX finalizer source untrusted: {symbol}')
            finalizers.append(symbol)
    # Validate all declared entry relocation references, not only hooks.
    for src in [descriptor,*extras]:
        known=extern_names(src)|exported_names(src)
        for line in src.splitlines():
            if 'DC' not in line or line.lstrip().startswith('*'):
                continue
            for symbol in REF.findall(line):
                if symbol not in known or symbol not in trusted:
                    raise ValueError(f'untrusted exported callable reference: {symbol}')
    return {'descriptor_spans':len(boundaries),'finalizers':finalizers}
