#!/usr/bin/env python3
"""Build a tiny exemplar index for quick inspection."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'references' / 'exemplars'
OUT = Path(__file__).resolve().parent.parent / 'references' / 'exemplar-index.md'


def extract(lines: list[str], heading: str) -> str:
    for i, line in enumerate(lines):
        if line.strip() == heading:
            for nxt in lines[i + 1:]:
                if nxt.strip():
                    return nxt.strip()
    return ''


def main() -> int:
    rows = ['# Exemplar index', '', '| file | 标签 | 核心立意 |', '|---|---|---|']
    for path in sorted(ROOT.glob('*.md')):
        lines = path.read_text(encoding='utf-8').splitlines()
        tags = extract(lines, '## 标签')
        thesis = extract(lines, '## 核心立意')
        rows.append(f'| {path.name} | {tags} | {thesis} |')
    OUT.write_text('\n'.join(rows) + '\n', encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
