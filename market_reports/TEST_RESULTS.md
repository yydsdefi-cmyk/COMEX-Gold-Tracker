# Test results — 2026-10-24

实际命令：`python -m unittest discover -q`，v1.0.1本地最终运行70项、0失败。原Gold40项+新market_tests30个测试方法；不把用例内多个assert重复计数。网络端到端与远端部署不算离线测试通过。

|要求|结果|实际证据/边界|
|---|---|---|
|1 数据采集正确性|PASS（fixture与本地live覆盖）|AAII百分比与spread、Cboe收盘、Alternative日期、SRF操作、ICI资产、Treasury类型金额；未来源可用性不保证|
|2 来源可追溯|PASS|每观察源URL/响应hash/抓取时刻；没有用抓取日期代替发布日期|
|3 日期与时区|PASS|MYT08/10到时、早运行不发布、美东DST 12/13小时转换、naive时间拒绝|
|4 缺失与过期|PASS|超时/拒绝变MISSING；future拒绝；来源时效；COMEX同日05之后与26h校验|
|5 计算|PASS|SRF10/19–23常规$12M，测试$67M排除；ICI7944.57B/21.49B；coupon213B含FRN30B、非FRN183B|
|6 阈值分类|PASS|SRF10/50/100B边界；Total单日严格<-1/-3/-5%；50B归类为显式工程解释|
|7 重复执行|PASS|相同capture/revision幂等、CSV去重；健康due不再采集；降级有意允许恢复尝试|
|8 部分API失败|PASS|缺失COMEX的daily/weekly仍显式降级生成，其余源保留；拒绝访问不重试绕过，超时最多2次|
|9 报告渲染|PASS（HTML结构/escaping）|真实daily/weekly可生成、viewport与链接、脚本注入转义；手机视觉验收另列|
|10 历史完整性|PASS|完整revision文件集合/hash；修改capture报错；保留旧revision；来源绑定|
|11 workflow权限|PASS（静态）|新workflow默认read、job按需write、固定ActionsSHA、无pull_request_target/force；远端实际权限另列|
|12 中断恢复|PASS|模拟未完成revision，无manifest不得发布；重跑补齐同revision；已完成内容冲突拒绝|
|本地真实daily端到端|PASS / DEGRADED|2026-10-24真实网络采集、Markdown/JSON/CSV、COMEX当前H/当天attempt；CNN418，AAII第二轮验证页|
|本地真实weekly端到端|PASS / DEGRADED|官方feed与Fed/BEA/BLS下周日历、FR文种/单文档生效日期；冷启动未积满7份日报；完整法律语义未等价|
|历史样本对比|PASS（核对并保留差异）|COMEX三库存、Ratio、四窗口与当天样本一致；今日Crypto取得51而早晨样本待确认；现货/期货、Treasury额外FRN、官方FR发布日期与公告日差异照实披露|
|GitHub实际执行/手动dispatch/Pages|PASS / DEGRADED|40065487640实际manual both成功，70项测试通过，先归档再Pages；缺失源明确披露|
|未来定时实际运行|UNKNOWN|配置可静态检查，必须未来真正schedule运行才可确认|
|完整原报告语义等价|BLOCKED/NOT ACHIEVED|无付费LLM的确定性系统不能凭标题断言完整法律影响；未知项保留，不能捏造|

首轮67测试曾1项失败：Treasury查询漏未来coupon。改用官方公告接口后检出额外30B FRN，调整为全部coupon213B、固定利率2/5/7Y183B、FRN30B并独立检查类型与AM/PM时间。最终通过不抹去先前失败。

复用范围：旧Gold采集、原报告历史、导出器及40测试；找到了未合并的一致性安全补丁，但本次不混入另一线程对Gold核心模块的额外变更；保持其候选证据供后续独立审阅。新报告档案自己的hash验证独立实现。

双线程收敛：用户2026-10-24明确以本线程继续并停止另一个。检查到另一工作区存在未提交market_intel/intelligence实现，但远端main仍1ed12c3d；未发布第二套系统、未覆盖该工作区、未混算其测试结果。此处仅发布market_reports/market_data这一套，远端提交前后使用预期HEAD检查。


最终补充证据：一次性验收run40065481203成功；360px与390px各检查首页、daily、weekly，body宽度等于viewport，无页面横向溢出，COMEX展开成功；Gold原latest.json/history.csv及market JSON/CSV/registry/quality共7路径HTTP200。下载的JSON证据存evidence-mobile-pages.json/evidence-manual-dispatch.json；截图来自同次真实托管Chromium测试并已人工视觉检查。独立干净远端worktree再跑70项测试通过、17个归档对象核验通过。Total/Registered/Eligible的5D/10D/20D独立Decimal复算9/9见evidence-independent-calculations.json。额外修复了BTC必须使用provider UTC日界（不能用美股ET日界），以及CNN epoch timestamp不代表独立发布时间。

排程未来真实执行仍UNKNOWN；完整原报告语义等价仍NOT ACHIEVED，不因上述工程测试通过而改写。验证时云端CNN/ICI/BLS缺失；网站本身和数据入口正常，缺失不是正常值0。

## v1.1 本地续做结果（部署前）

共93个回归方法通过，较v1.0.1新增23个方法；旧70个不算新增。新增覆盖：OCC实际公告状态、GovInfo两个法案身份/法律记录、cloture非成法、国会行动日与未知发布日期、美东周边界、FR5类分页/重复/失败/元数据错配、明确未来监管截止日、普通clarity/whether非Crypto信号、BTC/ETH直接与间接主题区分、ICI20周单位/类别/13周资产差、BLS错误HTML拒绝、旧capture字节不改、bot故障去重/恢复/人工issue保护。

实际本地端到端生成v2 daily/weekly（29来源）并保持旧档案通过。FR扫469份/5页，4份相关；此段为部署前本地证据；下节单独记录v1.1的真实云端验收。

## v1.1 最终云端验收

源码9136230f5628d3e1a2aabd8a3f6100d3673b75e7，真实manual both运行[40068302153](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/runs/40068302153)成功。云端93项测试0失败；独立新建远端worktree也93项通过，26个归档对象核验，CSV459条；六个v1 capture与两个v2 capture并存，旧档案未重写。

手机验收[40068297391](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/actions/runs/40068297391)成功：360/390px首页、日报、周报全部HTTP200，无页面横向溢出，COMEX展开成功；原Gold和市场共七条数据路径HTTP200。实际托管截图已下载并人工检查。永久JSON证据见evidence/v1.1-mobile-pages.json和v1.1-manual-dispatch.json。

云端29来源receipt，26 OK；CNN418、ICI/BLS403保持缺失。FR完整窗口469份/5页中4份相关；OCC公告与指定CLARITY/GENIUS状态成功读取，未将历史成法或cloture误标本周新成法。health-notice实际运行HEALTHY_NO_INCIDENT，没有制造真实故障issue；创建/去重/恢复/人工issue保护仅模拟测试通过，手机通知送达UNKNOWN。

清单独立核对发现OCC XML fixture在文本上传时CRLF转LF；测试语义相同，但旧hash不一致。已按远端实际字节重新生成MANIFEST，不修改真实数据。首个schedule仍未到时，真实调度UNKNOWN；完整法律语义等价仍NOT ACHIEVED，不能因93项通过而抹去限制。

## v1.2 本地候选验证

109个方法通过（原109中包括既有93+新增16），无跳过。新增覆盖CSV篡改、pointer错误capture/quality/time、路径越界、revision改名、内嵌capture不匹配、缺失capture、report目录/类型、quality漂移、来源观察遗漏、CSV中断无网络恢复且旧档案字节不改、坏capture阻止恢复、当前/历史页面分离、MYT日/周到期与4小时窗口、两报告独立时效、设备时间异常、实际Node执行浏览器脚本。

首次新回归2项旧fixture失败：健康due测试仅改pointer.degraded，旧capture测试缺派生CSV。分别改为真正全OK的合成receipt及从原始capture建立CSV，保留原测试目的，不取消新校验。真实v1/v2旧档案26对象通过增强核验。云端新版及浏览器日期状态尚待验收，旧版成功不代替新版结果。
