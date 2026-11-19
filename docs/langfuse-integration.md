# Langfuse 接入说明

Penguin 使用可选的 Langfuse Python SDK 记录 Agent 执行、模型调用、工具、上下文压缩和 benchmark 结果。默认关闭；关闭时不导入 Langfuse、不发送遥测请求。现有模型供应商和 Agent 执行流程继续使用 Anthropic SDK。

## 安装与配置

在项目根目录执行：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-observability.txt
cp .env.example .env
```

如果已有 `.env`，直接追加 Langfuse 配置。可选依赖锁定 `langfuse==5.2.0`；基础安装 `requirements.txt` 不需要 Langfuse。实现使用 OpenTelemetry 版 SDK API，不使用旧版 `trace()`/`generation()` 接口。

在 Langfuse 项目设置中创建项目 Key，填写：

```dotenv
PENGUIN_OBSERVABILITY_ENABLED=true
LANGFUSE_BASE_URL=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_SAMPLE_RATE=1.0
LANGFUSE_TRACING_ENVIRONMENT=development
LANGFUSE_RELEASE=your-git-commit
PENGUIN_OBSERVABILITY_CONTENT=metadata_only
PENGUIN_OBSERVABILITY_MAX_CHARS=8000
```

`LANGFUSE_BASE_URL` 填项目所在 Cloud 区域或自托管服务地址，不能填模型 API 地址。模型仍使用已有的 `API_KEY`、`BASE_URL`、`MODEL_ID`。`.env` 不进入版本控制。也可直接由部署环境注入变量。

先检查连接，发送一条不包含模型调用的合成 Trace：

```bash
python scripts/check_langfuse.py
```

脚本验证认证、输出 Trace ID；在 Langfuse 中按该 ID 查询。服务器异步入库，界面可能不会立即出现。修改连接配置后重启进程；客户端按进程懒初始化并复用。

然后运行实际任务（会使用配置的模型）：

```bash
python -m src -p "列出当前工作区的文件并给出说明"
python -m src
```

## 配置项

| 配置 | 默认值 | 说明 |
| --- | --- | --- |
| `PENGUIN_OBSERVABILITY_ENABLED` | `false` | `true`/`1`/`yes` 开启 |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | 无 | Langfuse 项目凭证 |
| `LANGFUSE_BASE_URL` | SDK 默认值 | 应显式设置为项目实际地址 |
| `LANGFUSE_SAMPLE_RATE` | `1.0` | 0–1 的 Trace 采样比例；benchmark 建议 1.0 |
| `LANGFUSE_TRACING_ENVIRONMENT` | SDK 默认值 | 开发、测试、生产环境区分 |
| `LANGFUSE_RELEASE` | 无 | 建议填写构建版本或 Git SHA |
| `PENGUIN_OBSERVABILITY_CONTENT` | `metadata_only` | `redacted` 开启经过处理的输入输出；其他值都不采集内容 |
| `PENGUIN_OBSERVABILITY_MAX_CHARS` | `8000` | 内容截断阈值，限制在 256–65536 字符 |

元数据模式记录 ID、模型、参数、耗时、状态、Token 用量等，不上传 prompt、响应正文、工具参数和工具输出。`redacted` 会处理常见密钥字段、Bearer Token 和已配置的模型密钥，并限制嵌套深度、列表长度和单字段内容。业务特定个人信息需要在 `src/observability.py` 的处理规则中补充。

该开关只约束远程观测；原有本地 JSONL、消息文件和 benchmark 报告仍按现有行为保存内容。部署时应分别管理这些本地文件的访问和保留期限。

## 追踪结构与覆盖范围

```text
cli.request / prdbench.run / swebench.instance
  agent.run / swebench.worker
    agent.iteration
      context.compact
        llm.compact.summarize / llm.compact.collapse
        llm.count_tokens
      llm.generate
      tool.read_file / tool.run_command / ...
        agent.subagent
        agent.team_run
        background.submit
          background.execute
```

- CLI 每次输入对应一次 Trace；Session ID 在第一次保存前生成，保存、恢复后保持稳定，`/reset` 开启新 Session。一次性运行也有 Session ID。
- `agent_run_id` 区分主 Agent、同步子 Agent 和队友；`iteration`、`attempt`、`tool_use_id` 用于定位具体轮次、应用层重试和工具调用。
- 模型 Generation 覆盖真正的流式消费，到最终响应读取后结束。首个非空文本或工具 JSON 增量记录首响应时间。中断、取消、截断、API 错误都有独立状态。
- 压缩中的两条非流式模型调用也记录 Generation。`count_tokens` 是普通 Span，不产生虚构的生成用量。主动/被动压缩记录消息数和估算 Token 前后变化。
- 工具 Span 位于真实 dispatcher 执行处；并行任务各复制一份 Context，工具耗时不依赖 UI 回调的回放时间。
- 队友线程及后台 shell 继承发起方上下文。当前实现将它们保留在发起 Trace 中，执行 Span 可以晚于父请求结束；启动耗时与执行耗时分别记录。进程结束会终止未完成的 daemon 线程。
- team 消息保存 `message_id`、发送方 Trace/Span ID；消息关联不改变接收方父 Span。
- JSONL 事件增加 `schema_version=2` 和可用的追踪字段。关闭观测或初始化失败时，没有远程 Trace ID；业务 run/session ID 仍可用于本地关联。回放的工具回调通过 `tool_use_id` 关联执行，回调 Span ID 可能是所在轮次而非工具自身。

工具的权限拒绝、参数校验失败、命令非零退出/超时显式记录。Agent 的 API 错误、上下文溢出、轮次上限和截断终止单独标记。子调用出错后被恢复，不会自动把整个任务标记失败。

## Token 与成本口径

每次模型响应直接读取 `usage`，记录 `input`、`output`、`cache_read_input_tokens`、`cache_creation_input_tokens`。不使用模块全局 `usage_stats` 差分计算 Trace 成本。压缩和队友的用量也包含在各自的 Generation 中。

缓存写入的 5 分钟/1 小时细分保存在 metadata，避免与缓存写入总量重复相加。需要按不同缓存 TTL 精确核算的服务，应进一步配置对应价格映射或导入供应商计算的费用。未知 usage 保持未知，不写成零；流中断未取得完整 usage 时可能少计实际消耗。

`model` 记录实际请求使用的模型 ID。Langfuse 按模型定义和 usage 类型计算费用；自定义别名、代理供应商或合同价格需要在项目 Models 设置中配置匹配规则及价格。未知价格时界面没有费用数据。这里的费用用于运行分析，账单对账仍以供应商为准。

每个 Generation 对应应用发起的一次 SDK 调用。应用层重试、输出上限升级和续写各自保留记录，包括最终被丢弃的响应。Anthropic SDK 内部 HTTP 自动重试可能包含在同一个 Generation 中。

## PRDBench

使用原命令即可，入口自动记录 Trace：

```bash
python -m src.prdbench.run_evaluation --source_dir PRDbench/ --root_path workspace/lf-run --mode dev
python -m src.prdbench.run_evaluation --root_path workspace/lf-run --mode eval
python -m src.prdbench.run_evaluation --root_path workspace/lf-run --mode score
```

独立实验使用不同的输出目录。`experiment_id` 从输出目录派生，项目 DEV/EVAL 使用同一观测 Session；每次执行拥有独立 run 和 Trace ID。整次 Agent 重试在 `prdbench.attempt` 下记录。

- 开发结果 `query_response.json` 保存 Trace ID 和源码摘要 `artifact_id`。
- `reports/<metric>.log` 保存评测 Trace、对应开发 Trace 和产物摘要。
- 校验有效且通过源码完整性检查的单项分数，以 `prdbench.metric.<metric>` 写到开发 Trace；值沿用 0/1/2。
- 评测 Trace 接收 `prdbench.report_valid`、`prdbench.eval_integrity_ok`。
- 汇总写入 `prdbench.project_score`（0–1）和 `prdbench.coverage`，沿用完整测试计划作分母、缺失报告按 0 的现有口径。覆盖率用于区分缺报告与低分。
- 回填检查开发 Trace/产物关联；旧开发任务的报告不会自动挂到新产物上。缺少追踪关联的历史报告不会凭空生成 Trace。
- Score ID 从目标 Trace 和指标名称稳定派生，同一指标重跑会更新当前值；每次评测的执行 Trace 仍独立保留。

`python -m src.prdbench` 的 HTTP `/run` 也支持 W3C `traceparent` 请求头，并在返回事件中携带 `trace_id`、`run_id`。

## SWE-bench

继续使用已有 runner，例如本地 JSONL 输入：

```bash
python scripts/run_swebench.py --dataset-file cases.jsonl --output artifacts/swebench/lf-run --model your-model-id --limit 1
```

主控进程先将 Trace ID 写入每题 `result.json`，再启动 worker。通过 `PENGUIN_TRACEPARENT`、`PENGUIN_SESSION_ID`、`PENGUIN_RUN_ID`、`PENGUIN_EXPERIMENT_ID` 传递上下文；worker 的 `worker_result.json` 和 `events.jsonl` 可关联同一 Trace。

正常退出时刷新剩余事件；worker 超时强杀时由主控记录 `timeout`，保留部分补丁。强杀不能保证 worker 最后一批观测已导出，SDK 队列也不提供进程崩溃后的持久化重放。

官方 harness 评测完成后回填：

```bash
python scripts/import_langfuse_scores.py --run-dir artifacts/swebench/lf-run --report official-report.json
```

支持官方汇总报告中的 `resolved_ids` / `unresolved_ids` / `error_ids`，以及以 instance ID 为键、含布尔 `resolved` 的逐题报告。只为明确评测的样本提交 `swebench.resolved`，跳过基础设施错误和缺失结果。`completed` 仅表示 Agent 执行完成，不会被转换成修复成功。

命令输出 `submitted`、`missing_trace`、`unavailable`。`submitted` 表示 SDK 接收，服务器仍需异步入库；缺失 Trace 或 SDK 不可用返回非零退出码。相同报告可重复导入，Score ID 保持不变。

## 故障处理与运行特性

| 现象 | 检查方式 |
| --- | --- |
| 没有 Trace | 检查开关、可选依赖、两个项目 Key 和正确区域地址；运行 `scripts/check_langfuse.py` |
| 有 Trace 但没有输入输出 | 默认 `metadata_only`；需要内容时设置 `redacted` 并重启 |
| Token 有值但费用为空 | 检查 Langfuse 中模型名称匹配、usage 类型和价格定义 |
| 评测分数未出现 | 检查产物与评测结果文件的 Trace ID、报告有效性、完整性检查及 SDK 日志 |
| 进程异常退出后缺最后几步 | 队列尚未导出；检查本地 JSONL 和主控的终态 |
| 连接失败 | 观测层警告后继续业务；修正配置并重启进程 |

SDK 每进程一个客户端，异步批量导出，批量阈值 128、刷新间隔 2 秒，单次网络请求超时 5 秒；CLI/评测主入口和 worker 在正常退出时 flush。不在逐 Token 路径发送网络请求。通过独立 TracerProvider 和导出过滤器避免导出其他库的 Span。跨进程遵循父采样标记；benchmark 建议全量采集，便于分数与成本对应。

观测初始化、更新、结束及分数提交失败都不会替换业务结果；业务异常仍原样传播。异常正文和 traceback 不交给 OTel 自动上传，只记录类型与终态。应用现有日志仍可能记录异常详情。

Cloud 和自托管使用同一套接入代码。自托管需规划 Web、Worker、PostgreSQL、ClickHouse、Redis/Valkey 和对象存储；请按实际部署版本的官方说明配置备份、保留期限和访问控制。

## 验证

```bash
python -m pip install pytest
API_KEY=test MODEL_ID=test-model PENGUIN_OBSERVABILITY_ENABLED=false python -m pytest -q test/test_observability.py test/test_observability_core.py test/test_observability_concurrency.py test/test_observability_entries.py
```

新增测试使用真实 Langfuse SDK 的内存导出器及模拟模型响应，覆盖关闭模式、父子链路、并发隔离、脱敏、异常降级、流消费/取消、重试与截断、压缩、队友、后台任务、会话恢复、SWE-bench 主控超时和 Score 幂等回填。它们不调用真实模型或远程 Langfuse。真实部署的认证与入库需要用已配置的服务执行连接检查。

基线测试注意事项：干净 checkout 中，`test/test_tools.py` 的部分旧测试依赖未纳入版本控制的 `workspace/test/sort.py`；`test/test_permissions.py::TestPermissionManagerStrict::test_write_file_confirm` 期望 confirm，而当前 strict 配置为 deny。这些失败已在接入前的 `8b52bba` 上复现。HTTP 服务测试需要允许本机 socket。

参考：[SDK 埋点](https://langfuse.com/docs/observability/sdk/instrumentation)、[Token 与费用](https://langfuse.com/docs/observability/features/token-and-cost-tracking)、[Score API](https://langfuse.com/docs/evaluation/evaluation-methods/scores-via-sdk)、[自托管选择](https://langfuse.com/resources/engineering/self-hosted-vs-cloud)。
