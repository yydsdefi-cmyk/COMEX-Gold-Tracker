# 每周市场与Crypto监管周报｜2026-11-28

生成 23:10 MYT｜目标周六10:00 MYT｜市场数据截至本次抓取；监管覆盖此前7个完整日期（来源发布日期口径），延迟抓取不冒充准点发布。

## 一周市场变化

本次引用此前 6 个不同MYT日期的日报档案，并使用本次采集；不足完整一周时不冒充7份晨报总结。

|指标|可核验期初→期末（实际日期）|变化|
|---|---|---|
|S&P 500（点）|2026-11-20 6,910.39 → 2026-11-27 7,297.49|+5.60 %|
|Nasdaq（点）|2026-11-20 22,617.73 → 2026-11-27 24,129.50|+6.68 %|
|US10Y（%）|2026-11-20 4.912 → 2026-11-27 4.936|+2.40 bp|
|DXY（点）|2026-11-20 103.81 → 2026-11-27 104.01|+0.19 %|
|WTI期货（USD/桶）|2026-11-20 83.98 → 2026-11-27 83.08|-1.07 %|
|Gold期货（USD/oz）|2026-11-20 3,515.40 → 2026-11-27 3,639.60|+3.53 %|
|BTC/USD（USD）|2026-11-21 60,094.09 → 2026-11-28 59,318.79|-1.29 %|
|AAII Spread（pp）|2026-11-18 -8.9 → 2026-11-25 -8.3|+0.6 pp|
|CNN F&G（点）|已核验独立日期不足|待确认|
|VIX（点）|2026-11-20 35.89 → 2026-11-27 23.81|-12.08 点|
|VIX3M（点）|2026-11-20 30.94 → 2026-11-27 23.82|-7.12 点|
|VIX/VIX3M（倍）|2026-11-20 1.160 → 2026-11-27 1.000|-0.160 倍|
|Crypto F&G（点）|2026-11-21 12 → 2026-11-28 10|-2 点|
|SRF（B USD）|2026-11-20 0.001000 → 2026-11-27 23.150000|+23.149000 B USD|
|MMF资产（B USD）|已核验独立日期不足|待确认|
|Registered Ratio（%）|已核验独立日期不足|待确认|

VIX/VIX3M同日配对：Backwardation → Contango；观察到 1次标签变化（区间内精确转折时刻未知；不是完整VIX期货曲线）。

基准取目标周初当日或之前最近可得日期；实际日期、缺基准和当前来源状态分开。历史点保留其旧时效标记，不拿它冒充今日数值；精确输入与单位见周报JSON analysis。

SRF已取得完整日期的使用量合计 $23.152000B；最大单日 2026-11-27 $23.150000B → Stress。按操作日期去重，测试操作排除；缺日不补0，合计不是未偿存量。

## 本周最重要变化

- AAII Bull-Bear Spread -8.9→-8.3pp，悲观程度下降（调查情绪，非收益预测）。

- Crypto F&G 12→10；最新 Extreme Fear，风险偏好降温（情绪解读）。

- Registered 20D -4.048%；持续观察库存收缩，不单独推断交割短缺。

趋势解释：变化方向可核验；“改善/恶化”不自动等同风险增减。三项情绪共振阈值未定义、拍卖后收益率反应未建立可核验事件窗口，均待确认。

## Gold库存与现金流动性

Activity 2026-11-25 / Report 2026-11-27｜Ratio 62.924%｜读取 OK｜库存风险 NORMAL

|分类|当前 M oz|5D|20D|
|---|---:|---:|---:|
|Total|22.613|-1.536%|-2.558%|
|Registered|14.229|+0.461%|-4.048%|
|Eligible|8.384|-4.748%|+0.080%|

四窗口、基准日与衔接异常见当天晨报和JSON。官方最新发布状态未独立确认；Pledged已包含Registered，Eligible下降不证明短缺。

[本次COMEX同提交快照](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/blob/43ab321723b462ed239d65ef2bd5630525631819/data/latest.json)

ICI总资产 $待确认T；周资产变化 $待确认B。观察/发布：待确认。资产变化不等于净流入；3个月流趋势待积累。

## Treasury / Fed

Bills｜已公告未来7日合计 **267.00B USD**（非尚未公告的完整供给预测）

Coupon（含TIPS/FRN）｜已公告未来7日合计 **待确认**（非尚未公告的完整供给预测）

- 2026-11-30 ET｜Bill 13-Week｜$95.00B｜公告 2026-11-25｜MYT 2026-12-01T00:30:00+08:00

- 2026-11-30 ET｜Bill 26-Week｜$82.00B｜公告 2026-11-25｜MYT 2026-12-01T00:30:00+08:00

- 2026-12-01 ET｜Bill 6-Week｜$90.00B｜公告 2026-11-25｜MYT 2026-12-02T00:30:00+08:00

最近coupon：2026-11-25 7-Year｜Bid-to-cover 2.43｜High yield 4.708%｜Tail/stop-through 待确认（无可核验WI收益率）。

## Crypto Regulatory Timeline（国会行动日／机构发布日期）

- 2026-11-23｜[CFTC Staff Issues Advisory Concerning the Use of Crypto Assets to Satisfy Financial Resources Requirements](https://www.cftc.gov/PressRoom/PressReleases/9331-26)｜cftc｜指引/声明/讲话（非正式规则证明）｜生效 待核验；行动/事件日期 未另提供

- 2026-11-25｜[SEC Investor Advisory Committee to Host Dec. 3 Virtual Meeting](https://www.sec.gov/newsroom/press-releases/2026-118-sec-investor-advisory-committee-host-dec-3-virtual-meeting)｜sec｜官方公告候选／法律状态待确认｜生效 待核验；行动/事件日期 未另提供

主题：代币化证券（确定性主题归类，不是价格影响结论）。

- 2026-11-27｜[Polytetramethylene Ether Glycol (PTMEG) From China, South Korea, Taiwan, and Vietnam; Scheduling of the Final Phase of Antidumping Duty Investigations; Correction](https://www.federalregister.gov/documents/2026/11/27/2026-24155/polytetramethylene-ether-glycol-ptmeg-from-china-south-korea-taiwan-and-vietnam-scheduling-of-the)｜federal_register｜通知（法律效力逐项核验）｜生效 待核验；行动/事件日期 未另提供｜[正式PDF](https://www.govinfo.gov/content/pkg/FR-2026-11-27/pdf/2026-24155.pdf)

## Congress：指定法案的官方状态

CLARITY｜第119届 HR3633｜当前官方文件未见成法记录｜[官方BILLSTATUS](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/hr/BILLSTATUS-119hr3633.xml)

最新已登记行动 2026-09-15：Motion by Senator Tillis to reconsider the vote by which cloture on the motion to proceed to the measure was not invoked (Record Vote No. 234) entered in Senate.；本周行动 0条。文件更新 2026-09-17T17:09:18Z，本次读取 2026-11-28T15:10:17.470053+00:00。成法与实施规则、生效日期分开。

GENIUS｜第119届 S1582｜存在成法记录：Public Law 119-27｜[官方BILLSTATUS](https://www.govinfo.gov/bulkdata/BILLSTATUS/119/s/BILLSTATUS-119s1582.xml)

最新已登记行动 2025-07-18：Became Public Law No: 119-27.；本周行动 0条。文件更新 2026-07-29T21:37:07Z，本次读取 2026-11-28T15:10:17.499135+00:00。成法与实施规则、生效日期分开。

来源覆盖：{"cftc": "OK", "clarity_bill": "OK", "congress": "OK", "fed": "OK", "federal_register": "OK", "genius_bill": "OK", "occ": "OK", "sec": "OK", "treasury_news": "OK", "whitehouse": "OK"}。Federal Register按完整日期窗口有界分页后本地筛选；Congress指定法案行动记录与一般发布Feed分开。机构时间戳转美东日期，FR用原刊登日期；未知事件日不猜。关键词筛选及新法案发现仍可能遗漏。

## 下周已知事件与风险

- 2026-12-02 21:30 MYT｜GDP（[BEA](https://www.bea.gov/news/schedule)）

- 2026-12-04 21:30 MYT｜就业报告（[NYFed calendar](https://www.newyorkfed.org/research/calendars/i-dec26.html)）

⚠ 日历覆盖待确认：bls

补充：纽约联储公开日历可旁证部分事件，不代表BLS直连已恢复；日历日期/时刻可能调整。

范围：美国BLS/BEA/FOMC及NYFed日历；不含付费共识预期与自动因果归因。FOMC时刻按14:00 ET惯例估计，临时变更待核验。

下周监管生效/意见截止节点：本次结构化官方记录未确认到；不等于没有节点。

## 结构性影响与未决问题

事实：上列公告的发布日期和Federal Register文种可追溯。解读：标题与文种不足以证明已通过、已生效或市场因果关系。

|资产|直接/间接影响|
|---|---|
|BTC|间接影响可能：加密资产交易/中介或稳定币生态事项；尚未证实该币种新增专属义务（推断，不是价格方向）。|
|ETH|直接相关主题：官方标题/摘要明确涉及该资产或规则对象；具体义务与生效范围仍须核正式文件。|
|Stablecoin|未确认本周直接法律影响；本次未查到不等于不存在。|
|Tokenized Securities|直接相关主题：官方标题/摘要明确涉及该资产或规则对象；具体义务与生效范围仍须核正式文件。|

结构性监管变化以已列文种和生效日期为事实基础；标题主题关联不是完整法律影响评估，下周监管截止日缺少可核验信息时保留待确认。

方法变更：免费确定性系统提供可审计数据与公告线索；不冒充原LLM的完整法律语义研究。详见METHOD_CHANGES.md。

## 来源与质量

[完整来源登记](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/source_registry.json)｜[数据质量](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/quality.json)；各条目附原始官方链接。
