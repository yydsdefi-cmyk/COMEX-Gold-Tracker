# COMEX Gold — 官方库存数据

数据生成时间：2026-11-14T03:31:53.920477+00:00
更新状态：UNCHANGED；数据时效：WITHIN_AGE_LIMIT
库存日期（Activity Date）：**2026-11-12**；报告日期：2026-11-13

单位：troy oz（金衡盎司）；保持 CME Gold Stocks 原始 Combined Total 口径（GC/4GC）。

| 项目 | 库存 | 单日变化 | 单日变化 % |
|---|---:|---:|---:|
| Combined Total | 22,904,341.590 | -25,849.198 | -0.112730% |
| Registered | 14,220,956.883 | -20,544.489 | -0.144258% |
| Eligible | 8,683,384.707 | -5,304.709 | -0.061053% |

Registered Ratio：62.088477%
库存变化分级：NORMAL（用户阈值，非 CME 风险评级）。

单日变化直接核对 CME PREV TOTAL 与 TOTAL TODAY；不补造前一个日期的历史记录。
5D 变化：-0.386404%（AVAILABLE_CONSECUTIVE_WEEKDAYS）。
10D 变化：-1.290910%（AVAILABLE_CONSECUTIVE_WEEKDAYS）。
20D 变化：-2.228184%（AVAILABLE_CONSECUTIVE_WEEKDAYS）。

| 库存分类 | 5D 变化 | 10D 变化 | 20D 变化 |
|---|---:|---:|---:|
| Registered | -122,541.107 oz / -0.854332% | -588,545.788 oz / -3.974109% | -596,012.123 oz / -4.022497% |
| Eligible | +33,694.459 oz / +0.389545% | +289,004.615 oz / +3.442835% | +74,030.419 oz / +0.859884% |
历史余额衔接异常：2026-09-18 → 2026-09-21。相邻报告前后余额不一致，原因未确认，不能解读为同量实物出库。

Pledged 已在 Registered 内，不另加；Eligible 单独下降不等于交割黄金短缺。
Registered 快速下降标记：False；连续下降标记：False
原始报告 SHA-256：`98c128268999ec354300871ce9ba35273447620e9a0e68be1dfa5e63e8b385fb`
原始文件：`raw/2026-11-12/98c128268999ec354300871ce9ba35273447620e9a0e68be1dfa5e63e8b385fb.xls`

20 日核验进度：20/20（COMPLETE_20_OBSERVATIONS）。
未取得日期只是工作日候选，不代表已确认的 CME 交易日。
来源：[CME Gold Stocks 原始文件](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)；[官方入口](https://www.cmegroup.com/solutions/clearing/operations-and-deliveries/nymex-delivery-notices.html)。

## 交给日报对话的约束

请引用上面的真实数值，并同时保留 Activity Date 与 Report Date。若更新失败或数据过旧，明确写上次可得数据及日期；
5D/10D/20D 按已核验的连续工作日候选报告计算，不是自然日；每个窗口保留实际基准日期。缺失的变化不估算、不写成 0；NORMAL 仅表示本报告总库存单日变化未触发用户阈值，不能表示不存在市场风险。
这份文件是一次数据快照，未来日报需要新下载并核验的版本。
