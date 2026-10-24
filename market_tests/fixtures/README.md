Live public-source parser fixtures retrieved 2026-10-24 UTC. HTML trimmed to factual data/table structures; Cboe CSV limited to 12 final rows. Test-only synthetic mutations are never imported into market_data or COMEX history. Fixtures test parsing and accounting; they do not prove future availability.


v1.3 nyfed_calendar_oct.html / nyfed_calendar_nov.html：从2026年10月公开日历及其实际下月链接提取月标题、全部工作日格和事件事实，去除导航脚本。10月ECI20:30 MYT、11月就业21:30 MYT校验DST。提取fixture的hash不冒充完整原响应hash；原响应证据另存source-check。
