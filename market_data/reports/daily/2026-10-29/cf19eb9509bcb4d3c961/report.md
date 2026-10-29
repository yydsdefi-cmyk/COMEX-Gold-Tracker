# 市场反向指标晨报｜2026-10-29

生成 09:40 MYT｜目标08:00 MYT｜规则生成，无LLM/API订阅。

## 7项总览

- 美股情绪：部分数据待确认，极端共振不能确认。

- Crypto：最新 51，与昨日/7日前分开核对。

- Event Risk：3项已读取日历候选；覆盖限制见下。

- SRF：Normal，不等同QE判断。

- Treasury：未来7日已公告供给分Bills/Coupon。

- COMEX：当天核验通过；库存风险另列。

- Cash Liquidity：待确认。

## Overnight（各自日期，非同步实时行情）

- S&P 500 **7,743.98** +0.28%｜观察 2026-10-28｜发布 未提供

- Nasdaq **26,549.85** +0.27%｜观察 2026-10-28｜发布 未提供

- US10Y **5.05** +5.20bp｜观察 2026-10-28｜发布 未提供

- DXY **待确认** 待确认%｜观察/发布：待确认

- WTI期货 **101.85** +1.95%｜观察 2026-10-28｜发布 未提供

- Gold期货 **4,077.00** +0.06%｜观察 2026-10-28｜发布 未提供

- BTC/USD **80,498.02** -0.38%｜观察 2026-10-29｜发布 未提供

Yahoo为次级来源；期货与现货有差异，最新日线可能仍在交易中，报价时刻见JSON。

## US Contrarian

AAII Bull/Neutral/Bear 36.9/17.3/45.8%｜Spread -8.9pp｜观察 2026-10-21｜发布 未提供

CNN F&G 待确认 ｜观察/发布：待确认

VIX 16.91｜观察 2026-10-28｜发布 未提供

VIX3M 19.22｜观察 2026-10-28｜发布 未提供

同日 2026-10-28 VIX/VIX3M **0.880** → Contango（期限比率标签，不代表VIX期货曲线全部形状）

解读：原规格未给AAII/VIX极端情绪数值阈值，三项共同极端状态保留待确认，不新增买卖信号。

## Crypto F&G（Alternative.me）

今日 2026-10-29｜51 Neutral

昨日 2026-10-28｜51 Neutral

7日前 2026-10-22｜68 Greed

观察日期以供应商UTC日戳为准；不拿“最新一条”冒充今日。

## 今日Event Risk（MYT）

- 2026-10-29 02:00 MYT｜FOMC利率决定（[Fed calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)）

- 2026-10-29 20:30 MYT｜GDP（[BEA](https://www.bea.gov/news/schedule) / [NYFed calendar](https://www.newyorkfed.org/research/calendars/nationalecon_cal)）

- 2026-10-29 20:30 MYT｜个人收入与PCE（[BEA](https://www.bea.gov/news/schedule) / [NYFed calendar](https://www.newyorkfed.org/research/calendars/nationalecon_cal)）

⚠ 日历覆盖待确认：bls

补充：纽约联储公开日历可旁证部分事件，不代表BLS直连已恢复；日历日期/时刻可能调整。

范围：美国BLS/BEA/FOMC及NYFed日历；不含付费共识预期与自动因果归因。FOMC时刻按14:00 ET惯例估计，临时变更待核验。

## SRF（常规隔夜操作）

$0.006000B → Normal｜观察 2026-10-28｜发布 未提供｜2场；完整度规则通过｜最后修订 2026-10-28T17:45:29+00:00（首次发布时间未单列）

API窗口内排除小额测试 1场；逐笔证据见JSON。

## Treasury

Bills｜已公告未来7日合计 **225.00B USD**（非尚未公告的完整供给预测）

Coupon（含TIPS/FRN）｜已公告未来7日合计 **44.00B USD**（非尚未公告的完整供给预测）

- 2026-10-29 ET｜Bill 4-Week｜$115.00B｜公告 2026-10-27｜MYT 2026-10-29T23:30:00+08:00

- 2026-10-29 ET｜Note 7-Year｜$44.00B｜公告 2026-10-22｜MYT 2026-10-30T01:00:00+08:00

- 2026-10-29 ET｜Bill 8-Week｜$110.00B｜公告 2026-10-27｜MYT 2026-10-29T23:30:00+08:00

最近coupon：2026-10-27 5-Year｜Bid-to-cover 2.33｜High yield 4.845%｜Tail/stop-through 待确认（无可核验WI收益率）。

最近coupon：2026-10-28 2-Year｜Bid-to-cover 3.05｜High yield 待确认%｜Tail/stop-through 待确认（无可核验WI收益率）。

## COMEX Gold

读取：GitHub提交 bf15ec31｜核验MYT 10-29 09:40｜采集尝试MYT 10-29 08:09:04｜数据核验通过

Activity 2026-10-27｜Report 2026-10-28｜UNCHANGED / WITHIN_AGE_LIMIT

Registered Ratio **63.900%**｜库存风险 NORMAL

|分类|当前 M oz|1D|5D|10D|20D|
|---|---:|---:|---:|---:|---:|
|Total|23.207|+0.044%|-0.844%|-1.147%|-0.992%|
|Registered|14.829|+0.035%|+0.082%|-0.322%|-2.042%|
|Eligible|8.378|+0.059%|-2.441%|-2.575%|+0.924%|

窗口：1D 官方PREV TOTAL / CME_PREV_TOTAL；5D 2026-10-20 / AVAILABLE_CONSECUTIVE_WEEKDAYS；10D 2026-10-13 / AVAILABLE_CONSECUTIVE_WEEKDAYS；20D 2026-09-29 / AVAILABLE_CONSECUTIVE_WEEKDAYS

历史衔接异常：2026-09-18→2026-09-21 PREVIOUS_BALANCE_MISMATCH_OR_REVISION；不可跨异常自行相减或推断实物出库。

官方最新发布状态未独立确认。

Pledged已在Registered内；Eligible单独下降不证明交割短缺；NORMAL仅指Total单日库存阈值。

[核验快照](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/blob/bf15ec31931e6f32ffeedf958f557b3e35a5723d/data/latest.json)｜[CME官方报告](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)

## Cash Liquidity / ICI

总资产 $待确认T｜周资产变化 $待确认B｜观察/发布：待确认

精确周净流量、约3个月已核验资金流趋势：待确认。资产高不等于近期逃向现金，也不意味着必然回流股市。

## 数据质量与来源

⚠ 缺失/过期/未核验：bls, cnn, dxy, ici。发布时间未提供则明确留空；抓取时间不代替发布时间。

本报告区分观察与解读；排除BTC seasonality、自选股、X讨论和普通财报清单。

- [aaii](https://www.aaii.com/sentimentsurvey)｜OK｜抓取 2026-10-29T01:40:48.707226+00:00

- [bea](https://www.bea.gov/news/schedule)｜OK｜抓取 2026-10-29T01:40:48.767461+00:00

- [bls](https://www.bls.gov/schedule/news_release/bls.ics)｜MISSING｜抓取 2026-10-29T01:40:46.475536+00:00｜HTTPError: HTTP Error 403: Forbidden

- [btc](https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=1mo&interval=1d)｜OK｜抓取 2026-10-29T01:40:49.516378+00:00

- [cftc](https://www.cftc.gov/RSS/RSSGP/rssgp.xml)｜OK｜抓取 2026-10-29T01:40:48.895933+00:00

- [clarity_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/hr/BILLSTATUS-119hr3633.xml)｜OK｜抓取 2026-10-29T01:40:48.947322+00:00

- [cnn](https://production.dataviz.cnn.io/index/fearandgreed/graphdata)｜MISSING｜抓取 2026-10-29T01:40:46.475536+00:00｜HTTPError: HTTP Error 418: Unknown Error

- [congress](https://www.govinfo.gov/rss/bills.xml)｜OK｜抓取 2026-10-29T01:40:49.039864+00:00

- [crypto](https://api.alternative.me/fng/?limit=31&format=json)｜OK｜抓取 2026-10-29T01:40:48.466547+00:00

- [dxy](https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?range=1mo&interval=1d)｜MISSING｜抓取 2026-10-29T01:40:49.334989+00:00｜ValueError: Duplicate indicator observation date

- [fed](https://www.federalreserve.gov/feeds/press_all.xml)｜OK｜抓取 2026-10-29T01:40:48.973120+00:00

- [federal_register](https://www.federalregister.gov/api/v1/documents.json?conditions%5Bpublication_date%5D%5Bgte%5D=2026-10-22&conditions%5Bpublication_date%5D%5Blte%5D=2026-10-28&order=oldest&per_page=100&page=1)｜OK｜抓取 2026-10-29T01:40:49.185129+00:00

- [fomc](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)｜OK｜抓取 2026-10-29T01:40:48.810253+00:00

- [genius_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/s/BILLSTATUS-119s1582.xml)｜OK｜抓取 2026-10-29T01:40:48.984619+00:00

- [gold](https://query1.finance.yahoo.com/v8/finance/chart/GC%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-10-29T01:40:49.405378+00:00

- [ici](https://www.ici.org/research/stats/mmf)｜MISSING｜抓取 2026-10-29T01:40:46.475536+00:00｜HTTPError: HTTP Error 403: Forbidden

- [nasdaq](https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?range=1mo&interval=1d)｜OK｜抓取 2026-10-29T01:40:49.272096+00:00

- [nyfed_calendar](https://www.newyorkfed.org/research/calendars/nationalecon_cal)｜OK｜抓取 2026-10-29T01:40:48.878476+00:00

- [occ](https://www.occ.gov/rss/occ_news.xml)｜OK｜抓取 2026-10-29T01:40:48.920405+00:00

- [sec](https://www.sec.gov/news/pressreleases.rss)｜OK｜抓取 2026-10-29T01:40:48.869842+00:00

- [sp500](https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=1mo&interval=1d)｜OK｜抓取 2026-10-29T01:40:49.174595+00:00

- [srf](https://markets.newyorkfed.org/api/rp/repo/all/results/lastTwoWeeks.json)｜OK｜抓取 2026-10-29T01:40:48.833479+00:00

- [treasury](https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&days=30)｜OK｜抓取 2026-10-29T01:40:48.754702+00:00

- [treasury_news](https://home.treasury.gov/news/press-releases)｜OK｜抓取 2026-10-29T01:40:57.183709+00:00

- [us10y](https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX?range=1mo&interval=1d)｜OK｜抓取 2026-10-29T01:40:49.329466+00:00

- [vix](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv)｜OK｜抓取 2026-10-29T01:40:48.513364+00:00

- [vix3m](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv)｜OK｜抓取 2026-10-29T01:40:48.483475+00:00

- [whitehouse](https://www.whitehouse.gov/presidential-actions/feed/)｜OK｜抓取 2026-10-29T01:40:49.072903+00:00

- [wti](https://query1.finance.yahoo.com/v8/finance/chart/CL%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-10-29T01:40:49.400723+00:00

- [comex](https://api.github.com/repos/yydsdefi-cmyk/COMEX-Gold-Tracker)｜OK｜抓取 2026-10-29T01:40:58.263013+00:00
