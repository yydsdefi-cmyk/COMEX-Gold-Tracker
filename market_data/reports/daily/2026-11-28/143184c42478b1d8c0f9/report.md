# 市场反向指标晨报｜2026-11-28

生成 23:10 MYT｜目标08:00 MYT｜规则生成，无LLM/API订阅。

## 7项总览

- 美股情绪：部分数据待确认，极端共振不能确认。

- Crypto：最新 10，与昨日/7日前分开核对。

- Event Risk：0项已读取日历候选；覆盖限制见下。

- SRF：Stress，不等同QE判断。

- Treasury：未来7日已公告供给分Bills/Coupon。

- COMEX：当天核验通过；库存风险另列。

- Cash Liquidity：待确认。

## Overnight（各自日期，非同步实时行情）

- S&P 500 **7,297.49** +1.60%｜观察 2026-11-27｜发布 未提供

- Nasdaq **24,129.50** +2.31%｜观察 2026-11-27｜发布 未提供

- US10Y **4.94** +8.80bp｜观察 2026-11-27｜发布 未提供

- DXY **104.01** +0.33%｜观察 2026-11-27｜发布 未提供

- WTI期货 **83.08** -0.72%｜观察 2026-11-27｜发布 未提供

- Gold期货 **3,639.60** +2.94%｜观察 2026-11-27｜发布 未提供

- BTC/USD **59,318.79** -0.91%｜观察 2026-11-28｜发布 未提供

Yahoo为次级来源；期货与现货有差异，最新日线可能仍在交易中，报价时刻见JSON。

## US Contrarian

AAII Bull/Neutral/Bear 37.1/17.5/45.4%｜Spread -8.3pp｜观察 2026-11-25｜发布 未提供

CNN F&G 待确认 ｜观察/发布：待确认

VIX 23.81｜观察 2026-11-27｜发布 未提供

VIX3M 23.82｜观察 2026-11-27｜发布 未提供

同日 2026-11-27 VIX/VIX3M **1.000** → Contango（期限比率标签，不代表VIX期货曲线全部形状）

解读：原规格未给AAII/VIX极端情绪数值阈值，三项共同极端状态保留待确认，不新增买卖信号。

## Crypto F&G（Alternative.me）

今日 2026-11-28｜10 Extreme Fear

昨日 2026-11-27｜12 Extreme Fear

7日前 2026-11-21｜12 Extreme Fear

观察日期以供应商UTC日戳为准；不拿“最新一条”冒充今日。

## 今日Event Risk（MYT）

已读取日历内未发现符合筛选的Tier-1事件；不等于完整全球经济日历无事件。

⚠ 日历覆盖待确认：bls

补充：纽约联储公开日历可旁证部分事件，不代表BLS直连已恢复；日历日期/时刻可能调整。

范围：美国BLS/BEA/FOMC及NYFed日历；不含付费共识预期与自动因果归因。FOMC时刻按14:00 ET惯例估计，临时变更待核验。

## SRF（常规隔夜操作）

$23.150000B → Stress｜观察 2026-11-27｜发布 未提供｜2场；完整度规则通过｜最后修订 2026-11-27T18:45:28+00:00（首次发布时间未单列）

观察：流动性使用量触发用户监控等级；超过$100B也不代表必然QE。

## Treasury

Bills｜已公告未来7日合计 **267.00B USD**（非尚未公告的完整供给预测）

Coupon（含TIPS/FRN）｜已公告未来7日合计 **待确认**（非尚未公告的完整供给预测）

- 2026-11-30 ET｜Bill 13-Week｜$95.00B｜公告 2026-11-25｜MYT 2026-12-01T00:30:00+08:00

- 2026-11-30 ET｜Bill 26-Week｜$82.00B｜公告 2026-11-25｜MYT 2026-12-01T00:30:00+08:00

- 2026-12-01 ET｜Bill 6-Week｜$90.00B｜公告 2026-11-25｜MYT 2026-12-02T00:30:00+08:00

最近coupon：2026-11-25 7-Year｜Bid-to-cover 2.43｜High yield 4.708%｜Tail/stop-through 待确认（无可核验WI收益率）。

## COMEX Gold

读取：GitHub提交 43ab3217｜核验MYT 11-28 23:10｜采集尝试MYT 11-28 11:18:42｜数据核验通过

Activity 2026-11-25｜Report 2026-11-27｜OK / WITHIN_AGE_LIMIT

Registered Ratio **62.924%**｜库存风险 NORMAL

|分类|当前 M oz|1D|5D|10D|20D|
|---|---:|---:|---:|---:|---:|
|Total|22.613|-0.469%|-1.536%|-1.384%|-2.558%|
|Registered|14.229|-0.056%|+0.461%|-0.089%|-4.048%|
|Eligible|8.384|-1.162%|-4.748%|-3.506%|+0.080%|

窗口：1D 官方PREV TOTAL / CME_PREV_TOTAL；5D 2026-11-18 / AVAILABLE_CONSECUTIVE_WEEKDAYS；10D 2026-11-11 / AVAILABLE_CONSECUTIVE_WEEKDAYS；20D 2026-10-28 / AVAILABLE_CONSECUTIVE_WEEKDAYS

历史衔接异常：2026-09-18→2026-09-21 PREVIOUS_BALANCE_MISMATCH_OR_REVISION；不可跨异常自行相减或推断实物出库。

官方最新发布状态未独立确认。

Pledged已在Registered内；Eligible单独下降不证明交割短缺；NORMAL仅指Total单日库存阈值。

[核验快照](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/blob/43ab321723b462ed239d65ef2bd5630525631819/data/latest.json)｜[CME官方报告](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)

## Cash Liquidity / ICI

总资产 $待确认T｜周资产变化 $待确认B｜观察/发布：待确认

精确周净流量、约3个月已核验资金流趋势：待确认。资产高不等于近期逃向现金，也不意味着必然回流股市。

## 数据质量与来源

⚠ 缺失/过期/未核验：bls, cnn, ici。发布时间未提供则明确留空；抓取时间不代替发布时间。

本报告区分观察与解读；排除BTC seasonality、自选股、X讨论和普通财报清单。

- [aaii](https://www.aaii.com/sentimentsurvey)｜OK｜抓取 2026-11-28T15:10:17.129969+00:00

- [bea](https://www.bea.gov/news/schedule)｜OK｜抓取 2026-11-28T15:10:17.228403+00:00

- [bls](https://www.bls.gov/schedule/news_release/bls.ics)｜MISSING｜抓取 2026-11-28T15:10:13.982908+00:00｜HTTPError: HTTP Error 403: Forbidden

- [btc](https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=1mo&interval=1d)｜OK｜抓取 2026-11-28T15:10:18.219544+00:00

- [cftc](https://www.cftc.gov/RSS/RSSGP/rssgp.xml)｜OK｜抓取 2026-11-28T15:10:17.407839+00:00

- [clarity_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/hr/BILLSTATUS-119hr3633.xml)｜OK｜抓取 2026-11-28T15:10:17.470053+00:00

- [cnn](https://production.dataviz.cnn.io/index/fearandgreed/graphdata)｜MISSING｜抓取 2026-11-28T15:10:13.982908+00:00｜HTTPError: HTTP Error 418: Unknown Error

- [congress](https://www.govinfo.gov/rss/bills.xml)｜OK｜抓取 2026-11-28T15:10:17.523635+00:00

- [crypto](https://api.alternative.me/fng/?limit=31&format=json)｜OK｜抓取 2026-11-28T15:10:17.137751+00:00

- [dxy](https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?range=1mo&interval=1d)｜OK｜抓取 2026-11-28T15:10:17.933898+00:00

- [fed](https://www.federalreserve.gov/feeds/press_all.xml)｜OK｜抓取 2026-11-28T15:10:17.498265+00:00

- [federal_register](https://www.federalregister.gov/api/v1/documents.json?conditions%5Bpublication_date%5D%5Bgte%5D=2026-11-21&conditions%5Bpublication_date%5D%5Blte%5D=2026-11-27&order=oldest&per_page=100&page=1)｜OK｜抓取 2026-11-28T15:10:17.652316+00:00

- [fomc](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)｜OK｜抓取 2026-11-28T15:10:17.419826+00:00

- [genius_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/s/BILLSTATUS-119s1582.xml)｜OK｜抓取 2026-11-28T15:10:17.499135+00:00

- [gold](https://query1.finance.yahoo.com/v8/finance/chart/GC%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-11-28T15:10:18.120145+00:00

- [ici](https://www.ici.org/research/stats/mmf)｜MISSING｜抓取 2026-11-28T15:10:13.982908+00:00｜HTTPError: HTTP Error 403: Forbidden

- [nasdaq](https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?range=1mo&interval=1d)｜OK｜抓取 2026-11-28T15:10:17.781104+00:00

- [nyfed_calendar](https://www.newyorkfed.org/research/calendars/nationalecon_cal)｜OK｜抓取 2026-11-28T15:10:17.857086+00:00

- [occ](https://www.occ.gov/rss/occ_news.xml)｜OK｜抓取 2026-11-28T15:10:17.460615+00:00

- [sec](https://www.sec.gov/news/pressreleases.rss)｜OK｜抓取 2026-11-28T15:10:17.349363+00:00

- [sp500](https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=1mo&interval=1d)｜OK｜抓取 2026-11-28T15:10:17.668765+00:00

- [srf](https://markets.newyorkfed.org/api/rp/repo/all/results/lastTwoWeeks.json)｜OK｜抓取 2026-11-28T15:10:17.222601+00:00

- [treasury](https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&days=30)｜OK｜抓取 2026-11-28T15:10:17.179722+00:00

- [treasury_news](https://home.treasury.gov/news/press-releases)｜OK｜抓取 2026-11-28T15:10:26.867553+00:00

- [us10y](https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX?range=1mo&interval=1d)｜OK｜抓取 2026-11-28T15:10:17.847745+00:00

- [vix](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv)｜OK｜抓取 2026-11-28T15:10:17.057197+00:00

- [vix3m](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv)｜OK｜抓取 2026-11-28T15:10:17.030070+00:00

- [whitehouse](https://www.whitehouse.gov/presidential-actions/feed/)｜OK｜抓取 2026-11-28T15:10:17.591287+00:00

- [wti](https://query1.finance.yahoo.com/v8/finance/chart/CL%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-11-28T15:10:18.046125+00:00

- [comex](https://api.github.com/repos/yydsdefi-cmyk/COMEX-Gold-Tracker)｜OK｜抓取 2026-11-28T15:10:27.555270+00:00
