#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / '.claude/commands/shenlun.md',
    ROOT / '.claude/skills/shenlun/SKILL.md',
    ROOT / '.claude/skills/shenlun/references/rubric.md',
    ROOT / '.claude/skills/shenlun/references/profiles/national.md',
    ROOT / '.claude/skills/shenlun/references/exemplar-index.md',
    ROOT / '.claude/skills/shenlun/templates/grading-report.json.example',
    ROOT / '.claude/skills/shenlun/scripts/build_exemplar_index.py',
    ROOT / '.claude/skills/shenlun/scripts/render_report.py',
    ROOT / 'README.md',
]

REQUIRED_JSON_KEYS = {
    'title',
    'total_score',
    'summary',
    'subscores',
    'issues',
    'paragraph_comments',
    'rewrite',
    'plan_7d',
}


def ensure_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        raise SystemExit(f'Missing required files: {missing}')


def ensure_readme_mentions_command() -> None:
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    if '/shenlun' not in readme:
        raise SystemExit('README.md does not mention /shenlun command entry')
    if '.claude/commands/shenlun.md' not in readme:
        raise SystemExit('README.md does not document the command file')


def ensure_json_schema() -> None:
    example_path = ROOT / '.claude/skills/shenlun/templates/grading-report.json.example'
    data = json.loads(example_path.read_text(encoding='utf-8'))
    missing = sorted(REQUIRED_JSON_KEYS - set(data.keys()))
    if missing:
        raise SystemExit(f'Example grading JSON is missing keys: {missing}')
    if not isinstance(data['subscores'], dict) or not data['subscores']:
        raise SystemExit('subscores must be a non-empty dict')
    if not isinstance(data['issues'], list) or not data['issues']:
        raise SystemExit('issues must be a non-empty list')


def run_exemplar_index_builder() -> None:
    script = ROOT / '.claude/skills/shenlun/scripts/build_exemplar_index.py'
    subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)
    index_text = (ROOT / '.claude/skills/shenlun/references/exemplar-index.md').read_text(encoding='utf-8')
    if '# Exemplar index' not in index_text:
        raise SystemExit('exemplar-index.md header missing after rebuild')
    exemplar_rows = [line for line in index_text.splitlines() if line.strip().startswith('| ') and line.strip().endswith(' |')]
    if len(exemplar_rows) < 6:
        raise SystemExit('exemplar index looks too small after rebuild')


def run_report_renderer() -> None:
    script = ROOT / '.claude/skills/shenlun/scripts/render_report.py'
    json_path = ROOT / '.claude/skills/shenlun/templates/grading-report.json.example'
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / 'report.html'
        subprocess.run([sys.executable, str(script), str(json_path), str(out_path)], check=True, cwd=ROOT)
        html = out_path.read_text(encoding='utf-8')
        required_snippets = ['申论批改报告示例', '评分雷达图', '<svg', '72/100']
        for snippet in required_snippets:
            if snippet not in html:
                raise SystemExit(f'Rendered report missing snippet: {snippet}')


def main() -> int:
    ensure_files_exist()
    ensure_readme_mentions_command()
    ensure_json_schema()
    run_exemplar_index_builder()
    run_report_renderer()
    print('shenlun smoke test passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
