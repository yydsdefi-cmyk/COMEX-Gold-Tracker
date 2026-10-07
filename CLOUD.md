# 云端采集与晨报接入

架构：GitHub Actions → CME 官方 XLS → 校验/原始文件归档 → Git 持久化历史 → GitHub Pages 数据文件。
不调用 OpenAI API，不使用本机排程。仓库和数据文件公开，只上传本项目代码及公开 CME 报告。

已部署：[数据入口](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/)、[JSON](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/latest.json)、[独立仓库](https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker)。
实际晨报接入规则见 [MORNING_BRIEF_INTEGRATION.md](MORNING_BRIEF_INTEGRATION.md)，包含已验证的 GitHub 文件读取备用路径。

## 排程

每天 Asia/Kuala_Lumpur 05:17、07:17、07:41，三个独立尝试。GitHub 的排程可能延迟，不能承诺 8AM 前一定更新。
失败也会发布 `update_status=FAILED` 和具体时间，保留上次核验数据，不把旧数据说成今日数据。
公开仓库的排程可能因 60 天无仓库活动而禁用；成功的采集会产生归档提交，但长期平台停机仍需检查 Actions。

## 发布文件

`latest.json`、`latest.txt`、`daily_brief.md`、`history.csv`、`validation.json`、`health.json`、`manifest.json`。
根页面只有同一份文字和数据链接，供浏览工具读取，不是 dashboard。
当前报告原始文件也按 `latest.json.provenance.raw_path` 发布；全部原始历史保存在仓库 `data/raw/`。

每次消费都比较 `last_update.attempted_at_utc` 与当前 UTC 时间，超过 26 小时标记云端更新逾期。
`health.json` 和 `freshness` 都是生成时的静态快照，不能因为缓存中的状态正常就断言现在正常。
同时核对 Activity Date、Report Date 与当前日期；节假日尚未分类，报告日期时效采用保守工作日规则。

## 部署设置

独立仓库默认分支必须为 `main`。Settings → Pages → Build and deployment → Source 选 **GitHub Actions**。
仓库 Actions 应允许标准 action，并允许本工作流的 `contents: write`（历史保存）、`pages: write`、`id-token: write`。
首次推送会运行；以后也可 Actions → Collect and publish COMEX Gold → Run workflow。
如 Git 推送失败，发布停止，以免未经持久化的历史对外报告为成功。

本机验证/导出：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -q
.\.venv\Scripts\python.exe -m comex_gold update
.\.venv\Scripts\python.exe -m comex_gold.cloud --output-dir public-data
```

导出目录必须是新目录，避免带入旧文件或本机其他文件。不要将 `.venv`、访问令牌或账户资料上传。

## 晨报任务提示词

把下面规则加入现有 8AM 晨报任务；部署后以真实数据地址替换 `DATA_BASE_URL`。

```text
COMEX Gold 必须实际打开 DATA_BASE_URL/latest.json，并以 DATA_BASE_URL/latest.txt 或根页面作为文字读取备用。
不能使用上一轮对话中的数字或搜索摘要作为本次最新数据。若工具拿不到上述内容，明确写“云端数据无法读取”，不猜数值。
读取 last_update.attempted_at_utc，和本次运行的当前 UTC 时间比较；超过 26 小时写“云端更新逾期”，不得引用静态 health 正常来覆盖。
update_status 为 FAILED、available 为 false、freshness 为 STALE，或者报告日期已明显过旧时明确标注。
始终显示 Activity Date、Report Date、Total、Registered、Eligible、Registered Ratio、1D、5D、20D 与实际来源链接。
null 或不可计算保持“暂不可计算”，不能写成 0；旧数据只能写成“上次可得数据（日期）”。
Pledged 已包含在 Registered，不重复加。Eligible 单独下降不等于可交割黄金短缺。
NORMAL 仅指总库存单日变化未触发库存阈值，不是黄金市场风险判断。
```

数据采集不依赖 OpenAI 订阅；晨报是否按时发送、能否浏览此地址，仍取决于 ChatGPT 任务本身的账户能力和运行工具。
接入成功需在实际晨报任务中完成一次真实读取，不能仅凭云端部署就声称已接入。

## 失败排查

- Actions 下载超时/403/429：查看 `fetch_status.json`；不绕过 CME 访问控制。云端网络若持续被拒，保留失败状态并换获授权的运行环境。
- Pages 404：核对 Source=GitHub Actions、部署 job 是否成功。
- `git push` 被拒：核对 Actions 写入权限、main 分支保护及并发人工提交；不强制覆盖。
- 5D/20D 缺失：当前真实报告不足或存在未分类日期间隙；从已取得的官方报告积累，不填造数据。

参考：[GitHub Pages 工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)、[GitHub 排程限制](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。

