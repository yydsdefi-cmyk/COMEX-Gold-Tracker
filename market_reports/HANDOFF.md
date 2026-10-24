# HANDOFF — Market Reports Migration

Version 1.0.0, 2026-10-24.

原始任务、完整原文、实际历史样本已恢复并保存在specs。原ChatGPT任务保持启用。唯一已授权目标仓库为 https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker ，GitHub连接确认账号有admin/push，实际写入及部署结果另以证据确认，不能从权限字段推定成功。

入口：README.md、METHOD_CHANGES.md、SOURCE_REGISTRY.md、TEST_RESULTS.md、DEPLOYMENT_STATUS.json。根目录原Gold README及comex_gold模块保持；仅在原Gold workflow添加叠加报告的步骤。新workflow和Gold共享并发组，防止Pages覆盖与Git写竞争。

状态：原40项回归+27项新增方法，共67项离线测试通过；真实daily和weekly本地生成完成。首次测试抓到Treasury漏未来券及第二次30B FRN漏计，已修正接口及分类；不得把初次失败记录改成通过。完整live源可用性以最新quality记录为准。

部署状态与后续证据在DEPLOYMENT_STATUS.json更新；提交前未完成远端验收时必须标PENDING/BLOCKED。不得把目标URL当成已发布URL。需检查push实际workflow、远端档案提交、Pages200与手机宽度、manual workflow_dispatch。schedule未来到时才有实际schedule证据；仅YAML正确只能列配置通过。

已知未等价迁移：CNN拒绝/AAII偶发验证页；完整监管语义、所有Congress动态、事件日期时间线、WI拍卖tail和因果反应、精确MMF净流与3个月流趋势。免费规则报表可自主运行，但这些缺口意味着不可宣称原报告100%无损替代。维护者无需ChatGPT；任何Python/GitHub维护者可按README运行。

不要删除或自动停掉原ChatGPT任务。既有Gold根数据入口必须保留。不得引入付费模型、试用、客户数据、常开主机或硬编码凭证。历史revision与source capture不可重写。
