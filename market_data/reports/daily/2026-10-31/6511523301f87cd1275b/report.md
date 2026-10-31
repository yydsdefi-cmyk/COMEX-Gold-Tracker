# 市场反向指标晨报｜2026-10-31

生成 09:43 MYT｜目标08:00 MYT｜规则生成，无LLM/API订阅。

## 7项总览

- 美股情绪：部分数据待确认，极端共振不能确认。

- Crypto：最新 30，与昨日/7日前分开核对。

- Event Risk：0项已读取日历候选；覆盖限制见下。

- SRF：Normal，不等同QE判断。

- Treasury：未来7日已公告供给分Bills/Coupon。

- COMEX：当天核验通过；库存风险另列。

- Cash Liquidity：待确认。

## Overnight（各自日期，非同步实时行情）

- S&P 500 **7,580.07** -1.82%｜观察 2026-10-30｜发布 未提供

- Nasdaq **25,437.00** -2.86%｜观察 2026-10-30｜发布 未提供

- US10Y **4.93** -6.00bp｜观察 2026-10-30｜发布 未提供

- DXY **101.96** -0.07%｜观察 2026-10-30｜发布 未提供

- WTI期货 **102.95** +0.93%｜观察 2026-10-30｜发布 未提供

- Gold期货 **3,884.90** -3.63%｜观察 2026-10-30｜发布 未提供

- BTC/USD **77,293.21** -0.62%｜观察 2026-10-31｜发布 未提供

Yahoo为次级来源；期货与现货有差异，最新日线可能仍在交易中，报价时刻见JSON。

## US Contrarian

AAII Bull/Neutral/Bear 37.8/20.7/41.4%｜Spread -3.6pp｜观察 2026-10-28｜发布 未提供

CNN F&G 待确认 ｜观察/发布：待确认

VIX 19.42｜观察 2026-10-30｜发布 未提供

VIX3M 20.78｜观察 2026-10-30｜发布 未提供

同日 2026-10-30 VIX/VIX3M **0.935** → Contango（期限比率标签，不代表VIX期货曲线全部形状）

解读：原规格未给AAII/VIX极端情绪数值阈值，三项共同极端状态保留待确认，不新增买卖信号。

## Crypto F&G（Alternative.me）

今日 2026-10-31｜30 Fear

昨日 2026-10-30｜30 Fear

7日前 2026-10-24｜51 Neutral

观察日期以供应商UTC日戳为准；不拿“最新一条”冒充今日。

## 今日Event Risk（MYT）

已读取日历内未发现符合筛选的Tier-1事件；不等于完整全球经济日历无事件。

⚠ 日历覆盖待确认：bls

⚠ 纽约联储补充日历覆盖：INCOMPLETE

范围：美国BLS/BEA/FOMC及NYFed日历；不含付费共识预期与自动因果归因。FOMC时刻按14:00 ET惯例估计，临时变更待核验。

## SRF（常规隔夜操作）

$0.000000B → Normal｜观察 2026-10-30｜发布 未提供｜2场；完整度规则通过｜最后修订 2026-10-30T17:45:21+00:00（首次发布时间未单列）

API窗口内排除小额测试 1场；逐笔证据见JSON。

## Treasury

Bills｜已公告未来7日合计 **277.00B USD**（非尚未公告的完整供给预测）

Coupon（含TIPS/FRN）｜已公告未来7日合计 **待确认**（非尚未公告的完整供给预测）

- 2026-11-02 ET｜Bill 13-Week｜$95.00B｜公告 2026-10-29｜MYT 2026-11-03T00:30:00+08:00

- 2026-11-02 ET｜Bill 26-Week｜$82.00B｜公告 2026-10-29｜MYT 2026-11-03T00:30:00+08:00

- 2026-11-03 ET｜Bill 6-Week｜$100.00B｜公告 2026-10-29｜MYT 2026-11-04T00:30:00+08:00

最近coupon：2026-10-28 2-Year｜Bid-to-cover 3.05｜High yield 待确认%｜Tail/stop-through 待确认（无可核验WI收益率）。

最近coupon：2026-10-29 7-Year｜Bid-to-cover 2.46｜High yield 4.894%｜Tail/stop-through 待确认（无可核验WI收益率）。

## COMEX Gold

读取：GitHub提交 2c7d27f0｜核验MYT 10-31 09:43｜采集尝试MYT 10-31 08:09:29｜数据核验通过

Activity 2026-10-29｜Report 2026-10-30｜UNCHANGED / WITHIN_AGE_LIMIT

Registered Ratio **63.823%**｜库存风险 NORMAL

|分类|当前 M oz|1D|5D|10D|20D|
|---|---:|---:|---:|---:|---:|
|Total|23.204|-0.011%|-0.340%|-0.950%|-1.175%|
|Registered|14.810|-0.132%|-0.032%|-0.050%|-1.836%|
|Eligible|8.394|+0.203%|-0.877%|-2.497%|+0.014%|

窗口：1D 官方PREV TOTAL / CME_PREV_TOTAL；5D 2026-10-22 / AVAILABLE_CONSECUTIVE_WEEKDAYS；10D 2026-10-15 / AVAILABLE_CONSECUTIVE_WEEKDAYS；20D 2026-10-01 / AVAILABLE_CONSECUTIVE_WEEKDAYS

历史衔接异常：2026-09-18→2026-09-21 PREVIOUS_BALANCE_MISMATCH_OR_REVISION；不可跨异常自行相减或推断实物出库。

官方最新发布状态未独立确认。

Pledged已在Registered内；Eligible单独下降不证明交割短缺；NORMAL仅指Total单日库存阈值。

[核验快照](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/blob/2c7d27f013a529c4aaa0d5aeb6d71169ad422472/data/latest.json)｜[CME官方报告](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)

## Cash Liquidity / ICI

总资产 $待确认T｜周资产变化 $待确认B｜观察/发布：待确认

精确周净流量、约3个月已核验资金流趋势：待确认。资产高不等于近期逃向现金，也不意味着必然回流股市。

## 数据质量与来源

⚠ 缺失/过期/未核验：bls, cnn, ici, nyfed_calendar, occ。发布时间未提供则明确留空；抓取时间不代替发布时间。

本报告区分观察与解读；排除BTC seasonality、自选股、X讨论和普通财报清单。

- [aaii](https://www.aaii.com/sentimentsurvey)｜OK｜抓取 2026-10-31T01:42:55.543201+00:00

- [bea](https://www.bea.gov/news/schedule)｜OK｜抓取 2026-10-31T01:42:55.934881+00:00

- [bls](https://www.bls.gov/schedule/news_release/bls.ics)｜MISSING｜抓取 2026-10-31T01:42:53.624278+00:00｜HTTPError: HTTP Error 403: Forbidden

- [btc](https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=1mo&interval=1d)｜OK｜抓取 2026-10-31T01:42:57.101641+00:00

- [cftc](https://www.cftc.gov/RSS/RSSGP/rssgp.xml)｜OK｜抓取 2026-10-31T01:42:55.985656+00:00

- [clarity_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/hr/BILLSTATUS-119hr3633.xml)｜OK｜抓取 2026-10-31T01:42:56.132691+00:00

- [cnn](https://production.dataviz.cnn.io/index/fearandgreed/graphdata)｜MISSING｜抓取 2026-10-31T01:42:53.624278+00:00｜HTTPError: HTTP Error 418: Unknown Error

- [congress](https://www.govinfo.gov/rss/bills.xml)｜OK｜抓取 2026-10-31T01:42:56.234621+00:00

- [crypto](https://api.alternative.me/fng/?limit=31&format=json)｜OK｜抓取 2026-10-31T01:42:55.355986+00:00

- [dxy](https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?range=1mo&interval=1d)｜OK｜抓取 2026-10-31T01:42:56.753134+00:00

- [fed](https://www.federalreserve.gov/feeds/press_all.xml)｜OK｜抓取 2026-10-31T01:42:56.096592+00:00

- [federal_register](https://www.federalregister.gov/api/v1/documents.json?conditions%5Bpublication_date%5D%5Bgte%5D=2026-10-24&conditions%5Bpublication_date%5D%5Blte%5D=2026-10-30&order=oldest&per_page=100&page=1)｜OK｜抓取 2026-10-31T01:42:56.571804+00:00

- [fomc](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)｜OK｜抓取 2026-10-31T01:42:55.860964+00:00

- [genius_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/s/BILLSTATUS-119s1582.xml)｜OK｜抓取 2026-10-31T01:42:56.147819+00:00

- [gold](https://query1.finance.yahoo.com/v8/finance/chart/GC%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-10-31T01:42:56.989273+00:00

- [ici](https://www.ici.org/research/stats/mmf)｜MISSING｜抓取 2026-10-31T01:42:53.624278+00:00｜HTTPError: HTTP Error 403: Forbidden

- [nasdaq](https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?range=1mo&interval=1d)｜OK｜抓取 2026-10-31T01:42:56.528445+00:00

- [nyfed_calendar](https://www.newyorkfed.org/research/calendars/nationalecon_cal)｜INCOMPLETE｜抓取 2026-10-31T01:42:56.029370+00:00

- [occ](https://www.occ.gov/rss/occ_news.xml)｜MISSING｜抓取 2026-10-31T01:42:57.034849+00:00｜ParseError: not well-formed (invalid token): line 51, column 120

- [sec](https://www.sec.gov/news/pressreleases.rss)｜OK｜抓取 2026-10-31T01:42:55.972799+00:00

- [sp500](https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=1mo&interval=1d)｜OK｜抓取 2026-10-31T01:42:56.409238+00:00

- [srf](https://markets.newyorkfed.org/api/rp/repo/all/results/lastTwoWeeks.json)｜OK｜抓取 2026-10-31T01:42:55.857696+00:00

- [treasury](https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&days=30)｜OK｜抓取 2026-10-31T01:42:55.780849+00:00

- [treasury_news](https://home.treasury.gov/news/press-releases)｜OK｜抓取 2026-10-31T01:43:05.320464+00:00

- [us10y](https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX?range=1mo&interval=1d)｜OK｜抓取 2026-10-31T01:42:56.638650+00:00

- [vix](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv)｜OK｜抓取 2026-10-31T01:42:55.229495+00:00

- [vix3m](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv)｜OK｜抓取 2026-10-31T01:42:55.219279+00:00

- [whitehouse](https://www.whitehouse.gov/presidential-actions/feed/)｜OK｜抓取 2026-10-31T01:42:56.251096+00:00

- [wti](https://query1.finance.yahoo.com/v8/finance/chart/CL%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-10-31T01:42:56.872906+00:00

- [comex](https://api.github.com/repos/yydsdefi-cmyk/COMEX-Gold-Tracker)｜OK｜抓取 2026-10-31T01:43:06.621082+00:00
