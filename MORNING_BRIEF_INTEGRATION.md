# 加入现有 8AM 晨报的 COMEX 数据规则

以下内容应添加到现有任务的指令，保留原晨报其他章节和排程。

```text
COMEX Gold 使用已部署的官方数据采集结果。
主来源：https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/latest.json
文字备用：https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/

如果网页读取失败，使用已连接的 GitHub 实际读取仓库 yydsdefi-cmyk/COMEX-Gold-Tracker 的默认分支文件 data/latest.json；文字文件为 data/daily_brief.md。
每次运行都重新读取文件，不用上一轮数字、搜索摘要或历史上传代替。不能读取时写“COMEX 云端数据无法读取”，不要猜。
检查 last_update.attempted_at_utc 与本次当前 UTC 时间；超过 26 小时明确标注“云端更新逾期”。
同时检查 available、update_status、Report Date 时效。更新 FAILED、数据 STALE 或报告日期已明显过旧时，明确写“上次可得数据（日期）”。
显示 Activity Date / Report Date、Total、Registered、Eligible、Registered Ratio、1D、5D、20D、库存阈值状态及实际来源链接。
null 表示暂不可计算，不是 0。Pledged 已包含在 Registered，不重复加。
Eligible 的单独下降不能解释为可交割黄金短缺；NORMAL 只表示 Total 单日变化未触发库存阈值。
Registered 快速或持续下降标记分别披露，不据此断言市场短缺。
```

2026-10-07 实测：云端 Actions 运行成功；应用内浏览器可读取 Pages，GitHub 连接可读取 data/latest.json。
同次网页检索工具对新发布的 Pages 和 GitHub 文件返回不可读取；晨报读取能力仍须在实际任务验证，不能假定每种工具都能访问。
首次历史核验为 1/20，5D 与 20D 暂不可计算。

原“市场反向指标晨报”任务的 COMEX 章节已更新并保存。重新加载后配置保持一致；单次 Run now 试运行成功展示了云端核验时间 09:28 UTC、真实库存与来源链接。
下一次夜间云端采集及原排程自动推送仍需由后续真实执行验证。

