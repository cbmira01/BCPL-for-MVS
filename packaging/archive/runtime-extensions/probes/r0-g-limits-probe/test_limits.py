"""Host boundary cases for R.0 approved G numbers; not an MVS claim."""
import struct
import unittest
from dataclasses import replace
from limits import *


def f(v):
    return struct.pack('>I', v & 0xffffffff)


def ident(s):
    return s.ljust(8).encode('cp037')


def reg(n=0, m=0, *, length=None):
    expected = 28+8*n+8*m
    data = bytearray('BCRG'.encode('cp037')+f(1)+f(28)+f(expected if length is None else length)
                     +f(n)+f(m)+f(0))
    for i in range(n):
        data += f(0x2000 + 16*i)+f(0x2008 + 16*i)
    for i in range(m):
        data += ident('P'+str(i))
    return bytes(data)


def pkg(k=1, d=0, *, name='PACKA', final=0, length=None):
    expected = 48+8*k+16*d
    data = bytearray('BCEX'.encode('cp037')+f(1)+f(48)+f(expected if length is None else length)
                     +ident(name)+f(1)+f(2)+f(k)+f(final)+f(d)+f(0))
    for i in range(k):
        data += f(200+i)+f(0x4000+4*i)
    for i in range(d):
        data += ident('D'+str(i))+f(1)+f(0)
    return bytes(data)


class LimitsTest(unittest.TestCase):
    def code(self, expected, fn):
        self.assertEqual(diagnostic(fn), expected)

    def test_constants(self):
        self.assertEqual((REG_MAX, PKG_MAX, AGG_MAX), (540,368,12316))

    def test_registry_empty_and_max(self):
        self.assertEqual(registry(reg()), ((),()))
        pairs, req = registry(reg(32,32))
        self.assertEqual((len(pairs),len(req)),(32,32))

    def test_registry_rejects_counts(self):
        for n,m in ((33,0),(0,33),(0xffffffff,0),(0,0xffffffff)):
            # Use a fixed-length safe header to exercise count validation.
            data=reg()
            d=bytearray(data); d[16:20]=f(n);d[20:24]=f(m)
            self.code(1003, lambda d=d: registry(bytes(d)))

    def test_registry_extent_and_header(self):
        self.code(1001,lambda: registry(reg(),begin=0x1001))
        self.code(1001,lambda: registry(reg(),end=0x1020))
        self.code(1002,lambda: registry('XXXX'.encode('cp037')+reg()[4:]))
        self.code(1002,lambda: registry(reg()[:4]+f(2)+reg()[8:]))
        self.code(1003,lambda: registry(reg(length=32)))
        self.code(1003,lambda: registry(reg(1,0)[:-8]))

    def test_descriptor_max_and_min(self):
        self.assertEqual(len(pkg(8,16)),368)
        self.assertEqual(len(descriptor(pkg(8,16),trusted_calls=frozenset(0x4000+4*i for i in range(8))).exports),8)
        self.assertEqual(len(descriptor(pkg(),trusted_calls={0x4000}).exports),1)

    def test_descriptor_bad_counts(self):
        for k,d in ((0,0),(9,0),(1,17),(0xffffffff,0),(1,0xffffffff)):
            data=bytearray(pkg());data[32:36]=f(k);data[40:44]=f(d)
            self.code(1006,lambda data=data: descriptor(bytes(data),trusted_calls={0x4000}))

    def test_descriptor_bad_header_and_span(self):
        self.code(1004,lambda:descriptor(pkg(),begin=0x2001, trusted_calls={0x4000}))
        self.code(1004,lambda:descriptor(pkg(),end=0x2100, trusted_calls={0x4000}))
        self.code(1005,lambda:descriptor('XXXX'.encode('cp037')+pkg()[4:],trusted_calls={0x4000}))
        self.code(1006,lambda:descriptor(pkg(length=100),trusted_calls={0x4000}))

    def test_export_and_finalizer(self):
        b=bytearray(pkg());b[48:52]=f(700)
        self.code(1008,lambda: descriptor(bytes(b),trusted_calls={0x4000}))
        b=bytearray(pkg());b[52:56]=f(0)
        self.code(1008,lambda: descriptor(bytes(b),trusted_calls={0x4000}))
        self.code(1013,lambda:descriptor(pkg(final=0x4001),trusted_calls={0x4000}))
        self.code(1013,lambda:descriptor(pkg(final=0x5000),trusted_calls={0x4000}))
        self.code(0,lambda:descriptor(pkg(final=0x4000),trusted_calls={0x4000}))

    def test_dependency_and_names(self):
        self.code(1014,lambda:descriptor(pkg(1,1,name='D0'),trusted_calls={0x4000}))
        self.code(1007,lambda:descriptor(pkg(name='a'),trusted_calls={0x4000}))
        self.code(1007,lambda:descriptor(pkg(name=''),trusted_calls={0x4000}))

    def test_duplicate_export(self):
        b=bytearray(pkg(k=2));b[56:60]=f(200)
        self.code(1008,lambda:descriptor(bytes(b),trusted_calls={0x4000,0x4004}))

    def test_preflight(self):
        a=descriptor(pkg(),trusted_calls={0x4000})
        b=replace(a,name='PACKB',exports=((201,0x4004),),dependencies=(('PACKA',1,1),))
        self.code(0,lambda:preflight((a,b),('PACKB',),occupied=frozenset(),allowed={200:'PACKA',201:'PACKB'}))
        self.code(1007,lambda:preflight((a,a),(),occupied=frozenset(),allowed={200:'PACKA'}))
        self.code(1009,lambda:preflight((a,),(),occupied=frozenset({200}),allowed={200:'PACKA'}))
        self.code(1010,lambda:preflight((a,),('MISSING',),occupied=frozenset(),allowed={200:'PACKA'}))
        self.code(1010,lambda:preflight((b,),(),occupied=frozenset(),allowed={201:'PACKB'}))
        self.code(1011,lambda:preflight((replace(a,minor=0),b),(),occupied=frozenset(),allowed={200:'PACKA',201:'PACKB'}))
        self.code(1012,lambda:preflight((b,a),(),occupied=frozenset(),allowed={200:'PACKA',201:'PACKB'}))
        self.code(1014,lambda:preflight((replace(a,dependencies=(('PACKA',1,0),)),),(),occupied=frozenset(),allowed={200:'PACKA'}))


if __name__ == '__main__':
    unittest.main()
