"""Offline tests for Hercules printer cursor safety and readback."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/mvs/printer-window.py'
SPEC = importlib.util.spec_from_file_location('printer_window', SCRIPT)
WINDOW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WINDOW)


class PrinterWindowTests(unittest.TestCase):
    def test_capture_read_and_repeated_append(self):
        with tempfile.TemporaryDirectory() as tmp:
            printer, cursor = Path(tmp) / 'prt.txt', Path(tmp) / 'cursor.json'
            printer.write_bytes(b'OLD\n')
            WINDOW.capture(printer, cursor)
            self.assertEqual(WINDOW.read(printer, cursor), b'')
            with printer.open('ab') as out:
                out.write(b'****A START JOB 1 ABC\n')
            self.assertEqual(WINDOW.read(printer, cursor), b'****A START JOB 1 ABC\n')
            with printer.open('ab') as out:
                out.write(b'****A END JOB 1 ABC\n')
            self.assertEqual(WINDOW.read(printer, cursor),
                             b'****A START JOB 1 ABC\n****A END JOB 1 ABC\n')
            self.assertEqual(cursor.stat().st_mode & 0o777, 0o600)

    def test_partial_line_never_fabricates_banner(self):
        with tempfile.TemporaryDirectory() as tmp:
            printer, cursor = Path(tmp) / 'prt.txt', Path(tmp) / 'cursor.json'
            printer.write_bytes(b'partial old')
            WINDOW.capture(printer, cursor)
            with printer.open('ab') as out:
                out.write(b' continuation\n****A START JOB 4 NEW\n')
            self.assertEqual(WINDOW.read(printer, cursor), b'****A START JOB 4 NEW\n')

    def test_rotation_truncation_and_prefix_rewrite_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            printer, cursor = Path(tmp) / 'prt.txt', Path(tmp) / 'cursor.json'
            printer.write_bytes(b'OLD\n')
            WINDOW.capture(printer, cursor)
            printer.write_bytes(b'A\n')
            with self.assertRaises(WINDOW.PrinterWindowError):
                WINDOW.read(printer, cursor)
            printer.write_bytes(b'WRONG BUT LONG\n')
            with self.assertRaises(WINDOW.PrinterWindowError):
                WINDOW.read(printer, cursor)
            printer.rename(Path(tmp) / 'old.txt')
            printer.write_bytes(b'WRONG BUT LONG\n')
            with self.assertRaises(WINDOW.PrinterWindowError):
                WINDOW.read(printer, cursor)

    def test_cli_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            printer, cursor = Path(tmp) / 'prt.txt', Path(tmp) / 'cursor.json'
            printer.write_bytes(b'OLD\n')
            command = [sys.executable, str(SCRIPT)]
            capture = subprocess.run(command + ['capture', '--printer', str(printer),
                                                 '--cursor-file', str(cursor)],
                                     cwd=ROOT, capture_output=True)
            self.assertEqual(capture.returncode, 0, capture.stderr)
            with printer.open('ab') as out:
                out.write(b'NEW\n')
            before = printer.stat().st_mtime_ns
            result = subprocess.run(command + ['read', '--printer', str(printer),
                                                '--cursor-file', str(cursor)],
                                    cwd=ROOT, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, b'NEW\n')
            self.assertEqual(before, printer.stat().st_mtime_ns)
            printer.write_bytes(b'WRONG BUT LONG\n')
            rejected = subprocess.run(command + ['read', '--printer', str(printer),
                                                  '--cursor-file', str(cursor)],
                                      cwd=ROOT, capture_output=True)
            self.assertEqual(rejected.returncode, 2)
            self.assertIn(b'printer-window:', rejected.stderr)


if __name__ == '__main__':
    unittest.main()
