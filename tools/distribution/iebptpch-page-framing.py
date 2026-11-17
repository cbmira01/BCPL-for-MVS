#!/usr/bin/env python3
"""TA.0 IEBPTPCH page-continuation headings, without member guessing.

IEBPTPCH repeats a MEMBER NAME heading after a new printer PAGE. These are
continuations of one member, not a new PDS directory member. This function
removes only well-formed, sequential-page repeats; the existing strict FB80
record decoder remains responsible for payload, block and identity checks.
"""
from __future__ import annotations

import re
from typing import Callable, Pattern

PAGE = re.compile(r'^\s*PAGE\s+(\d{4})\s*$')


def coalesce_page_headings(
    lines: list[str], *, members: list[str], header: Pattern[str],
    first: Pattern[str], second: Pattern[str], require: Callable[[bool, str], None],
) -> tuple[list[str], list[tuple[int, str]], dict[str, int]]:
    """Return print lines, logical member heading offsets, repeat counts.

    A repeated name is discarded only when directly preceded by a PAGE line,
    that page increments from the preceding page for this member, and at
    least one complete hex record was printed since the prior heading.
    A new logical member must match the next selected name exactly.
    """
    logical: list[tuple[int, str]] = []
    normalized: list[str] = []
    repeats: dict[str, int] = {}
    current_page: int | None = None
    member_last_page: int | None = None
    last_heading_line: int | None = None

    for pos, line in enumerate(lines):
        if page := PAGE.fullmatch(line):
            current_page = int(page.group(1))
        match = header.fullmatch(line)
        if not match:
            normalized.append(line)
            continue
        name = match.group(1)
        is_continuation = bool(logical and name == logical[-1][1])
        if is_continuation:
            before = pos - 1
            while before >= 0 and not lines[before].strip():
                before -= 1
            page = PAGE.fullmatch(lines[before]) if before >= 0 else None
            require(page is not None and member_last_page is not None and
                    int(page.group(1)) == member_last_page + 1,
                    f'{name}: repeated print heading lacks next PAGE marker')
            require(last_heading_line is not None, 'missing earlier member heading')
            # Never accept empty/redundant headings simply by adding a PAGE.
            records = 0
            for i in range(last_heading_line + 1, pos - 1):
                if (first.fullmatch(lines[i].rstrip(' ')) and
                        second.fullmatch(lines[i + 1].rstrip(' '))):
                    records += 1
            require(records > 0, f'{name}: page continuation has no complete FB80 record')
            member_last_page = int(page.group(1))
            repeats[name] += 1
            last_heading_line = pos
            continue
        next_member = len(logical)
        require(next_member < len(members) and name == members[next_member],
                'printed member headers missing, duplicated or reordered')
        logical.append((len(normalized), name))
        repeats[name] = 0
        member_last_page = current_page
        last_heading_line = pos
        normalized.append(line)

    require([name for _, name in logical] == members,
            'printed member headers missing, duplicated or reordered')
    return normalized, logical, repeats
