# 市场反向指标晨报｜2026-11-13

生成 13:39 MYT｜目标08:00 MYT｜规则生成，无LLM/API订阅。

## 7项总览

- 美股情绪：部分数据待确认，极端共振不能确认。

- Crypto：最新 20，与昨日/7日前分开核对。

- Event Risk：1项已读取日历候选；覆盖限制见下。

- SRF：Normal，不等同QE判断。

- Treasury：未来7日已公告供给分Bills/Coupon。

- COMEX：当天核验通过；库存风险另列。

- Cash Liquidity：待确认。

## Overnight（各自日期，非同步实时行情）

- S&P 500 **7,592.40** -0.35%｜观察 2026-11-12｜发布 未提供

- Nasdaq **25,366.09** -0.39%｜观察 2026-11-12｜发布 未提供

- US10Y **5.10** +10.50bp｜观察 2026-11-12｜发布 未提供

- DXY **103.17** +0.00%｜观察 2026-11-13｜发布 未提供

- WTI期货 **88.20** -0.61%｜观察 2026-11-13｜发布 未提供

- Gold期货 **3,922.00** +0.94%｜观察 2026-11-13｜发布 未提供

- BTC/USD **68,374.75** -7.56%｜观察 2026-11-13｜发布 未提供

Yahoo为次级来源；期货与现货有差异，最新日线可能仍在交易中，报价时刻见JSON。

## US Contrarian

AAII Bull/Neutral/Bear 30.8/17.8/51.4%｜Spread -20.6pp｜观察 2026-11-11｜发布 未提供

CNN F&G 待确认 ｜观察/发布：待确认

VIX 18.70｜观察 2026-11-12｜发布 未提供

VIX3M 20.06｜观察 2026-11-12｜发布 未提供

同日 2026-11-12 VIX/VIX3M **0.932** → Contango（期限比率标签，不代表VIX期货曲线全部形状）

解读：原规格未给AAII/VIX极端情绪数值阈值，三项共同极端状态保留待确认，不新增买卖信号。

## Crypto F&G（Alternative.me）

今日 2026-11-13｜20 Extreme Fear

昨日 2026-11-12｜28 Fear

7日前 2026-11-06｜28 Fear

观察日期以供应商UTC日戳为准；不拿“最新一条”冒充今日。

## 今日Event Risk（MYT）

- 2026-11-13 21:30 MYT｜PPI生产物价指数（[NYFed calendar](https://www.newyorkfed.org/research/calendars/nationalecon_cal)）

⚠ 日历覆盖待确认：bls

补充：纽约联储公开日历可旁证部分事件，不代表BLS直连已恢复；日历日期/时刻可能调整。

范围：美国BLS/BEA/FOMC及NYFed日历；不含付费共识预期与自动因果归因。FOMC时刻按14:00 ET惯例估计，临时变更待核验。

## SRF（常规隔夜操作）

$0.001000B → Normal｜观察 2026-11-12｜发布 未提供｜2场；完整度规则通过｜最后修订 2026-11-12T18:45:26+00:00（首次发布时间未单列）

## Treasury

Bills｜已公告未来7日合计 **277.00B USD**（非尚未公告的完整供给预测）

Coupon（含TIPS/FRN）｜已公告未来7日合计 **35.00B USD**（非尚未公告的完整供给预测）

- 2026-11-16 ET｜Bill 13-Week｜$95.00B｜公告 2026-11-12｜MYT 2026-11-17T00:30:00+08:00

- 2026-11-16 ET｜Bill 26-Week｜$82.00B｜公告 2026-11-12｜MYT 2026-11-17T00:30:00+08:00

- 2026-11-17 ET｜Bill 6-Week｜$100.00B｜公告 2026-11-12｜MYT 2026-11-18T00:30:00+08:00

- 2026-11-18 ET｜Bond 20-Year｜$16.00B｜公告 2026-11-12｜MYT 2026-11-19T02:00:00+08:00

- 2026-11-19 ET｜TIPS 9-Year 8-Month｜$19.00B｜公告 2026-11-12｜MYT 2026-11-20T02:00:00+08:00

最近coupon：2026-11-10 10-Year｜Bid-to-cover 2.46｜High yield 5.020%｜Tail/stop-through 待确认（无可核验WI收益率）。

最近coupon：2026-11-12 30-Year｜Bid-to-cover 2.36｜High yield 5.441%｜Tail/stop-through 待确认（无可核验WI收益率）。

## COMEX Gold

读取：GitHub提交 9cf08e20｜核验MYT 11-13 13:39｜采集尝试MYT 11-13 11:33:59｜数据核验通过

Activity 2026-11-11｜Report 2026-11-12｜UNCHANGED / WITHIN_AGE_LIMIT

Registered Ratio **62.108%**｜库存风险 NORMAL

|分类|当前 M oz|1D|5D|10D|20D|
|---|---:|---:|---:|---:|---:|
|Total|22.930|-0.001%|-0.291%|-1.190%|-2.256%|
|Registered|14.242|+0.000%|-0.798%|-3.962%|-3.884%|
|Eligible|8.689|-0.003%|+0.552%|+3.716%|+0.535%|

窗口：1D 官方PREV TOTAL / CME_PREV_TOTAL；5D 2026-11-04 / AVAILABLE_CONSECUTIVE_WEEKDAYS；10D 2026-10-28 / AVAILABLE_CONSECUTIVE_WEEKDAYS；20D 2026-10-14 / AVAILABLE_CONSECUTIVE_WEEKDAYS

历史衔接异常：2026-09-18→2026-09-21 PREVIOUS_BALANCE_MISMATCH_OR_REVISION；不可跨异常自行相减或推断实物出库。

官方最新发布状态未独立确认。

Pledged已在Registered内；Eligible单独下降不证明交割短缺；NORMAL仅指Total单日库存阈值。

[核验快照](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/blob/9cf08e20801206634903d418f7e24d6b3cf55adb/data/latest.json)｜[CME官方报告](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)

## Cash Liquidity / ICI

总资产 $待确认T｜周资产变化 $待确认B｜观察/发布：待确认

精确周净流量、约3个月已核验资金流趋势：待确认。资产高不等于近期逃向现金，也不意味着必然回流股市。

## 数据质量与来源

⚠ 缺失/过期/未核验：bls, cnn, ici。发布时间未提供则明确留空；抓取时间不代替发布时间。

本报告区分观察与解读；排除BTC seasonality、自选股、X讨论和普通财报清单。

- [aaii](https://www.aaii.com/sentimentsurvey)｜OK｜抓取 2026-11-13T05:38:58.646401+00:00

- [bea](https://www.bea.gov/news/schedule)｜OK｜抓取 2026-11-13T05:38:58.717886+00:00

- [bls](https://www.bls.gov/schedule/news_release/bls.ics)｜MISSING｜抓取 2026-11-13T05:38:56.162453+00:00｜HTTPError: HTTP Error 403: Forbidden

- [btc](https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=1mo&interval=1d)｜OK｜抓取 2026-11-13T05:38:59.530131+00:00

- [cftc](https://www.cftc.gov/RSS/RSSGP/rssgp.xml)｜OK｜抓取 2026-11-13T05:38:58.875667+00:00

- [clarity_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/hr/BILLSTATUS-119hr3633.xml)｜OK｜抓取 2026-11-13T05:38:58.972871+00:00

- [cnn](https://production.dataviz.cnn.io/index/fearandgreed/graphdata)｜MISSING｜抓取 2026-11-13T05:38:56.162453+00:00｜HTTPError: HTTP Error 418: Unknown Error

- [congress](https://www.govinfo.gov/rss/bills.xml)｜OK｜抓取 2026-11-13T05:38:59.079840+00:00

- [crypto](https://api.alternative.me/fng/?limit=31&format=json)｜OK｜抓取 2026-11-13T05:38:58.551675+00:00

- [dxy](https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?range=1mo&interval=1d)｜OK｜抓取 2026-11-13T05:38:59.463769+00:00

- [fed](https://www.federalreserve.gov/feeds/press_all.xml)｜OK｜抓取 2026-11-13T05:38:59.016291+00:00

- [federal_register](https://www.federalregister.gov/api/v1/documents.json?conditions%5Bpublication_date%5D%5Bgte%5D=2026-11-06&conditions%5Bpublication_date%5D%5Blte%5D=2026-11-12&order=oldest&per_page=100&page=1)｜OK｜抓取 2026-11-13T05:38:59.281336+00:00

- [fomc](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)｜OK｜抓取 2026-11-13T05:38:58.819489+00:00

- [genius_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/s/BILLSTATUS-119s1582.xml)｜OK｜抓取 2026-11-13T05:38:59.040121+00:00

- [gold](https://query1.finance.yahoo.com/v8/finance/chart/GC%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-11-13T05:38:59.565194+00:00

- [ici](https://www.ici.org/research/stats/mmf)｜MISSING｜抓取 2026-11-13T05:38:56.162453+00:00｜HTTPError: HTTP Error 403: Forbidden

- [nasdaq](https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?range=1mo&interval=1d)｜OK｜抓取 2026-11-13T05:38:59.298537+00:00

- [nyfed_calendar](https://www.newyorkfed.org/research/calendars/nationalecon_cal)｜OK｜抓取 2026-11-13T05:38:59.398670+00:00

- [occ](https://www.occ.gov/rss/occ_news.xml)｜OK｜抓取 2026-11-13T05:38:58.974776+00:00

- [sec](https://www.sec.gov/news/pressreleases.rss)｜OK｜抓取 2026-11-13T05:38:58.902123+00:00

- [sp500](https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=1mo&interval=1d)｜OK｜抓取 2026-11-13T05:38:59.214739+00:00

- [srf](https://markets.newyorkfed.org/api/rp/repo/all/results/lastTwoWeeks.json)｜OK｜抓取 2026-11-13T05:38:59.135812+00:00

- [treasury](https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&days=30)｜OK｜抓取 2026-11-13T05:38:58.668520+00:00

- [treasury_news](https://home.treasury.gov/news/press-releases)｜OK｜抓取 2026-11-13T05:39:07.242794+00:00

- [us10y](https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX?range=1mo&interval=1d)｜OK｜抓取 2026-11-13T05:38:59.361206+00:00

- [vix](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv)｜OK｜抓取 2026-11-13T05:38:58.474773+00:00

- [vix3m](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv)｜OK｜抓取 2026-11-13T05:38:58.460019+00:00

- [whitehouse](https://www.whitehouse.gov/presidential-actions/feed/)｜OK｜抓取 2026-11-13T05:38:59.139474+00:00

- [wti](https://query1.finance.yahoo.com/v8/finance/chart/CL%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-11-13T05:38:59.465011+00:00

- [comex](https://api.github.com/repos/yydsdefi-cmyk/COMEX-Gold-Tracker)｜OK｜抓取 2026-11-13T05:39:08.203315+00:00
