Live public-source parser fixtures retrieved 2026-10-24 UTC. HTML trimmed to factual data/table structures; Cboe CSV limited to 12 final rows. Test-only synthetic mutations are never imported into market_data or COMEX history. Fixtures test parsing and accounting; they do not prove future availability.


v1.3 nyfed_calendar_oct.html / nyfed_calendar_nov.html：从2026年10月公开日历及其实际下月链接提取月标题、全部工作日格和事件事实，去除导航脚本。10月ECI20:30 MYT、11月就业21:30 MYT校验DST。提取fixture的hash不冒充完整原响应hash；原响应证据另存source-check。

v1.4 macro fixtures (2026-11-28)：eia_crude.html / eia_spr.html 按 EIA dnav LeafHandler 实际表格结构（table.FloatTitle、B6 年月、B5 日期、B3 数值）构造；2026-09/10 的数值抄自 2026-11-28 页面上的实际数值，截到测试时钟 2026-10-24 之前。ust_curve.csv 按美国财政部 daily_treasury_yield_curve CSV 的实际表头构造，数值是测试用的合成数据，不代表真实收益率。
