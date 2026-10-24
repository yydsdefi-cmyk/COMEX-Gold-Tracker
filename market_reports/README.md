# 市场晨报与Crypto监管周报

目标：每日08:00、周六10:00（Asia/Kuala_Lumpur），GitHub Actions自动采集、规则分析、Git归档、Pages手机阅读。无需ChatGPT、常开电脑或付费模型。

- Dashboard: https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/
- 晨报: https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/daily.html
- 周报: https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/weekly.html
- 工作流: https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/workflows/market-reports.yml

当前v1.3.0，2026-10-24已实际发布并条件验收（150项云端测试、真实manual both、360/390px手机与展开周表检查通过）；基础设施PASS，数据覆盖DEGRADED，完整原报告语义不等价。详见 [部署状态](DEPLOYMENT_STATUS.json) 和 [HANDOFF](HANDOFF.md)。

完整原提示词在 `specs/original_missions.json`；2026-10-24两份原任务输出在相邻文件。原任务保持启用，没有调用自动化修改接口。

## 本地运行与手动执行

Python 3.12，安装根目录 `requirements.txt`。新报表模块仅使用标准库；复用原Gold导出器的XLS依赖。

```bash
python -m pip install -r requirements.txt
python -m unittest discover -q
python -m market_reports verify
python -m market_reports recover  # only rebuild derived CSV after immutable archive checks
python -m market_reports.audit  # inspect PASS_CALCULABLE_ONLY / FAIL / BLOCKED
python -m market_reports run --report both
python -m comex_gold.cloud --output-dir public-data
python -m market_reports publish --site public-data
```

分别运行 `--report daily` 或 `--report weekly`；`--report due` 按MYT判断是否到时。手动运行会保留同一天的新revision，不覆盖旧内容。出错后的临时目录不能被误当成已发布成功。导出Gold需新的空目录。

手机：打开工作流地址 → Run workflow → report选daily/weekly/both → Run workflow。检查报告日期与质量，不能只看绿色工作流。原Gold入口及JSON路径保持不变，市场报表只加在 `/market/`。

## 调度与恢复

UTC `00:00/00:17/00:47` 每日，对应MYT08:00/08:17/08:47。周六UTC `02:00/02:27/03:17`，对应MYT10:00/10:27/11:17。不承诺准点：GitHub可能延迟或丢弃任务。Python再次检查MYT；不会提前发布。MYT无夏令时，美国事件使用America/New_York转换，季节性相差12或13小时。

正常已完成的due运行不重复采集；降级报告在目标时间后4小时内允许重试。每日/每周分别以MYT日期建立指针，数据与报告内容使用不可变hash/revision保存；CSV对相同源/指标/日期/值/发布日期去重，并保留修订值。新revision完整验证后才更新指针。中断后允许未引用的半成品，禁止发布；已有内容冲突或hash不符则中止，绝不静默覆盖。

两个工作流共享 `comex-cloud` 并发组，不互相取消。Gold每次发布也叠加已归档市场报表，避免下一次Gold运行擦掉dashboard。写Git成功后才部署Pages；推送冲突时停止，不force push。每天真实归档提交使仓库保持活动；如果平台/账号长期停机，仍可能触发60天无活动停用，不能自证从未调度的任务。页面打开时按MYT目标分别检查日报与周报：目标后4小时内标排队/补跑，之后标逾期；不使用另一份报告的生成时间掩盖漏更。

## 数据质量与限制

详见 `METHOD_CHANGES.md`、`SOURCE_REGISTRY.md`、`TEST_RESULTS.md`。缺失、过期、未来时间、操作不全分别标记。publication_date未知保持null，不用HTTP Date、抓取时间或网页修改时间冒充。观察日期、发布日期和抓取时间均保留。所有派生计算不调用LLM。

CNN官方接口可能418/403/429；AAII偶尔返回验证页；不绕过访问限制。次级Yahoo免费行情非稳定SLA，Gold/WTI使用明确标注的期货，并不冒充现货。SRF合并同日常规隔夜操作，排除明确标注的small value exercises，未知操作保留列表；少于2场标provisional，制度改变时须更新完整度规则。

COMEX仍使用原采集器的真实报告窗口，不按自然日重算。每次核对GitHub当前H、同H快照、最近采集workflow运行、当天05:00之后的attempt；风险NORMAL与读取核验分开。`is_latest_confirmed=false`照实披露。

监管模块是官方公告筛选、Federal Register元数据与正式GovInfo PDF索引。它不声称穷尽所有立法/讲话，不从标题断言法律效力或资产影响；Rule/Proposed Rule/Notice和生效日期分开。完整中文法律语义研究尚未等价迁移，见方法变更。

## 费用

当前公开仓库 + 标准ubuntu GitHub-hosted runner + GitHub Pages + Git归档；不调用任何付费LLM或数据API，预计新增订阅费USD0/月。Pages临时artifact仅保留1天；历史长期在Git。依赖GitHub和来源站当前免费政策/限额，免费不是永久服务保证。不要改成私有仓库或larger runner而假设仍无限免费。

## 失败提醒与排障

每源状态、错误、响应hash在quality/JSON和Actions日志。非核心缺项产生Actions warning；COMEX/SRF/Crypto/VIX/VIX3M关键源失败，在发布清楚标记的降级报告后使工作流失败。GitHub原生失败通知是否送达取决于账号Actions通知设置；本项目没有验证手机推送送达，没有外部消息服务。平台未创建任何运行时，本工作流也不能提醒自身。

- 页面旧：看报告实际日期和Actions最近schedule，不以网页可打开或绿色旧状态证明今日成功。
- CNN/AAII缺项：保留待确认；稍后手动Run，勿更换伪造浏览器身份或代理绕过限制。
- COMEX异常：先检查原Gold工作流，核对attempt和Report/Activity Date；report date在周末可能正常落后。
- Git推送失败：检查contents写权限/分支规则，合并远端变更后重跑，勿强推历史。
- Pages失败：Settings→Pages应为GitHub Actions，检查github-pages环境是否要求审批；不要删除原Gold站点。
- hash校验失败：停止发布，保留问题文件，从Git历史恢复已知完整revision；不要手动改历史值或仅删manifest。
- 时间/源schema变化：修改适配器并运行真实fixture及边界测试，保留方法版本和CHANGELOG。

维护：每月看一次source quality与定时记录，按需更新已固定SHA的Actions和依赖；不需要本机常开。完整无人值守仍受外部数据和GitHub可用性约束。


## 交付入口

|交付|地址/文件|
|---|---|
|仓库|https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker |
|Dashboard / 报告样本|[首页](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/) / [晨报](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/daily.html) / [周报](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/weekly.html)|
|运行时来源登记|[source_registry.json](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/source_registry.json)|
|数据质量|[quality.json](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/quality.json)|
|交接/排障|[HANDOFF.md](HANDOFF.md)，上文维护和失败排查|
|原始任务与历史样本|[原完整prompts](specs/original_missions.json)，[历史晨报](specs/historical_daily_2026-10-24.md)，[历史周报](specs/historical_weekly_2026-10-24.md)|
|方法与免费LLM比较|[METHOD_CHANGES.md](METHOD_CHANGES.md)|
|来源说明|[SOURCE_REGISTRY.md](SOURCE_REGISTRY.md)|
|测试及验收|[TEST_RESULTS.md](TEST_RESULTS.md)，[DEPLOYMENT_STATUS.json](DEPLOYMENT_STATUS.json)|
|机器证据|[v1.2手动触发](evidence/v1.2-manual-dispatch.json)，[手机页面](evidence/v1.2-mobile-pages.json)，[逐份时效](evidence/v1.2-clock-pages.json)，[云端验证](evidence/v1.2-cloud-validation.json)，[隔离恢复](evidence/v1.2-isolated-recovery.json)，[独立复算](evidence-independent-calculations.json)|
|文件完整性/变更|[MANIFEST.json](MANIFEST.json)，[CHANGELOG.md](CHANGELOG.md)|

目标为MYT每日08:00和周六10:00。临时诊断schedule已成功，延迟22分20秒；其both模式不代表正式due排程已通过。首次正式目标尚未到时，实际延迟以GitHub为准。原两项ChatGPT任务仍保留。

## v1.1：监管覆盖与故障记录

新增OCC公告和CLARITY/GENIUS官方BILLSTATUS行动记录。周报现在把国会行动、机构公告、FR刊登和所载生效日期分开；FR有界扫描完整7日文档窗口后本地筛选，明确PARTIAL/未知。旧报告与v1数据不重写，v2捕获包含新增来源。

真实失败会在本仓库维护一个带标记的bot故障issue，恢复后关闭；不更改人工issue，不发测试假故障。仅health-notice job有issues:write，报表job权限不扩大；是否手机收到通知仍未核验。若仓库禁用Issues/拒绝token写入，health-notice会失败并保留Actions日志，报表和Pages的已发布结果不会回滚。

云端ICI/BLS/CNN限制仍存在。ICI工作簿适配器本地成功不是云端成功，不能把fixture或本地旧数据当作云端新值。

## v1.2 档案验证与恢复

`verify`只读核对capture、完整报告revision、最新指针及CSV派生视图。`recover`先核验不可变档案，只重建缺失/不一致CSV，不修改旧capture或报告；不可变档案损坏时停止。工作流联网前执行recover，成功后按原有顺序归档及发布。不要手动改pointer或quality来把降级报告涂成正常。

目标前的健康手动预览不会抑制到时重新生成；111项本地与云端测试及手机实际日期状态已验收。浏览器时效提示以设备时钟为准，不是主动推送。原任务、数据缺项及首次真正schedule未到时的限制保持。

## v1.3 已部署，条件验收

新增NYFed公开日历旁证、SRF完整度保护、有单位的周变化和只读Decimal审计；实际状态见DEPLOYMENT_STATUS.json。BLS/ICI/CNN的云端限制不因本地可读而消失。Pages保留近180天及每类最新报告，更旧记录从按月导航打开仓库Markdown，完整CSV/JSON及修订保留。

最新验收见[HANDOFF v1.3](HANDOFF.md)及[机器证据](evidence/v1.3-cloud-validation.json)；[最终展开周表](evidence/v1.3-expanded-mobile.json)和[独立数值审计](evidence/v1.3-numeric-audit.json)已长期归档。两个临时验收workflow已移除，不再循环等待时间或重复生成。

## 手机查看

打开Dashboard并收藏，选择晨报或周报；再次查看时刷新，核对报告日期及来源质量。支持有现代浏览器的手机、平板和电脑，阅读不需登录GitHub或安装App。GitHub云端按MYT每日08:00、周六10:00生成，关闭设备或网页不影响运行；准点受GitHub排队影响。网页本身不主动推送通知。
