#!/usr/bin/env python3
"""Render a self-contained HTML report for shenlun grading."""
from __future__ import annotations

import html
import json
import math
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
    return ''.join(f'<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>' for k, v in mapping.items())


def cards(items: list[dict[str, str]]) -> str:
    if not items:
        return '<p>无逐段点评。</p>'
    parts = []
    for item in items:
        title = esc(item.get('section', '未命名段落'))
        comment = esc(item.get('comment', ''))
        parts.append(f'<div class="mini-card"><h3>{title}</h3><p>{comment}</p></div>')
    return ''.join(parts)


def parse_num(text: str) -> float:
    digits = ''.join(ch for ch in text if ch.isdigit() or ch == '.')
    return float(digits) if digits else 0.0


def radar_polygon(subscores: dict[str, str]) -> str:
    if not subscores:
        return ''
    values = []
    labels = list(subscores.keys())
    for raw in subscores.values():
        if '/' in raw:
            left, right = raw.split('/', 1)
            score = parse_num(left)
            total = parse_num(right) or 1.0
            values.append(max(0.0, min(1.0, score / total)))
        else:
            values.append(max(0.0, min(1.0, parse_num(raw) / 20.0)))
    n = len(values)
    cx, cy, r = 160, 160, 110
    pts = []
    label_pts = []
    grid = []
    for layer in range(1, 6):
        cur = []
        rr = r * layer / 5
        for i in range(n):
            angle = -math.pi / 2 + 2 * math.pi * i / n
            x = cx + rr * math.cos(angle)
            y = cy + rr * math.sin(angle)
            cur.append(f'{x:.1f},{y:.1f}')
        grid.append(f'<polygon points="{" ".join(cur)}" class="grid" />')
    for i, val in enumerate(values):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        x = cx + r * val * math.cos(angle)
        y = cy + r * val * math.sin(angle)
        pts.append(f'{x:.1f},{y:.1f}')
        lx = cx + (r + 24) * math.cos(angle)
        ly = cy + (r + 24) * math.sin(angle)
        label = labels[i]
        label_pts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle">{esc(label)}</text>')
    spokes = []
    for i in range(n):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        spokes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" class="spoke" />')
    polygon = ' '.join(pts)
    return f'<svg viewBox="0 0 320 320" aria-label="评分雷达图"><g>{"".join(grid)}{"".join(spokes)}<polygon points="{polygon}" class="shape" />{"".join(label_pts)}</g></svg>'


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
    subscores = data.get('subscores', {})
    subscores_table = rows(subscores)
    radar = radar_polygon(subscores)
    issues = list_items(data.get('issues', []))
    rewrite = esc(data.get('rewrite', ''))
    plan = list_items(data.get('plan_7d', []))
    comments = cards(data.get('paragraph_comments', []))
    html_text = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; line-height: 1.6; background: #f7f7f8; color: #111827; }}
.wrap {{ max-width: 1080px; margin: 0 auto; }}
.hero, .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 18px; padding: 24px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
.hero {{ margin-bottom: 20px; }}
.grid {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 20px; margin-bottom: 20px; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
.score {{ font-size: 48px; font-weight: 800; margin: 0; }}
.muted {{ color: #4b5563; }}
table {{ width: 100%; border-collapse: collapse; }}
td, th {{ border-bottom: 1px solid #e5e7eb; text-align: left; padding: 10px 8px; vertical-align: top; }}
ul {{ margin: 0; padding-left: 20px; }}
pre {{ white-space: pre-wrap; word-break: break-word; background: #f3f4f6; padding: 16px; border-radius: 12px; overflow-x: auto; }}
.mini-card {{ background: #fafafa; border: 1px solid #ececec; border-radius: 14px; padding: 16px; margin-bottom: 12px; }}
svg {{ width: 100%; height: auto; }}
.grid {{ fill: none; stroke: #e5e7eb; stroke-width: 1; }}
.spoke {{ stroke: #e5e7eb; stroke-width: 1; }}
.shape {{ fill: rgba(59,130,246,0.16); stroke: #2563eb; stroke-width: 2; }}
text {{ font-size: 12px; fill: #374151; }}
@media (max-width: 800px) {{ .grid, .two {{ grid-template-columns: 1fr; }} body {{ margin: 16px; }} }}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <h1>{title}</h1>
    <p class="score">{total_score}</p>
    <p class="muted">{summary}</p>
  </div>
  <div class="grid">
    <div class="card">
      <h2>分项分</h2>
      <table>{subscores_table}</table>
    </div>
    <div class="card">
      <h2>评分雷达图</h2>
      {radar}
    </div>
  </div>
  <div class="two">
    <div class="card">
      <h2>主要失分点</h2>
      <ul>{issues}</ul>
    </div>
    <div class="card">
      <h2>7 天提升计划</h2>
      <ul>{plan}</ul>
    </div>
  </div>
  <div class="card" style="margin-bottom:20px;">
    <h2>逐段点评</h2>
    {comments}
  </div>
  <div class="card">
    <h2>建议改写</h2>
    <pre>{rewrite}</pre>
  </div>
</div>
</body>
</html>'''
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
