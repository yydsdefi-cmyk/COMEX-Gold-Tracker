# 给下一位LLM的接手指令

继续现有“市场晨报与Crypto监管周报GitHub自动化”项目，先阅读同目录HANDOFF.md、DEPLOYMENT_STATUS.json、METHOD_CHANGES.md、SOURCE_REGISTRY.md、specs/original_missions.json及evidence/2026-10-26-live-validation.json。

唯一生产仓库：https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker ，分支main。不要另起一套系统。完整交接包中的source/是带数据的仓库快照；离线阅读和审计可直接使用，写回前必须从当前远端读取最新HEAD并保留其他人的变更。

目标：每日08:00、周六10:00 Asia/Kuala_Lumpur自动生成报表，无新增订阅/API费用，无需ChatGPT、常开电脑。实现已部署；2026-10-25和26的正式daily due排程成功，首次生成约08:25和08:36，不能声称准点。2026-10-31周报首个正式排程尚未验证。当前来源30项中27项OK，CNN418、ICI403、BLS403仍缺失；完整法规法律影响分析没有等价实现。

先检查最新报告日期、质量及真实Actions日志，区分schedule、push、workflow_dispatch和rerun attempt；不要把测试输出的合成capture或旧周报的审计结果当作本次采集。不要反复查询UTC等待未来排程，也不要重复已有测试或主动生成相同报告，除非有代码变化、失败或新的验证目的。

如只需分析数据，读取：
- https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/daily.json
- https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/weekly.json
- https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/history.csv
- https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/quality.json
- https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/history.csv
- https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/imports/index.json

先列实际覆盖日期、缺失、单位与修订；区分观测日期、发布日期、供应商时间和抓取时间。CSV不是完整点时版本库，需时点重建时读取market_data/captures。旧导入是10/12–16的每日快照，LEGACY_NOT_REVERIFIED，不能当作官方观测历史或完整旧晨报。法规影响需继续读官方正文，不从标题断言生效或币价因果。

如已获得仓库写权限，可以在原项目内自主修复、验证并完成合理维护；没有写权限时先完成只读审计与具体补丁。新的LLM不会继承旧ChatGPT的GitHub授权；需要使用用户在新平台安全连接的账户，禁止把密钥写入对话、文件或公开仓库。

约束：保留所有不可变capture、报告revision和原Gold端点；不强推、不改hash掩盖损坏；不激活收费资源、不绕过来源访问限制、不擅自停用原ChatGPT任务、不扩大公开写权限。对已有授权内可逆维护无需反复分阶段询问。回复用简洁中文，报告PASS/FAIL/BLOCKED/UNKNOWN及证据，完成后更新交接。

优先顺序：核对真实运行与数据质量；在10/31自然发生后验证周报schedule；研究可合法稳定读取的CNN/ICI/BLS方案；有旧原件时补充历史；按需求增强全文法规研究。保持零新增费用和清晰的未完成边界。
