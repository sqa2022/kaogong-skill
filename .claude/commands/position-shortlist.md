请读取 `inputs/profile.md` 与 `inputs/positions.csv`，按照仓库中的岗位推荐 skill 完成一次岗位初筛与排序，并将结果写入 `outputs/shortlist.md`。

要求：
1. 先做硬性筛选，再做偏好排序。
2. 对所有边界条件显式标注“待核验”。
3. 输出至少包含：结论摘要、候选人画像摘要、明确不可报岗位、推荐岗位 Top N、下一步建议。
4. 推荐岗位需要给出：推荐等级、推荐理由、风险点、建议核验项。

如果用户通过参数传入文件路径，则优先使用参数。否则使用默认路径：
- profile: `inputs/profile.md`
- positions: `inputs/positions.csv`
- output: `outputs/shortlist.md`
