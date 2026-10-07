# 免费历史回补核验

核验日期：2026-10-07。新增费用：$0。

26 份真实 CME Gold Stocks Excel，通过 Internet Archive 免费取得。每份均验证 CDX 原文件 SHA-1、保存 SHA-256，并逐项核对库存、出入库、调整、仓库求和及日期；另直接从原工作表读取 4 个汇总库存单元格和两个日期，与解析结果比较。

最新 2026-10-06 报告的存档字节与当前 CME 直接下载字节完全一致。历史来源明确记录为 internet_archive_original_cme，不冒充直接从当前 CME 下载历史。

Activity Date 覆盖 2026-08-28 至 2026-10-05；最近 20 个工作日候选全部取得，核验 20/20。未取得候选日期：[]。

5D Total：0.309046%；20D：不可计算（MISSING_WEEKDAY_OR_UNCONFIRMED_HOLIDAY）。

2026-09-18 → 2026-09-21：Eligible 与 Total 的上一份 TOTAL TODAY 和下一份 PREV TOTAL 不一致；后者表内仓库明细数量也减少。原因未确认，不将差额视为实物出库。20D 窗口还包含未分类的 9 月 7 日日期间隙，因此保持 null。报告数足够不等于序列可以直接相减。

没有将免费第三方周度 CSV 或 DataMine 旧样本导入生产历史。每个生产观察的存档地址、时间、哈希在 history.csv 与 observations 中保留；最新同字节报告优先保留当前 CME 直接下载来源。

| Activity Date | Report Date | Total oz | Registered oz | Eligible oz | 勾稽检查 | 原报告存档 |
|---|---|---:|---:|---:|---:|---|
| 2026-08-28 | 2026-08-31 | 27,300,849.162 | 14,910,864.121 | 12,389,985.041 | 296 | [XLS](https://web.archive.org/web/20260901082918id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-08-31 | 2026-09-01 | 27,345,948.270 | 14,938,907.799 | 12,407,040.471 | 296 | [XLS](https://web.archive.org/web/20260901220003id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-01 | 2026-09-02 | 27,345,658.911 | 15,103,739.335 | 12,241,919.576 | 296 | [XLS](https://web.archive.org/web/20260902211225id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-02 | 2026-09-03 | 27,377,617.005 | 15,105,765.419 | 12,271,851.586 | 296 | [XLS](https://web.archive.org/web/20260903211258id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-03 | 2026-09-04 | 27,377,617.005 | 15,110,183.011 | 12,267,433.994 | 296 | [XLS](https://web.archive.org/web/20260904213004id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-04 | 2026-09-08 | 27,377,681.307 | 15,110,183.011 | 12,267,498.296 | 296 | [XLS](https://web.archive.org/web/20260908211310id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-08 | 2026-09-09 | 27,377,456.250 | 15,120,219.224 | 12,257,237.026 | 296 | [XLS](https://web.archive.org/web/20260909220002id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-09 | 2026-09-10 | 27,377,527.229 | 15,120,219.224 | 12,257,308.005 | 296 | [XLS](https://web.archive.org/web/20260910211331id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-10 | 2026-09-11 | 27,348,516.543 | 15,120,219.224 | 12,228,297.319 | 296 | [XLS](https://web.archive.org/web/20260911211239id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-11 | 2026-09-14 | 27,348,516.543 | 15,120,219.224 | 12,228,297.319 | 296 | [XLS](https://web.archive.org/web/20260914220001id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-14 | 2026-09-15 | 27,383,818.341 | 15,155,521.022 | 12,228,297.319 | 296 | [XLS](https://web.archive.org/web/20260915211239id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-15 | 2026-09-16 | 27,383,818.341 | 15,155,521.022 | 12,228,297.319 | 296 | [XLS](https://web.archive.org/web/20260916234546id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-16 | 2026-09-17 | 27,383,818.341 | 15,156,292.646 | 12,227,525.695 | 296 | [XLS](https://web.archive.org/web/20260917220001id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-17 | 2026-09-18 | 27,383,786.190 | 15,156,292.646 | 12,227,493.544 | 296 | [XLS](https://web.archive.org/web/20260918234705id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-18 | 2026-09-21 | 27,415,786.919 | 15,156,292.646 | 12,259,494.273 | 296 | [XLS](https://web.archive.org/web/20260921220048id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-21 | 2026-09-22 | 23,356,390.373 | 15,185,624.842 | 8,170,765.531 | 164 | [XLS](https://web.archive.org/web/20260922211411id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-22 | 2026-09-23 | 23,356,326.071 | 15,185,624.842 | 8,170,701.229 | 164 | [XLS](https://web.archive.org/web/20260923211408id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-23 | 2026-09-24 | 23,356,326.071 | 15,185,624.842 | 8,170,701.229 | 164 | [XLS](https://web.archive.org/web/20260924211639id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-24 | 2026-09-25 | 23,356,326.071 | 15,156,338.144 | 8,199,987.927 | 164 | [XLS](https://web.archive.org/web/20260925211338id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-25 | 2026-09-28 | 23,387,988.611 | 15,156,338.144 | 8,231,650.467 | 164 | [XLS](https://web.archive.org/web/20260928220012id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-28 | 2026-09-29 | 23,407,279.211 | 15,103,820.838 | 8,303,458.373 | 164 | [XLS](https://web.archive.org/web/20260929211043id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-29 | 2026-09-30 | 23,439,258.332 | 15,138,204.297 | 8,301,054.035 | 164 | [XLS](https://web.archive.org/web/20261001081653id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-09-30 | 2026-10-01 | 23,467,833.896 | 15,086,528.079 | 8,381,305.817 | 164 | [XLS](https://web.archive.org/web/20261001211303id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-10-01 | 2026-10-02 | 23,479,747.126 | 15,086,528.079 | 8,393,219.047 | 164 | [XLS](https://web.archive.org/web/20261002220001id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-10-02 | 2026-10-05 | 23,479,618.522 | 15,086,528.079 | 8,393,090.443 | 164 | [XLS](https://web.archive.org/web/20261005211234id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
| 2026-10-05 | 2026-10-06 | 23,479,618.522 | 15,086,528.079 | 8,393,090.443 | 164 | [XLS](https://web.archive.org/web/20261007081907id_/https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls) |
