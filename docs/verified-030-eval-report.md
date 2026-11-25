# verified-030 SWE-bench 测评报告(glm-5.3-flash)

- 测评窗口:2026-11-23 ~ 2026-11-24
- 验证集合:verified-030(SWE-bench_Verified 分层抽样 30 题,seed=20261123)
- 模型:glm-5.3-flash(兼容 Anthropic Messages 接口)
- 最终成绩:**19/30 resolved(63.3%),unresolved 11,error 0**
- 合并预测:`artifacts/swebench/verified-030-glm-merged-predictions.jsonl`
- 评分报告:`logs/run_evaluation/verified030-glm-*` 与 `artifacts/swebench/reports/penguin-glm-5.3-flash.verified030-*.json`
- 全程 Langfuse 全量追踪(1968 次 LLM 请求、2187 次工具调用,span 级输入输出完整落库)

## 1. 最终结果

### 1.1 按 repo 分布

| repo | resolved/总 | 备注 |
|---|---|---|
| xarray | 2/2 | 效率最高(单题 ~10 分钟) |
| flask / requests / seaborn | 3/3 | 新时代 repo,宿主机测试可跑 |
| pytest | 2/2 | |
| django | 4/7 | 11265/11490/12304/16901 过 |
| sklearn | 2/3 | |
| sympy | 2/4 | 老 sympy(py3.6 时代)宿主机无法 import |
| astropy | 1/2 | 7166 补评过,8872 未过 |
| matplotlib | 2/3 | 26208 跑满 100 轮 iteration_limit |
| **sphinx** | **0/3** | 全军覆没,见 §3.2 |
| **pylint** | **0/1** | 同上 |

### 1.2 逐题状态

- Resolved(19):astropy-7166、django-11265/11490/12304/14999/16901、matplotlib-22719/23412、seaborn-3069、flask-5014、requests-5414、xarray-4094/7233、pytest-7432/7571、sklearn-13135/15100、sympy-13878/14711
- Unresolved(11):astropy-8872、django-11400/11885、matplotlib-26208、pylint-4970、sklearn-25102、sphinx-11510/7985/8459、sympy-16597/20428
- 11 个 unresolved 全部含非空 patch(493B–5713B),其中 3 题为 iteration_limit 出口;patch 均已随合并 predictions 评分判定

### 1.3 生成阶段的出口统计(30 题)

- completed 27、iteration_limit 3(跑满 100 轮仍导出 patch)
- api_error 曾出现 5 题,全部由 API 配额(5 小时滚动 code 1308 / 周月 code 1310)或瞬时网络错误打断,重跑后清零
- 单题耗时:5 分钟 ~ 2.8 小时,平均 ~40 分钟;timeout 7200s 从未成为决定性出口

## 2. 执行行为分析(Langfuse 全量数据)

### 2.1 延迟瓶颈:模型 API 首字节等待占 87%

| 时间构成 | 总量 | 占比 |
|---|---|---|
| LLM 等首字节(TTFT) | 722 分钟 | 占 LLM 时间 **87.1%** |
| LLM 流式生成 | 106 分钟 | 13% |
| 工具执行 | 260 分钟 | (LLM+工具)总 1088 分钟 |

- 单请求:平均 25.3s,p90 72.6s,最长 722s;glm 接口"服务端基本生成完才吐字节",客户端表现为 9–13 分钟"挂起"后瞬间吐完
- 工具侧异常消耗:6 次 run_command timeout(370s 上限,共 ~37 分钟)+ 3 次 search_files timeout
- **结论:87% 等待在模型服务端,本地优化(工具、并行、日志)收效甚微;提速只有换更快的端点或降低单请求输出量(减少整文件重写)**

### 2.2 工具调用质量:结构错误率 0.1%

- 2187 次调用,invalid_arguments 仅 2 次;30 次 permission_denied 全部是权限系统按设计拦截(repo 外写 `/tmp`、`$()` 替换、rm 类 CONFIRM→deny),无一次造成任务失败
- run_command 非零退出 121 次 = "跑测试失败"的正常探索,非模型失误
- 真正的模型幻觉/失误 ~12 次(0.5%):幻觉绝对路径(`/home/featurize/repo/...`)、目录名拼错(漏 `glm`)、`path: false` 类型错乱、引用不存在的 build 产物、edit_file 参数冲突(2)、pylint 老 API 臆断——共性是**未先 ls/read 验证路径就直接操作**,全部自愈

### 2.3 环境适应行为(宿主机模式的典型轨迹)

以 sympy-16597 为例,模型面对"跑不了测试"呈现四级适应阶梯,从不轻易放弃:

1. 探测(`pip list | grep`、`python -c "import sympy"`)
2. 正常安装(30 次 pip install,28 成功)
3. 手工构造环境:从 PyPI 下载老版 wheel(1.4/1.5)解压到 /tmp、写 Python 3.11 兼容 shim
4. 放弃"跑测试"这个动作,转入静态推理盲改——方向常对(sympy-16597 的 `integer -> finite` 正是标准修法)但没有验证,天花板明显

### 2.4 工具调用幻觉现象与归因

工具 ERROR 中剔除权限拦截与正常试错后,存在 ~12 次**模型幻觉/失误**(占 2187 次调用的 0.5%)。全部自愈,但模式值得记录:

#### 现象清单(按根因分类)

| 根因 | 现象实例 | 出处 | 次数 |
|---|---|---|---|
| **路径凭记忆拼接** | run_command `cd` 到不存在的目录 | pytest-7432 用 `verified-030-20261123T083900Z`(漏 `glm` 段);django-11265 同类 `cd: can't cd` | ~4 |
| **幻觉绝对路径** | edit_file 指向 `/home/featurize/repo/sphinx/builders/linkcheck.py`——该路径在实例上从未存在 | sphinx-7985 | 1 |
| **版本错配幻觉** | edit_file 编辑 `repo/sphinx/build/...`(fresh checkout 无构建产物);search_files grep `choices.py`(该 django 版本文件已改名) | sphinx-7985、django-12304 | ~3 |
| **类型错乱** | read_file 传入 `path: false`(把布尔表达式结果当路径) | matplotlib-23412 | 1 |
| **调用形态混淆** | edit_file 同时提供 `edits` 数组与 `old_string`/`new_string`(二者互斥) | sphinx-7985 | 2 |
| **API 版本臆断** | 按训练记忆的旧 API 调用 `PyLinter.check(jobs=...)`,宿主机新版报 TypeError | pylint-4970 | 1 |

#### 根因分析

1. **长路径靠记忆复述,不做验证**。workspace 前缀(`/home/featurize/work/penguin-coding/artifacts/swebench/verified-030-glm-20261123T083900Z/...`)长达 80+ 字符,模型从上下文"背写"时漏段/错段;且写绝对路径前从不先 `ls` 验证目录结构。
2. **训练语料的版本先验污染**。模型对知名 repo(sphinx/pylint/django)带着训练时的文件结构记忆,fresh checkout 与记忆不符时,模型按记忆编造路径与文件名(build 产物、已改名模块),而非先探查。
3. **同工具多调用形态未做互斥校验**。edit_file 同时支持 `edits` 数组和 `old_string`/`new_string` 两种形态,schema 未声明互斥,模型偶尔同时给出;dispatcher 的 `_validate_args` 不拦(只校验类型不校验互斥)。
4. **依赖 API 签名凭训练记忆**。调用宿主机上与其训练版本不同的库时,不先读源码确认签名。

#### 防御建议(按成本排序)

1. **system prompt 规约**(零成本):增加"访问任何路径前先 `ls`/`list_directory` 确认;调用库函数前先读源码确认签名"
2. **dispatcher 校验**(低成本):edit_file 互斥形态校验;file 工具 path 类型严格校验(bool/number 直接 invalid_arguments)
3. **相对路径优先**(低成本):工具已支持相对 workspace 的路径,在 system prompt 中引导模型用相对路径,消灭长前缀拼错问题
4. **路径提示回显**(中成本):file-not-found 错误消息中回显 workspace 实际路径与相似目录列表,帮助模型自我纠正(实测模型被拒后自愈率 100%,但每次浪费 1–2 轮)

### 2.5 上下文压缩:0 次触发——根因是 token 基准被缓存语义破坏(已修复)

30 个 `context.compact` span 全部是 proactive 初始化占位(消息 1→1,耗时 0)。事后归因不是阈值太高,而是**触发基准被 prompt 缓存语义破坏**:

- 机制:`needs_compaction` 以 API 上报的 `input_tokens` + 本轮增量为基准,超过 `MAX_CONTEXT_TOKENS(100k) × 70%` 触发 L2 摘要
- 实测:glm 网关启用自动 prompt 缓存,`input_tokens` 只计**未缓存增量**(中位 474 tokens),缓存前缀单独报在 `cache_read_input_tokens`(中位 25.2k)——`input + cache_read` 才是真实 prompt(p50 25.9k / p90 51.4k / **max 74.7k**,与 messages.json 字符估算 75.6k 交叉吻合)
- 后果:基准 ~474 而非 ~25.7k,永不越过 70k 触发线;5 题估算峰值 65–76k tokens(sklearn-25102 最高)在应该压缩的区间运行而未压缩;被动的 400 "prompt too long" 恢复路径也从未触发(glm 窗口 200k 级,离硬限很远)
- 上下文膨胀的实际代价:TTFT 尾部加长、老消息挤占;199–203 条消息的题(sphinx-7985/seaborn-3069/matplotlib-26208)均已处于应压缩区间
- **修复**:`stream_response` 的 usage 事件改为上报 `input_tokens + cache_read_input_tokens`(有效 prompt 尺寸),`needs_compaction` 无需改动即可在真实 70% 处触发;附回归测试(test_observability_core.py,含 cache_read 场景)

**工具输出限制**(减缓增长的有效机制,与主流一致):原始命令输出截断 `MAX_OUTPUT_LENGTH=30,000` 字符,进入上下文的工具结果截断 `MAX_TOOL_RESULT_CHARS=10,000` 字符。

**主流 coding agent 对照**(约值,随版本变动):Claude Code 200K 窗口、接近上限自动 compact(~92–95%,依赖精确 token 计数)、Bash 输出截断 30,000 字符;Gemini CLI 1M 窗口、~70% 触发压缩(与本机同比例);Codex CLI 128–272K 窗口、命令输出 ~10KiB;SWE-agent 观察 ~4K token 级截断;OpenHands 长观察 ~10k 字符截断。共同点是压缩都依赖可信的 token 计数——本机输在 glm 的缓存语义上,而非阈值设定。

### 2.6 文件读取两级截断 → edit 漏匹配(已修复)

edit_file 的 16 次 `old_string not found` 并非全是模型记忆偏差,**结构性根因是两级截断叠加后,模型从未见过目标编辑区**:

1. `read_file` 最多读 `MAX_READ_SIZE=100KB`,超出时在**尾部**追加截断警告;
2. 工具结果进上下文时 `parallel_executor` 统一调 `_truncate_for_context(10k 字符)`:保留**头 5k + 中间标记 + 尾 5k**。

叠加后果:大文件(>10k 字符)模型只能看到头 5k 和尾 5k,**中段(编辑目标最常在的位置)不可见**——且尾部警告恰好被保留,给了模型"我已看到全部内容"的错觉。模型凭印象拼 old_string → 匹配失败 → 升级为整文件重写(与 §2.1 的超长响应问题在此汇合:重写正是超长响应的主要来源)。

**修复**:
- `read_file` 新增 `offset`(1-based 行号)/ `limit` 分页参数,返回头部带 `[Showing lines X-Y of Z total]` 行号定位,未读完时提示 `use offset=N+1 to read more`
- `edit_file` 失败提示带**锚点行号**(`_nearest_match_hint`):old_string 首行在文件中出现的行号 + "用 `read_file offset=N` 重读该区域再试精确文本"
- 回归测试 4 个(分页/越界/锚点提示/参数互斥),失败集合与基线一致

### 2.7 iteration_limit 机制、实测代价与预算感知收敛(已实现)

**机制**:worker 以 `max_iterations=100` 启动;每轮注入迭代感知提示;模型调 `exit_loop` 为正常出口;轮数耗尽 → `iteration_limit`(finally 仍导出 patch)。

**实测代价**:3 题触发(matplotlib-26208/seaborn-3069/sphinx-7985),**全部 unresolved**,烧掉 75 分钟–2.8 小时;seaborn-3069 同一命令连打 5 次——后半程为纯空转。但 django-11265 92 轮才 completed,说明**轮数 ≠ 进展**,不能简单砍数字。

**业界对照**:SWE-bench 系脚手架(SWE-agent/OpenHands/mini-swe-agent)均有硬上限(~30–100 steps,评测需要确定性边界);交互式 CLI(Claude Code/Codex CLI)无硬上限,靠模型自停 + 上下文压缩 + 用户打断。本项目两者兼具,保留硬上限合理。

**已实现——预算感知收敛**(`BUDGET_FINALIZE_RATIO=0.85`,`_budget_hint`):
- remaining ≤ 5:`Budget exhausted`——停止探索,立即 exit_loop
- remaining ≤ 15%(>85% 已用):`Budget nearly exhausted`——不再开新调查,收敛当前最佳修复
- 其余:Keep working
- 替换了原来自相矛盾的 `remaining ≤ 5 → "Keep working"`;效果是把"耗尽被掐断"变成"主动收尾",导出 patch 的完成度更高

**规划中——no-progress tracker**:重复命令(≥3 次)/主要命令结果哈希连续不变(≥2 轮)/连续 ≥5 轮无成功写操作 → 两级 verdict(warn → finalize)注入迭代提示;真实进展(edit/write 成功、新结果哈希)即重置。与预算收敛互补:预算管"还剩多少",tracker 管"是否在原地打转"。

## 3. 经验与教训

### 3.1 运营层

1. **API 配额是最大运营风险**:5 小时滚动限额 + 周/月限额会打断长跑(本轮共 5 题 api_error 全源于此)。长跑前确认配额窗口;中断后换新输出目录 + `--instance-ids` 重跑,勿原目录重试
2. **评分的 eval 镜像是消耗品**:harness 每次评测后清理实例镜像;若镜像已存在则跳过构建——**预构建 + 立即评测**是绕过网络抖动的可靠手段
3. **Docker 内 GitHub clone 高频 TLS 中断**(GnuTLS -110 / HTTP2 framing),宿主机正常:大仓库 clone 失败时重试即可;根治方案是把本地 repo 打 tar 注入构建上下文,替换 setup_repo.sh 的 clone 行(需加 `git config --global safe.directory`,否则 dubious ownership)
4. **不要 `docker commit` 业务容器**注入配置——会连带捕获 CMD/ENTRYPOINT,导致 harness 的 `tail -f /dev/null` 被 bash 当脚本名执行、容器秒退。正确做法:`printf 'FROM <image>\nENTRYPOINT []\nCMD []\n' | docker build -t <image> -`
5. **老 astropy 需要 `pip install --no-build-isolation`**(新版 setuptools 无 pkg_resources);sklearn-25102 的脚本含新版 pip 已删除的 `--no-use-pep517`,需去掉
6. **多会话并行时小心互踩**:用户侧会话与 Claude 会话同时操作同一输出目录/镜像,会产生难以追踪的清理竞争;评分产物目录(`logs/run_evaluation/`)按 run_id 隔离是有效的
7. 每 3 分钟的例行汇报(CronCreate)+ 事件监控(Monitor)组合被证明适合数小时级长跑的看护;杀后台任务时注意 kill 模式不要匹配到自己的包装 shell

### 3.2 模型/流程层

1. **宿主机模式有系统性天花板**:Python 3.11 跑不了老 repo 测试 → 模型被迫走 §2.3 的盲改路线。sphinx 0/3、pylint 0/1 部分归因于此。**已将 skill 默认改为 Docker 模式**(`--docker --dataset`),env 镜像跨 run 复用
2. **换模型/换网关时必须校验 usage 语义**:glm 的 `input_tokens` 只计未缓存增量,缓存前缀在 `cache_read_input_tokens`;依赖单一字段的控制逻辑(压缩、计费、限速预估)会被系统性欺骗。教训:**一切以 token 为基准的控制回路,都要与本地估算交叉验证**,不可信上_provider 单字段
3. **sphinx/pylint 类(repo 自带测试基建复杂、依赖文档构建)是弱项**:即使环境正确也可能因测试基建跑不通而盲改;后续可对这两个 repo 单独分析 run_instance 日志
4. **模型幻觉路径(0.5%)可通过规约压缩**:system prompt 增加"操作路径前先 ls/read 验证"一条即可
5. **iteration_limit 不是浪费**:跑满 100 轮的题仍导出了可用 patch(seaborn-3069 patch 5.7KB),交评分判定即可,不必盲目重跑;但 3 个 iteration_limit 题全部 unresolved,后半程空转代价真实(§2.7)——已实现预算感知收敛(`BUDGET_FINALIZE_RATIO=0.85`)并在 system prompt 中加入 PATCH DISCIPLINE(最小 diff/禁止整文件重写/edit 失败先重读/路径先验证/命令显式 timeout/不重复执行)
6. **工具结果的截断警告必须放在内容头部**:尾部警告会被下游"头尾保留、中段丢弃"式截断切掉或形成"已见全文"错觉;read_file 已改为行号定位头 + offset/limit 分页,edit_file 失败提示带锚点行号(§2.6)
6. **单请求输出量影响延迟**:39K token 级的整文件重写响应一次就吃掉 ~12 分钟;在 system prompt 中强调最小化 diff 有望降低 TTFT 尾部压力

### 3.3 权限与沙箱

- 宿主机模式:permission 机制是唯一防线,不要放开;profile=permissive + headless(CONFIRM→deny)下,30 次 denied 全部正确拦截,代价可忽略
- Docker 模式:保护对象降级为"容器内未提交工作 + testbed 环境",已实施两项放开:`PRDBENCH_MODE=true`(豁免 `$()`)与 `CODE_AGENT_EXTRA_ALLOWED_DIRS=/tmp`(放行容器本地 /tmp);DENY(真破坏性)与 CONFIRM(rm 类)保留

## 4. 流程时间线(备查)

| 时间(UTC) | 事件 |
|---|---|
| 11-23 08:39 | 主生成 run 启动(宿主机模式) |
| 11-23 17:38 | API 5h 限额打断,仅完成 6 题 |
| 11-24 01:41 | 实例重租、环境恢复后 `--resume` 续跑 24 题 |
| 11-24 06:59 | 5 个 api_error 题 retry2 重跑(parallel 3) |
| 11-24 15:41 | retry2 完成:5/5 completed |
| 11-24 17:xx | 合并 predictions;官方评分启动 |
| 11-24 19:41 | 三轮评分(主 + netretry + final14/7166)全部完成,合计 19/30 resolved |
| 11-24 20:00~ | Langfuse 行为分析:TTFT 87% 瓶颈、压缩 0 触发根因(缓存语义)、两级截断漏匹配、iteration_limit 空转 |
| 11-25 | 修复落地:压缩基准(input+cache_read)、read_file offset/limit 分页、edit 锚点提示、预算感知收敛(0.85)、PATCH DISCIPLINE system prompt、docker 模式权限放开;env 镜像存档 30.7GB |

## 5. 下一步建议

1. 换模型对比时直接用 docker 模式 + 现存 env 镜像(同题环境成本为零)
2. 对 unresolved 11 题可做一次 docker 模式重生成(让模型看到真实测试结果),评估盲改 vs 真环境的差距
3. sphinx/pylint 弱项单独归因:读 `logs/run_evaluation/*/sphinx-doc__*/run_instance.log` 的测试输出
4. 归还实例前按 runbook §1/§6 核对产物持久化;env 镜像已存档(`images-env-verified030.tar.gz`,30.7GB,gunzip -t 校验通过)
5. 下轮跑分验证 agent 改进集(最小 diff 规约、预算收敛、压缩修复)的量化效果:对比轮次分布、超长响应次数(基线 92 次 ≥10k)、重复命令数(基线 18 次)
