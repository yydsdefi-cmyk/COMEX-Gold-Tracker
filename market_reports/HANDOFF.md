# HANDOFF — Market Reports Migration

Version 1.2.0, 2026-10-24.

原始任务、完整原文、实际历史样本已恢复并保存在specs。原ChatGPT任务保持启用。唯一已授权目标仓库为 https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker ，GitHub连接确认账号有admin/push，实际写入及部署结果另以证据确认，不能从权限字段推定成功。

入口：README.md、METHOD_CHANGES.md、SOURCE_REGISTRY.md、TEST_RESULTS.md、DEPLOYMENT_STATUS.json。根目录原Gold README及comex_gold模块保持；仅在原Gold workflow添加叠加报告的步骤。新workflow和Gold共享并发组，防止Pages覆盖与Git写竞争。

状态：原40项回归+30项新增方法，共70项离线测试通过；真实daily和weekly本地生成完成。首次测试抓到Treasury漏未来券及第二次30B FRN漏计，已修正接口及分类；不得把初次失败记录改成通过。完整live源可用性以最新quality记录为准。

最终部署证据见DEPLOYMENT_STATUS.json及本文最终验收。未来schedule到时才有实际调度证据；仅配置正确和manual通过不能宣称未来schedule已成功。

已知未等价迁移：CNN拒绝/AAII偶发验证页；完整监管语义、所有Congress动态、事件日期时间线、WI拍卖tail和因果反应、精确MMF净流与3个月流趋势。免费规则报表可自主运行，但这些缺口意味着不可宣称原报告100%无损替代。维护者无需ChatGPT；任何Python/GitHub维护者可按README运行。

不要删除或自动停掉原ChatGPT任务。既有Gold根数据入口必须保留。不得引入付费模型、试用、客户数据、常开主机或硬编码凭证。历史revision与source capture不可重写。


## v1.0.1 验收历史（2026-10-24）

**基础设施已真实部署；总体CONDITIONAL，未达原报告完整语义等价。** 最终源码commit为c342517df4f4e43d2952169d9d6cc1cd981fa60e。真实manual workflow_dispatch `both` 运行40065487640成功，云端70测试通过，daily/weekly同一capture归档后Pages成功。一次性验收40065481203成功：360/390px各3页、详情交互、7条公开数据路径均通过；JSON证据永久保存在相邻evidence文件。一次性验收workflow在最终交付提交移除，常规报表job没有actions:write。

从最新远端建立独立干净worktree，70测试通过，17个archive对象通过hash/来源绑定核验；当时CSV456条。独立Decimal复算Total/Registered/Eligible的5D/10D/20D共9项通过，不调用原collector计算函数。原Gold在新增叠加步骤后实际运行40064686634成功，原入口未覆盖。CSV条数/档案对象数是验收时点值，后续正常增加。

云端26个source receipts中23项OK；CNN418、ICI403、BLS403。首次本地ICI/BLS可读不能作为云端成功证据，没有用本地旧值填云端空缺。AAII偶发验证页也会保留缺失。监管仍是官方文种/生效日期+主题线索，非穷尽法律研究。原ChatGPT两任务保持启用；不要因工作流绿色就删原任务。

排程配置已在main核验。新排程首次到时尚未来临：首个目标2026-10-25 08:00 MYT，下次周报2026-10-31 10:00 MYT；不能把push/manual说成schedule。GitHub原生失败通知送达未验证。当前预计新增订阅费USD0/月，无LLM、常开电脑或ChatGPT依赖。

运行时网站、源码、原prompts、样本、source registry、quality、历史、MANIFEST、CHANGELOG均可从README入口访问；精确状态以DEPLOYMENT_STATUS.json为准。重复线程收敛为这一套，不发布market_intel/intelligence第二套。

## v1.1 验收历史

已真实部署，条件验收。源码9136230f5628d3e1a2aabd8a3f6100d3673b75e7；manual both 40068302153及手机40068297391成功。云端和独立远端checkout均93测试通过；26归档对象/459 CSV行验证，旧schema1保留。OCC及两个指定国会法案官方状态已接入，FR完整窗口分页及法律阶段/美东日期核对已部署。

29来源中26 OK；CNN418、ICI/BLS403仍缺失。ICI工作簿适配器可离线验证，不代表云端可取。SEC priorities仅线索，不宣称已读被拒绝正文。完整法律语义研究仍未等价；首次实际schedule未到时仍UNKNOWN。

故障issue机制的正常云端分支已运行，输出HEALTHY_NO_INCIDENT、未创建issue；创建/去重/恢复逻辑经模拟测试，未故意制造真实生产故障。通知送达取决于GitHub设置，未验证。临时探测及验收workflow已移除，仅保留两个生产workflow。后续优先检查首次实际定时运行与来源质量；不需ChatGPT或本机常开。当前新增订阅费预计USD0/月，原两任务和Gold功能保留。

当前机器证据在evidence/v1.1-*.json；旧证据保留为历史。MANIFEST按实际Git字节重新计算，覆盖新增源码、fixture、交接文档和两个生产workflow。

## v1.2 当前交付状态

已部署，条件验收。源码fb0f1b335e2d36411bcf032c031551573935e5aa。真实manual both [40070992174](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/runs/40070992174)和手机验收[40070987079](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/runs/40070987079)成功。云端与全新远端worktree各111测试通过、0跳过；38归档对象、CSV463行，六个schema1和六个schema2 capture并存。与v1.1逐字节比较72个旧不可变文件，无修改。

增强核验覆盖revision内容寻址、报告目录/日期/capture、quality与来源、pointer字段及CSV派生视图。verify只读拒绝漂移；recover在全部不可变对象验证后重建CSV；坏capture绝不自动改hash。另对真实数据的隔离副本模拟CSV中断：只读拒绝、恢复后与冻结CSV一致，90个不可变文件不变，没有源网络请求。原Gold导出器叠加前后10文件hash不变；云端原Gold两数据入口HTTP200。

当前首页、日报、周报按MYT目标独立检查发布时效，允许4小时补跑窗口，之后提示逾期。实际浏览器模拟周日12:00 MYT时显示daily OVERDUE、weekly CURRENT；7个边界检查通过。历史页单独标记；目标前的健康手动预览不会使定时运行跳过。

29来源中26 OK，CNN418/ICI403/BLS403仍明确缺失；没有用本地可读值冒充云端。法律语义等价仍NOT ACHIEVED。首个新schedule尚未到时，真实执行仍UNKNOWN：下一目标2026-10-25 08:00 MYT、周报2026-10-31 10:00 MYT。配置及workflow active已核对，不能以模拟日期或manual代替真实schedule。health-notice正常分支成功，未制造生产故障；手机通知送达未验证。

临时验收/探测workflow已移除，只保留原Gold与market-reports两个生产workflow；无永久actions:write权限扩张。预计新增订阅费USD0/月，仍无需ChatGPT或常开电脑。最新机器证据在evidence/v1.2-*.json；旧证据原样保留。原两个ChatGPT任务未修改。
