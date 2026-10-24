# Source registry

运行时完整URL、来源类型、工程时效、解析器和限制：`market_data/source_registry.json`，发布到 `/market/source_registry.json`。逐次receipt含响应SHA256、字节数、抓取UTC、HTTP状态和实际解析结果。hash绑定响应字节，不构成来源真实性的独立签名；不是全部原网页的再发布档案。

|指标/主题|来源|说明|
|---|---|---|
|AAII|https://www.aaii.com/sentimentsurvey|公共最新及近期周度；周截至≠网页修改日期|
|CNN F&G|https://production.dataviz.cnn.io/index/fearandgreed/graphdata|官方origin非稳定公开API，拒绝访问时缺失|
|VIX/VIX3M|https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv 与VIX3M_History.csv|Cboe官方收盘CSV，同日才算期限比|
|Crypto F&G|https://api.alternative.me/fng/?limit=31&format=json|UTC供应商日戳和原分类|
|SRF|https://markets.newyorkfed.org/api/rp/repo/all/results/lastTwoWeeks.json|USD accepted，逐场、排除明确小额演习|
|Treasury拍卖|https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&days=30|公告日、拍卖日、USD规模、需求指标；不是未来未公告的供给|
|COMEX|https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker|同提交快照+collector workflow runs；官方源https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls|
|ICI|https://www.ici.org/research/stats/mmf|表格USD billions；资产变化不是净流|
|Overnight|https://query1.finance.yahoo.com/v8/finance/chart/|次级行情，^GSPC/^IXIC/^TNX/DX-Y.NYB/CL=F/GC=F/BTC-USD|
|日历BLS|https://www.bls.gov/schedule/news_release/bls.ics|官方时间，转换MYT|
|日历BEA|https://www.bea.gov/news/schedule|GDP/PCE等|
|FOMC|https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm|会议结束日；发布时间惯例假设另列|
|SEC|https://www.sec.gov/news/pressreleases.rss|公告窗口；未从每份正文穷尽法律含义|
|CFTC|https://www.cftc.gov/RSS/RSSGP/rssgp.xml|同上|
|Fed|https://www.federalreserve.gov/feeds/press_all.xml|同上|
|Treasury新闻|https://home.treasury.gov/news/press-releases|官方有日期索引|
|Congress/GPO|https://www.govinfo.gov/rss/bills.xml|立法文本发布，不覆盖全部表决/行动|
|White House|https://www.whitehouse.gov/presidential-actions/feed/|总统行动RSS|
|Federal Register|https://www.federalregister.gov/api/v1/documents.json|公共政府机器元数据；HTML/XML不是正式法律版本，正式PDF链接到GovInfo；生效日来自单文档JSON|

官方技术与费用参考：

- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- https://markets.newyorkfed.org/static/docs/markets-api.html
- https://www.treasurydirect.gov/legal-information/developers/web-api-security/
- https://www.federalregister.gov/developers/documentation/api/v1

来源变动或被拒时，不切换到无标注的第三方估计。周报使用有限官方渠道，不声称对整个美国监管信息完备。

v1.1新增来源：

|来源|用途与限制|
|---|---|
|https://www.occ.gov/rss/occ_news.xml |正式机构公告标题/摘要；最终规则公告不自动等于生效|
|https://www.govinfo.gov/bulkdata/BILLSTATUS/119/hr/BILLSTATUS-119hr3633.xml |119届CLARITY法案的官方行动和成法记录；不覆盖其它届次新法案发现|
|https://www.govinfo.gov/bulkdata/BILLSTATUS/119/s/BILLSTATUS-119s1582.xml |119届GENIUS法案的官方行动及Public Law记录；实施义务/日期另核|
|Federal Register完整日期窗口分页 |删除依赖不明确OR搜索语义的文本query；保留页响应hash、总count、覆盖状态和逐份相关文档元数据|
|https://www.ici.org/mm_summary_data_2025.xls |ICI当前官方页面链接的20周TNA工作簿；云端403未解决，只在HTML成功且明确链接时尝试。未知发布时间不推算|

公开来源云端验证证据：[source-verification-2026-10-24.json](evidence/source-verification-2026-10-24.json)。诊断探针为临时工作流，验收后移除；不持续换路由访问被拒来源。


v1.3：NYFed官方编辑日历 https://www.newyorkfed.org/research/calendars/nationalecon_cal ，实际NEXT MONTH示例 https://www.newyorkfed.org/research/calendars/i-nov26.html 。月份动态读取，不硬编码未来年月；这不是BLS站点访问恢复。云端两页HTTP200证据见evidence/v1.3-nyfed-source-check.json，run40071922697。

SRF制度参考 https://www.newyorkfed.org/markets/opolicy/operating_policy_251210 及其官方FAQ。Pages容量依据 https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits （2026-10-24核验，公开站点1GB上限）。
