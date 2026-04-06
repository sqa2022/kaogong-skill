# Claude Code Shenlun Skill

把一篇申论题目或草稿，变成结构化审题、参考范文、分项评分和可视化批改报告。

这个仓库当前只做一件事：把 **申论** 做成一个能直接演示、直接截图、直接传播的 Claude Code skill。首版不追求“大而全”的考公平台，而是先把最有传播力、最容易建立口碑的一条链路做透。

## 能做什么

`/shenlun` 当前聚焦三类任务：

- `analyze`：审题、题型判断、立意、提纲、写作辅助
- `exemplar`：按主题检索本地参考范文；不匹配时生成 AI 参考范文
- `grade`：对用户提交的申论进行分项评分、逐段点评、失分诊断和改写建议

## 一句话示例

`/shenlun analyze national examples/prompt-demo.md`

`/shenlun exemplar national 基层治理`

`/shenlun grade national examples/student-draft-demo.md`

## 为什么先只做申论

因为申论最适合 skill 形态：

1. 输入天然结构化：题干、材料、作答要求、草稿。
2. 输出天然可展示：提纲、范文、评分表、HTML 报告。
3. 传播上更有冲击力：审题前后对比、低分稿改写、高分表达替换，都很适合截图和短视频。

## 当前设计原则

### 1. 单入口命令

对外只保留一个命令 `/shenlun`，通过 mode 切换任务，降低记忆成本。

### 2. 先检索，后生成

范文模式优先检索本地样本库，只有相似样本不足时才生成新的 AI 参考范文，减少“每次都长得差不多”的问题。

### 3. 内部评分框架而非“官方原文”

`rubric.md` 与 `profiles/` 下的内容是仓库内部的操作化框架，目的是让批改更稳定，而不是伪装成真实考试机构的官方评分条文。

### 4. 输出要可落地

所有模式都要求输出能直接拿去练习，而不是停留在泛泛建议层：

- `analyze` 要给可写作提纲
- `exemplar` 要说明可借鉴点
- `grade` 要给失分证据、局部改写和 7 天提升计划

## 仓库结构

```text
.claude/skills/shenlun/
├── SKILL.md
├── references/
│   ├── modes.md
│   ├── rubric.md
│   ├── phrases.md
│   ├── exemplar-policy.md
│   ├── profiles/
│   │   ├── national.md
│   │   ├── beijing.md
│   │   └── jiangsu-a.md
│   └── exemplars/
│       ├── community-governance.md
│       ├── digital-governance.md
│       ├── rural-revitalization.md
│       ├── elderly-care.md
│       ├── grassroots-burden-reduction.md
│       ├── business-environment.md
│       ├── employment-first.md
│       ├── emergency-response.md
│       ├── ecological-governance.md
│       └── cultural-renewal.md
├── scripts/
│   ├── render_report.py
│   └── build_exemplar_index.py
└── templates/
    ├── grading-report.json.example
    └── analysis-output.md
examples/
├── prompt-demo.md
├── topic-material-01.md
├── student-draft-demo.md
├── student-draft-weak.md
└── student-draft-revised.md
docs/
├── roadmap.md
├── shenlun-branch-scope.md
└── demo-script.md
eval/
├── cases.md
└── rubric-checklist.md
outputs/
└── demo-report.html
```

## 快速安装

把整个 `.claude/skills/shenlun` 目录拷到你的项目里即可。

项目级安装示例：

`mkdir -p .claude/skills && cp -R /path/to/this-repo/.claude/skills/shenlun .claude/skills/`

## 建议演示顺序

### 演示一：审题到写作

`/shenlun analyze national examples/topic-material-01.md`

预期看到：题型判断、核心矛盾、主立意、提纲、可直接起笔的正文框架。

### 演示二：主题范文检索

`/shenlun exemplar national 基层治理`

预期看到：相似主题样本、每篇可借鉴点、必要时给出新的 AI 参考范文。

### 演示三：批改打分

`/shenlun grade national examples/student-draft-weak.md`

预期看到：总分、分项分、逐段点评、关键失分点、建议改写。

### 演示四：导出 HTML 报告

`python .claude/skills/shenlun/scripts/render_report.py .claude/skills/shenlun/templates/grading-report.json.example outputs/demo-report.html`

## 适合做内容传播的展示点

1. **低分稿 → 改写稿**：最容易形成转发。
2. **审题拆解卡**：适合做图文封面。
3. **分项评分雷达图/报告**：更容易建立“专业感”。
4. **同一主题多篇范文对比**：有利于引发评论区讨论。

## 这版还不做什么

- 不做行测
- 不做职位表匹配
- 不做实时招录公告抓取
- 不承诺与真实阅卷口径一一对应

## 下一步优先级

1. 扩充本地范文库到 20–30 篇
2. 补 10 个标准化评测样本
3. 增加 profile 化权重和题型约束
4. 优化 HTML 报告样式，适合截图传播

## 许可证

MIT
