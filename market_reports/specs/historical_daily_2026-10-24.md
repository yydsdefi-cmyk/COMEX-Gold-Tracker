# 市场晨报｜2026-10-24（六）
**核验 08:03 MYT｜美股截至10/23收盘｜USD**

### 7项总览
**美股情绪：** 偏恐惧；VIX上升，极端共振未确认。  
**Crypto：** 最新50 Neutral；今日值待确认。  
**Event Risk：** 今日无Tier-1美国宏观事件。  
**SRF：** $0B → Normal。  
**Treasury：** 下周重点2Y/5Y/7Y，公告金额合计$183B。  
**COMEX：** 🟢 今日采集通过；Registered 20D −2.26%。  
**Cash Liquidity：** MMF周资产增加$21.49B。

### ① Overnight｜10/23
S&P 500 **7,623.68（−0.52%）**｜Nasdaq **25,955.34（−0.21%）**｜US10Y **5.00%（+4bp）**。citeturn3search1turn6search2

DXY **101.76**（报道时）｜WTI **$103.27**（结算）｜Gold **$4,026.15/oz**（10/23 09:36 UTC现货）｜BTC **约$81,464**（10/23行情参考，非实时）。citeturn6news33turn4news60turn4search2turn10search3

### ② US Contrarian
**urlAAIIhttps://www.aaii.com/sentimentsurvey｜week ending 10/21：** Bull **36.9%**｜Neutral **17.3%**｜Bear **45.8%**｜Spread **−8.9pp**。citeturn2view3

**urlCNN F&Ghttps://www.cnn.com/markets/fear-and-greed：** 待确认。

**VIX 19.45**（10/23）｜**VIX3M 20.12**（最近可靠值10/22）。同日可比口径10/22：19.03 / 20.12＝**0.946 → Contango**；10/23 Ratio待确认。citeturn3search2turn8search6

**判断：** AAII偏悲观，但尚无法确认三项共同处于极端恐惧区。

### ③ Crypto F&G
**今日10/24：待确认｜昨日10/23：50 Neutral｜7日前10/17：55 Greed。**

urlAlternative.me官方APIturn2view0

### ④ 今日 Event Risk｜MYT
**10/24（周六）：无已确认Tier-1美国宏观事件。**

### ⑤ SRF｜纽约联储
**10/23两场操作：$0 + $0＝$0B → Normal。** 官方结果已公布；SRF使用量不等于QE。citeturn1view1

### ⑥ Treasury｜10/24–10/31
**Bills：** 10/26–29重点13W、26W、52W及短期Bills；Offering Amount待官方核验，**合计待确认**。

**Coupons：** 10/27 01:00 MYT｜2Y **$69B**；10/28 01:00｜5Y **$70B**；10/30 01:00｜7Y **$44B**。**公告转录合计$183B**，官方原始公告尚未独立复核。citeturn4search1

### ⑦ COMEX Gold｜CME采集器

**读取：GitHub提交 `1ed12c3d`｜本次核验08:03 MYT｜采集尝试07:59:59 MYT｜数据核验通过。**

本次读取该提交的JSON，并核对最新schedule采集于**08:00:13 MYT成功完成**；与采集尝试相差14秒，符合规则。

**Activity：10/22｜Report：10/23**  
**状态：NORMAL / UNCHANGED / WITHIN_AGE_LIMIT**  
**Registered Ratio：63.627%。**

| 分类 | 当前库存 | 1D | 5D | 10D | 20D |
|---|---:|---:|---:|---:|---:|
| Total | **23.283M oz** | −0.257% | −0.612% | −0.828% | −0.314% |
| Registered | **14.814M oz** | −0.018% | −0.018% | −1.678% | **−2.257%** |
| Eligible | **8.469M oz** | −0.673% | −1.634% | +0.694% | +3.277% |

**观察：** Total单日减少**60,090 oz**，未触发−1%警戒；Registered 20D累计减少**342,054 oz**，继续单独观察。

**窗口基准：** 5D＝10/15、10D＝10/08、20D＝09/24，全部可计算。历史9/18→9/21存在余额衔接异常，但当前窗口未跨断点。

Pledged已包含在Registered；Eligible下降不能单独证明交割短缺。NORMAL仅代表Total单日库存警戒未触发。

**官方最新发布状态未独立确认**（`is_latest_confirmed=false`）。

来源：url本次GitHub提交JSONhttps://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/blob/1ed12c3d753a97200e2cd68a9c50c7a383dc7d67/data/latest.json｜url今日定时采集记录https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/runs/40042687320｜urlCME官方报告https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls

### ⑧ Cash Liquidity｜ICI
**10/22发布、截至10/21：MMF总资产$7.94457T｜周资产增加$21.49B。**

前周减少$40.46B，本周转增。资产变化可近似反映资金流，但不是精确净流入，也不能单独证明资金逃向现金。citeturn2view2

---

后续可执行：

- [补齐10/23 CNN与VIX3M官方数据](f)
- [制作最新COMEX手机趋势图](f)
