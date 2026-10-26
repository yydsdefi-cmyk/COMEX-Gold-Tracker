# 市场报表自动化交接 — 2026-10-26

这是当前接手入口，仅涵盖市场晨报、Crypto监管周报及复用的COMEX Gold Tracker。方法版本仍为1.3.0；本轮核验真实运行并更新交接，没有改计算、调度或权限，没有触发新采集。旧交接全文保存在handoff_history/HANDOFF_2026-10-24.md。

## 当前结果

|项目|当前事实|
|---|---|
|生产仓库|https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker ，main；本轮核验基线aff037c54d44db5b714f1fdda7d1cfe809bbb5e8|
|正式晨报schedule|PASS：10/25与10/26真实schedule事件，REPORT_KIND=due，采集、归档和Pages成功|
|准点08:00|不保证；首次生成10/25 08:25:17 MYT、10/26 08:36:06 MYT|
|正式周报schedule|UNKNOWN：首次目标2026-10-31 10:00 MYT；当前10/24周报来自push/manual路径|
|最新晨报|10/26；最新revision于09:30:07 MYT生成，capture fa5fd67ce7e93a5da48321c7803dd1a83d3eac58ea4e2926669b99f28a14857c|
|最新周报|10/24；capture 7860be4b5f122e9ca494250530837257b50d1137f13459aa9c5e461247e5d8bf|
|来源|DEGRADED：30项receipt、27项OK；CNN418、ICI403、BLS403。NYFed补充日历不代表BLS直连恢复|
|当前验证|最近真实云端159测试通过；干净远端快照verify核对72对象，修改前MANIFEST的79项哈希全部一致|
|数值审计|10/24周报13项可算值PASS、0 FAIL、3不可算；不代表10/26所有值或完整法律语义均通过|
|原Gold|10/25–26六次schedule成功；Activity 10/22、Report 10/23；10/26 07:56:55 MYT尝试UNCHANGED；is_latest_confirmed=false|
|完整语义等价|NOT ACHIEVED：全文法律影响、部分资金流/拍卖指标仍不足，见METHOD_CHANGES.md|
|手机通知|UNKNOWN；网页不主动推送，原生GitHub失败通知送达取决于账户设置|
|原ChatGPT任务|本轮未修改；10/24恢复的原prompt在specs。10/26只读查询未取得匹配记录，当前启停UNKNOWN，不据此推断删除或仍启用|

本交接后main可能新增文档提交；接手时重新读取远端HEAD。本轮没有为文档更新重复运行159项回归，使用刚完成的云端证据；已重新只读核验当前档案和最新周报数字。

## 公开入口

- 首页：https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/
- 晨报：https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/daily.html
- 周报：https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/weekly.html
- 报表工作流：https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/workflows/market-reports.yml
- 原Gold工作流：https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/workflows/collect-and-publish.yml

手机/平板/电脑的现代浏览器可直接阅读，无需登录。新LLM可读取公开文件分析；写回仓库或手动Actions需要用户在新平台安全连接GitHub，新LLM不继承旧ChatGPT授权。

## 调度与发布

全部目标时间Asia/Kuala_Lumpur，UTC+8无夏令时；美国事件用America/New_York处理DST。

|工作流|UTC cron|MYT配置目标|
|---|---|---|
|daily|0,17,47 0 * * *|每日08:00、08:17、08:47|
|weekly|0,27 2 * * 6；17 3 * * 6|周六10:00、10:27、11:17|
|原Gold|17 21 * * *；17 23 * * *；41 23 * * *|每日05:17、07:17、07:41|

GitHub可能延迟或未触发某个cron；本轮观察到每日报表2次真实运行，不能说3个配置点全部执行。不要循环查询UTC等待未来排程，也不要增加临时cron作无目的重复验收。

两个workflow共享comex-cloud并发组，cancel-in-progress=false。Gold-only发布也叠加现有市场页。生产顺序：checkout main、依赖、回归、recover、due采集、独立周变化audit、Git归档、合并Gold/市场导出、Pages、来源警告与关键源检查。先归档后发布；推送冲突停止，不force。

健康due有当期报告就不再采集；降级报告目标后4小时内允许恢复尝试，提前手动预览不抑制正式到时生成。页面daily/weekly分别检查CURRENT/PENDING/OVERDUE，避免一个新报告掩盖另一个漏更。

comex/srf/crypto/vix/vix3m关键源失败时，先发布明确降级报告再使job失败。独立health-notice维护一个bot拥有的故障issue，恢复后关闭；平台完全没创建运行时，任务无法自我通知。没有外部消息服务。

重跑修复必须保留：上传name与deploy artifact_name都用github-pages-${{ github.run_id }}-${{ github.run_attempt }}，防止同run多attempt默认名冲突。40096226964真实attempt2已成功。当前市场workflow固定Actions SHA；原Gold仍有@v标签，不能称全仓库均固定SHA。

## 给其他LLM的数据接口

以下路径根地址为https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/ ：

|用途|路径|
|---|---|
|最新结构化报告|market/daily.json、market/weekly.json|
|对应中文文本|market/daily.md、market/weekly.md|
|市场历史|market/history.csv|
|质量及来源登记|market/quality.json、market/source_registry.json|
|旧导入目录|market/imports/index.json；条目csv/json相对该目录解析|
|Gold完整历史与快照|根目录history.csv、latest.json|

报告JSON包含kind、intended_local_date、target_time_myt、capture_id、capture、quality、method_version；weekly另含analysis.weekly_comparisons/upcoming_tier1。receipt保存来源URL、抓取时刻、响应hash、状态、观测和错误，并不保存所有原始HTTP正文。

市场CSV字段：source,metric,observation_date,publication_date,value,unit,fetched_at_utc,response_sha256,quality。当前525行是观测/修订值记录，不是525个交易日。未知发布日期留空，不能用HTTP修改时间、供应商更新戳或抓取时刻替代。

CSV按源/指标/观测日/值/发布日期合并相同读取；它不是完整vintage流水。需历史时点重建“当时可知信息”时读market_data/captures，并承认未知首次发布日期；不能仅凭CSV抓取时刻声称完成严格point-in-time回测。历史STALE可能只表示抓取时较旧，不自动表示历史值错误；当前源是否失联另看quality。

分析先核对实际覆盖、单位、缺失和修订，按观测日对齐。未来拍卖日的已公告规模不是已完成拍卖。Gold/WTI行情为期货，不是现货；US10Y变化为bp，情绪差为pp/点，库存oz/M oz，空白不是0。

## 源文件、档案与旧数据

- market_data/captures/<sha256>.json：不可变capture，当前24份，schema1/2/3分别6/6/12。
- market_data/reports/<daily|weekly>/<MYT日期>/<revision>/：不可变report.md/report.json/quality.json/MANIFEST.json，当前44个revision；日期目录latest.json为最后更新的可变指针。
- 当前daily日期为10/24、25、26，weekly只有10/24。网页呈现近180天及每类最新报告，更早条目链接Git；全量CSV及修订留在仓库。
- market_data/history.csv是可从已核验capture重建的派生视图。不要覆盖capture/revision或修改hash“修复”损坏。
- 原Gold历史为data/history.csv，39条，Activity范围08/28至10/22；不假设连续无缺口或20D一定可算。
- market_data/imports/legacy-7ba0d79023bd8e6b.json保留10/12–16旧导出5个每日快照，2个缺失单元，LEGACY_NOT_REVERIFIED。AAII为周度当时沿用值，COMEX快照日未逐行对应Activity/Report Date。保留原值、M oz单位、日期语义，不并入已回源CSV，不伪造旧完整晨报。其他完整旧报告尚未恢复。
- specs/original_missions.json为完整原prompt/原调度配置，同目录有原报告样本；METHOD_CHANGES.md逐项说明未等价要求；SOURCE_REGISTRY.md及运行时registry登记源和限制。

## 核心计算限制

SRF：<10B Normal；[10,50)B Stress；[50,100]B Red Alert；>100B Severe。原50B有重叠，本实现选择已披露工程解释。排除明确SVE/test/exercise，常规两场完整度为当前制度假设；部分场次不能显示全天Normal，高SRF不等于QE。

COMEX：Total单日严格<-1/-3/-5%对应黄/橙/红；Pledged已在Registered内，不重复加。Eligible下降不等于可交割黄金短缺。1D来自官方PREV TOTAL，多日按原采集器连续报告窗口，null和连续性异常保留，不跨断点自行相减。读取同HEAD快照并核对当天MYT05:00后、无未来、≤26h的采集尝试与运行匹配。官方最新状态未独立确认时照实披露。

周变化保持实际基准日期和%/bp/pp/B USD单位；VIX比率使用同观察日，只是VIX/VIX3M，不称完整期货曲线。ICI资产差不是精确净流量。全文法律生效、适用范围及资产影响需官方正文核验，提案/讲话/标题相关性不能充当生效义务。

## 运行、测试及恢复

在仓库根目录用Python3.12建立venv，安装requirements.txt。无LLM key或计费API要求；报表主要用标准库，复用Gold的XLS依赖。

```bash
python -m pip install -r requirements.txt
python -m unittest discover -q
python -m market_reports verify
python -m market_reports.audit
python -m market_reports recover
python -m market_reports run --report due
python -m market_reports run --report both
python -m comex_gold.cloud --output-dir public-data
python -m market_reports publish --site public-data
python -m market_reports.imports old.csv --data-dir market_data
```

verify/audit只读。recover仅在不可变档案通过后恢复派生CSV。run --report both会真实联网并产生修订，仅在需要时运行；Gold导出目录需为空。导入器只接受当前已验证列结构，其他格式先设计映射并保留原件。

测试stdout会打印合成capture和“No report due”；不能取日志首个capture_id当真实采集。结合实际步骤、归档和指针。audit CLI默认检查最新weekly，因此10/26日志13项审计仍对应10/24周报。早期失败记录保留，后续成功不抹去Treasury漏券、上传截断和重跑冲突的历史。

当前真实证据：首次daily 40146588471、10/26首次40250109746、10/26恢复40254481640、最近Gold40246990539。链接格式https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/runs/加run_id。机器证据evidence/2026-10-26-live-validation.json；历史手机360/390px验收是10/24证据，本轮未重新测试所有设备。

## 费用、权限与接手边界

架构为公开仓库、标准ubuntu GitHub-hosted runner、Pages、Git归档；新增订阅/模型调用费0。平台政策和限额会变化，不承诺永久免费或无限流量，不擅自改私有仓库、larger runner、计费云服务或付费数据。

网站公开静态只读，普通访客可下载内容、源码及公开提交信息，分享URL不授予写权限。没有登录、上传、交易或公开写入口。不要发布私人持仓、账户或密钥。10/24常见密钥格式扫描无匹配不等于完整安全审计；本轮未变更权限或重新做安全审计，不保证无恶意流量/账户风险。

原ChatGPT任务本轮未修改，当前启停UNKNOWN，不擅自删除。GitHub执行不依赖它们。新的LLM有GitHub授权才可写回；不把token贴入对话、代码或交接文件。

## 下一步

先用TAKEOVER_PROMPT_ZH.md接手，核对最新main、报告日期、quality和实际schedule，不重建已有系统。10/31自然到时后验证weekly due；研究合法稳定的CNN/ICI/BLS来源，不绕过403/418；有旧原件再补历史；按用户需求补全文法规研究。可选维护包括核验后固定原Gold的Actions SHA。

用户偏好简洁中文、合理可逆维护直接执行、避免重复工作和多轮审批。既有授权内可自主修复并验证，但不得引入费用、强推、改不可变历史、擅改原任务或代发外部消息。结果区分PASS/FAIL/BLOCKED/UNKNOWN，完工后更新交接。
