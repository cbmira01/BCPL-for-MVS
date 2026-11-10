#!/usr/bin/env python3
"""Byte-window reader for Hercules' append-only printer stream.

A cursor is captured immediately before a JES submission. Reads refuse a
replaced, truncated or rewritten printer prefix; they never fall back to
unbounded history when a cursor is invalid.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ANCHOR_LENGTH = 64


class PrinterWindowError(ValueError):
    pass


def capture(printer: Path, cursor_file: Path) -> None:
    with printer.open('rb') as stream:
        stat = os.fstat(stream.fileno())
        offset = stat.st_size
        length = min(offset, ANCHOR_LENGTH)
        stream.seek(offset - length)
        anchor = stream.read(length)
        if len(anchor) != length:
            raise PrinterWindowError('printer file changed during cursor capture')
        data = {
            'schema': 1, 'device': stat.st_dev, 'inode': stat.st_ino,
            'offset': offset, 'anchor_length': length,
            'anchor_sha256': hashlib.sha256(anchor).hexdigest(),
            'partial_line': bool(offset and not anchor.endswith(b'\n')),
        }
    cursor_file.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement: no reader can consume a partially written cursor.
    name = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='ascii', dir=cursor_file.parent,
                                         prefix='.printer-cursor-', delete=False) as out:
            name = out.name
            os.fchmod(out.fileno(), 0o600)
            json.dump(data, out, sort_keys=True)
            out.write('\n')
        os.replace(name, cursor_file)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def read(printer: Path, cursor_file: Path) -> bytes:
    try:
        data = json.loads(cursor_file.read_text(encoding='ascii'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrinterWindowError(f'invalid cursor: {exc}') from exc
    if (not isinstance(data, dict) or data.get('schema') != 1
            or any(type(data.get(k)) is not int for k in
                   ('device', 'inode', 'offset', 'anchor_length'))
            or data['offset'] < 0 or not 0 <= data['anchor_length'] <= ANCHOR_LENGTH
            or data['anchor_length'] != min(data['offset'], ANCHOR_LENGTH)
            or type(data.get('partial_line')) is not bool
            or not isinstance(data.get('anchor_sha256'), str)
            or len(data['anchor_sha256']) != 64):
        raise PrinterWindowError('invalid cursor fields')
    with printer.open('rb') as stream:
        stat = os.fstat(stream.fileno())
        offset = data['offset']
        if (stat.st_dev != data['device'] or stat.st_ino != data['inode']
                or stat.st_size < offset):
            raise PrinterWindowError('printer file replaced or truncated since capture')
        length = data['anchor_length']
        stream.seek(offset - length)
        anchor = stream.read(length)
        if hashlib.sha256(anchor).hexdigest() != data['anchor_sha256']:
            raise PrinterWindowError('printer content changed since capture')
        stream.seek(offset)
        text = stream.read()
    # If capture occurred within an unfinished line, the first fragment is
    # not a new JES record. Never splice it into a fabricated START banner.
    if data['partial_line']:
        position = text.find(b'\n')
        return b'' if position == -1 else text[position + 1:]
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('capture', 'read'))
    parser.add_argument('--printer', type=Path, required=True)
    parser.add_argument('--cursor-file', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == 'capture':
            capture(args.printer, args.cursor_file)
        else:
            sys.stdout.buffer.write(read(args.printer, args.cursor_file))
        return 0
    except (PrinterWindowError, OSError) as exc:
        print(f'printer-window: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
