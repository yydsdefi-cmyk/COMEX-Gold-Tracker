# 市场反向指标晨报｜2026-11-18

生成 14:27 MYT｜目标08:00 MYT｜规则生成，无LLM/API订阅。

## 7项总览

- 美股情绪：部分数据待确认，极端共振不能确认。

- Crypto：最新 11，与昨日/7日前分开核对。

- Event Risk：0项已读取日历候选；覆盖限制见下。

- SRF：Normal，不等同QE判断。

- Treasury：未来7日已公告供给分Bills/Coupon。

- COMEX：⚠本次未通过采集核验。

- Cash Liquidity：待确认。

## Overnight（各自日期，非同步实时行情）

- S&P 500 **7,340.53** -1.03%｜观察 2026-11-17｜发布 未提供

- Nasdaq **24,328.38** -0.74%｜观察 2026-11-17｜发布 未提供

- US10Y **5.10** -1.80bp｜观察 2026-11-17｜发布 未提供

- DXY **103.66** +0.17%｜观察 2026-11-18｜发布 未提供

- WTI期货 **84.54** -1.71%｜观察 2026-11-18｜发布 未提供

- Gold期货 **3,784.30** -2.07%｜观察 2026-11-18｜发布 未提供

- BTC/USD **64,593.82** -0.40%｜观察 2026-11-18｜发布 未提供

Yahoo为次级来源；期货与现货有差异，最新日线可能仍在交易中，报价时刻见JSON。

## US Contrarian

AAII Bull/Neutral/Bear 30.8/17.8/51.4%｜Spread -20.6pp｜观察 2026-11-11｜发布 未提供

CNN F&G 待确认 ｜观察/发布：待确认

VIX 25.46｜观察 2026-11-17｜发布 未提供

VIX3M 24.98｜观察 2026-11-17｜发布 未提供

同日 2026-11-17 VIX/VIX3M **1.019** → Backwardation（期限比率标签，不代表VIX期货曲线全部形状）

解读：原规格未给AAII/VIX极端情绪数值阈值，三项共同极端状态保留待确认，不新增买卖信号。

## Crypto F&G（Alternative.me）

今日 2026-11-18｜11 Extreme Fear

昨日 2026-11-17｜12 Extreme Fear

7日前 2026-11-11｜29 Fear

观察日期以供应商UTC日戳为准；不拿“最新一条”冒充今日。

## 今日Event Risk（MYT）

已读取日历内未发现符合筛选的Tier-1事件；不等于完整全球经济日历无事件。

⚠ 日历覆盖待确认：bls

补充：纽约联储公开日历可旁证部分事件，不代表BLS直连已恢复；日历日期/时刻可能调整。

范围：美国BLS/BEA/FOMC及NYFed日历；不含付费共识预期与自动因果归因。FOMC时刻按14:00 ET惯例估计，临时变更待核验。

## SRF（常规隔夜操作）

$0.104000B → Normal｜观察 2026-11-17｜发布 未提供｜2场；完整度规则通过｜最后修订 2026-11-17T18:45:24+00:00（首次发布时间未单列）

## Treasury

Bills｜已公告未来7日合计 **300.00B USD**（非尚未公告的完整供给预测）

Coupon（含TIPS/FRN）｜已公告未来7日合计 **35.00B USD**（非尚未公告的完整供给预测）

- 2026-11-18 ET｜Bill 17-Week｜$75.00B｜公告 2026-11-17｜MYT 2026-11-19T00:30:00+08:00

- 2026-11-18 ET｜Bond 20-Year｜$16.00B｜公告 2026-11-12｜MYT 2026-11-19T02:00:00+08:00

- 2026-11-19 ET｜Bill 4-Week｜$115.00B｜公告 2026-11-17｜MYT 2026-11-20T00:30:00+08:00

- 2026-11-19 ET｜Bill 8-Week｜$110.00B｜公告 2026-11-17｜MYT 2026-11-20T00:30:00+08:00

- 2026-11-19 ET｜TIPS 9-Year 8-Month｜$19.00B｜公告 2026-11-12｜MYT 2026-11-20T02:00:00+08:00

## COMEX Gold

读取：GitHub提交 0ad6aac6｜核验MYT 11-18 14:27｜采集尝试MYT 11-18 10:53:51｜⚠读取/更新异常：SNAPSHOT_BEHIND_RUN

Activity 2026-11-16｜Report 2026-11-17｜OK / WITHIN_AGE_LIMIT

以下仅为上次可得旧数据，不代表今日已更新。

Registered Ratio **61.696%**｜库存风险 NORMAL

|分类|当前 M oz|1D|5D|10D|20D|
|---|---:|---:|---:|---:|---:|
|Total|22.996|-0.142%|+0.001%|-0.628%|-1.835%|
|Registered|14.188|-0.235%|-0.379%|-3.402%|-4.248%|
|Eligible|8.808|+0.008%|+0.618%|+4.193%|+2.318%|

窗口：1D 官方PREV TOTAL / CME_PREV_TOTAL；5D 2026-11-09 / AVAILABLE_CONSECUTIVE_WEEKDAYS；10D 2026-11-02 / AVAILABLE_CONSECUTIVE_WEEKDAYS；20D 2026-10-19 / AVAILABLE_CONSECUTIVE_WEEKDAYS

历史衔接异常：2026-09-18→2026-09-21 PREVIOUS_BALANCE_MISMATCH_OR_REVISION；不可跨异常自行相减或推断实物出库。

官方最新发布状态未独立确认。

Pledged已在Registered内；Eligible单独下降不证明交割短缺；NORMAL仅指Total单日库存阈值。

[核验快照](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/blob/0ad6aac604dbaa2d24b589d087185d8e98bae047/data/latest.json)｜[CME官方报告](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)

## Cash Liquidity / ICI

总资产 $待确认T｜周资产变化 $待确认B｜观察/发布：待确认

精确周净流量、约3个月已核验资金流趋势：待确认。资产高不等于近期逃向现金，也不意味着必然回流股市。

## 数据质量与来源

⚠ 缺失/过期/未核验：bls, cnn, ici, comex。发布时间未提供则明确留空；抓取时间不代替发布时间。

本报告区分观察与解读；排除BTC seasonality、自选股、X讨论和普通财报清单。

- [aaii](https://www.aaii.com/sentimentsurvey)｜OK｜抓取 2026-11-18T06:27:28.630808+00:00

- [bea](https://www.bea.gov/news/schedule)｜OK｜抓取 2026-11-18T06:27:28.614851+00:00

- [bls](https://www.bls.gov/schedule/news_release/bls.ics)｜MISSING｜抓取 2026-11-18T06:27:26.392293+00:00｜HTTPError: HTTP Error 403: Forbidden

- [btc](https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=1mo&interval=1d)｜OK｜抓取 2026-11-18T06:27:29.049810+00:00

- [cftc](https://www.cftc.gov/RSS/RSSGP/rssgp.xml)｜OK｜抓取 2026-11-18T06:27:28.664859+00:00

- [clarity_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/hr/BILLSTATUS-119hr3633.xml)｜OK｜抓取 2026-11-18T06:27:28.726227+00:00

- [cnn](https://production.dataviz.cnn.io/index/fearandgreed/graphdata)｜MISSING｜抓取 2026-11-18T06:27:26.392293+00:00｜HTTPError: HTTP Error 418: Unknown Error

- [congress](https://www.govinfo.gov/rss/bills.xml)｜OK｜抓取 2026-11-18T06:27:28.786132+00:00

- [crypto](https://api.alternative.me/fng/?limit=31&format=json)｜OK｜抓取 2026-11-18T06:27:28.486857+00:00

- [dxy](https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?range=1mo&interval=1d)｜OK｜抓取 2026-11-18T06:27:28.969656+00:00

- [fed](https://www.federalreserve.gov/feeds/press_all.xml)｜OK｜抓取 2026-11-18T06:27:28.775415+00:00

- [federal_register](https://www.federalregister.gov/api/v1/documents.json?conditions%5Bpublication_date%5D%5Bgte%5D=2026-11-11&conditions%5Bpublication_date%5D%5Blte%5D=2026-11-17&order=oldest&per_page=100&page=1)｜OK｜抓取 2026-11-18T06:27:28.921173+00:00

- [fomc](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)｜OK｜抓取 2026-11-18T06:27:28.635981+00:00

- [genius_bill](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/s/BILLSTATUS-119s1582.xml)｜OK｜抓取 2026-11-18T06:27:28.747396+00:00

- [gold](https://query1.finance.yahoo.com/v8/finance/chart/GC%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-11-18T06:27:29.026147+00:00

- [ici](https://www.ici.org/research/stats/mmf)｜MISSING｜抓取 2026-11-18T06:27:26.392293+00:00｜HTTPError: HTTP Error 403: Forbidden

- [nasdaq](https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?range=1mo&interval=1d)｜OK｜抓取 2026-11-18T06:27:28.911084+00:00

- [nyfed_calendar](https://www.newyorkfed.org/research/calendars/nationalecon_cal)｜OK｜抓取 2026-11-18T06:27:28.855314+00:00

- [occ](https://www.occ.gov/rss/occ_news.xml)｜OK｜抓取 2026-11-18T06:27:28.715612+00:00

- [sec](https://www.sec.gov/news/pressreleases.rss)｜OK｜抓取 2026-11-18T06:27:28.658956+00:00

- [sp500](https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=1mo&interval=1d)｜OK｜抓取 2026-11-18T06:27:28.880288+00:00

- [srf](https://markets.newyorkfed.org/api/rp/repo/all/results/lastTwoWeeks.json)｜OK｜抓取 2026-11-18T06:27:28.824958+00:00

- [treasury](https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&days=30)｜OK｜抓取 2026-11-18T06:27:28.539242+00:00

- [treasury_news](https://home.treasury.gov/news/press-releases)｜OK｜抓取 2026-11-18T06:27:37.886505+00:00

- [us10y](https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX?range=1mo&interval=1d)｜OK｜抓取 2026-11-18T06:27:28.934531+00:00

- [vix](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv)｜OK｜抓取 2026-11-18T06:27:28.473549+00:00

- [vix3m](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv)｜OK｜抓取 2026-11-18T06:27:28.464026+00:00

- [whitehouse](https://www.whitehouse.gov/presidential-actions/feed/)｜OK｜抓取 2026-11-18T06:27:28.805396+00:00

- [wti](https://query1.finance.yahoo.com/v8/finance/chart/CL%3DF?range=1mo&interval=1d)｜OK｜抓取 2026-11-18T06:27:28.988948+00:00

- [comex](https://api.github.com/repos/yydsdefi-cmyk/COMEX-Gold-Tracker)｜UNVERIFIED｜抓取 2026-11-18T06:27:38.975809+00:00
