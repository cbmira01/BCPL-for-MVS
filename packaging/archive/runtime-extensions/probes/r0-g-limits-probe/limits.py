#!/usr/bin/env python3
"""R.0 G *test-only* reference validation of bounded, linked descriptors.

Byte strings stand in for *trusted, independently bounded* relocatable data.
This is not a runtime memory-safety mechanism or a BCPLMAIN registrar.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

NMAX = MMAX = 32
KMAX, DMAX = 8, 16
REG_MAX = 28 + 8 * NMAX + 8 * MMAX
PKG_MAX = 48 + 8 * KMAX + 16 * DMAX
AGG_MAX = REG_MAX + NMAX * PKG_MAX
GLOBAL_MAX = 699


class Reject(ValueError):
    def __init__(self, code: int):
        self.code = code
        super().__init__(f'R.0 diagnostic {code}')


def word(data: bytes, off: int) -> int:
    return unpack_from('>I', data, off)[0]


def identifier(raw: bytes) -> str:
    # Test-only syntax check: nonempty, printable uppercase EBCDIC CL8.
    if len(raw) != 8:
        raise Reject(1007)
    try:
        value = raw.decode('cp037')
    except UnicodeError:
        raise Reject(1007) from None
    core = value.rstrip(' ')
    if not core or any(not x.isprintable() or x == ' ' or x != x.upper()
                       for x in core):
        raise Reject(1007)
    return core


def span(data: bytes, begin: int, end: int, minimum: int,
         maximum: int, code: int) -> None:
    # The host fixture checks lengths only AFTER trusted source supplies
    # the bytes. These addresses are simulated, not live MVS pointers.
    if (begin < 0 or end <= begin or begin & 3 or end & 3
            or end - begin != len(data)
            or not minimum <= len(data) <= maximum):
        raise Reject(code)


@dataclass(frozen=True)
class Package:
    name: str
    major: int
    minor: int
    exports: tuple[tuple[int, int], ...]
    dependencies: tuple[tuple[str, int, int], ...]
    finalizer: int


def registry(data: bytes, begin=0x1000, *, end=None):
    if end is None:
        end = begin + len(data)
    span(data, begin, end, 28, REG_MAX, 1001)
    if (data[:4] != 'BCRG'.encode('cp037')) or (word(data, 4), word(data, 8), word(data, 24)) != (1, 28, 0):
        raise Reject(1002)
    n, m = word(data, 16), word(data, 20)
    if n > NMAX or m > MMAX or 28 + 8*n + 8*m != len(data) or word(data, 12) != len(data):
        raise Reject(1003)
    pairs = tuple((word(data, 28+8*i), word(data, 32+8*i)) for i in range(n))
    requirements = tuple(identifier(data[28+8*n+8*i:36+8*n+8*i])
                         for i in range(m))
    if len(set(requirements)) != len(requirements):
        raise Reject(1014)
    return pairs, requirements


def descriptor(data: bytes, begin=0x2000, *, end=None, trusted_calls=frozenset()):
    if end is None:
        end = begin + len(data)
    span(data, begin, end, 48, PKG_MAX, 1004)
    if (data[:4] != 'BCEX'.encode('cp037')) or (word(data, 4), word(data, 8), word(data, 44)) != (1, 48, 0):
        raise Reject(1005)
    name = identifier(data[16:24])
    k, d = word(data, 32), word(data, 40)
    if not 1 <= k <= KMAX or d > DMAX or 48+8*k+16*d != len(data) or word(data, 12) != len(data):
        raise Reject(1006)
    exports = tuple((word(data, 48+8*i), word(data, 52+8*i)) for i in range(k))
    slots = [g for g, _ in exports]
    if (len(set(slots)) != k or any(not 1 <= g <= GLOBAL_MAX or a == 0 or a & 3 or a not in trusted_calls
                                      for g, a in exports)):
        raise Reject(1008)
    finalizer = word(data, 36)
    if finalizer and (finalizer & 3 or finalizer not in trusted_calls):
        raise Reject(1013)
    deps = tuple((identifier(data[48+8*k+16*i:56+8*k+16*i]),
                  word(data, 56+8*k+16*i), word(data, 60+8*k+16*i))
                 for i in range(d))
    if len({row[0] for row in deps}) != len(deps) or any(row[0] == name for row in deps):
        raise Reject(1014)
    return Package(name, word(data, 24), word(data, 28), exports, deps, finalizer)


def preflight(packages: tuple[Package, ...], required: tuple[str, ...],
              *, occupied: frozenset[int], allowed: dict[int, str]):
    """Test-only effective ownership/dependency model; publishes nothing."""
    if len(packages) > NMAX or len(required) > MMAX:
        raise Reject(1003)
    names = [p.name for p in packages]
    if len(set(names)) != len(names):
        raise Reject(1007)
    installed: dict[str, Package] = {}
    claimed: set[int] = set()
    for p in packages:
        for g, address in p.exports:
            if g in claimed or g in occupied or allowed.get(g) != p.name:
                raise Reject(1009)
            claimed.add(g)
        for dep, major, minor in p.dependencies:
            if dep == p.name or len({x[0] for x in p.dependencies}) != len(p.dependencies):
                raise Reject(1014)
            if dep not in names:
                raise Reject(1010)
            if installed.get(dep) is None:
                raise Reject(1012)
            provider = installed[dep]
            if provider.major != major or provider.minor < minor:
                raise Reject(1011)
        installed[p.name] = p
    if any(name not in installed for name in required):
        raise Reject(1010)
    return 0


def diagnostic(operation):
    try:
        operation()
    except Reject as e:
        return e.code
    return 0
