# COMEX Gold — 官方库存数据

数据生成时间：2026-11-25T04:10:45.483619+00:00
更新状态：OK；数据时效：WITHIN_AGE_LIMIT
库存日期（Activity Date）：**2026-11-23**；报告日期：2026-11-24

单位：troy oz（金衡盎司）；保持 CME Gold Stocks 原始 Combined Total 口径（GC/4GC）。

| 项目 | 库存 | 单日变化 | 单日变化 % |
|---|---:|---:|---:|
| Combined Total | 22,748,372.335 | -1,125.285 | -0.004946% |
| Registered | 14,250,257.194 | +50,661.365 | 0.356780% |
| Eligible | 8,498,115.141 | -51,786.650 | -0.605699% |

Registered Ratio：62.642975%
库存变化分级：NORMAL（用户阈值，非 CME 风险评级）。

单日变化直接核对 CME PREV TOTAL 与 TOTAL TODAY；不补造前一个日期的历史记录。
5D 变化：-1.077116%（AVAILABLE_CONSECUTIVE_WEEKDAYS）。
10D 变化：-1.076293%（AVAILABLE_CONSECUTIVE_WEEKDAYS）。
20D 变化：-1.932453%（AVAILABLE_CONSECUTIVE_WEEKDAYS）。

| 库存分类 | 5D 变化 | 10D 变化 | 20D 变化 |
|---|---:|---:|---:|
| Registered | +62,668.046 oz / +0.441710% | +8,755.822 oz / +0.061481% | -573,583.250 oz / -3.869330% |
| Eligible | -310,362.451 oz / -3.523452% | -256,258.768 oz / -2.927208% | +125,319.119 oz / +1.496742% |
历史余额衔接异常：2026-09-18 → 2026-09-21。相邻报告前后余额不一致，原因未确认，不能解读为同量实物出库。

Pledged 已在 Registered 内，不另加；Eligible 单独下降不等于交割黄金短缺。
Registered 快速下降标记：False；连续下降标记：False
原始报告 SHA-256：`0f359ac45eb6c38a8b89d3e9a2680c020e4fc5e6dacd151ae265a74177b2abd3`
原始文件：`raw/2026-11-23/0f359ac45eb6c38a8b89d3e9a2680c020e4fc5e6dacd151ae265a74177b2abd3.xls`

20 日核验进度：20/20（COMPLETE_20_OBSERVATIONS）。
未取得日期只是工作日候选，不代表已确认的 CME 交易日。
来源：[CME Gold Stocks 原始文件](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)；[官方入口](https://www.cmegroup.com/solutions/clearing/operations-and-deliveries/nymex-delivery-notices.html)。

## 交给日报对话的约束

请引用上面的真实数值，并同时保留 Activity Date 与 Report Date。若更新失败或数据过旧，明确写上次可得数据及日期；
5D/10D/20D 按已核验的连续工作日候选报告计算，不是自然日；每个窗口保留实际基准日期。缺失的变化不估算、不写成 0；NORMAL 仅表示本报告总库存单日变化未触发用户阈值，不能表示不存在市场风险。
这份文件是一次数据快照，未来日报需要新下载并核验的版本。
