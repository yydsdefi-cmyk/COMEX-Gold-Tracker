# 市场晨报与Crypto监管周报

目标：每日08:00、周六10:00（Asia/Kuala_Lumpur），GitHub Actions自动采集、规则分析、Git归档、Pages手机阅读。无需ChatGPT、常开电脑或付费模型。

- Dashboard: https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/
- 晨报: https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/daily.html
- 周报: https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/weekly.html
- 工作流: https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/workflows/market-reports.yml

以上是部署目标地址；实际部署验收状态以 `DEPLOYMENT_STATUS.json` / `HANDOFF.md` 为准，文件存在不等于部署成功。

完整原提示词在 `specs/original_missions.json`；2026-10-24两份原任务输出在相邻文件。原任务保持启用，没有调用自动化修改接口。

## 本地运行与手动执行

Python 3.12，安装根目录 `requirements.txt`。新报表模块仅使用标准库；复用原Gold导出器的XLS依赖。

```bash
python -m pip install -r requirements.txt
python -m unittest discover -q
python -m market_reports verify
python -m market_reports run --report both
python -m comex_gold.cloud --output-dir public-data
python -m market_reports publish --site public-data
```

分别运行 `--report daily` 或 `--report weekly`；`--report due` 按MYT判断是否到时。手动运行会保留同一天的新revision，不覆盖旧内容。出错后的临时目录不能被误当成已发布成功。导出Gold需新的空目录。

手机：打开工作流地址 → Run workflow → report选daily/weekly/both → Run workflow。检查报告日期与质量，不能只看绿色工作流。原Gold入口及JSON路径保持不变，市场报表只加在 `/market/`。

## 调度与恢复

UTC `00:00/00:17/00:47` 每日，对应MYT08:00/08:17/08:47。周六UTC `02:00/02:27/03:17`，对应MYT10:00/10:27/11:17。不承诺准点：GitHub可能延迟或丢弃任务。Python再次检查MYT；不会提前发布。MYT无夏令时，美国事件使用America/New_York转换，季节性相差12或13小时。

正常已完成的due运行不重复采集；降级报告在目标时间后4小时内允许重试。每日/每周分别以MYT日期建立指针，数据与报告内容使用不可变hash/revision保存；CSV对相同源/指标/日期/值/发布日期去重，并保留修订值。新revision完整验证后才更新指针。中断后允许未引用的半成品，禁止发布；已有内容冲突或hash不符则中止，绝不静默覆盖。

两个工作流共享 `comex-cloud` 并发组，不互相取消。Gold每次发布也叠加已归档市场报表，避免下一次Gold运行擦掉dashboard。写Git成功后才部署Pages；推送冲突时停止，不force push。每天真实归档提交使仓库保持活动；如果平台/账号长期停机，仍可能触发60天无活动停用，不能自证从未调度的任务。页面打开时会检查26小时发布年龄。

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
