# 原方法保留与必要变化

原始提示词从两项实际Automation配置恢复，非记忆重构；完整原文和2026-10-24历史样本随代码存档。跨线程文件搜索两轮无Library结果；找到了2026-10-21交接文件及COMEX离线候选修复。未找到独立、完整的finance automation可行性研究工程，因此不声称已恢复它。

|原要求|实施与证据边界|
|---|---|
|AAII/CNN/VIX/VIX3M/期限比、Crypto今日/昨日/7日前|逐源采集，VIX比率只取共同日期，Crypto按实际日期找值。AAII仅公共近期周度，不请求成员历史。未定义AAII/VIX极端阈值，联合极端保留待确认。|
|Overnight S&P/Nasdaq/US10Y/DXY/WTI/Gold/BTC|免费Yahoo次级日线；Gold/WTI为期货，非历史样本里的现货。标记可能盘中，不宣称官方统一收盘。US10Y差值×100为bp。|
|所有数据截至/发布时间|源给出的才填，未知null；不把抓取/HTTP修改时间当发布时间。ICI表中发布日期、AAII week ending、NYFed lastUpdated保留不同语义。|
|SRF <$10B、$10–50B、$50–100B、>$100B|原文50B边界重叠未明确；本版本显式取[10,50) Stress、[50,100] Red Alert、>100 Severe；10B Stress。不是把推断冒充原文。日内各场USD相加，SVE排除；2场为当前制度完整度假设。|
|COMEX防旧快照|读取当前ref H、同H latest.json和专属采集workflow最近6条运行（比混合所有workflow更精确）；异常重新取H一次。当天MYT≥05:00、无未来、≤26h、无失败/落后运行；保持四窗口与null。独立验算Total=Registered+Eligible及Ratio；官方XLS和连续性复算仍由原采集器负责。|
|Treasury供给、BTC/high yield/tail、拍卖后反应|采用官方announced?days=30后按auction date客户端筛选。首轮search的默认日期字段漏Nov2结算券，独立检查发现并修复；不是沿用漏项。Bill/Coupon分开，FRN/TIPS用字段正确分类；无WI报价不生成tail或因果反应。历史样本2Y/5Y/7Y共183B，官方新检查另有30B FRN，全部coupon口径213B。|
|Tier-1最多3个、下周事件|官方BLS/BEA/FOMC，MYT与美东DST转换。FOMC14:00 ET是明确披露的惯例假设；不从会议日历伪造时刻已逐次公布。日历不是全市场覆盖。|
|ICI资产、周净流入/约3个月|ICI周资产和资产差可得；差额不等于净流入。精确净流与3个月趋势缺数据时留待确认。没有把总资产高解释成即将买股票。|
|周总结与监管Timeline|累计真实日报并保留独立日期；冷启动明确不足7天，可用同源历史序列补趋势但不伪称原晨报历史。官方RSS、Treasury索引、GovInfo bill publications、Federal Register搜索+单文档生效元数据。按发布日期排序，未知event_date留空；原任务按事件日期的完整Timeline尚不等价。|
|完整中文监管结构变化与资产影响|规则系统能提供可核验的文种/日期与主题相关性，不具备完整法律语义判断。只把标题相关性标为推断；保留适用范围和影响待正文核验。关键词可能遗漏、feed窗口有限、没有条目不表示没有事件。|
|手机版极简|首页七项总览与可展开详情，机器数据另有JSON/CSV；详细核验说明保留以便追溯。|
|不依赖ChatGPT/付费API|纯Python+HTML，零模型请求。原任务未删未暂停。|

未定义的原阈值不会用常见投资阈值补成“你的规则”。新增staleness是工程保守值（天数）：AAII/ICI10、Cboe/SRF4、Crypto1、BTC2、其他行情4；不是交易阈值或已核验交易日历。完整免费经济预期、WI报价、监管语义阅读存在真实能力边界，不能宣称原报告100%无损迁移。

免费LLM不是本系统的必要依赖：免费API配额/模型/地区/条款随时变，可能需要新账号、key或计费项目；GitHub standard runner不保证足够RAM/时限运行能可靠完成中英文法规分析的本地模型；低质量小模型也会引入无法验证的法律断言。因此本版不依赖任何免费试用、Google赠款、GitHub Models token或ChatGPT订阅额度。模板足够生成数字比较与监控等级；完整监管研究不足以仅凭模板等价替代。若以后接可选LLM，必须保留无LLM运行路径及单独预算/权限审计。

公开政策核验（2026-10-24）：GitHub官方说明公开仓库标准托管runner免费、Pages支持GitHub Free公开仓库，schedule可能高负荷延迟/丢失、60天无活动自动停用。相关官方链接列在SOURCE_REGISTRY.md。免费政策不是永久承诺。
