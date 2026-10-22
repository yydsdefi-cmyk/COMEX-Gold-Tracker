# COMEX Gold — 官方库存数据

数据生成时间：2026-10-22T21:41:44.601910+00:00
更新状态：OK；数据时效：WITHIN_AGE_LIMIT
库存日期（Activity Date）：**2026-10-21**；报告日期：2026-10-22

单位：troy oz（金衡盎司）；保持 CME Gold Stocks 原始 Combined Total 口径（GC/4GC）。

| 项目 | 库存 | 单日变化 | 单日变化 % |
|---|---:|---:|---:|
| Combined Total | 23,343,063.686 | -61,317.544 | -0.261992% |
| Registered | 14,816,969.006 | +0.000 | 0.000000% |
| Eligible | 8,526,094.680 | -61,317.544 | -0.714040% |

Registered Ratio：63.474826%
库存变化分级：NORMAL（用户阈值，非 CME 风险评级）。

单日变化直接核对 CME PREV TOTAL 与 TOTAL TODAY；不补造前一个日期的历史记录。
5D 变化：-0.496159%（AVAILABLE_CONSECUTIVE_WEEKDAYS）。
10D 变化：-0.572739%（AVAILABLE_CONSECUTIVE_WEEKDAYS）。
20D 变化：-0.056783%（AVAILABLE_CONSECUTIVE_WEEKDAYS）。

| 库存分类 | 5D 变化 | 10D 变化 | 20D 变化 |
|---|---:|---:|---:|
| Registered | +0.000 oz / +0.000000% | -250,172.020 oz / -1.660381% | -368,655.836 oz / -2.427663% |
| Eligible | -116,396.165 oz / -1.346790% | +115,706.999 oz / +1.375763% | +355,393.451 oz / +4.349608% |
历史余额衔接异常：2026-09-18 → 2026-09-21。相邻报告前后余额不一致，原因未确认，不能解读为同量实物出库。

Pledged 已在 Registered 内，不另加；Eligible 单独下降不等于交割黄金短缺。
Registered 快速下降标记：False；连续下降标记：False
原始报告 SHA-256：`3a0f46fd1df52d3c44196487239ad035db0b0eeaf6ffcbf2bbad8e591ec30241`
原始文件：`raw/2026-10-21/3a0f46fd1df52d3c44196487239ad035db0b0eeaf6ffcbf2bbad8e591ec30241.xls`

20 日核验进度：20/20（COMPLETE_20_OBSERVATIONS）。
未取得日期只是工作日候选，不代表已确认的 CME 交易日。
来源：[CME Gold Stocks 原始文件](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)；[官方入口](https://www.cmegroup.com/solutions/clearing/operations-and-deliveries/nymex-delivery-notices.html)。

## 交给日报对话的约束

请引用上面的真实数值，并同时保留 Activity Date 与 Report Date。若更新失败或数据过旧，明确写上次可得数据及日期；
5D/10D/20D 按已核验的连续工作日候选报告计算，不是自然日；每个窗口保留实际基准日期。缺失的变化不估算、不写成 0；NORMAL 仅表示本报告总库存单日变化未触发用户阈值，不能表示不存在市场风险。
这份文件是一次数据快照，未来日报需要新下载并核验的版本。
