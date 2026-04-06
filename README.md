# Claude Code Shenlun Skill

一个面向 Claude Code 的申论 skill 仓库，当前分支 `feat/shenlun-core` 只聚焦申论主链路：审题分析、立意提纲、写作辅助、范文检索/生成、批改评分。

## 当前设计取向

这个分支不追求“大而全”的考公助手，而是先把申论做成一个能被演示、能被截图、能被传播的单点工具。对外只暴露一个主命令：`/shenlun`。

这样做有两个好处：

1. 传播上简单：一句话就能讲明白，“一个命令完成申论审题、范文、批改”。
2. 维护上收敛：冷启动阶段先把一条链路做透，后续再拆成更细的 skill 或接 MCP 数据源。

## 当前能力范围

`/shenlun` 至少覆盖三类任务：

1. `analyze`：题目分析讲解并辅助写作。
2. `exemplar`：从本地范文库检索近似主题；检索不到时生成 AI 参考范文。
3. `grade`：按内部操作化 rubric 对用户提交的申论进行打分、批改、改写。

## 建议调用方式

`/shenlun analyze national examples/prompt-demo.md`

`/shenlun exemplar national 基层治理`

`/shenlun grade national examples/student-draft-demo.md`

## 仓库结构

```text
.claude/skills/shenlun/
├── SKILL.md
├── references/
│   ├── modes.md
│   ├── rubric.md
│   ├── exemplar-policy.md
│   └── exemplars/
│       ├── community-governance.md
│       ├── digital-governance.md
│       └── rural-revitalization.md
├── scripts/
│   └── render_report.py
└── templates/
    └── grading-report.json.example
examples/
├── prompt-demo.md
└── student-draft-demo.md
docs/
├── roadmap.md
└── shenlun-branch-scope.md
```

## 设计原则

### 1. 单命令入口

用户只需要记住 `/shenlun`，其余通过 mode 参数切换。

### 2. 范文能力分两层

先查本地 AI 参考范文库，再决定是否生成新的参考范文。这样演示更稳定，也便于后续扩展成真正的检索库。

### 3. 评分与“官方标准”分离

当前 `rubric.md` 是为了让批改输出稳定、可复现、可迭代的“内部操作化评分框架”，不是官方阅卷标准原文。

### 4. 输出尽量结构化

批改任务不仅给总评，还要求给分项分、失分证据、局部改写、整篇提升方案，并可选生成 HTML 报告。

## 这版还没有做的事

1. 没接入实时政策/时评/公告数据源。
2. 没接真实年份和地区的精细评分 profile。
3. 没做 benchmark/eval 自动化。
4. 没把范文库扩到真正可用的规模。

## 下一步最值钱的增量

1. 补 20–30 篇高质量 AI 参考范文与题材索引。
2. 加 10 个标准化评测 case，做前后对比截图。
3. 把 `grade` 输出接成视觉化 HTML 报告。
4. 再决定是否拆成更细的 skill。
