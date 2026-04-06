#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path

EDU = {'中专': 1, '大专': 2, '专科': 2, '本科': 3, '学士': 3, '硕士': 4, '研究生': 4, '博士': 5}
P_ALIASES = {
    'preferred_regions': ['地区偏好', '地区意向'],
    'hukou': ['户籍/生源地', '户籍', '生源地'],
    'education': ['学历'],
    'degree': ['学位'],
    'major': ['专业'],
    'politics': ['政治面貌'],
    'fresh_grad': ['是否应届', '应届身份'],
    'age': ['年龄'],
    'experience_years': ['基层工作经历年限', '工作经历年限'],
    'notes': ['备注', '补充说明'],
}
C_ALIASES = {
    'agency': ['机构', '招录机关', '用人单位', '部门'],
    'title': ['岗位名称', '职位名称', '职位', '岗位'],
    'region': ['地区', '工作地点', '所在地'],
    'education': ['学历要求', '学历'],
    'degree': ['学位要求', '学位'],
    'major': ['专业要求', '专业', '专业类别'],
    'politics': ['政治面貌要求', '政治面貌'],
    'fresh_grad': ['是否限应届', '限应届', '应届要求'],
    'experience': ['基层工作经历要求', '工作经历要求', '基层经历'],
    'headcount': ['招考人数', '招录人数', '人数'],
    'notes': ['备注', '其他条件', '说明'],
    'source': ['来源链接', '公告链接', '链接'],
}


def norm(x):
    return re.sub(r'\s+', '', (x or '').strip())


def split_items(x):
    return [s.strip() for s in re.split(r'[,，/；;、]', x or '') if s.strip()]


def level(x):
    x = norm(x)
    for k, v in EDU.items():
        if k in x:
            return v
    return 0


def to_bool(x):
    x = norm(x).lower()
    if x in {'是', 'yes', 'y', 'true', '应届'}:
        return 'yes'
    if x in {'否', 'no', 'n', 'false', '非应届'}:
        return 'no'
    return 'unknown'


def to_int(x):
    m = re.search(r'(\d+)', x or '')
    return int(m.group(1)) if m else None


def parse_profile(path):
    raw = {}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if '：' in line:
            k, v = line.split('：', 1)
        elif ':' in line:
            k, v = line.split(':', 1)
        else:
            continue
        raw[k.strip()] = v.strip()
    out = {}
    for k, aliases in P_ALIASES.items():
        out[k] = ''
        for a in aliases:
            if a in raw:
                out[k] = raw[a]
                break
    return out


def resolve(fieldnames, aliases):
    for a in aliases:
        if a in fieldnames:
            return a
    nmap = {norm(x): x for x in fieldnames}
    for a in aliases:
        if norm(a) in nmap:
            return nmap[norm(a)]
    return ''


def load_positions(path):
    with Path(path).open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    cols = {k: resolve(fieldnames, aliases) for k, aliases in C_ALIASES.items()}
    out = []
    for row in rows:
        item = {k: row.get(col, '').strip() if col else '' for k, col in cols.items()}
        out.append(item)
    return out


def major_match(major, req):
    major, req = norm(major), norm(req)
    if not req:
        return 0.5, '专业要求缺失，需人工核验'
    if '不限' in req:
        return 0.8, '专业不限'
    if major and major in req:
        return 1.0, '专业精确匹配'
    related = ['计算机类', '电子信息类', '软件工程', '数据科学', '人工智能']
    if '计算机科学与技术' in major and any(norm(x) in req for x in related):
        return 0.6, '疑似相关专业，建议人工核验专业目录'
    return 0.0, '专业要求不匹配'


def eligibility(profile, pos):
    reject, risks = [], []
    if level(profile.get('education')) and level(pos.get('education')) and level(profile.get('education')) < level(pos.get('education')):
        reject.append('学历不满足')
    if level(profile.get('degree')) and level(pos.get('degree')) and level(profile.get('degree')) < level(pos.get('degree')):
        reject.append('学位不满足')
    preq, ppol = norm(pos.get('politics')), norm(profile.get('politics'))
    if preq and '不限' not in preq and '中共党员' in preq and '党员' not in ppol:
        reject.append('政治面貌不满足')
    freq = norm(pos.get('fresh_grad'))
    if '应届' in freq:
        fg = to_bool(profile.get('fresh_grad'))
        if fg == 'no':
            reject.append('应届身份不满足')
        elif fg == 'unknown':
            risks.append('应届身份需人工核验')
    exp_req = (pos.get('experience') or '') + ' ' + (pos.get('notes') or '')
    exp_need = to_int(exp_req)
    exp_have = to_int(profile.get('experience_years') or '0') or 0
    if exp_need and ('基层' in exp_req or '工作经历' in exp_req) and exp_have < exp_need:
        reject.append('基层/工作经历不满足')
    notes, hukou = pos.get('notes') or '', norm(profile.get('hukou'))
    if '户籍' in notes or '生源' in notes:
        ok = True
        for region in ['北京', '天津', '河北']:
            if region in notes and region not in hukou:
                ok = False
        if not ok:
            reject.append('户籍/生源地限制可能不满足')
    _, mreason = major_match(profile.get('major'), pos.get('major'))
    if mreason == '专业要求不匹配':
        reject.append('专业不满足')
    elif '人工核验' in mreason:
        risks.append(mreason)
    if reject:
        return 'reject', reject, risks
    if risks:
        return 'review', [], risks
    return 'pass', [], []


def score(profile, pos, status):
    reasons = []
    region_score = 0.5
    for r in split_items(profile.get('preferred_regions')):
        if norm(r) and norm(r) in norm(pos.get('region')):
            region_score = 1.0
            reasons.append('地区偏好匹配')
            break
    major_score, mreason = major_match(profile.get('major'), pos.get('major'))
    reasons.append(mreason)
    notes = (pos.get('notes') or '') + ' ' + (pos.get('experience') or '')
    restriction = 0.9
    if any(k in notes for k in ['夜班', '执法', '出差', '值班', '体测', '党员', '基层']):
        restriction = 0.3
    elif any(k in notes for k in ['服从分配', '轮岗']):
        restriction = 0.5
    else:
        reasons.append('限制条件相对宽松')
    head = to_int(pos.get('headcount')) or 1
    head_score = 1.0 if head >= 4 else 0.7 if head >= 2 else 0.4
    if head_score >= 0.7:
        reasons.append('招录人数相对友好')
    s = round(region_score * 0.35 + major_score * 0.35 + restriction * 0.15 + head_score * 0.15 - (0.08 if status == 'review' else 0), 3)
    return max(0.0, min(s, 1.0)), reasons


def level_tag(s, status):
    if status == 'review':
        return '冲刺'
    if s >= 0.8:
        return '稳妥'
    if s >= 0.6:
        return '保底'
    return '冲刺'


def render(profile, rows):
    passed = [x for x in rows if x['status'] == 'pass']
    rejected = [x for x in rows if x['status'] == 'reject']
    review = [x for x in rows if x['status'] == 'review']
    top = sorted([x for x in rows if x['status'] != 'reject'], key=lambda x: x['score'], reverse=True)[:10]
    top_names = '暂无'
    if top:
        top_names = '、'.join([f"{x['title']}（{x['region']}）" for x in top[:3]])
    lines = ['# 岗位推荐 shortlist', '', '## 一、结论摘要', f'- 总岗位数：{len(rows)}', f'- 明确可报：{len(passed)}', f'- 明确不可报：{len(rejected)}', f'- 待人工核验：{len(review)}', f'- 优先推荐：{top_names}', '', '## 二、候选人画像摘要', f"- 地区偏好：{profile.get('preferred_regions') or '未提供'}", f"- 学历/学位：{profile.get('education') or '未提供'} / {profile.get('degree') or '未提供'}", f"- 专业：{profile.get('major') or '未提供'}", f"- 政治面貌：{profile.get('politics') or '未提供'}", f"- 应届身份：{profile.get('fresh_grad') or '未提供'}", f"- 年龄：{profile.get('age') or '未提供'}", f"- 备注：{profile.get('notes') or '无'}", '', '## 三、明确不可报岗位']
    if not rejected:
        lines.append('- 暂无')
    else:
        for x in rejected:
            lines.append(f"- {x['title']}（{x['agency']}，{x['region']}）：{'；'.join(x['reject'])}")
    lines.extend(['', '## 四、推荐岗位 Top N'])
    if not top:
        lines.append('- 暂无')
    else:
        for i, x in enumerate(top, 1):
            lines.extend([f"### {i}. {x['title']}（{x['agency']}，{x['region']}）", f"- 推荐等级：{x['level']}", f"- 资格状态：{'待人工核验' if x['status'] == 'review' else '初步可报'}", f"- 综合得分：{x['score']}", '- 推荐理由：'])
            for r in x['reasons'][:4]:
                lines.append(f'  - {r}')
            lines.append('- 风险点：')
            if x['risks']:
                for r in x['risks'][:3]:
                    lines.append(f'  - {r}')
            else:
                lines.append('  - 暂未发现明显边界风险')
            lines.append('- 建议核验项：')
            if x['status'] == 'review' or x['risks']:
                for r in (x['risks'] or ['请复核岗位备注与官方专业目录']):
                    lines.append(f'  - {r}')
            else:
                lines.append('  - 复核官方公告、职位表和专业目录')
            if x['source']:
                lines.append(f"- 来源链接：{x['source']}")
            lines.append('')
    lines.extend(['## 五、下一步建议', '1. 先人工复核所有“待人工核验”岗位中的专业目录、应届口径和备注限制。', '2. 在稳妥/保底岗位中优先准备 5 到 8 个主报名目标。', '3. 对出差、值班、执法、轮岗等现实强度相关字段做二次排雷。'])
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--profile', required=True)
    ap.add_argument('--positions', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    profile = parse_profile(args.profile)
    rows = []
    for pos in load_positions(args.positions):
        status, reject, risks = eligibility(profile, pos)
        s, reasons = score(profile, pos, status)
        rows.append({'title': pos.get('title') or '未命名岗位', 'agency': pos.get('agency') or '未注明机构', 'region': pos.get('region') or '未注明地区', 'status': status, 'reject': reject, 'risks': risks, 'score': s, 'level': level_tag(s, status), 'reasons': reasons, 'source': pos.get('source') or ''})
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(profile, rows), encoding='utf-8')


if __name__ == '__main__':
    main()
