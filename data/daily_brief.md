# COMEX Gold — 官方库存数据

数据生成时间：2026-10-07T09:24:39.797544+00:00
更新状态：UNCHANGED；数据时效：WITHIN_AGE_LIMIT
库存日期（Activity Date）：**2026-10-05**；报告日期：2026-10-06

单位：troy oz（金衡盎司）；保持 CME Gold Stocks 原始 Combined Total 口径（GC/4GC）。

| 项目 | 库存 | 单日变化 | 单日变化 % |
|---|---:|---:|---:|
| Combined Total | 23,479,618.522 | +0.000 | 0.000000% |
| Registered | 15,086,528.079 | +0.000 | 0.000000% |
| Eligible | 8,393,090.443 | +0.000 | 0.000000% |

Registered Ratio：64.253719%
库存变化分级：NORMAL（用户阈值，非 CME 风险评级）。

单日变化直接核对 CME PREV TOTAL 与 TOTAL TODAY；不补造前一个日期的历史记录。
5D 变化：暂不可计算（INSUFFICIENT_HISTORY）。
20D 变化：暂不可计算（INSUFFICIENT_HISTORY）。

Pledged 已在 Registered 内，不另加；Eligible 单独下降不等于交割黄金短缺。
Registered 快速下降标记：False；连续下降标记：None
原始报告 SHA-256：`8e75b564bc56aed654325f48bdaa28a2e17d4e698bffc0ab22ff1b83d15ef0d0`
原始文件：`raw/2026-10-05/8e75b564bc56aed654325f48bdaa28a2e17d4e698bffc0ab22ff1b83d15ef0d0.xls`

20 日核验进度：1/20（INCOMPLETE）。
未取得日期只是工作日候选，不代表已确认的 CME 交易日。
来源：[CME Gold Stocks 原始文件](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)；[官方入口](https://www.cmegroup.com/solutions/clearing/operations-and-deliveries/nymex-delivery-notices.html)。

## 交给日报对话的约束

请引用上面的真实数值，并同时保留 Activity Date 与 Report Date。若更新失败或数据过旧，明确写上次可得数据及日期；
缺失的 5D/20D 不估算、不写成 0；NORMAL 仅表示本报告总库存单日变化未触发用户阈值，不能表示不存在市场风险。
这份文件是一次数据快照，未来日报需要新下载并核验的版本。
