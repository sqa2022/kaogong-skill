# Demo script

## 60 秒演示脚本

1. 打开示例题：`examples/topic-material-01.md`
2. 执行：`/shenlun analyze national examples/topic-material-01.md`
3. 展示输出中的“核心矛盾、主立意、提纲”
4. 再执行：`/shenlun grade national examples/student-draft-weak.md`
5. 展示“总分、失分点、局部改写、7 天提升计划”
6. 最后执行：`python .claude/skills/shenlun/scripts/render_report.py .claude/skills/shenlun/templates/grading-report.json.example outputs/demo-report.html`
7. 打开 `outputs/demo-report.html` 截图

## 适合截的 4 张图

- 审题拆解
- 低分稿关键失分点
- 改写前后对比
- HTML 评分雷达图
