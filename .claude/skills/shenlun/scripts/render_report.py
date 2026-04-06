#!/usr/bin/env python3
"""Render a simple self-contained HTML report for shenlun grading."""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value))


def list_items(items: list[str]) -> str:
    if not items:
        return '<li>无</li>'
    return ''.join(f'<li>{esc(item)}</li>' for item in items)


def rows(mapping: dict[str, object]) -> str:
    if not mapping:
        return '<tr><td>无</td><td>-</td></tr>'
    return ''.join(
        f'<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>' for k, v in mapping.items()
    )


def paragraphs(items: list[dict[str, str]]) -> str:
    if not items:
        return '<p>无逐段点评。</p>'
    parts: list[str] = []
    for item in items:
        title = esc(item.get('section', '未命名段落'))
        comment = esc(item.get('comment', ''))
        parts.append(f'<div class="card"><h3>{title}</h3><p>{comment}</p></div>')
    return ''.join(parts)


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: render_report.py input.json output.html', file=sys.stderr)
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    data = json.loads(input_path.read_text(encoding='utf-8'))

    title = esc(data.get('title', '申论批改报告'))
    total_score = esc(data.get('total_score', '未提供'))
    summary = esc(data.get('summary', ''))
    subscores = rows(data.get('subscores', {}))
    issues = list_items(data.get('issues', []))
    rewrite = esc(data.get('rewrite', ''))
    plan = list_items(data.get('plan_7d', []))
    comments = paragraphs(data.get('paragraph_comments', []))

    html_text = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; line-height: 1.6; background: #fafafa; color: #1f2937; }}
.wrap {{ max-width: 960px; margin: 0 auto; }}
.hero {{ background: white; border: 1px solid #e5e7eb; border-radius: 16px; padding: 24px; margin-bottom: 20px; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
.card {{ background: white; border: 1px solid #e5e7eb; border-radius: 16px; padding: 20px; margin-bottom: 16px; }}
.score {{ font-size: 42px; font-weight: 700; margin: 0; }}
table {{ width: 100%; border-collapse: collapse; }}
td, th {{ border-bottom: 1px solid #e5e7eb; text-align: left; padding: 10px 8px; vertical-align: top; }}
ul {{ margin: 0; padding-left: 20px; }}
pre {{ white-space: pre-wrap; word-break: break-word; background: #f3f4f6; padding: 16px; border-radius: 12px; }}
@media (max-width: 720px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <h1>{title}</h1>
    <p class="score">{total_score}</p>
    <p>{summary}</p>
  </div>
  <div class="grid">
    <div class="card">
      <h2>分项分</h2>
      <table>{subscores}</table>
    </div>
    <div class="card">
      <h2>主要失分点</h2>
      <ul>{issues}</ul>
    </div>
  </div>
  <div class="card">
    <h2>逐段点评</h2>
    {comments}
  </div>
  <div class="card">
    <h2>建议改写</h2>
    <pre>{rewrite}</pre>
  </div>
  <div class="card">
    <h2>7 天提升计划</h2>
    <ul>{plan}</ul>
  </div>
</div>
</body>
</html>
'''
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
