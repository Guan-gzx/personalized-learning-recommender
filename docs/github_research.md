# GitHub 选型与借鉴记录

本项目在 2026-09-04 做了定向 GitHub 调研，最终选择“借鉴方法、保持本项目可运行”的整合方式。

| 项目 | 观察到的可借鉴点 | 本项目的落地 |
|---|---|---|
| [KG4EX.Exercise-Recommendation](https://github.com/chanllon/KG4EX.Exercise-Recommendation) | CIKM 2023 的可解释知识图谱习题推荐；使用知识掌握水平、下题出现概率和遗忘率，并强调路径解释 | 加入图谱邻域嵌入、前置路径解释、推荐高亮；不直接复制其训练代码或数据文件 |
| [knowledge-tracing-collection-pytorch](https://github.com/hcnoh/knowledge-tracing-collection-pytorch) | MIT 许可；覆盖 DKT、DKVMN、SAKT 和 GKT 等知识追踪模型，提供 ASSISTments 数据训练组织方式 | 保持纯 PyTorch 依赖，新增 `TemporalMasteryNet` 训练脚本和时间切分评估 |
| [Exercise-Recommendation-System](https://github.com/AiFangzhe/Exercise-Recommendation-System) | 概念感知知识追踪与策略推荐的研究路线 | 将“当前掌握状态 → 题目策略”抽象成可解释排序分数，先做可复现原型 |

## 许可证与复现边界

`knowledge-tracing-collection-pytorch` 的仓库元数据标注 MIT；KG4Ex 仓库页面主要提供论文和实验说明，未在页面上发现明确的开源许可证。因此本项目只引用公开论文/README 中的设计思想，未复制其源代码、模型权重或数据。真实实验仍需从 ASSISTments 或 EdNet 官方渠道取得并遵守数据许可。
